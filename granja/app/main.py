import logging
import schedule

from pymongo import MongoClient
from bson.errors import InvalidId
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List


from .events import Emit


app = FastAPI()
mongodb_client = MongoClient("granja_service_mongodb", 27017)

emit_events = Emit()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')




class Constructions(BaseModel):
    id: str | None = None # "posX,posY"
    posX: str
    posY: str
    userId: str
    hasPlant: bool
    plantId: str
    readyToPlant: bool
    daysTillDone: int
    isWatered: bool

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)

class Plants(BaseModel):
    id: str | None = None
    name: str
    daysToGrow: int
    lifeExpectancy: int
    minHarvest: int
    maxHarvest: int
    description: str

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)

class User(BaseModel):
    id: str | None = None
    currentSize: str
    maxSize: str
    constructions: List[Constructions]
    
    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)

@app.get("/")
async def root():
    logging.info("👋 Hello world (end-point)!")
    return {"Hello": "World"}


@app.post("/build")
async def plant_request(userId: str, plantId: str, posX: str, posY: str):
    try:
        #Get de BD para comprobar estado de slot para plantar...
        farm = mongodb_client.service_01.players.find(userId)
        slot = farm["construcciones"][posX+','+posY]
        if slot["isAvailable"]:
            plantInfo = mongodb_client.service_01.plants.find(plantId)
            slot["plantId"] = plantId
            slot["isAvailable"] = 0
            slot["grownDays"] = 0
            slot["hasPlant"] = 1
            slot["daysTillDone"] = plantInfo["daysTillDone"]
            slot["hp"] = plantInfo["hp"]
        mongodb_client.service_01.players.update_one(
            {'_id': userId}, {"$set": slot}
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Position not available:["+posX+","+posY+"].")



@app.post("/harvest/{construction_id}")
def harvest(construction_id: str, construction: dict):
    try:
        construction_id = ObjectId(construction_id)
        mongodb_client.service_01.constructions.update_one(
            {'_id': construction_id}, {"$set": construction})

        emit_events.send(construction_id, "update", construction)

        return Constructions(
            **mongodb_client.service_01.players.find_one({"_id": construction_id})
        )

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Construction not found")
    return

@app.get("/users", response_model=list[User])
def users_all():
    return [User(**user) for user in mongodb_client.service_01.users.find()]

@app.post("/users")
def users_create(user: User):
    inserted_id = user.id

    new_user = User(
        **mongodb_client.service_01.users.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    emit_events.send(inserted_id, "create", new_user.dict())

    logging.info(f"✨ New user created: {new_user}")

    return new_user

## New Day Flow

def newDay():
    # para cada usuario
    var currUser = User()
    # Consulta lluvia
    isNotRaining = False
 
    for construction in currUser.constructions:
        if construction.posX in range(int(currUser.currentSize.split(',')[0])):
            if construction.posY in range(int(currUser.currentSize.split(",")[1])):
                if construction.isWatered:
                    construction.dayStillDone =- 1
                    construction.daysToGrow += 1
                    if isNotRaining:
                        construction.isWatered = False
    
    return

schedule.every().day.do(newDay())

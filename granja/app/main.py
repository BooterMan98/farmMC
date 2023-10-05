import logging
import schedule
import json

from pymongo import MongoClient, InsertOne
from bson.errors import InvalidId
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List
import json

from .events import Emit

app = FastAPI()
mongodb_client = MongoClient("granja_service_mongodb", 27017)

emit_events = Emit()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

   

class Constructions(BaseModel):
    id: str | None = None # "posX,posY"
    posX: int
    posY: int
    hasPlant: bool
    plantId: str
    isBuilt: bool
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
    userId: str | None = None
    currentSize: str
    maxSize: str
    nextTier: int
    constructions: List[Constructions]
    
    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)

mongodb_client.service_01.User.create_index([("userId", 1)], name="user_index", unique=True)

@app.get("/")
async def root():
    logging.info("👋 Hello world (end-point)!")
    return {"Hello": "World"}


@app.post("/harvest/{construction_id}")
def harvest(construction_id: str, construction: dict):
    try:
        construction_id = ObjectId(construction_id)
        mongodb_client.service_01.constructions.update_one(
            {'_id': construction_id}, {"$set": construction})

        emit_events.send(construction_id, "update", construction)

        return Constructions(
            **mongodb_client.service_01.users.find_one({"_id": construction_id})
        )

    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Construction not found")
    return

@app.post("/plants")
async def plant_request(userId: str, plantId: str, posX: str, posY: str):
    try:
        #Get de BD para comprobar estado de slot para plantar...
        farm = mongodb_client.service_01.users.find(userId)
        slot = farm["construcciones"][posX+','+posY]
        if slot["isBuilt"]:
            plantInfo = mongodb_client.service_01.plants.find(plantId)
            slot["plantId"] = plantId
            slot["isAvailable"] = 0
            slot["grownDays"] = 0
            slot["hasPlant"] = 1
            slot["daysTillDone"] = plantInfo["daysTillDone"]
            slot["hp"] = plantInfo["hp"]
        mongodb_client.service_01.users.update_one(
            {'_id': userId}, {"$set": slot}
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Position not available:["+posX+","+posY+"].")

@app.get("/users/all", response_model=list[User])
def users_all() -> List[User]:
    try:
        userList = mongodb_client.service_01.users.find()
        return [User(**user) for user in userList]

    except:
        HTTPException(status_code=404, detail="Something wasn't found")

@app.get("/users/{user_id}")
def users_get(user_id: str) -> User:
    try:
        return User(
            **mongodb_client.service_01.users.find_one({"userId": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/plants", response_model=list[Plants])
def plants_all():
    return [Plants(**plant) for plant in mongodb_client.service_01.plants.find()]

@app.post("/users")
def users_create(id: str) -> User:
    userDict = {}
    constructions = []
    for i in range(10):
        for j in range(10):
            if i < 3 and j < 3:
                constructions.append({'posX': i, 'posY': j, 'hasPlant': False, 'plantId': '', 'isBuilt': True, 'daysTillDone': 0, 'isWatered': False, 'nextTier': 4})
            else:
                constructions.append({'posX': i, 'posY': j, 'hasPlant': False, 'plantId': '', 'isBuilt': False, 'daysTillDone': 0, 'isWatered': False, 'nextTier': 4})
    userDict = {'userId': id, 'currentSize': str(3), 'maxSize': str(10), 'constructions': constructions, 'nextTier': 4 }
    inserted_id = mongodb_client.service_01.users.insert_one(userDict).inserted_id

    new_user = User(
        **mongodb_client.service_01.users.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )
    emit_events.send(inserted_id, "create", new_user.dict())

    logging.info(f"✨ New user created: {new_user}")

    return new_user


@app.post("/newplant")
def plants_create(user: Plants):
    #inserted_id = user.id
    inserted_id = mongodb_client.service_01.plants.insert_one(
        user.dict()
    ).inserted_id

    new_plant = Plants(
        **mongodb_client.service_01.plants.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    emit_events.send(inserted_id, "create", new_plant.dict())

    logging.info(f"✨ New user created: {new_plant}")

    return new_plant

#insertPlants()
@app.post("/upgradeFarm")
def upgrade(userId: str) -> User:
    try:
        currentUser = mongodb_client.service_01.users.find(userId)
    except:
        raise HTTPException(status_code=404, detail="User not found")
        
    if currentUser.nextTier == -1:
        raise HTTPException(status_code=403, detail="Maximum upgrades reached")

    try:
        url = f"http://dummy_service:80/checkConstructionViable?tier={currentUser.nextTier}&userId={userId}"
        isUpgradeViable = requests.get(url).json()
        if isUpgradeViable:
            url = f"http://dummy_service:80/buyConstruction?tier={currentUser.nextTier}&userId={userId}"
            purchaseSuccesfull = requests.get(url).json()
            if purchaseSuccesfull:
                changes = upgradeFarm(currentUser)
    except:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        mongodb_client.service_01.users.update_one({'_id': userId}, {"$set": changes})
        returnValue = mongodb_client.service_01.users.find_one(userId)
        return User(**returnValue)

def upgradeFarm(user: User):

    currentSize = int(user.currentSize)
    constructions = user.constructions.copy()
    nextTier = user.nextTier
    for j in range(currentSize):
        constructions[currentSize][j].daysTillDone = 2
    for i in range(currentSize):
        constructions[i][currentSize].daysTillDone = 2
    nextTier += 1
    currentSize += 1


    return {constructions, nextTier, str(currentSize)}



## New Day Flow
def newDay():
    # para cada usuario
    try:
        users = mongodb_client.service_1.User.find()
    except:
        print("error")
    else:
        for user in users:
            url = f"http://dummy_service:80/weather"
            isRaining = requests.get(url).json()
            constructions = user.constructions.copy()
            for construction in constructions:
                if construction.posX in range(int(user.currentSize.split(',')[0])):
                    if construction.posY in range(int(user.currentSize.split(",")[1])):
                        if construction.isBuilt and construction.isWatered:
                            construction.daysTillDone =- 1
                            construction.daysToGrow += 1
                            if not isRaining:
                                construction.isWatered = False
                        if not construction.isBuilt and construction.daysTillDone > 0:
                            construction.daysTillDone =- 1
                            construction.isBuilt = True if construction.daysTillDone == 0 else False
        
            try:
                mongodb_client.service_1.User.update_one({"userId": user["userId"]}, {"$set": {"constructions": construction}})
            except:
                raise HTTPException(status_code=404, detail="User not found")


    return

schedule.every().day.do(newDay)

@app.get("/newDay")
def manualNewDay():
    newDay()

schedule.every().day.do(newDay)


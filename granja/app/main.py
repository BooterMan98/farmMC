import logging
import schedule
import json

from pymongo import MongoClient, InsertOne
from bson.errors import InvalidId
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
import json

from .events import Emit


def getPlants():
    jsonPath = './plants.json'
    try:
        with open(jsonPath, 'r') as json_file:
            plantsData = json.load(json_file)

        # Now, 'data' contains the contents of the JSON file as a Python variable
        print(plantsData)
        return plantsData
    except FileNotFoundError:
        print(f"The file '{jsonPath}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

app = FastAPI()
mongodb_client = MongoClient("granja_service_mongodb", 27017)

emit_events = Emit()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

'''
def getPlants():
    jsonPath = './plants.json'
    try:
        with open(jsonPath, 'r') as json_file:
            plantsData = json.load(json_file)

        # Now, 'data' contains the contents of the JSON file as a Python variable
        print(plantsData)
        return plantsData
    except FileNotFoundError:
        print(f"The file '{jsonPath}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")  
'''

def insertPlants():
    collection = mongodb_client.plants
    requesting = []
    with open(r"./plants.json") as f:
        for jsonObj in f:
            myDict = json.loads(jsonObj)
            requesting.append(InsertOne(myDict))

    result = collection.bulk_write(requesting)
    client.close()

class Constructions(BaseModel):
    id: str | None = None # "posX,posY"
    posX: int
    posY: int
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
    userId: str
    currentSize: str
    maxSize: str
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

@app.post("/plants")
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

@app.get("/users/all", response_model=list[User])
def users_all():
    try:
        userList = mongodb_client.service_01.users.find()
        return [User(**user) for user in userList]

    except:
        HTTPException(status_code=404, detail="Something wasn't found")

@app.get("/users/{user_id}")
def users_get(user_id: str):
    try:
        user_id = ObjectId(user_id)
        return User(
            **mongodb_client.service_01.users.find_one({"_id": user_id})
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/plants", response_model=list[Plants])
def plants_all():
    return [Plants(**plant) for plant in mongodb_client.service_01.plants.find()]

'''
@app.post("/users")
def users_create(user: User):
    #inserted_id = user.id
    inserted_id = mongodb_client.service_01.users.insert_one(
        user.dict()
    ).inserted_id

    new_user = User(
        **mongodb_client.service_01.users.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    emit_events.send(inserted_id, "create", new_user.dict())

    logging.info(f"✨ New user created: {new_user}")

    return new_user

'''
@app.post("/users")
def users_create(id: str):
    userDict = {}
    constructions = []
    for i in range(10):
        constructions.append({'posX': i, 'posY': i, 'hasPlant': False, 'plantId': '', 'readyToPlant': False, 'daysTillDone': 2, 'isWatered': False})
    userDict = {'userMicroServiceId': id, 'currentSize': 10, 'maxSize': 20, 'constructions': constructions }
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
def upgrade(user: User):
    mongodb_client.service_01.users.find(user.id)
    




## New Day Flow
def newDay():
    # para cada usuario
    try:
        users = mongodb_client.service_1.User.find()
    except:
        print("error")
    else:
        for user in users:
            isRaining = False
            for construction in user.constructions:
                if construction.posX in range(int(user.currentSize.split(',')[0])):
                    if construction.posY in range(int(user.currentSize.split(",")[1])):
                        if construction.readyToPlant and construction.isWatered:
                            print("Help")
                            construction.dayStillDone =- 1
                            construction.daysToGrow += 1
                            if not isRaining:
                                construction.isWatered = False
        
            try:
                mongodb_client.service_1.User.update_one({"userId": user["userId"]}, {"$set": {"constructions": Constructions}})
            except:
                print("error")

    return

schedule.every().day.do(newDay)

@app.get("/newDay")
def manualNewDay():
    newDay()

schedule.every().day.do(newDay)


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
    id: str | None = None
    posX: int
    posY: int
    hasPlant: bool = Field(default=False)
    plantId: str = Field(default='')
    isBuilt: bool = Field(default=False)
    daysTillDone: int = Field(default=0)
    hp: int = Field(default=0)
    isWatered: bool = Field(default=False)

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
async def plant_request(userId: str, plantName: str, posX: int, posY: int):
    try:
        #Get de BD para comprobar estado de slot para plantar...
        farm = mongodb_client.service_01.users.find_one({"userId": userId})
        slot = farm["constructions"][posX*10+posY]
        if slot["isBuilt"]:
            plantInfo = mongodb_client.service_01.plants.find_one({"name": plantName})
            update_data = {
                "constructions.$.plantId": plantInfo["id"],
                "constructions.$.isAvailable": 0,
                "constructions.$.grownDays": 0,
                "constructions.$.hasPlant": 1,
                "constructions.$.daysTillDone": plantInfo["daysToGrow"],
                "constructions.$.hp": plantInfo["lifeExpectancy"]
            }
            match_construction = {"posX": posX, "posY": posY, "isBuilt": True}
            mongodb_client.service_01.users.update_one(
                {"userId": userId, "constructions": {"$elemMatch": match_construction}},
                {"$set": update_data}
            )
            
            logging.info(f"✨ Plant request successfull: {update_data}")

            user_slot = mongodb_client.service_01.users.find_one(
                {"userId": userId, "constructions": {"$elemMatch": match_construction}},
                {"constructions.$": 1}
            )
            if user_slot and 'constructions' in user_slot:
                specific_slot = user_slot['constructions'][0]
            else:
                specific_slot = None

            return specific_slot

        print("paso4")
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Position not available: "+str(posX*10+posY))

@app.post("/add_plants")
def insertPlants():
    f= open ('./app/plants.json', "r")
    
    # Reading from file
    data = json.loads(f.read())
    
    # Iterating through the json list
    
    for plant in data["Plantas"]:
        plant = Plants(**plant)
        mongodb_client.service_01.plants.insert_one(plant.dict())

    # Closing file
    f.close()

@app.get("/users/all", response_model=list[User])
def users_all():
    try:
        userList = mongodb_client.service_01.users.find({})
        userOutput = [User(**user) for user in userList]
        return userOutput

    except:
        raise HTTPException(status_code=404, detail="Something wasn't found")

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
                constructions.append( {"posX":i, "posY":j, "isBuilt":True } )
            else:
                constructions.append( { "posX":i,"posY":j })

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
        userList = mongodb_client.service_01.users.find({})
        userOutput = [User(**user) for user in userList]    
    except:
        print("error")
    else:
        print(userOutput)
        for user in userOutput:
            url = f"http://dummy_service:80/weather"
            isRaining = True#isRaining = requests.get(url).json()

            OGconstructions = user.constructions.copy()
            constructions = []
            maxSize = int(user.currentSize)
            for construction in OGconstructions:
                if (construction.posX in range(maxSize) and 
                    construction.posY in range(maxSize)):
                    
                    if construction.isBuilt and construction.hasPlant:
                        if construction.isWatered:
                            construction.daysTillDone -= 1
                            construction.isWatered = False
                        if isRaining:
                            construction.isWatered = True
                            
                    elif not construction.isBuilt and construction.daysTillDone > 0:
                        construction.daysTillDone -= 1
                        construction.isBuilt = construction.daysTillDone == 0
                        
                constructions.append(construction.dict())


                            
            print("$########## Final: ",constructions)
            try:
                print(user.userId)
                mongodb_client.service_01.users.update_one({"userId": user.userId}, {"$set": {"constructions": constructions}})

                
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise HTTPException(status_code=404, detail="User not found")

    return

schedule.every().day.do(newDay)

@app.get("/newDay")
def manualNewDay():
    newDay()

schedule.every().day.do(newDay)


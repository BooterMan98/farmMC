import logging
import schedule
import json

from pymongo import MongoClient, InsertOne
from bson.errors import InvalidId
from bson.objectid import ObjectId
from fastapi import FastAPI, Response
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List
import json
from pymongo.errors import PyMongoError

from .events import Emit

app = FastAPI()
mongodb_client = MongoClient("granja-service-mongodb", 27017)

emit_events = Emit()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

   

class Constructions(BaseModel):
    id: str | None = None #borrar
    posX: int
    posY: int
    hasPlant: bool = Field(default=False)
    plantId: str = Field(default='')
    isBuilt: bool = Field(default=False)
    daysTillDone: int = Field(default=0)
    hp: int = Field(default=0)
    isWatered: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": 
                [
                    {
                "posX": 0,
                "posY": 0,
                "hasPlant": False,
                "plantId": "",
                "isBuilt": True,
                "daysTillDone": 0,
                "hp": 0,
                "isWatered": False
                },                    
                {
                "etc..."
                }
                ]
            }
        

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

    class Config:
        schema_extra = {
            "example": 
            {
                "id": "65401e4bfe1ebc983d3df03a",
                "name": "Arandano",
                "daysToGrow": 10,
                "lifeExpectancy": 2,
                "minHarvest": 4,
                "maxHarvest": 10,
                "description": "El arándano es un fruto carnoso que crece silvestre en casi todo el hemisferio norte. Es una baya globosa, de unos 6mm de diámetro y de color negro azulado. Su pulpa es aromática, jugosa y de sabor algo ácido. Contiene numerosas semillas pardas de pequeño tamaño."
            }            
        }

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

    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "userId": "Cesar",
                "currentSize": "4",
                "maxSize": "10",
                "nextTier": 4,
                "constructions": [
                    {
                        "posX": 0,
                        "posY": 0,
                        "hasPlant": False,
                        "plantId": "Arandano",
                        "isBuilt": True,
                        "daysTillDone": 0,
                        "hp": 0,
                        "isWatered": False
                    },
                    {"etc..."}
                ]
            }
        }
    
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
    '''
    Harvest plant in a construction.
    returns construction information.
    '''
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
    '''
    Seeds a plant in the construction posX, posY of a specific user.
    returns specific constructions updated with plant.
    '''
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
    '''
    Add plants to the database from a json file, just for testing
    '''
    f= open ('./app/plants.json', "r")
    
    # Reading from file
    data = json.loads(f.read())
    
    # Iterating through the json list
    
    for plant in data["Plantas"]:
        plant = Plants(**plant)
        mongodb_client.service_01.plants.insert_one(plant.dict())

    # Closing file
    f.close()

@app.get("/users", response_model=list[User])
def users_all():
    '''
    Fetches all users and their respective constructions.
    returns all users info and constructions.
    '''
    try:
        userList = list(mongodb_client.service_01.users.find({}))
        print(userList)
        userOutput = [User(**user) for user in userList]
        return userOutput

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        # This is to catch other unexpected errors, but be cautious about exposing raw error messages to the client.
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/users/{user_id}")
def users_get(user_id: str) -> User:
    '''
    Fetches a specific user and its respective constructions.
    returns user info and constructions.
    '''
    try:
        return User(
        **mongodb_client.service_01.users.find_one(
            {"userId": user_id}
        )
        )
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="User not found")



@app.get("/plants", response_model=list[Plants])
def plants_all():
    '''
    Fetches all plants available in the database to be used in a construction.
    returns list of plants.
    '''
    return [Plants(**plant) for plant in mongodb_client.service_01.plants.find()]

@app.post("/users")
def users_create(id: str) -> User:
    '''
    Creates a new user.
    Returns the new user and a list with user constructions.
    '''
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
    '''
    Adds a new plant to the database.
    returns the new plant created.
    '''
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
    '''
    Increases the available constructions by 1 row and 1 column. Sets days till done parameter to 2.
    It means that in 2 days the new rows and columns will be ready to plant.
    returns user info with respective constructions
    '''
    mostrar(userId)
    newNextTier,newCurrentSize = None,None
    try:
        currentUser= mongodb_client.service_01.users.find_one({"userId": userId})
        
    except:
        raise HTTPException(status_code=404, detail="User not found")
    
    nextTier = currentUser["nextTier"]
    if nextTier == -1:
        raise HTTPException(status_code=403, detail="Maximum upgrades reached")

    try:
        url = f"http://dummy-service:80/checkConstructionViable?tier={nextTier}&userId={userId}"

        isUpgradeViable = True #requests.get(url).json()
        if isUpgradeViable:
            url = f"http://dummy-service:80/buyConstruction?tier={nextTier}&userId={userId}"
            purchaseSuccesfull = True #requests.get(url).json()
            if purchaseSuccesfull:
                
                constructions,newNextTier,newCurrentSize = upgradeFarm(currentUser)

                mongodb_client.service_01.users.update_one(
                {"userId": userId},
                {"$set": {"constructions":constructions, "nextTier":newNextTier, "currentSize":newCurrentSize }}
                )
                
                return User(**mongodb_client.service_01.users.find_one(   {"userId": userId} ))
    except:
        raise HTTPException(status_code=404, detail="User not found")

def upgradeFarm(user: User):
    currentSize = int(user["currentSize"])
    constructions = user["constructions"].copy()
    nextTier = user["nextTier"]
    for j in range(nextTier):
        constructions[nextTier*10+j]["daysTillDone"] = 2
    
    for i in range(nextTier):
         constructions[i*10+nextTier]["daysTillDone"] = 2
    
    nextTier += 1
    currentSize += 1

    return constructions, nextTier, str(currentSize)


def mostrar(id):
    print(id)
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
            url = f"http://dummy-service:80/weather/santiago"


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


@app.delete("/users/delete/{userId}")
def deleteUser(userId: str):
    try:
        result = mongodb_client.service_01.users.delete_one({"userId": userId})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # No content to return, so signify with a 204 status code
        return Response(status_code=204)

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        # Be cautious about exposing raw error messages to the client in a production environment.
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


schedule.every().day.do(newDay)


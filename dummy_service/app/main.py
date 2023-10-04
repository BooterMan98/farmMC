import logging

from pymongo import MongoClient
from bson.errors import InvalidId
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
import json
import random




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


@app.get("/weather")
def getWeather():
    isRaining = random.choice([True, False])
    return isRaining

    
@app.post("/checkConstructionViable")
def checkConstructionViable(tier:str, userId:str):
    constructionPrices = {
        "3":100,
        "4":500,
        "5":2500,
        "6":10000,
        "7":100000,
        "8":500000,
        "9":1000000
    }   
    viable = random.choice([True, False])
    return viable

@app.post("/buyConstruction")
def buyConstruction(constId:str, userId:str):
    viable = random.choice([True, False])
    return viable


@app.post("/resourceAvailable")
def buyConstruction(plantId:str, userId:str):
    viable = random.choice([True, False])
    return viable

@app.post("/useResource")
def buyConstruction(plantId:str, userId:str):
    viable = random.choice([True, False])
    return viable

@app.post("/resourcesObtained")
def buyConstruction(constId:str, userId:str):
    viable = random.choice([True, False])
    return viable
import time
import logging
import requests

from ariadne import QueryType
from ariadne import MutationType
from ariadne import ObjectType
from ariadne import make_executable_schema
from ariadne import load_schema_from_path

from ariadne.asgi import GraphQL

from graphql.type import GraphQLResolveInfo

from starlette.middleware.cors import CORSMiddleware


type_defs = load_schema_from_path("./app/schema.graphql")

query = QueryType()
mutation = MutationType()

user = ObjectType("User")
plant = ObjectType("Plants")
construction = ObjectType("Constructions")


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


@query.field("getUser")
def resolve_get_user(obj, resolve_info: GraphQLResolveInfo, id):
    response = requests.get(f"http://granja_service/users/{id}")

    if response.status_code == 200:
        return response.json()


@user.field("userId")
@query.field("listUsers")
def resolve_list_users(obj, resolve_info: GraphQLResolveInfo):
    # Make it slow
    time.sleep(3)
    
    response = requests.get(f"http://granja_service/user/all")

    if response.status_code == 200:
        return response.json()


@query.field("listPlants")
def resolve_list_players(obj, resolve_info: GraphQLResolveInfo):
    response = requests.get(f"http://granja_service/plants")

    if response.status_code == 200:
        return response.json()



@mutation.field("createUser")
def resolve_create_user(obj, resolve_info: GraphQLResolveInfo, id):
    payload = dict(id=id)

    return requests.post(f"http://granja_service/users", json=payload).json()


@mutation.field("plant")
def resolve_plant(obj, resolve_info: GraphQLResolveInfo, userId, plantName, posX, posY):
    payload = dict(
        userId=userId,
        plantName=plantName,
        posX=posX,
        posY=posY
    )

    return requests.post(f"http://granja_service/plants", json=payload).json()


@mutation.field("harvest")
def resolve_harvest(obj, resolve_info: GraphQLResolveInfo, construction_id, construction):
    payload = dict(construction_idid=construction_id,
        construction=construction
    )

    return requests.post(f"http://granja_service/harvest/{construction_id}", json=payload).json()

@mutation.field("upgradeFarm")
def resolve_upgrade_farm(obj, resolve_info: GraphQLResolveInfo, id):
    payload = dict(userId=id)

    return requests.post(f"http://granja_service/upgradeFarm", json=payload).json()


schema = make_executable_schema(type_defs, query, mutation, user, construction,plant)
app = CORSMiddleware(GraphQL(schema, debug=True), allow_origins=['*'], allow_methods=("GET", "POST", "OPTIONS"))

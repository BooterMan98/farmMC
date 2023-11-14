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
    response = requests.get(f"http://granja-service:5001/users/{id}")

    if response.status_code == 200:
        return response.json()

@query.field("listUsers")
def resolve_list_users(obj, resolve_info: GraphQLResolveInfo):
    response = requests.get(f"http://granja-service:5001/users/")

    if response.status_code == 200:
        return response.json()


@query.field("listPlants")
def resolve_list_plants(obj, resolve_info: GraphQLResolveInfo):
    response = requests.get(f"http://granja-service:5001/plants")

    if response.status_code == 200:
        return response.json()



@mutation.field("createUser")
def resolve_create_user(obj, resolve_info: GraphQLResolveInfo, userId):
    print(f"http://granja_service:5001/users?id={userId}")
    return requests.post(f"http://granja-service:5001/users?id={userId}").json()


@mutation.field("plant")
def resolve_plant(obj, resolve_info: GraphQLResolveInfo, userId, plantName, posX, posY):
    return requests.post(f"http://granja-service:5001/plants?userId={userId}&plantName={plantName}&posX={posX}&posY={posY}").json()


@mutation.field("harvest")
def resolve_harvest(obj, resolve_info: GraphQLResolveInfo, construction_id, construction):
    payload = dict(construction_idid=construction_id,
        construction=construction
    )

    return requests.post(f"http://granja-service:5001/harvest/{construction_id}", json=payload).json()

@mutation.field("upgradeFarm")
def resolve_upgrade_farm(obj, resolve_info: GraphQLResolveInfo, userId):

    return requests.post(f"http://granja-service:5001/upgradeFarm?userId={userId}").json()


schema = make_executable_schema(type_defs, query, mutation, user, construction,plant)
app = CORSMiddleware(GraphQL(schema, debug=True), allow_origins=['*'], allow_methods=("GET", "POST", "OPTIONS"))

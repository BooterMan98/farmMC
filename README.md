# Microservicio Granja

Para levantar el servicio se debe ejecutar los siguiente en una terminal en la carpeta raíz del proyecto

```bash
# Comandos corresponden a macOS, en otros SO pueden ser ligeramente distintos

docker-compose -f ./granja/docker-compose.yml up -d
docker-compose -f ./message_broker/docker-compose.yml up -d
docker-compose -f ./dummy_service/docker-compose.yml up -d
```

Se puede acceder a este en http://localhost:5001 o http://localhost:5001/docs para ver las apis disponibles 




## Front

Para levantar el front-end se debe ejecutar
```bash
docker-compose -f ./api-gateway/docker-compose.yml up -d
docker-compose -f ./chatbot/docker-compose.yml up -d

```

se puede acceder por http://localhost:3000 al front-end y por http://localhost:5050/graphiql se puede explorar el *api-gateway*

en le siguiente link esta el video demostración: https://youtu.be/-ip6tMSNfno

## Tests

Para correr las pruebas, hay que primero levantar 

```bash
docker exec -it granja-granja-service-1 bash  

pytest
``````

## Deployment a kubernetes 

La información del deployment y los nombres de los servicios usados dentro del cluster estan en el branch `cluster-deployments`
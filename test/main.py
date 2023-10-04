id = '10'
constructions = []
for i in range(10):
    constructions.append({'posX': i, 'posY': i, 'hasPlant': False, 'plantId': '', 'readyToPlant': False, 'daysTillDone': 2, 'isWatered': False})
userDict = {'userMicroServiceId': id, 'currentSize': 10, 'maxSize': 20, 'constructions': constructions }
print(userDict['constructions'][2])
import { use } from "react";

class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }
  
  greet() {
    const greetingMessage = this.createChatBotMessage("Hi, friend.")
    this.updateChatbotState(greetingMessage)
  }

  noEnougthParameters() {
    console.log("ad")
    const message = this.createChatBotMessage("Hey! I need more information to understand what you want to do >:c")
    this.updateChatbotState(message)

  }

  async createFarm() {
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: 'mutation { createUser(userId:"1232421") { id }}',
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      const data = await response.json();
  
      if (data.errors) {
        throw new Error(data.errors[0].message);
      }
  
      const successMessage = this.createChatBotMessage(`Farm created Successfully ${data.data.createUser.id}`, { widget: 'farmRender' });
      console.log(data);
      this.updateChatbotState(successMessage);
  
    } catch (error) {
      const failureMessage = this.createChatBotMessage(`There was a problem and the farm could not be created. Error: ${error.message}`);
      this.updateChatbotState(failureMessage);
    }
  }

  async viewFarm() {
    const user = "1232421"
    let farmResponse = null
    let farmRetrievedSuccessfuly = false
    while (farmResponse == null) {
      [farmRetrievedSuccessfuly, farmResponse] = await this.requestFarmData(user)
      if (!farmRetrievedSuccessfuly) {
        return
      }
    }

    if (farmRetrievedSuccessfuly) {
      const successMessage = this.createChatBotMessage("This is your farm stats:", {widget:"farmRender"})
      this.updateChatbotState(successMessage)
      // Current size
      console.log(farmResponse)

      const currentSize = farmResponse["currentSize"]
      const currentSizeText = `Your current farm size is ${currentSize}x${currentSize}`
      const currentSizeMessage = this.createChatBotMessage(currentSizeText)
      this.updateChatbotState(currentSizeMessage)
      // Farm Slots
      const constructions = farmResponse["constructions"]
      for (const slot of constructions) {
        let posX = slot.posX
        let posY = slot.posY
        let isBuilt = slot.isbuilt
        let hasPlant = slot.hasPlant
        let daysTillDone = slot.daysTillDone
        let isWatered = slot.isWatered

        if (hasPlant) {
          let slotMessage = `The plant at position (${posX},${posY})`
          if (daysTillDone < 0) {
            slotMessage = slotMessage + ` has ${daysTillDone} days left to be harvestable`

            const watered = " and has been watered today"
            const notWatered = " and hasn't been watered today"
            slotMessage = isWatered ? (slotMessage + watered) : (slotMessage + notWatered)
          } else if (daysTillDone == 0) {
            slotMessage = slotMessage + `can be harvested`
          }
          let slotWidthPlantMessage = this.createChatBotMessage(slotMessage)
          this.updateChatbotState(slotWidthPlantMessage)
        }

        if (!isBuilt && daysTillDone > 0) {
          let slotMessage = `The slot at position (${posX},${posY}) is being built and currently has ${daysTillDone} days left to be done`
          let constructionSlotMessage = this.createChatBotMessage(slotMessage)
          this.updateChatbotState(constructionSlotMessage)
        }
      }

    }
  }

  
  async upgradeFarm() {
    let [succesfullFarmUpgrade, currentSize] = await this.requestPlantUpgrade("1232421")
    if (succesfullFarmUpgrade) {
      const successMessage = this.createChatBotMessage(`Farm upgrade on the way, your new size wil be ${currentSize}x${currentSize}.`)
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the farm could not be upgraded, try again later :(")
      this.updateChatbotState(failureMessage)
    }
  }

  async plantCrop(plant, posX, posY) {
    const cropPlantedSuccessfully = await this.requestToPlantCrop(plant, posX, posY)
    if (cropPlantedSuccessfully) {
      const successMessage = this.createChatBotMessage("crop planted Succesfully")
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the crop could not be planted, try again later :(")
      this.updateChatbotState(failureMessage)
    }
  }
  
  async listPlants() {
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: '{listPlants {name}}',
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      const data = await response.json();
  
      if (data.errors) {
        throw new Error(data.errors[0].message);
      }

      let newData = data.listPlants
      if (newData == undefined) {
        newData = []
      } 

      const successMessage = this.createChatBotMessage(`Here is the plant list`, {widget: "plantList", payload: {newData}})
      this.updateChatbotState(successMessage)

    } catch (error) {
      const failureMessage = this.createChatBotMessage(`There was a problem and the list could not be retrieved, try again later : Error: ${error.message}`)
      this.updateChatbotState(failureMessage)
    }
  }


  async harvestPlant(posX, posY) {
    let succesfullharvest = await this.requestPlantHarvest("1232421", posX, posY)
    if (succesfullharvest) {
      const successMessage = this.createChatBotMessage(`Plant Harvested! ${currentSize}x${currentSize}.`)
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the farm could not be upgraded, try again later :(")
      this.updateChatbotState(failureMessage)
    }
  }
  
  updateChatbotState(message) {
 
// NOTE: This function is set in the constructor, and is passed in      // from the top level Chatbot component. The setState function here     // actually manipulates the top level state of the Chatbot, so it's     // important that we make sure that we preserve the previous state.
 
    
   this.setState(prevState => ({
    	...prevState, messages: [...prevState.messages, message]
    }))
  }

  // Helpers below... Beware...
  // Note to us: these helpers could be reduced to one function

  async requestFarmData(userId) {
    let sresponse = ""
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: `
            {getUser(id: "${userId}") {
              currentSize
              maxSize
              
              constructions {
                hasPlant
                posX
                posY
                daysTillDone
                isWatered
                isBuilt
              }
            }
          }`,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      sresponse = data.data.getUser

      if (data.errors) {
        throw new Error(data.errors[0].message);
      }

    } catch (error) {
      const failureMessage = this.createChatBotMessage(`Theated. Error: ${error.message}`);
      this.updateChatbotState(failureMessage);
      return [false, sresponse]
    }
    return [true, sresponse]
  }


  async requestToPlantCrop(plant, posX, posY) {
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: `mutation { plant(userId:"1232421", plantName: "${plant}", posX:${posX}, posY${posY} ) { hasPlant }}`,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.errors) {
        throw new Error(data.errors[0].message);
      }

    } catch (error) {
      const failureMessage = this.createChatBotMessage(`Theated. Error: ${error.message}`);
      this.updateChatbotState(failureMessage);
      return false
    }


    return true
  }

  async requestPlantHarvest(userId, posX, posY) {
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: `mutation { harvest(userId: "${userId}", posX:${posX}, posY:${posY} ) { hasPlant }}`,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.errors) {
        throw new Error(data.errors[0].message);
      }

    } catch (error) {
      const failureMessage = this.createChatBotMessage(`Theated. Error: ${error.message}`);
      this.updateChatbotState(failureMessage);
      return false
    }


    return true
  }

  async requestPlantUpgrade(userId=1232421) {
    let sresponse = ""
    try {
      const response = await fetch("http://localhost:5050", {
        method: "POST",
        body: JSON.stringify({
          query: `mutation { upgradeFarm(userId:"${userId}") { currentSize }}`,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      sresponse = await data.data.upgradeFarm

      if (data.errors) {
        throw new Error(data.errors[0].message);
      }

    } catch (error) {
      const failureMessage = this.createChatBotMessage(`Error: ${error.message}`);
      this.updateChatbotState(failureMessage);
      return false, sresponse.currentSize
    }


    console.log(sresponse)
    return [ true, sresponse.currentSize]
  }



  
}

export default ActionProvider


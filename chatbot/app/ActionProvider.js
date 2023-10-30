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
  
  async upgradeFarm() {
    let [succesfullFarmUpgrade, currentSize] = await requestPlantUpgrade("1232421")
    console.log(succesfullFarmUpgrade, currentSize)
    if (succesfullFarmUpgrade) {
      const successMessage = this.createChatBotMessage(`Farm upgrade on the way, your new size wil be ${currentSize}x${currentSize}.`)
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the farm could not be upgraded, try again later :(")
      this.updateChatbotState(failureMessage)
    }
  }

  async plantCrop(plant, posX, posY) {
    const cropPlantedSuccessfully = await requestToPlantCrop(plant, posX, posY)
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


  updateChatbotState(message) {
 
// NOTE: This function is set in the constructor, and is passed in      // from the top level Chatbot component. The setState function here     // actually manipulates the top level state of the Chatbot, so it's     // important that we make sure that we preserve the previous state.
 
    
   this.setState(prevState => ({
    	...prevState, messages: [...prevState.messages, message]
    }))
  }

  
}

export default ActionProvider

// Helpers below... Beware...

async function requestToPlantCrop(plant, posX, posY) {
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

async function requestPlantUpgrade(userId=1232421) {
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


class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }
  
  greet() {
    const greetingMessage = this.createChatBotMessage("Hi, friend.")
    this.updateChatbotState(greetingMessage)
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
  
  upgradeFarm() {
    let succesfullFarmUpgrade = false
    if (succesfullFarmUpgrade) {
      const successMessage = this.createChatBotMessage("Farm upgrade on the way")
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the farm could not be upgraded, try again later :(")
      this.updateChatbotState(failureMessage)
    }
  }

  plantCrop() {
    let cropPlantedSuccessfully = false
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

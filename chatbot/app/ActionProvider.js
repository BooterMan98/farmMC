class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }
  
  greet() {
    const greetingMessage = this.createChatBotMessage("Hi, friend.")
    this.updateChatbotState(greetingMessage)
  }

  createFarm() {
    let succesfullFarmCreation = false
    if (succesfullFarmCreation) {
      const successMessage = this.createChatBotMessage("Farm created Succesfully")
      this.updateChatbotState(successMessage)
    } else {
      const failureMessage = this.createChatBotMessage("There was a problem and the farm could not be created, try again later :(")
      this.updateChatbotState(failureMessage)
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
  
  updateChatbotState(message) {
 
// NOTE: This function is set in the constructor, and is passed in      // from the top level Chatbot component. The setState function here     // actually manipulates the top level state of the Chatbot, so it's     // important that we make sure that we preserve the previous state.
 
    
   this.setState(prevState => ({
    	...prevState, messages: [...prevState.messages, message]
    }))
  }
}

export default ActionProvider

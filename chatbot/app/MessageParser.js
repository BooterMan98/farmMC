class MessageParser {
  constructor(actionProvider) {
    this.actionProvider = actionProvider;
  }

  parse(message) {
    const lowerCaseMessage = message.toLowerCase()
    console.log(lowerCaseMessage.includes("create") && lowerCaseMessage.includes("farm"))
    
    if (lowerCaseMessage.includes("hello")) {
      this.actionProvider.greet()
    } else if (lowerCaseMessage.includes("create") && lowerCaseMessage.includes("farm")) {
      this.actionProvider.createFarm()
    } else if (lowerCaseMessage.includes("plant")  && lowerCaseMessage.includes("crop"))  {
      this.actionProvider.plantCrop()
    } else if (lowerCaseMessage.includes("upgrade") && lowerCaseMessage.includes("farm")) {
      this.actionProvider.upgradeFarm()
    } else if (lowerCaseMessage.includes("plant")  && lowerCaseMessage.includes("list")) {
      this.actionProvider.listPlants()
    }
  }
}

export default MessageParser

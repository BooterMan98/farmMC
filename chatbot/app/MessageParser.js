class MessageParser {
  constructor(actionProvider) {
    this.actionProvider = actionProvider;
  }

  parse(message) {
    const lowerCaseMessage = message.toLowerCase()
    
    if (lowerCaseMessage.includes("hello")) {
      this.actionProvider.greet()
    } else if (lowerCaseMessage.includes("create") && lowerCaseMessage.includes("farm")) {
      this.actionProvider.createFarm()
    } else if (lowerCaseMessage.includes("plant")  && lowerCaseMessage.includes("crop"))  {
      const parameters = lowerCaseMessage.split(" ")
      console.log(parameters.length < 5)
      console.log(parameters.length)
      if (parameters.lenght < 5) {
        console.log("dafsfa")
        this.actionProvider.notEnougthParameters()
      } else {
        this.actionProvider.plantCrop(parameters[2], parameters[3], parameters[4])
      } 
    } else if (lowerCaseMessage.includes("upgrade") && lowerCaseMessage.includes("farm")) {
      this.actionProvider.upgradeFarm()
    } else if (lowerCaseMessage.includes("plant")  && lowerCaseMessage.includes("list")) {
      this.actionProvider.listPlants()
    } else if (lowerCaseMessage.includes("harvest") &&lowerCaseMessage.includes("plant")) {
      const parameters = lowerCaseMessage.split(" ")
      console.log(parameters.length < 5)
      console.log(parameters.length)
      if (parameters.lenght < 4) {
        console.log("dafsfa")
        this.actionProvider.notEnougthParameters()
      } else {
        this.actionProvider.harvestPlant(parameters[2], parameters[3])
      } 
    }
  }
}

export default MessageParser

import { createChatBotMessage } from 'react-chatbot-kit';
import FarmRender from './widgets/render';
import PlantList from './widgets/plantList';

const config = { 
  botName: "FarmBot",
  initialMessages: [createChatBotMessage("Hi, I'm here to help you grow your own farm! How can I help you today?")],
  widgets: [
    {
      widgetName: 'farmRender',
      widgetFunc: (props) => <FarmRender {...props} />,
    },
    {
      widgetName: "plantList",
      widgetFunc: (props) => <PlantList {...props} />,
    }
  ],
  customStyles: {
    botMessageBox: {
      backgroundColor: "#376B7E",
    },
    chatButton: {
      backgroundColor: "#376B7E",
    },
  },
}

export default config

import { createChatBotMessage } from 'react-chatbot-kit';
import FarmRender from './widgets/render';

const config = { 
  botName: "FarmBot",
  initialMessages: [createChatBotMessage("Hi, I'm here to help you grow your own farm! How can I help you today")],
  widgets: [
    {
      widgetName: 'farmRender',
      widgetFunc: (props) => <FarmRender {...props} />,
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

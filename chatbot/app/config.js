import { createChatBotMessage } from 'react-chatbot-kit';

const config = { 
  botName: "FarmBot",
  initialMessages: [createChatBotMessage("Hi, I'm here to help you grow your own farm! How can I help you today")],
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

"use client"
import 'react-chatbot-kit/build/main.css'

import Image from 'next/image'
import Chatbot from 'react-chatbot-kit'

import ActionProvider from './ActionProvider';
import MessageParser from './MessageParser';
import config from './config';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
        <Chatbot config={config} actionProvider={ActionProvider} 	    messageParser={MessageParser} />
    </main>
  )
}

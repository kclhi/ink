import React, {useState} from 'react';
import axios, {AxiosResponse} from 'axios';
import DOMPurify from 'dompurify';
import QRCodeGenerator from './QRCodeGenerator';

import './Chat.css';
import { CHAT_SERVER_URL, APP_URL } from './config';

const Chat: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(event.target.value);
  };

  const sendMessage = async(message: string) => {
    setMessages((prevMessages) => [...prevMessages, {text: message, sender: 'user'}]);

    try {
      const response: AxiosResponse = await axios.post(
        CHAT_SERVER_URL + '/sendMessage',
        {
          message: message
        },
        {withCredentials: true}
      );

      setMessages((prevMessages) => [...prevMessages, {text: response.data.message, sender: 'chatbot'}]);

      setInputText('');
    } catch(error) {
      console.error('Error sending message to API:', error);
    }
  };

  const sendMessageButton = async() => {
    if(!inputText) return;
    sendMessage(inputText);
  };

  const sendMessageKey = async(event: React.KeyboardEvent<HTMLInputElement>) => {
    if(!inputText) return;
    if(event && event.key !== 'Enter') return;
    sendMessage(inputText);
  };

  const signMessages = async() => {
    if(!messages) return;

    try {
      const signatureResponse = await axios.post(
        CHAT_SERVER_URL + '/signMessages',
        {},
        {withCredentials: true}
      );
      const timestampResponse = await axios.post(CHAT_SERVER_URL + '/getTimestamp', {
        signedMessages: signatureResponse.data.signature
      });

      const verificationURL: string =
      APP_URL +
        '/verifySignature?messages=' +
        encodeURIComponent(btoa(JSON.stringify(messages))) +
        '&signedMessages=' +
        encodeURIComponent(signatureResponse.data.signature) +
        '&timestamp=' +
        encodeURIComponent(timestampResponse.data.timestamp);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text:
            'This chat has now been verified. To demonstrate this, share or visit the following link: <a href="' +
            verificationURL +
            '">' +
            signatureResponse.data.signature.substring(0, 7) +
            '</a>',
          sender: 'chatbot'
        },
        {
          text: verificationURL,
          sender: 'chatbot'
        }
      ]);
      setInputText('');
    } catch(error) {
      console.error('Error sending message to API:', error);
    }
  };

  return (
    <div>
      <div className="padlock-div">
        <button onClick={signMessages} className="padlock-button">
          <i className="fas fa-lock"></i>
        </button>
        <div className="chat-window">
          {messages.map((message, index) =>
            !message.text.startsWith('http') ? (
              <div
                key={index}
                className={`message ${message.sender}`}
                dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(message.text)}}
              ></div>
            ) : (
              <div key={index} className={`message ${message.sender}`}>
                <QRCodeGenerator url={message.text} />
              </div>
            )
          )}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={sendMessageKey}
            placeholder="Type your message..."
          />
          <button className="paper-airplane-button" onClick={sendMessageButton}>
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;

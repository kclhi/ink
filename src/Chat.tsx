import React, {useEffect, useRef, useState} from 'react';
import axios, {AxiosResponse} from 'axios';
import DOMPurify from 'dompurify';
import QRCodeGenerator from './QRCodeGenerator';

import './Chat.css';
import {CHAT_SERVER_URL, APP_URL, MAX_QR_LENGTH} from './config';

const Chat: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>(() => {
    return JSON.parse(sessionStorage.getItem('messages') || '[]');
  });
  const [loading, setLoading] = useState(false);
  const bottom = useRef<null | HTMLDivElement>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(event.target.value);
  };

  useEffect(() => {
    sessionStorage.setItem('messages', JSON.stringify(messages));
    bottom.current?.scrollIntoView({behavior: 'smooth'});
  }, [messages]);

  const sendMessage = async(message: string) => {
    setLoading(true);
    setInputText('');
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
      setLoading(false);
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
      const signatureResponse = await axios.post(CHAT_SERVER_URL + '/signMessages', {}, {withCredentials: true});
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
      const newMessages: Message[] = [
        {
          text:
            'This chat has now been verified. To demonstrate this, share or visit the following link: <a href="' +
            verificationURL +
            '">' +
            signatureResponse.data.signature.substring(0, 7) +
            '</a>',
          sender: 'chatbot'
        }
      ];
      if(verificationURL.length < MAX_QR_LENGTH)
        newMessages.push({
          text: verificationURL,
          sender: 'chatbot'
        });

      setMessages((prevMessages) => [...prevMessages, ...newMessages]);
      setInputText('');
    } catch(error) {
      console.error('Error sending message to API:', error);
    }
  };

  return (
    <div>
      <div className="padlock-div" style={{opacity: loading ? 0.5 : 1}}>
        <button onClick={signMessages} className="padlock-button" disabled={loading}>
          <i className="fas fa-lock"></i>
        </button>
        <div className="chat-window" style={{overflowY: loading ? 'hidden' : 'auto'}}>
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
          {loading && <div className="loading-spinner"></div>}
          <div ref={bottom} />
        </div>
        <div className="input-container">
          <input
            type="text"
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={sendMessageKey}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button className="paper-airplane-button" onClick={sendMessageButton} disabled={loading}>
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
      <footer>
        <div>
          Chatting with
          <select>
            <option>Llama2</option>
          </select>
        </div>
      </footer>
    </div>
  );
};

export default Chat;

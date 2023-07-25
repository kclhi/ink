import React, {useState} from 'react';
import axios, {AxiosResponse} from 'axios';
import DOMPurify from 'dompurify';

const Chat: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(event.target.value);
  };

  const sendMessage = async(message: string) => {
    setMessages((prevMessages) => [...prevMessages, {text: message, sender: 'user'}]);

    try {
      const response: AxiosResponse = await axios.post('http://localhost:8000/sendMessage', {
        message: message
      });

      setMessages((prevMessages) => [...prevMessages, {text: response.data.message, sender: 'bot'}]);

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
      const response = await axios.post(
        'http://localhost:8000/signMessages',
        messages.map((message) => ({message: message.text}))
      );

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text:
            'This chat has now been verified: <a href="/verifySignature/' +
            encodeURIComponent(JSON.stringify(messages.map((message) => ({message: message.text})))) +
            '/' +
            encodeURIComponent(response.data.signature) +
            '">' +
            response.data.signature.substring(0, 7) +
            '</a>',
          sender: 'bot'
        }
      ]);

      setInputText('');
    } catch(error) {
      console.error('Error sending message to API:', error);
    }
  };

  return (
    <div>
      <div className="chat-window">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender}`}
            dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(message.text)}}
          ></div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={inputText}
          onChange={handleInputChange}
          onKeyDown={sendMessageKey}
          placeholder="Type your message..."
        />
        <button onClick={sendMessageButton}>Send</button>
        <button onClick={signMessages}>Verify</button>
      </div>
    </div>
  );
};

export default Chat;

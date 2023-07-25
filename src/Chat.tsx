import React, {useState} from 'react';
import axios from 'axios';

const Chat: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(event.target.value);
  };

  const sendMessage = async() => {
    if(!inputText) return;

    setMessages((prevMessages) => [...prevMessages, {text: inputText, sender: 'user'}]);

    try {
      const response = await axios.post('http://localhost:8000/sendMessage', {
        message: inputText
      });

      setMessages((prevMessages) => [...prevMessages, {text: response.data.message, sender: 'bot'}]);

      setInputText('');
    } catch(error) {
      console.error('Error sending message to API:', error);
    }
  };

  return (
    <div>
      <div className="chat-window">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input type="text" value={inputText} onChange={handleInputChange} placeholder="Type your message..." />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Chat;

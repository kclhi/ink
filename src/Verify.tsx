import React, {useEffect, useState} from 'react';
import axios, {AxiosResponse} from 'axios';
import {useSearchParams} from 'react-router-dom';

import './Chat.css';
import DOMPurify from 'dompurify';

const Verify: React.FC = () => {
  const [verificationData, setVerificationData] = useState<Verified | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [time, setTime] = useState<Date>(new Date());
  const [searchParams] = useSearchParams();
  const messages: string | null = searchParams.get('messages');
  const signature: string | null = searchParams.get('signedMessages');
  const timestamp: string | null = searchParams.get('timestamp');
  const [parsedMessages, setParsedMessages] = useState<Message[]>([]);

  useEffect(() => {
    const verify = async(): Promise<void> => {
      try {
        const response: AxiosResponse<Verified> = await axios.get(
          'http://localhost:8000/verifySignature?messages=' +
            encodeURIComponent(messages || '') +
            '&signedMessages=' +
            encodeURIComponent(signature || '') +
            '&timestamp=' +
            encodeURIComponent(timestamp || '')
        );
        setVerificationData(response.data);
        setParsedMessages(JSON.parse(atob(messages || '')));
      } catch(error) {
        console.error('Error verifiying chat:', error);
        return setLoading(false);
      }
      try {
        const response: AxiosResponse<Time> = await axios.post('http://localhost:8000/extractTime', {
          timestamp: timestamp
        });
        setTime(new Date(response.data.time));
        setLoading(false);
      } catch(error) {
        console.error('Error getting timestamp:', error);
        setLoading(false);
      }
    };
    verify();
  }, [messages, signature, timestamp]);

  return (
    <div>
      {loading ? (
        <p>Verifying signature...</p>
      ) : verificationData && verificationData.verified ? (
        <div style={{textAlign: 'center'}}>
          <p>Yep, that&apos;s one of our chats.</p>
          <p>
            It took place on{' '}
            {time.toLocaleString('en-gb', {weekday: 'long'}) +
              ' ' +
              time.getDate() +
              (['st', 'nd', 'rd'][((((time.getDate() + 90) % 100) - 10) % 10) - 1] || 'th') +
              ' ' +
              time.toLocaleString('en-gb', {month: 'long'})}{' '}
            at {time.toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true})} (UTC):
          </p>
          <div className="chat-window">
            {parsedMessages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.sender}`}
                dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(message.text)}}
              ></div>
            ))}
          </div>
          <div className="split-div">
            <div className="left-column">
              <i className="fas fa-lock"></i>
            </div>
            <div className="right-column">{signature}</div>
          </div>
          <div className="split-div">
            <div className="left-column">
              <i className="fas fa-clock"></i>
            </div>
            <div className="right-column">{timestamp}</div>
          </div>
        </div>
      ) : (
        <p>We could not verify your conversation at this time</p>
      )}
    </div>
  );
};

export default Verify;

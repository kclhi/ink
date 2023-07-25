import React, {useEffect, useState} from 'react';
import axios, {AxiosResponse} from 'axios';
import {useParams} from 'react-router-dom';

const Verify: React.FC = () => {
  const [verificationData, setVerificationData] = useState<Verified | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const {messages, signature} = useParams<VerificationDetails>();

  useEffect(() => {
    const fetchData = async(): Promise<void> => {
      try {
        const response: AxiosResponse<Verified> = await axios.get(
          'http://localhost:8000/verifySignature/' +
            encodeURIComponent(messages || '') +
            '/' +
            encodeURIComponent(signature || '')
        );
        setVerificationData(response.data);
        setLoading(false);
      } catch(error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };
    fetchData();
  }, [messages, signature]);

  return (
    <div>
      {loading ? (
        <p>Verifying signature...</p>
      ) : verificationData ? (
        <div>
          <p>Verified: {verificationData.verified.toString()}</p>
        </div>
      ) : (
        <p>We could not verify your conversation at this time</p>
      )}
    </div>
  );
};

export default Verify;

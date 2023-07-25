import React from 'react';
import Chat from './Chat';
import './App.css';

const Home: React.FC = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Ink</h1>
      </header>
      <main>
        <Chat />
      </main>
    </div>
  );
};

export default Home;

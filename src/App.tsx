import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Home from './Home';
import Verify from './Verify';
import Header from './Header';

const App: React.FC = () => {
  return (
    <Router basename={'/ink'}>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/verifySignature" element={<Verify />} />
      </Routes>
    </Router>
  );
};

export default App;

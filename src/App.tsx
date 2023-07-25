import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Home from './Home';
import Verify from './Verify';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/verifySignature/:messages/:signature" element={<Verify />} />
      </Routes>
    </Router>
  );
};

export default App;

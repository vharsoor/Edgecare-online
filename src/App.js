import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import GmailPage from './GmailPage';
import CalenderPage from './CalenderPage';
import FacebookPage from './FacebookPage';
import RedditPage from './RedditPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/gmail" element={<GmailPage />} />
        <Route path="/calender" element={<CalenderPage />} />
        <Route path="/facebook" element={<FacebookPage />} />
        <Route path="/reddit" element={<RedditPage />} />
      </Routes>
    </Router>
  );
}

function Home() {
  return (
    <div className="app">
      <div className="left-side">
        <h2>Welcome to use EdgeCare Online Data Collection Tool</h2>
        <img src="/assu.png" alt="EdgeCare" className="centered-image" />
      </div>
      <div className="right-side">
        <div className="button-container">

          <h2>Social Media Platform Source</h2>
          
          <div className="button-with-image">
            <img src="/gmail.jpg" alt="Gmail" className="button-image" />
            <Link to="/gmail" className="button-link">
              <button className="button">Gmail</button>
            </Link>
          </div>
          <div className="button-with-image">
            <img src="/calender.JPG" alt="Calendar" className="button-image" />
            <Link to="/calender" className="button-link">
              <button className="button">Calendar</button>
            </Link>
          </div>
          <div className="button-with-image">
            <img src="/Facebook.png" alt="Facebook" className="button-image" />
            <Link to="/facebook" className="button-link">
              <button className="button">Facebook</button>
            </Link>
          </div>
          <div className="button-with-image">
            <img src="/reddit.JPG" alt="Reddit" className="button-image" />
            <Link to="/reddit" className="button-link">
              <button className="button">Reddit</button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

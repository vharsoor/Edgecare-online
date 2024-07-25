import React, { useState,useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import './App.css';
import GmailPage from './GmailPage';
import CalenderPage from './CalenderPage';
import FacebookPage from './FacebookPage';
import RedditPage from './RedditPage';
import SpotifyPage from './SpotifyPage';
import InstagramPage from './InstagramPage';
// import ChatPage from './ChatPage';

import LoginPage from './LoginPage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

 useEffect(() => {
    console.log("Entered useEffect")
    const checkAuth = async () => {
      console.log("Entered checkAuth")
      try {
	// Get the current path from the frontend
        const currentPath = window.location.pathname;
	const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');

        // Construct the backend URL based on the frontend path
        const backendURL = `https://backend.stresswatch.net${currentPath}?code=${code}`;

        // Make the fetch request to the backend
        const response = await fetch(backendURL, {
          method: 'GET',
          credentials: 'include',
        });

        //if (response.ok) {
         // setIsAuthenticated(true);
	  //console.log("Already authenticated");
        //} else {
	  //console.log("Not authenticated")
          //setIsAuthenticated(false);
        //}
      } catch (error) {
        console.error('Error checking authentication:', error);
        //setIsAuthenticated(false);
      }
    };


    const checkAuthStatus = async () => {
      console.log("Entered checkAuthStatus");
      try {
        const response = await fetch('https://backend.stresswatch.net/api/check-auth', {
          method: 'GET',
          credentials: 'include',
        });

        const data = await response.json();

        if (response.ok && data.authenticated) {
          setIsAuthenticated(true);
          console.log("User authenticated");
        } else {
          setIsAuthenticated(false);
          console.log("User not authenticated");
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        setIsAuthenticated(false);
      }
    };


    checkAuth();
    checkAuthStatus();
    //const currentPath = window.location.pathname;
    //if (currentPath.startsWith('/callback')) {
      //checkAuth();
    //} else {
      //console.log('Not an API path');
    //}
  }, []);

  return (
    <Router>
     <Routes>
      {isAuthenticated ? (
        //<Routes>
	 <>
          <Route path="/" element={<Home />} />
          <Route path="/gmail" element={<GmailPage />} />
          <Route path="/calender" element={<CalenderPage />} />
          <Route path="/facebook" element={<FacebookPage />} />
          <Route path="/reddit" element={<RedditPage />} />
          <Route path="/spotify" element={<SpotifyPage />} />
          <Route path="/instagram" element={<InstagramPage />} />
	  <Route path="*" element={<Navigate to="/" replace />} />
	 </>
        //</Routes>
      ) : (
        <Route path="*" element={<LoginPage setAuth={setIsAuthenticated} />} />
	//<LoginPage setAuth={setIsAuthenticated} />
      )}
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

	  {// <div className="button-with-image">
          //   <img src="/gmail.jpg" alt="Gmail" className="button-image" />
          //   <Link to="/gmail" className="button-link">
          //     <button className="button">Gmail</button>
          //   </Link>
          // </div>
		  }
          <div className="button-with-image">
            <img src="/google.png" alt="google" className="button-image" />
            <Link to="/calender" className="button-link">
              <button className="button">Google</button>
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
          <div className="button-with-image">
            <img src="spotify.jpg" alt="Spotify" className="button-image" />
            <Link to="/spotify" className="button-link">
              <button className="button">Spotify</button>
            </Link>
          </div>
          {/* <div className="button-with-image">
            <img src="chat.png" alt="Chat" className="button-image" />
            <Link to="/chat" className="button-link">
              <button className="button">Chat</button>
            </Link>
          </div> */}
          <div className="button-with-image">
        	    <img src="instagram.jpg" alt="Instagram" className="button-image" />
        	    <Link to="/instagram" className="button-link">
        	      <button className="button">Instagram</button>
        	    </Link>
        	  </div>
        </div>
      </div>
    </div>
  );
}

export default App;

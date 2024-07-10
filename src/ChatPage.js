import React, { useState } from 'react';
import './ChatPage.css';
import {public_ip} from './config'
//const PUBLICIP = `54.81.251.130`;

function ChatPage() {
    const [message, setMessage] = useState('');
    const [chatData, setChatData] = useState(null);
  
    const handleAuthenticate = () => {
      fetch(`http://${public_ip}:4000/api/google_auth`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then(response => response.json())
        .then(data => {
          setChatData(data);
        })
        .catch(error => {
          console.error('Error during authentication:', error);
          setMessage('Error during authentication. Please try again.');
        });
    };
  
    return (
      <div className="google-page">
        <div className="google-left-side">
          <img src="/chat.png" alt="Google" className="full-image" />
        </div>
        <div className="google-right-side">
          <button className="authenticate-button" onClick={handleAuthenticate}>
            Authenticate with Gmail
          </button>
          {message && <p className="message">{message}</p>}
          {chatData && (
            <div className="chat-messages">
              <h3>Chat Messages:</h3>
              {Object.keys(chatData).map((spaceName, index) => (
                <div key={index} className="chat-space">
                  <h4>{spaceName}</h4>
                  {chatData[spaceName].map((message, msgIndex) => (
                    <p key={msgIndex}>{message}</p>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }
  
  export default ChatPage;
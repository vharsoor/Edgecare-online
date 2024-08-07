import React, { useState } from 'react';
import './GmailPage.css';
import {public_ip} from './config'
//const PUBLICIP = `54.81.251.130`;

function GooglePage() {
  //const [selectedFile, setSelectedFile] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [message, setMessage] = useState('');
  const [emails, setEmails] = useState(null);

  const handleAuthenticate = () => {
    fetch(`http://${public_ip}:4000/api/google_auth`, {
      method: 'GET',
      headers: {
      'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.auth_url) {
          setAuthUrl(data.auth_url);
          //window.open(data.auth_url, '_blank');
	  window.location.href = data.auth_url;
        } else {
          setMessage('Failed to get authorization URL.');
        }
      })
      .catch(error => {
        console.error('Error during authentication:', error);
        setMessage('Error during authentication. Please try again.');
      });
  };

  return (
    <div className="google-page">
      <div className="google-left-side">
        <img src="/googleUI.png" alt="Google" className="full-image" />
      </div>
      <div className="google-right-side">
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Gmail
        </button>
        {message && <p className="message">{message}</p>}
        {emails && (
          <div className="emails">
            <h3>Received Emails:</h3>
            {emails.received_emails.map((email, index) => (
              <div key={index} className="email">
                <p><strong>Subject:</strong> {email.subject}</p>
                <p><strong>Date:</strong> {email.date}</p>
                <p><strong>Snippet:</strong> {email.snippet}</p>
                <p><strong>Body:</strong> {email.body}</p>
              </div>
            ))}
            <h3>Sent Emails:</h3>
            {emails.sent_emails.map((email, index) => (
              <div key={index} className="email">
                <p><strong>Subject:</strong> {email.subject}</p>
                <p><strong>Date:</strong> {email.date}</p>
                <p><strong>Snippet:</strong> {email.snippet}</p>
                <p><strong>Body:</strong> {email.body}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GooglePage;




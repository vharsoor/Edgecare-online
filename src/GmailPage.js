import React, { useState } from 'react';
import './GmailPage.css';
import {public_ip} from './config'
//const PUBLICIP = `54.81.251.130`;

function GooglePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [message, setMessage] = useState('');
  const [emails, setEmails] = useState(null);

  const handleAuthenticate = () => {
    if (!selectedFile) {
      setMessage('Please select a credentials file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('credentials_path', selectedFile);

    fetch(`http://${public_ip}:4000/api/google_auth`, {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        if (data.auth_url) {
          setAuthUrl(data.auth_url);
          window.open(data.auth_url, '_blank');
        } else {
          setMessage('Failed to get authorization URL.');
        }
      })
      .catch(error => {
        console.error('Error during authentication:', error);
        setMessage('Error during authentication. Please try again.');
      });
  };

  const handleExchangeCode = () => {
    fetch(`http://${public_ip}:4000/api/exchange_code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: authCode,
        credentials_path: selectedFile.name
      }),
    })
      .then(response => response.json())
      .then(data => {
        setMessage(data.message || 'Authentication successful!');
      })
      .catch(error => {
        console.error('Error during authentication:', error);
        setMessage('Error during authentication. Please try again.');
      });
  };

  const handleGmailCollect = () => {
    fetch(`http://${public_ip}:4000/api/gmail_collect`)
      .then(response => response.json())
      .then(data => {
        setEmails(data);
        setMessage('Emails fetched successfully!');
      })
      .catch(error => {
        console.error('Error fetching emails:', error);
        setMessage('Error fetching emails. Please try again.');
      });
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleAuthCodeChange = (event) => {
    setAuthCode(event.target.value);
  };

  return (
    <div className="google-page">
      <div className="google-left-side">
        <img src="/googleUI.png" alt="Google" className="full-image" />
      </div>
      <div className="google-right-side">
        <h2>Please upload your Google credentials file</h2>
        <input
          type="file"
          className="file-input"
          onChange={handleFileChange}
        />
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Google
        </button>
        {authUrl && (
          <div>
            <p>Open the following URL in a new tab and authorize the application:</p>
            <a href={authUrl} target="_blank" rel="noopener noreferrer">{authUrl}</a>
          </div>
        )}
        {authUrl && (
          <div>
            <input
              type="text"
              value={authCode}
              onChange={handleAuthCodeChange}
              placeholder="Enter authorization code"
              className="auth-code-input"
            />
            <button className="exchange-code-button" onClick={handleExchangeCode}>
              Exchange Code
            </button>
          </div>
        )}
        <button className="fetch-emails-button" onClick={handleGmailCollect}>
          Fetch Emails
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




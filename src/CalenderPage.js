import React, { useState } from 'react';
import './CalendarPage.css';
import {public_ip} from './config'

function CalendarPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [message, setMessage] = useState('');
  const [events, setEvents] = useState(null);

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

  const handleFetchCalendarEvents = () => {
    fetch(`http://${public_ip}:4000/api/fetch_calendar_events`)
      .then(response => response.json())
      .then(data => {
        setEvents(data);
        setMessage('Calendar events fetched successfully!');
      })
      .catch(error => {
        console.error('Error fetching calendar events:', error);
        setMessage('Error fetching calendar events. Please try again.');
      });
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleAuthCodeChange = (event) => {
    setAuthCode(event.target.value);
  };

  return (
    <div className="calendar-page">
      <div className="calendar-left-side">
        <img src="/calenderUI.JPG" alt="Google" className="full-image" />
      </div>
      <div className="calendar-right-side">
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
        <button className="fetch-events-button" onClick={handleFetchCalendarEvents}>
          Fetch Calendar Events
        </button>
        {message && <p className="message">{message}</p>}
        {events && (
          <div className="events">
            <h3>Calendar Events:</h3>
            {events.map((event, index) => (
              <div key={index} className="event">
                <p><strong>Summary:</strong> {event.summary}</p>
                <p><strong>Start:</strong> {event.start}</p>
                <p><strong>End:</strong> {event.end}</p>
                <p><strong>Description:</strong> {event.description}</p>
                <p><strong>Location:</strong> {event.location}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CalendarPage;

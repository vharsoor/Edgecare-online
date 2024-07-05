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

    fetch(`http://${public_ip}:4000/api/google_auth`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

  const handleExchangeCode = () => {
    fetch(`http://${public_ip}:4000/api/exchange_code`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: authCode,
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
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Google
        </button>
        {authUrl && (
          <div>
            
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


import React, { useState,useEffect } from 'react';
import './CalendarPage.css';
import {public_ip} from './config'

function CalendarPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [message, setMessage] = useState('');
  const [events, setEvents] = useState(null);
  const [emails, setEmails] = useState(null);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState(null);

  console.log('CalendarPage component mounted');
  const handleAuthenticate = () => {

    fetch(`https://${public_ip}/api/google_auth`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json', },
      credentials: 'include',
    })
      .then(response => response.json())
      .then(data => {
        if (data.auth_url) {
          setAuthUrl(data.auth_url);
          //window.open(data.auth_url, '_blank');
          window.location.href = data.auth_url;
        } else if (data.output) {
	  setEvents(data.output.events || []);
	  setEmails(data.output.emails || { received_emails: [], sent_emails: [] });
	} else {
          setMessage('Failed to get authorization URL or output');
        }
      })
      .catch(error => {
        console.error('Error during authentication:', error);
        setMessage('Error during authentication. Please try again.');
      });
  };

 useEffect(() => {
  const getCodeFromUrl = () => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('code');
  };

  const fetchAuthCode = async () => {
    const code = getCodeFromUrl();
    
    if (code) {
      try {
        const response = await fetch(`https://backend.stresswatch.net/api/exchange_code?code=${code}`, {
          method: "GET",
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('Failed to exchange code with backend');
        }

        const data = await response.json();
        setEvents(data.calendar || []);
        setEmails(data.gmail || { received_emails: [], sent_emails: [] });
      } catch (err) {
        setError('Error fetching code. Please try again.');
        console.error('Error fetching data:', err);
      }
    } else {
      setError('No authorization code found in URL.');
    }
  };

  fetchAuthCode();
}, []);
 

  return (
    <div className="calendar-page">
      <div className="calendar-left-side">
        <img src="/googleUI.jpg" alt="Google" className="full-image" />
      </div>
      <div className="calendar-right-side">
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Google
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

export default CalendarPage;


import React, { useState } from 'react';
import './SpotifyPage.css';
import {public_ip} from './config'
//const PUBLICIP = `54.81.251.130`;

function SpotifyPage() {
  //const [selectedFile, setSelectedFile] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [message, setMessage] = useState('');

  const handleAuthenticate = () => {
    fetch(`http://${public_ip}:4000/api/spotify_auth`, {
      method: 'GET',
      headers: {
      'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.auth_url) {
          setAuthUrl(data.auth_url);
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
    <div className="spotify-page">
      <div className="spotify-left-side">
        <img src="/spotifyUI.jpg" alt="Spotify" className="full-image" />
      </div>
      <div className="spotify-right-side">
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Spotify
        </button>
        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}

export default SpotifyPage;




import React, { useState } from 'react';
import './InstagramPage.css';
import {public_ip} from './config'

function InstagramPage() {

  const handleAuthenticate = () => {
    console.log("Starting authentication process...");
    fetch(`http://${public_ip}:4000/api/instagram_auth`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        console.log("Response from server:", data);
        if (data.auth_url) {
          console.log("Redirecting to Auth URL:", data.auth_url);
          window.location.href = data.auth_url; // Redirect the user to the auth URL
        } else {
          console.error('Auth URL not received');
        }
      })
      .catch(error => {
        console.error('Error during authentication:', error);
      });
  };

  /*const handleInputChange = (event) => {
    const { name, value } = event.target;
    if (name === 'clientId') {
      setClientId(value);
    } else if (name === 'clientSecret') {
      setClientSecret(value);
    } else if (name === 'publicUrl') {
      setPublicUrl(value);
    }
  };*/

  return (
    <div className="instagram-page">
      <div className="instagram-left-side">
        <img src="/instagramUI.jpg" alt="Instagram" className="full-image" />
      </div>
      <div className="instagram-right-side">
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Instagram
        </button>
      </div>
    </div>
  );
}

export default InstagramPage;

import React, { useState } from 'react';
import './FacebookPage.css';

function FacebookPage() {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [publicUrl, setPublicUrl] = useState('');

  const handleAuthenticate = () => {
    console.log("Starting authentication process...");
    fetch('http://127.0.0.1:5000/api/facebook_auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ client_id: clientId, client_secret: clientSecret, public_url: publicUrl }),
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

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    if (name === 'clientId') {
      setClientId(value);
    } else if (name === 'clientSecret') {
      setClientSecret(value);
    } else if (name === 'publicUrl') {
      setPublicUrl(value);
    }
  };

  return (
    <div className="facebook-page">
      <div className="facebook-left-side">
        <img src="/facebookUI.png" alt="Facebook" className="full-image" />
      </div>
      <div className="facebook-right-side">
        <h2>Please enter your Facebook App credentials</h2>
        <input
          type="text"
          placeholder="Enter Client ID"
          className="user-input"
          name="clientId"
          value={clientId}
          onChange={handleInputChange}
        />
        <input
          type="text"
          placeholder="Enter Client Secret"
          className="user-input"
          name="clientSecret"
          value={clientSecret}
          onChange={handleInputChange}
        />
        <input
          type="text"
          placeholder="Enter Public URL"
          className="user-input"
          name="publicUrl"
          value={publicUrl}
          onChange={handleInputChange}
        />
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Facebook
        </button>
      </div>
    </div>
  );
}

export default FacebookPage;

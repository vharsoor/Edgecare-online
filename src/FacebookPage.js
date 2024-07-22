import React, { useState } from 'react';
import './FacebookPage.css';
import {public_ip} from './config'

function FacebookPage() {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [publicUrl, setPublicUrl] = useState('');
  const [output, setOutput] = useState(null);

  const handleAuthenticate = () => {
    console.log("Starting authentication process...");
    fetch(`http://${public_ip}:4000/api/facebook_auth`, {
      //method: 'POST',
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      //body: JSON.stringify({ client_id: clientId, client_secret: clientSecret, public_url: publicUrl }),
    })
      .then(response => response.json())
      .then(data => {
        console.log("Response from server:", data);
        if (data.auth_url) {
          console.log("Redirecting to Auth URL:", data.auth_url);
          window.location.href = data.auth_url; // Redirect the user to the auth URL
        } else if (data.output) {
	  setOutput(data.output);
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
    <div className="facebook-page">
      <div className="facebook-left-side">
        <img src="/FacebookUI.png" alt="Facebook" className="full-image" />
      </div>
      <div className="facebook-right-side">
        <button className="authenticate-button" onClick={handleAuthenticate}>
          Authenticate with Facebook
        </button>
	{output && (
	  <pre>{JSON.stringify(output)}</pre>
	)}
      </div>
    </div>
  );
}

export default FacebookPage;

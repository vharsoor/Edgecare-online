import React, { useState } from 'react';
import './RedditPage.css';
import { public_ip } from './config';

function RedditPage() {
  const [redditId, setRedditId] = useState('');

  const handleDownload = () => {
    fetch(`http://${public_ip}:4000/api/reddit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ reddit_id: redditId }),
    })
      .then(response => {
        return response.blob();
      })
      .then(blob => {

        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${redditId}.zip`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch(error => {
        console.error('Error:', error);
        
      });
  };
  const handleInputChange = (event) => {
    setRedditId(event.target.value);
  };

  return (
    <div className="reddit-page">
      <div className="reddit-left-side">
        <img src="/redditUI.png" alt="Reddit" className="full-image" />
      </div>
      <div className="reddit-right-side">
        <h2>Please enter the target Reddit User ID</h2>
        <input
          type="text"
          placeholder="Enter Reddit User ID"
          className="user-input"
          value={redditId}
          onChange={handleInputChange}
        />
        <button className="download-button" onClick={handleDownload}>
          Download
        </button>
      </div>
    </div>
  );
}

export default RedditPage;

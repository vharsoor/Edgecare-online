import React, { useState } from 'react';
import './RedditPage.css';

function RedditPage() {
  const [redditId, setRedditId] = useState('');

  const handleDownload = () => {
    fetch('http://127.0.0.1:5000/api/reddit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reddit_id: redditId }),
    })
      .then(response => {
        console.log(response);
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

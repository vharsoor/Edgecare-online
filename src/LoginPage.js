import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

function LoginPage({ setAuth }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await fetch('http://54.81.251.130:4000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                // Login successful
                setAuth(true);  // Update authentication state in React state
                navigate('/');  // Redirect to homepage -> all the platforms
            } else {
                // Login failed
                alert('Invalid credentials');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed. Please try again.');
        }
    };

    return (
        <div className="login-page">
            <img src="/asulogo.png" alt="ASU School Image" className="login-image" />
            <h2>Login to ASU EdgeCare Application </h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <div className="password-container">
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button
                    type="button"
                    className="password-toggle-button"
                    onClick={() => setShowPassword(!showPassword)}
                >
                    {showPassword ? 'hide' : 'show'}
                </button>
            </div>
            <button onClick={handleLogin} className="login-button" >Login</button>
        </div>
    );
}

export default LoginPage;


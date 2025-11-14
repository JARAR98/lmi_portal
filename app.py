from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'lmi-wifi-portal-secret-key-2025'
# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS in dev
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'LMIAdmin2025!'

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Create data directory if it doesn't exist
DATA_DIR = '/app/data'
os.makedirs(DATA_DIR, exist_ok=True)

# File to store user data
USER_DATA_FILE = os.path.join(DATA_DIR, 'users.json')

# Initialize user data file if it doesn't exist
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    """Load users from JSON file"""
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return []

def save_user(user_data):
    """Save user data to JSON file"""
    try:
        users = load_users()
        users.append(user_data)
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        return False

# HTML template for the login page
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LMI Connect - WiFi Access</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 100%;
            padding: 40px;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .wifi-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
        }
        h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .checkbox-group {
            display: flex;
            align-items: flex-start;
            margin-bottom: 25px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin-right: 10px;
            margin-top: 3px;
        }
        .checkbox-group label {
            margin-bottom: 0;
            font-weight: 400;
            font-size: 13px;
            color: #666;
        }
        .btn-submit {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-submit:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .message {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }
        .error { background: #fee; color: #c33; border-left: 4px solid #c33; }
        .success { background: #efe; color: #3c3; border-left: 4px solid #3c3; }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="wifi-icon">📶</div>
        <h1>LMI Connect</h1>
        <p class="subtitle">Please provide your information to access the network</p>
        <div class="message error" id="errorMessage"></div>
        <div class="message success" id="successMessage"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="fullName">Full Name *</label>
                <input type="text" id="fullName" required placeholder="Enter your full name">
            </div>
            <div class="form-group">
                <label for="purpose">Purpose of Visit *</label>
                <select id="purpose" required>
                    <option value="">Select purpose</option>
                    <option value="business">Business</option>
                    <option value="personal">Personal</option>
                    <option value="guest">Guest</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="checkbox-group">
                <input type="checkbox" id="terms" required>
                <label for="terms">I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy" target="_blank">Privacy Policy</a></label>
            </div>
            <button type="submit" class="btn-submit" id="submitBtn">Connect to WiFi</button>
        </form>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #666;">Connecting...</p>
        </div>
        <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 13px; margin-bottom: 10px;">Administrator Access</p>
            <a href="/admin/login" style="display: inline-block; padding: 10px 20px; background: #764ba2; color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; transition: all 0.3s ease;" onmouseover="this.style.background='#5a3a7a'" onmouseout="this.style.background='#764ba2'">🔐 Login as Admin</a>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');
            
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
            
            const formData = {
                fullName: document.getElementById('fullName').value,
                purpose: document.getElementById('purpose').value,
                terms: document.getElementById('terms').checked,
                timestamp: new Date().toISOString()
            };
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            form.style.display = 'none';
            
            try {
                const response = await fetch('/api/auth', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    successMessage.textContent = 'Authentication successful! Redirecting...';
                    successMessage.style.display = 'block';
                    setTimeout(() => {
                        window.location.href = result.redirectUrl || '/success';
                    }, 2000);
                } else {
                    throw new Error(result.message || 'Authentication failed');
                }
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
                submitBtn.disabled = false;
                loading.style.display = 'none';
                form.style.display = 'block';
            }
        });
    </script>
</body>
</html>'''

SUCCESS_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connected - WiFi Access</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 100%;
            padding: 60px 40px;
            text-align: center;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .success-icon {
            width: 100px;
            height: 100px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
        }
        h1 { color: #333; font-size: 32px; margin-bottom: 15px; }
        p { color: #666; font-size: 16px; line-height: 1.6; }
        .btn-home {
            display: inline-block;
            margin-top: 30px;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-home:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>You're Connected!</h1>
        <p>Welcome to our WiFi network. You now have full internet access.</p>
        <p style="margin-top: 15px; font-size: 14px; color: #999;">Session started at {{ timestamp }}</p>
        <a href="https://www.google.com" class="btn-home">Start Browsing</a>
    </div>
</body>
</html>'''

# Terms of Service HTML
TERMS_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - LMI Connect</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; margin-bottom: 30px; border-bottom: 2px solid #667eea; padding-bottom: 15px; }
        h2 { color: #667eea; margin-top: 25px; margin-bottom: 15px; }
        p { margin-bottom: 15px; }
        ul { margin-left: 20px; margin-bottom: 15px; }
        li { margin-bottom: 10px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 14px; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .back-link { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #667eea; color: white; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Login</a>
        <h1>Terms of Service</h1>
        <p><strong>Last Updated: November 14, 2025</strong></p>
        
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using the LMI Connect WiFi network, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.</p>
        
        <h2>2. Use License</h2>
        <p>Permission is granted to temporarily download one copy of the materials (information or software) on LMI Connect for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:</p>
        <ul>
            <li>Modify or copy the materials</li>
            <li>Use the materials for any commercial purpose or for any public display</li>
            <li>Attempt to decompile or reverse engineer any software contained on LMI Connect</li>
            <li>Remove any copyright or other proprietary notations from the materials</li>
            <li>Transfer the materials to another person or "mirror" the materials on any other server</li>
        </ul>
        
        <h2>3. Disclaimer</h2>
        <p>The materials on LMI Connect are provided on an 'as is' basis. LMI makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.</p>
        
        <h2>4. Limitations</h2>
        <p>In no event shall LMI or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on LMI Connect.</p>
        
        <h2>5. Accuracy of Materials</h2>
        <p>The materials appearing on LMI Connect could include technical, typographical, or photographic errors. LMI does not warrant that any of the materials on LMI Connect are accurate, complete, or current.</p>
        
        <h2>6. Links</h2>
        <p>LMI has not reviewed all of the sites linked to its website and is not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by LMI of the site. Use of any such linked website is at the user's own risk.</p>
        
        <h2>7. Modifications</h2>
        <p>LMI may revise these terms of service for its website at any time without notice. By using this website, you are agreeing to be bound by the then current version of these terms of service.</p>
        
        <h2>8. Governing Law</h2>
        <p>These terms and conditions are governed by and construed in accordance with the laws of the jurisdiction in which LMI operates, and you irrevocably submit to the exclusive jurisdiction of the courts in that location.</p>
        
        <div class="footer">
            <p>&copy; 2025 LAKAN MOTORS - LMI Connect. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''

# Privacy Policy HTML
PRIVACY_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - LMI Connect</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; margin-bottom: 30px; border-bottom: 2px solid #667eea; padding-bottom: 15px; }
        h2 { color: #667eea; margin-top: 25px; margin-bottom: 15px; }
        p { margin-bottom: 15px; }
        ul { margin-left: 20px; margin-bottom: 15px; }
        li { margin-bottom: 10px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 14px; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .back-link { display: inline-block; margin-bottom: 20px; padding: 8px 16px; background: #667eea; color: white; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Login</a>
        <h1>Privacy Policy</h1>
        <p><strong>Last Updated: November 14, 2025</strong></p>
        
        <h2>1. Introduction</h2>
        <p>LAKAN MOTORS ("LMI", "we", "us", or "our") operates the LMI Connect WiFi service ("Service"). This page informs you of our policies regarding the collection, use, and disclosure of personal data when you use our Service and the choices you have associated with that data.</p>
        
        <h2>2. Information Collection and Use</h2>
        <p>We collect several different types of information for various purposes to provide and improve our Service to you.</p>
        <h3>Types of Data Collected:</h3>
        <ul>
            <li><strong>Personal Data:</strong> While using our Service, we may ask you to provide us with certain personally identifiable information that can be used to contact or identify you ("Personal Data"). This may include, but is not limited to:
                <ul style="margin-top: 10px;">
                    <li>Full Name</li>
                    <li>Purpose of visit/use</li>
                    <li>IP Address</li>
                    <li>Browser and device information</li>
                    <li>Usage Data</li>
                </ul>
            </li>
            <li><strong>Usage Data:</strong> We may also collect information on how the Service is accessed and used ("Usage Data"). This may include information such as your computer's Internet Protocol address (e.g. IP address), browser type, browser version, the pages you visit, the time and date of your visit, the time spent on those pages, and other diagnostic data.</li>
            <li><strong>Cookies:</strong> We use cookies and similar tracking technologies to track activity on our Service and hold certain information.</li>
        </ul>
        
        <h2>3. Use of Data</h2>
        <p>LAKAN MOTORS uses the collected data for various purposes:</p>
        <ul>
            <li>To provide and maintain our Service</li>
            <li>To notify you about changes to our Service</li>
            <li>To allow you to participate in interactive features of our Service when you choose to do so</li>
            <li>To provide customer support</li>
            <li>To gather analysis or valuable information so that we can improve our Service</li>
            <li>To monitor the usage of our Service</li>
            <li>To detect, prevent and address technical and security issues</li>
        </ul>
        
        <h2>4. Security of Data</h2>
        <p>The security of your data is important to us but remember that no method of transmission over the Internet or method of electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your Personal Data, we cannot guarantee its absolute security.</p>
        
        <h2>5. Changes to This Privacy Policy</h2>
        <p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date at the top of this Privacy Policy.</p>
        
        <h2>6. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us at support@lakanmotors.com</p>
        
        <div class="footer">
            <p>&copy; 2025 LAKAN MOTORS - LMI Connect. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''

# Admin Login HTML
ADMIN_LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - LMI Connect</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            color: #999;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-login:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .message {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }
        .error { background: #fee; color: #c33; border-left: 4px solid #c33; }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Portal</h1>
        <p class="subtitle">LMI Connect Administration</p>
        <div class="message error" id="errorMessage"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" required placeholder="Enter admin username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" required placeholder="Enter admin password">
            </div>
            <button type="submit" class="btn-login" id="loginBtn">Login</button>
        </form>
        <a href="/" class="back-link">← Back to WiFi Login</a>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('errorMessage');
            const loginBtn = document.getElementById('loginBtn');
            
            errorMessage.style.display = 'none';
            loginBtn.disabled = true;
            
            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    window.location.href = result.redirectUrl || '/admin';
                } else {
                    throw new Error(result.message || 'Login failed');
                }
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
                loginBtn.disabled = false;
            }
        });
    </script>
</body>
</html>'''

# Admin Dashboard HTML
ADMIN_DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - LMI Connect</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 28px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }
        .btn-logout {
            background: rgba(255,255,255,0.3);
            color: white;
            border: 1px solid white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .btn-logout:hover {
            background: rgba(255,255,255,0.5);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #999;
            margin-top: 5px;
            font-size: 14px;
        }
        .table-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .table-header {
            background: #667eea;
            color: white;
            padding: 20px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #f0f2f5;
            padding: 15px 20px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 1px solid #e0e0e0;
        }
        td {
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .timestamp {
            color: #999;
            font-size: 13px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .refresh-btn {
            background: white;
            color: #667eea;
            border: 1px solid white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            background: rgba(255,255,255,0.9);
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 Admin Dashboard</h1>
            <p>LMI Connect WiFi Portal Management</p>
        </div>
        <a href="/admin/logout" class="btn-logout">Logout</a>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalUsers">0</div>
                <div class="stat-label">Total Users Logged In</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="businessUsers">0</div>
                <div class="stat-label">Business Visits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="guestUsers">0</div>
                <div class="stat-label">Guest Visits</div>
            </div>
        </div>

        <div class="table-container">
            <div class="table-header">
                <span>📋 Connected Users</span>
                <button class="refresh-btn" onclick="loadUsers()">🔄 Refresh</button>
            </div>
            <div id="usersContainer" class="loading">
                <div class="spinner"></div>
                <p>Loading users...</p>
            </div>
        </div>
    </div>

    <script>
        async function loadUsers() {
            try {
                const container = document.getElementById('usersContainer');
                container.innerHTML = '<div class="spinner"></div><p>Loading users...</p>';
                
                const response = await fetch('/api/admin/users');
                const result = await response.json();
                
                if (result.success && result.users) {
                    renderUsers(result.users);
                    updateStats(result.users);
                } else {
                    container.innerHTML = '<div class="no-data">No users found or error loading data</div>';
                }
            } catch (error) {
                document.getElementById('usersContainer').innerHTML = '<div class="no-data">Error loading users: ' + error.message + '</div>';
            }
        }
        
        function updateStats(users) {
            document.getElementById('totalUsers').textContent = users.length;
            const businessUsers = users.filter(u => u.purpose === 'business').length;
            const guestUsers = users.filter(u => u.purpose === 'guest').length;
            document.getElementById('businessUsers').textContent = businessUsers;
            document.getElementById('guestUsers').textContent = guestUsers;
        }
        
        function renderUsers(users) {
            if (users.length === 0) {
                document.getElementById('usersContainer').innerHTML = '<div class="no-data">No users logged in yet</div>';
                return;
            }
            
            let html = '<table><thead><tr><th>Full Name</th><th>Purpose</th><th>IP Address</th><th>Login Time</th></tr></thead><tbody>';
            
            users.forEach(user => {
                const loginTime = new Date(user.server_timestamp).toLocaleString();
                html += '<tr>';
                html += '<td><strong>' + escapeHtml(user.fullName) + '</strong></td>';
                html += '<td>' + escapeHtml(user.purpose) + '</td>';
                html += '<td><code>' + escapeHtml(user.ip_address) + '</code></td>';
                html += '<td class="timestamp">' + loginTime + '</td>';
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            document.getElementById('usersContainer').innerHTML = html;
        }
        
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        loadUsers();
        setInterval(loadUsers, 30000);
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Serve the login page"""
    return render_template_string(LOGIN_HTML)

@app.route('/success')
def success():
    """Serve the success page"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(SUCCESS_HTML, timestamp=timestamp)

# ============= TERMS & PRIVACY ROUTES =============

@app.route('/terms')
def terms():
    """Serve Terms of Service page"""
    return render_template_string(TERMS_HTML)

@app.route('/privacy')
def privacy():
    """Serve Privacy Policy page"""
    return render_template_string(PRIVACY_HTML)

# ============= ADMIN ROUTES =============

@app.route('/admin')
@login_required
def admin_dashboard():
    """Serve admin dashboard"""
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Handle admin login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = username
            logger.info(f"Admin {username} logged in")
            return jsonify({'success': True, 'redirectUrl': '/admin'}), 200
        else:
            logger.warning(f"Failed admin login attempt with username: {username}")
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/logout')
def admin_logout():
    """Handle admin logout"""
    if 'admin' in session:
        logger.info(f"Admin {session['admin']} logged out")
        session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/api/admin/users', methods=['GET'])
@login_required
def api_admin_users():
    """Get list of authenticated users (admin only)"""
    try:
        users = load_users()
        return jsonify({
            'success': True,
            'count': len(users),
            'users': users
        }), 200
    except Exception as e:
        logger.error(f"Error fetching users for admin: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch users'
        }), 500

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Handle authentication requests"""
    try:
        data = request.get_json()
        
        # Validate required fields (email and phone removed)
        required_fields = ['fullName', 'purpose', 'terms']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Add server-side timestamp and IP
        data['server_timestamp'] = datetime.now().isoformat()
        data['ip_address'] = request.remote_addr
        data['user_agent'] = request.headers.get('User-Agent', '')
        
        # Save user data
        if save_user(data):
            logger.info(f"New user authenticated: {data['fullName']}")
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirectUrl': '/success'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save user data'
            }), 500
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of authenticated users (admin endpoint)"""
    try:
        users = load_users()
        return jsonify({
            'success': True,
            'count': len(users),
            'users': users
        }), 200
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch users'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

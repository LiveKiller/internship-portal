# Internship Portal Backend Deployment Guide

This guide provides instructions for deploying the Internship Portal backend to various free hosting services without limitations.

## Option 1: Render

[Render](https://render.com/) offers a free tier with the following benefits:
- Free web services with 512 MB RAM
- 750 hours of runtime per month
- Automatic HTTPS/SSL
- Continuous deployment from Git

### Deployment Steps:

1. **Sign up for Render**:
   - Go to [render.com](https://render.com/) and create an account

2. **Create a new Web Service**:
   - Click "New" and select "Web Service"
   - Connect your GitHub/GitLab repository
   - Select the branch to deploy

3. **Configure your service**:
   - Name: `internship-portal-backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
   - Select the free plan

4. **Environment Variables**:
   - Add your MongoDB connection string as `MONGODB_URI`
   - Add your JWT secret key as `JWT_SECRET_KEY`
   - Add any other required environment variables

5. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

## Option 2: Railway

[Railway](https://railway.app/) offers a generous free tier:
- 5$ worth of resources per month (free)
- 512 MB RAM
- Shared CPU
- 1 GB disk

### Deployment Steps:

1. **Sign up for Railway**:
   - Go to [railway.app](https://railway.app/) and create an account
   - Connect your GitHub account

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure your service**:
   - Set the start command to `python run.py`
   - Add environment variables (MongoDB URI, JWT secret, etc.)

4. **Deploy**:
   - Railway will automatically build and deploy your application
   - You can view logs and monitor your application from the dashboard

## Option 3: Fly.io

[Fly.io](https://fly.io/) offers a free tier with:
- 3 shared-cpu-1x 256MB VMs
- 3GB persistent volume storage (total)
- 160GB outbound data transfer

### Deployment Steps:

1. **Install Flyctl**:
   - Install the Fly CLI tool following instructions at [fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/)

2. **Sign up and log in**:
   ```
   flyctl auth signup
   ```

3. **Initialize your app**:
   - Navigate to your project directory
   ```
   cd internship-portal
   flyctl launch
   ```
   - This will create a `fly.toml` file

4. **Configure your app**:
   - Edit the `fly.toml` file to set environment variables
   - Create a `Dockerfile` if you don't have one

5. **Deploy**:
   ```
   flyctl deploy
   ```

## Option 4: PythonAnywhere

[PythonAnywhere](https://www.pythonanywhere.com/) offers a free tier with:
- One web app
- 512MB storage
- Limited CPU time and bandwidth (but sufficient for development)

### Deployment Steps:

1. **Sign up for PythonAnywhere**:
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and create an account

2. **Upload your code**:
   - Use the Files tab to upload your code or clone from GitHub
   ```
   git clone https://github.com/yourusername/internship-portal.git
   ```

3. **Set up a virtual environment**:
   ```
   mkvirtualenv --python=/usr/bin/python3.8 myenv
   pip install -r requirements.txt
   ```

4. **Configure a web app**:
   - Go to the Web tab
   - Click "Add a new web app"
   - Choose "Manual configuration" and select Python version
   - Set the path to your Flask app (e.g., `/home/yourusername/internship-portal/run.py`)
   - Set WSGI configuration file to point to your Flask app

5. **Set environment variables**:
   - In the Web tab, under "WSGI configuration file", add your environment variables

## Preparing Your Application for Deployment

Before deploying, make sure to:

1. **Update database connection**:
   - Use environment variables for database connection strings
   - Make sure your application reads from `os.environ.get('MONGODB_URI')`

2. **Configure CORS**:
   - Update CORS settings to allow requests from your frontend domain
   ```python
   from flask_cors import CORS
   CORS(app, origins=["https://your-frontend-domain.com"])
   ```

3. **Set up proper logging**:
   - Configure logging to help with debugging
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

4. **Create a requirements.txt file**:
   ```
   pip freeze > requirements.txt
   ```

5. **Create a Procfile** (for some platforms):
   ```
   web: python run.py
   ```

## MongoDB Hosting Options

For your database, you can use:

1. **MongoDB Atlas**:
   - Free tier with 512MB storage
   - Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Create a cluster, database user, and whitelist your IP

2. **Railway MongoDB**:
   - Can be added as a plugin to your Railway project
   - 1GB storage in free tier

## Connecting Frontend to Backend

After deploying your backend, update your frontend configuration to point to your new backend URL:

```javascript
// In your frontend config file
const API_URL = 'https://your-backend-url.com';
```

## Monitoring and Maintenance

- Set up health check endpoints to monitor your application
- Use logging to track errors and performance
- Set up alerts for downtime or errors

Remember to check the terms of service for each platform as they may change over time.

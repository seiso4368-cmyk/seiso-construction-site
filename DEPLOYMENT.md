# Seiso Construction Website - Deployment Guide

## Overview

This is a Flask-based construction company website with email contact functionality. The site is configured for deployment on Railway.app.

## Features

- **Responsive Design**: Mobile-friendly website
- **Contact Form**: Collects customer inquiries with email notifications
- **Email Integration**: Sends emails via Gmail SMTP
- **Auto-replies**: Automatic confirmation emails to customers
- **Admin Notifications**: Alerts for new contact submissions

## Prerequisites

- Python 3.8+
- Git
- Railway.app account (https://railway.app)
- Gmail account with App Password

## Local Development

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd construction-company-site
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
PORT=5000
```

**Note**: Use an [App Password](https://myaccount.google.com/apppasswords) from your Gmail account, not your regular password.

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deployment to Railway.app

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit with email functionality"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Railway.app

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose your repository
5. Railway will automatically detect the Flask app

### 3. Configure Environment Variables on Railway

In your Railway project dashboard:

1. Go to "Variables"
2. Add the following variables:
   - `MAIL_USERNAME`: your-email@gmail.com
   - `MAIL_PASSWORD`: your-app-password
   - `MAIL_DEFAULT_SENDER`: your-email@gmail.com
   - `SECRET_KEY`: your-secret-key

**Important**: Do NOT commit `.env` file to GitHub. It's already in `.gitignore`.

### 4. Deploy

Railway will automatically deploy when you push to the main branch.

## Troubleshooting

### Email Not Sending

1. Verify Gmail App Password is correct
2. Check that "Less secure app access" is not blocking the connection
3. Review Railway logs for error messages

### 404 Errors on Routes

Ensure all template files are in the `templates/` directory and static files are in the `static/` directory.

### Port Issues

Railway automatically assigns a port. The app reads from the `PORT` environment variable.

## File Structure

```
construction-company-site/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Process file for deployment
├── railway.json          # Railway.app configuration
├── .env                  # Environment variables (local only)
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── services.html
│   ├── portfolio.html
│   └── contact.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── main.js
    │   ├── contact.js
    │   └── portfolio.js
    └── images/
```

## Support

For issues or questions, contact the development team.

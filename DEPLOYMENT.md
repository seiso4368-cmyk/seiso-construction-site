# Seiso Construction Website - Deployment Guide

## Overview

This is a Flask-based construction company website with email contact functionality. The site is configured for deployment on a standard Python host such as StormerHost.

## Features

- **Responsive Design**: Mobile-friendly website
- **Contact Form**: Collects customer inquiries with email notifications
- **Email Integration**: Sends emails via Gmail SMTP
- **Auto-replies**: Automatic confirmation emails to customers
- **Admin Notifications**: Alerts for new contact submissions

## Prerequisites

- Python 3.8+
- Git
- StormerHost account with Python/Flask hosting, SSH, Git, or FTP access
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
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_RECIPIENT=where-bookings-should-go@example.com
MAX_UPLOAD_MB=25
MAX_FILE_SIZE_MB=10
MAX_FILE_COUNT=5
PORT=5000
```

**Note**: Use an [App Password](https://myaccount.google.com/apppasswords) from your Gmail account, not your regular password. Consultation requests can include project files as email attachments, so make sure the recipient mailbox can receive attachments up to your configured upload limits.

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deployment to StormerHost

1. Pull or upload the latest `main` branch from GitHub to the StormerHost application directory.
2. Configure the application to run with the project `Procfile` command:

   ```bash
   gunicorn app:app
   ```

3. Configure the required environment variables in the StormerHost hosting panel or server environment. Keep secrets such as `RESEND_API_KEY`, `RESEND_FROM`, `RESEND_RECIPIENT`, and `SECRET_KEY` out of GitHub.
4. Point `seisoconstruction.com` to the StormerHost application and restart the Python/Gunicorn service.
5. Confirm that the live site is serving the latest GitHub commit before testing the contact form.

## Troubleshooting

### Email or Attachment Sending Issues

1. Verify the SMTP username and app password are correct.
2. Confirm `MAIL_RECIPIENT` is set to the address where consultation requests should be delivered.
3. Keep uploads within the configured attachment limits. Many email providers reject large video attachments; if that happens, reduce `MAX_UPLOAD_MB`, `MAX_FILE_SIZE_MB`, or request smaller videos.
4. Review the StormerHost application logs for error messages.

### 404 Errors on Routes

Ensure all template files are in the `templates/` directory and static files are in the `static/` directory.

### Port Issues

The hosting provider should expose its assigned port through the `PORT` environment variable.

## File Structure

```
construction-company-site/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Process file for deployment
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

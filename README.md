# BuildPro Construction Website

A professional, responsive website for a construction company built with Python Flask, HTML, CSS, and JavaScript.

## Features

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Professional design with smooth animations and transitions
- **Multiple Pages**: Home, Services, Portfolio, and Contact pages
- **Contact Form**: Functional contact form with validation and server-side processing
- **Portfolio Filtering**: Filter portfolio projects by category
- **Mobile Menu**: Hamburger menu for mobile navigation
- **SEO Friendly**: Semantic HTML structure for better search engine optimization

## Project Structure

```
construction-company-site/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates
│   ├── base.html                   # Base template with navigation and footer
│   ├── index.html                  # Home page
│   ├── services.html               # Services page
│   ├── portfolio.html              # Portfolio page
│   └── contact.html                # Contact page
└── static/                         # Static files
    ├── css/
    │   └── style.css               # Main stylesheet
    └── js/
        ├── main.js                 # General JavaScript functionality
        ├── portfolio.js            # Portfolio filtering
        └── contact.js              # Contact form handling
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- VS Code (or any text editor)

### Steps

1. **Clone or download the project** to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd construction-company-site
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Open in browser**:
   Navigate to `http://localhost:5000` in your web browser

## Usage

### Pages

- **Home** (`/`): Landing page with hero section, features, and service preview
- **Services** (`/services`): Detailed service offerings with process steps
- **Portfolio** (`/portfolio`): Showcase of completed projects with filtering
- **Contact** (`/contact`): Contact information and inquiry form

### Customization

#### Update Company Information

Edit the following files to customize company details:

- **Company Name**: Update "BuildPro" in `templates/base.html` and `templates/index.html`
- **Contact Info**: Edit footer and contact page in respective template files
- **Colors**: Modify CSS variables in `static/css/style.css`:
  ```css
  :root {
      --primary-color: #1e3a8a;      /* Main blue */
      --secondary-color: #f97316;    /* Orange accent */
      --accent-color: #64748b;       /* Gray text */
  }
  ```

#### Add Your Content

- **Services**: Edit `templates/services.html` to add your specific services
- **Portfolio**: Add projects to `templates/portfolio.html` with appropriate categories
- **Images**: Place images in `static/images/` and reference them in templates

#### Modify Styling

- Main stylesheet: `static/css/style.css`
- Responsive breakpoints are included for mobile (480px) and tablet (768px)

### Contact Form

The contact form currently logs submissions to the console. To enable email notifications:

1. Install email library:
   ```bash
   pip install python-dotenv
   ```

2. Update `app.py` to send emails (example with SMTP):
   ```python
   import smtplib
   from email.mime.text import MIMEText
   
   # Add email sending logic in the submit_contact route
   ```

## Development

### Adding New Pages

1. Create a new HTML template in `templates/` extending `base.html`
2. Add a new route in `app.py`
3. Add navigation link in `templates/base.html`

### Adding JavaScript Features

- General functionality: `static/js/main.js`
- Page-specific scripts: Create new files in `static/js/` and include in templates

### Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE11: Not supported (uses modern CSS features)

## Deployment

### Local Testing

Run the development server:
```bash
python app.py
```

### Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

2. **Set Flask to production mode**:
   ```python
   app.run(debug=False)
   ```

3. **Deploy to platforms** like:
   - Heroku
   - PythonAnywhere
   - AWS
   - Google Cloud
   - DigitalOcean

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, modify `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to different port
```

### CSS Not Loading

- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Restart the Flask development server
- Check that static files path is correct

### Form Not Submitting

- Check browser console for JavaScript errors (F12)
- Verify Flask server is running
- Check network tab in browser developer tools

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Design**: Responsive CSS Grid and Flexbox
- **Icons**: Unicode emoji for visual elements

## License

This project is provided as-is for your construction company website.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask documentation: https://flask.palletsprojects.com/
3. Check browser console for error messages

---

**Happy building! 🏗️**

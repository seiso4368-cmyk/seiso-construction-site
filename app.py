from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message_text = data.get('message')
        
        # Validate required fields
        if not all([name, email, phone, message_text]):
            return jsonify({
                'success': False,
                'message': 'All fields are required.'
            }), 400
        
        # Send email to admin
        msg = Message(
            subject=f'New Contact Form Submission from {name}',
            recipients=[os.getenv('MAIL_DEFAULT_SENDER')],
            body=f"""New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message_text}
"""
        )
        
        # Send reply to customer
        reply_msg = Message(
            subject='We received your message - Seiso Construction',
            recipients=[email],
            body=f"""Dear {name},

Thank you for contacting Seiso Construction. We have received your message and will get back to you as soon as possible.

Best regards,
Seiso Construction Team
"""
        )
        
        mail.send(msg)
        mail.send(reply_msg)
        
        print(f"Contact form received and email sent: {name}, {email}, {phone}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message. We will contact you soon!'
        })
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

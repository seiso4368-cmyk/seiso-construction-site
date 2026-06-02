from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import mimetypes
import os
import smtplib
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Public business inbox used as a non-secret fallback for recipient/sender metadata.
# SMTP login still requires MAIL_USERNAME and MAIL_PASSWORD in production.
DEFAULT_CONTACT_EMAIL = os.getenv('SEISO_CONTACT_EMAIL', 'seiso4368@gmail.com')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Upload / email attachment limits. Keep this conservative because many email
# providers reject messages with large attachments.
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_MB', '25')) * 1024 * 1024
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILE_COUNT = int(os.getenv('MAX_FILE_COUNT', '5'))

ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'heic',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt',
    'dwg', 'dxf',
    'mp4', 'mov', 'avi', 'mkv', 'webm'
}

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_USERNAME') or DEFAULT_CONTACT_EMAIL

# Fail fast when SMTP is unreachable instead of letting the web worker hang until Gunicorn kills it.
app.config['MAIL_TIMEOUT'] = int(os.getenv('MAIL_TIMEOUT', '20'))

mail = Mail(app)


def allowed_file(filename):
    """Return True when the upload extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_form_value(field_name, default=''):
    """Read and trim a form field safely."""
    return request.form.get(field_name, default).strip()


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
    return render_template('contact.html', max_file_count=MAX_FILE_COUNT, max_file_size_mb=MAX_FILE_SIZE_MB)


@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle consultation booking and contact form submissions with attachments."""
    try:
        name = clean_form_value('name')
        email = clean_form_value('email')
        phone = clean_form_value('phone')
        subject = clean_form_value('subject')
        consultation_date = clean_form_value('consultation_date')
        consultation_time = clean_form_value('consultation_time')
        project_address = clean_form_value('project_address')
        project_budget = clean_form_value('project_budget')
        message_text = clean_form_value('message')

        # Validate required fields
        if not all([name, email, phone, subject, consultation_date, consultation_time, message_text]):
            return jsonify({
                'success': False,
                'message': 'Please complete all required fields, including consultation date and time.'
            }), 400

        uploaded_files = [file for file in request.files.getlist('project_files') if file and file.filename]

        if len(uploaded_files) > MAX_FILE_COUNT:
            return jsonify({
                'success': False,
                'message': f'Please upload no more than {MAX_FILE_COUNT} files.'
            }), 400

        prepared_attachments = []
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            if not filename:
                continue

            if not allowed_file(filename):
                return jsonify({
                    'success': False,
                    'message': f'The file type for "{filename}" is not supported. Please upload images, videos, PDFs, documents, spreadsheets, or plan files.'
                }), 400

            file_bytes = uploaded_file.read()
            if len(file_bytes) > MAX_FILE_SIZE_BYTES:
                return jsonify({
                    'success': False,
                    'message': f'"{filename}" is too large. Each file must be {MAX_FILE_SIZE_MB} MB or smaller.'
                }), 400

            content_type = uploaded_file.content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            prepared_attachments.append({
                'filename': filename,
                'content_type': content_type,
                'data': file_bytes,
                'size_mb': len(file_bytes) / (1024 * 1024)
            })

        recipient = os.getenv('MAIL_RECIPIENT') or app.config.get('MAIL_DEFAULT_SENDER') or DEFAULT_CONTACT_EMAIL
        if not recipient:
            return jsonify({
                'success': False,
                'message': 'Email recipient is not configured. Please set MAIL_RECIPIENT or MAIL_DEFAULT_SENDER in the Railway service Variables tab, then deploy the staged changes.'
            }), 500

        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            return jsonify({
                'success': False,
                'message': 'Email SMTP login is not configured in the running Railway service. Please confirm MAIL_USERNAME and MAIL_PASSWORD are set on the production service and deploy the staged changes.'
            }), 500

        attachment_summary = '\n'.join(
            f"- {item['filename']} ({item['size_mb']:.2f} MB)" for item in prepared_attachments
        ) or 'No files attached.'

        # Send email to admin with booking details and attachments
        admin_msg = Message(
            subject=f'New Consultation Booking from {name}',
            recipients=[recipient],
            reply_to=email,
            body=f"""New consultation booking request:

Name: {name}
Email: {email}
Phone: {phone}
Project Type: {subject}
Preferred Date: {consultation_date}
Preferred Time: {consultation_time}
Project Address: {project_address or 'Not provided'}
Estimated Budget: {project_budget or 'Not provided'}

Project Details:
{message_text}

Attached Files:
{attachment_summary}
"""
        )

        for attachment in prepared_attachments:
            admin_msg.attach(
                filename=attachment['filename'],
                content_type=attachment['content_type'],
                data=attachment['data']
            )

        # Send confirmation reply to customer without attaching their uploaded files
        reply_msg = Message(
            subject='We received your consultation request - Seiso Construction',
            recipients=[email],
            body=f"""Dear {name},

Thank you for booking a consultation with Seiso Construction. We have received your request and will review your project details.

Preferred consultation date: {consultation_date}
Preferred consultation time: {consultation_time}
Files received: {len(prepared_attachments)}

A member of our team will contact you soon to confirm the consultation.

Best regards,
Seiso Construction Team
"""
        )

        try:
            print(
                f"Sending consultation booking email via {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')} "
                f"with timeout={app.config.get('MAIL_TIMEOUT')}s, recipient={recipient}, files={len(prepared_attachments)}",
                flush=True
            )
            mail.send(admin_msg)
            mail.send(reply_msg)
        except (smtplib.SMTPException, OSError, TimeoutError, socket.timeout) as email_error:
            print(
                f"SMTP error sending consultation booking email: {type(email_error).__name__}: {email_error}",
                flush=True
            )
            return jsonify({
                'success': False,
                'message': 'We could not send your request because the email service did not respond. Please contact us directly while we finish email setup.'
            }), 502

        print(f"Consultation booking received and email sent: {name}, {email}, {phone}, files={len(prepared_attachments)}", flush=True)

        return jsonify({
            'success': True,
            'message': 'Thank you. Your consultation request and project files have been sent successfully!'
        })
    except Exception as e:
        print(f"Error sending consultation booking email: {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'We could not send your request right now. Please try again later or contact us directly.'
        }), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'message': f'The uploaded files are too large. Please keep the total upload under {os.getenv("MAX_UPLOAD_MB", "25")} MB.'
    }), 413


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

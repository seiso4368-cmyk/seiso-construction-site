from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from email.utils import parseaddr
import mimetypes
import os
import smtplib
import socket
import ssl
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

# Email configuration. This version intentionally uses direct smtplib instead
# of Flask-Mail because the Flask-Mail version in production opens SMTP sockets
# without passing a timeout, which allows Gmail SMTP attempts to hang until
# Gunicorn kills the worker.
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER') or MAIL_USERNAME or DEFAULT_CONTACT_EMAIL
MAIL_TIMEOUT = int(os.getenv('MAIL_TIMEOUT', '20'))


def allowed_file(filename):
    """Return True when the upload extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_form_value(field_name, default=''):
    """Read and trim a form field safely."""
    return request.form.get(field_name, default).strip()


def normalize_sender(sender_value):
    """Return a usable email address from a sender value."""
    parsed_name, parsed_email = parseaddr(sender_value or '')
    return parsed_email or sender_value or DEFAULT_CONTACT_EMAIL


def attach_prepared_files(email_message, prepared_attachments):
    """Attach uploaded files to an EmailMessage."""
    for attachment in prepared_attachments:
        content_type = attachment['content_type'] or 'application/octet-stream'
        if '/' in content_type:
            maintype, subtype = content_type.split('/', 1)
        else:
            maintype, subtype = 'application', 'octet-stream'

        email_message.add_attachment(
            attachment['data'],
            maintype=maintype,
            subtype=subtype,
            filename=attachment['filename']
        )


def send_messages_with_timeout(messages):
    """Send all messages through SMTP with an explicit socket timeout."""
    previous_default_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(MAIL_TIMEOUT)

    try:
        print(
            f"Opening SMTP connection to {MAIL_SERVER}:{MAIL_PORT} "
            f"ssl={MAIL_USE_SSL}, tls={MAIL_USE_TLS}, timeout={MAIL_TIMEOUT}s",
            flush=True
        )

        if MAIL_USE_SSL:
            smtp_context = ssl.create_default_context()
            with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=MAIL_TIMEOUT, context=smtp_context) as smtp:
                smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
                for message in messages:
                    smtp.send_message(message)
        else:
            with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=MAIL_TIMEOUT) as smtp:
                smtp.ehlo()
                if MAIL_USE_TLS:
                    smtp_context = ssl.create_default_context()
                    smtp.starttls(context=smtp_context)
                    smtp.ehlo()
                smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
                for message in messages:
                    smtp.send_message(message)
    finally:
        socket.setdefaulttimeout(previous_default_timeout)


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

        recipient = os.getenv('MAIL_RECIPIENT') or MAIL_DEFAULT_SENDER or DEFAULT_CONTACT_EMAIL
        if not recipient:
            return jsonify({
                'success': False,
                'message': 'Email recipient is not configured. Please set MAIL_RECIPIENT or MAIL_DEFAULT_SENDER in the Railway service Variables tab, then deploy the staged changes.'
            }), 500

        if not MAIL_USERNAME or not MAIL_PASSWORD:
            return jsonify({
                'success': False,
                'message': 'Email SMTP login is not configured in the running Railway service. Please confirm MAIL_USERNAME and MAIL_PASSWORD are set on the production service and deploy the staged changes.'
            }), 500

        sender_email = normalize_sender(MAIL_DEFAULT_SENDER)
        attachment_summary = '\n'.join(
            f"- {item['filename']} ({item['size_mb']:.2f} MB)" for item in prepared_attachments
        ) or 'No files attached.'

        admin_msg = EmailMessage()
        admin_msg['Subject'] = f'New Consultation Booking from {name}'
        admin_msg['From'] = sender_email
        admin_msg['To'] = recipient
        admin_msg['Reply-To'] = email
        admin_msg.set_content(f"""New consultation booking request:

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
""")
        attach_prepared_files(admin_msg, prepared_attachments)

        reply_msg = EmailMessage()
        reply_msg['Subject'] = 'We received your consultation request - Seiso Construction'
        reply_msg['From'] = sender_email
        reply_msg['To'] = email
        reply_msg.set_content(f"""Dear {name},

Thank you for booking a consultation with Seiso Construction. We have received your request and will review your project details.

Preferred consultation date: {consultation_date}
Preferred consultation time: {consultation_time}
Files received: {len(prepared_attachments)}

A member of our team will contact you soon to confirm the consultation.

Best regards,
Seiso Construction Team
""")

        try:
            print(
                f"Sending consultation booking email via direct SMTP {MAIL_SERVER}:{MAIL_PORT} "
                f"with timeout={MAIL_TIMEOUT}s, recipient={recipient}, files={len(prepared_attachments)}",
                flush=True
            )
            send_messages_with_timeout([admin_msg, reply_msg])
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
        print(f"Error sending consultation booking email: {type(e).__name__}: {str(e)}", flush=True)
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

from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename
from urllib import request as urlrequest
from urllib import error as urlerror
import base64
import html
import json
import mimetypes
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Public business inbox used as a non-secret fallback for recipient metadata.
DEFAULT_CONTACT_EMAIL = os.getenv('SEISO_CONTACT_EMAIL', 'seiso4368@gmail.com')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')


def is_secure_request():
    """Recognise HTTPS correctly when the app runs behind LiteSpeed or a proxy."""
    forwarded_proto = request.headers.get('X-Forwarded-Proto', '').split(',')[0].strip().lower()
    return (
        request.is_secure
        or request.environ.get('HTTPS', '').lower() in {'on', '1', 'true'}
        or forwarded_proto == 'https'
    )


@app.before_request
def enforce_https():
    """Send all public traffic to the encrypted version of the website."""
    if not is_secure_request():
        return redirect(request.url.replace('http://', 'https://', 1), code=301)

# Upload / email attachment limits. Resend allows up to 40 MB per email after
# Base64 encoding, so this keeps form submissions safely below that ceiling.
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

# Resend HTTPS Email API configuration. This avoids SMTP ports entirely, which
# is important because Railway is currently unable to reach Gmail SMTP from the
# production container.
RESEND_API_URL = os.getenv('RESEND_API_URL', 'https://api.resend.com/emails')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
RESEND_FROM = os.getenv('RESEND_FROM')
RESEND_RECIPIENT = os.getenv('RESEND_RECIPIENT') or os.getenv('MAIL_RECIPIENT') or DEFAULT_CONTACT_EMAIL
RESEND_TIMEOUT = int(os.getenv('RESEND_TIMEOUT', os.getenv('MAIL_TIMEOUT', '20')))
SEND_CUSTOMER_CONFIRMATION = os.getenv('SEND_CUSTOMER_CONFIRMATION', 'true').lower() == 'true'


class ResendAPIError(Exception):
    """Raised when Resend rejects or cannot process an email request."""

    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def allowed_file(filename):
    """Return True when the upload extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_form_value(field_name, default=''):
    """Read and trim a form field safely."""
    return request.form.get(field_name, default).strip()


def plain_to_html(text):
    """Convert a plain-text message into simple HTML with escaped content."""
    escaped = html.escape(text)
    return '<div style="font-family:Arial,sans-serif;line-height:1.5;white-space:pre-wrap;">' + escaped + '</div>'


def send_resend_email(payload):
    """Send one email through Resend using only Python standard-library HTTPS."""
    if not RESEND_API_KEY:
        raise ResendAPIError('RESEND_API_KEY is not configured.')

    if not RESEND_FROM:
        raise ResendAPIError('RESEND_FROM is not configured.')

    body = json.dumps(payload).encode('utf-8')
    headers = {
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        # Railway reached Resend but received a 403 body of "error code: 1010".
        # Use an explicit application User-Agent instead of urllib's default
        # Python user agent to avoid edge/WAF rejection of generic clients.
        'User-Agent': 'SeisoConstructionWebsite/1.0 (+https://seisoconstruction.com)',
    }
    req = urlrequest.Request(RESEND_API_URL, data=body, headers=headers, method='POST')

    try:
        with urlrequest.urlopen(req, timeout=RESEND_TIMEOUT) as response:
            response_body = response.read().decode('utf-8', errors='replace')
            return json.loads(response_body) if response_body else {}
    except urlerror.HTTPError as http_error:
        response_body = http_error.read().decode('utf-8', errors='replace')
        raise ResendAPIError(
            f'Resend returned HTTP {http_error.code}.',
            status_code=http_error.code,
            response_body=response_body,
        ) from http_error
    except (urlerror.URLError, TimeoutError, socket.timeout, OSError) as network_error:
        raise ResendAPIError(f'Resend network error: {network_error}') from network_error


# Cache control decorator for static assets
def cache_static(max_age=31536000):  # 1 year for static assets
    def decorator(f):
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.cache_control.max_age = max_age
            response.cache_control.public = True
            return response
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Add cache and browser security headers to all responses
@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        # Cache static assets for 1 year
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
        response.add_etag()
    else:
        # Don't cache HTML pages
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    if is_secure_request():
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000')
    return response

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
                'content': base64.b64encode(file_bytes).decode('ascii'),
                'size_mb': len(file_bytes) / (1024 * 1024),
            })

        if not RESEND_RECIPIENT:
            return jsonify({
                'success': False,
                'message': 'Email recipient is not configured. Please set RESEND_RECIPIENT or MAIL_RECIPIENT in Railway Variables, then redeploy.'
            }), 500

        if not RESEND_API_KEY:
            return jsonify({
                'success': False,
                'message': 'Resend API key is not configured. Please set RESEND_API_KEY in Railway Variables, then redeploy.'
            }), 500

        if not RESEND_FROM:
            return jsonify({
                'success': False,
                'message': 'Resend sender is not configured. Please set RESEND_FROM to a verified Resend sender address, then redeploy.'
            }), 500

        attachment_summary = '\n'.join(
            f"- {item['filename']} ({item['size_mb']:.2f} MB)" for item in prepared_attachments
        ) or 'No files attached.'

        admin_text = f"""New consultation booking request:

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

        admin_payload = {
            'from': RESEND_FROM,
            'to': [RESEND_RECIPIENT],
            'subject': f'New Consultation Booking from {name}',
            'text': admin_text,
            'html': plain_to_html(admin_text),
            'reply_to': email,
        }

        if prepared_attachments:
            admin_payload['attachments'] = [
                {
                    'filename': item['filename'],
                    'content': item['content'],
                    'content_type': item['content_type'],
                }
                for item in prepared_attachments
            ]

        customer_text = f"""Dear {name},

Thank you for booking a consultation with Seiso Construction. We have received your request and will review your project details.

Preferred consultation date: {consultation_date}
Preferred consultation time: {consultation_time}
Files received: {len(prepared_attachments)}

A member of our team will contact you soon to confirm the consultation.

Best regards,
Seiso Construction Team
"""

        customer_payload = {
            'from': RESEND_FROM,
            'to': [email],
            'subject': 'We received your consultation request - Seiso Construction',
            'text': customer_text,
            'html': plain_to_html(customer_text),
            'reply_to': RESEND_RECIPIENT,
        }

        try:
            print(
                f"Sending consultation booking email via Resend HTTPS API, "
                f"recipient={RESEND_RECIPIENT}, customer_confirmation={SEND_CUSTOMER_CONFIRMATION}, "
                f"files={len(prepared_attachments)}, timeout={RESEND_TIMEOUT}s, user_agent=custom",
                flush=True,
            )
            admin_result = send_resend_email(admin_payload)
            print(f"Resend admin email accepted: {admin_result}", flush=True)

            if SEND_CUSTOMER_CONFIRMATION:
                customer_result = send_resend_email(customer_payload)
                print(f"Resend customer confirmation accepted: {customer_result}", flush=True)
        except ResendAPIError as email_error:
            print(
                f"Resend error sending consultation booking email: {email_error}; "
                f"status={email_error.status_code}; body={email_error.response_body}",
                flush=True,
            )
            return jsonify({
                'success': False,
                'message': 'We could not send your request because the email service did not accept the message. Please contact us directly while we finish email setup.'
            }), 502

        print(f"Consultation booking received and email sent via Resend: {name}, {email}, {phone}, files={len(prepared_attachments)}", flush=True)

        return jsonify({
            'success': True,
            'message': 'Thank you. Your consultation request and project files have been sent successfully!'
        })
    except Exception as e:
        print(f"Error processing consultation booking request: {type(e).__name__}: {str(e)}", flush=True)
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

# Rebuild triggered at Sat Jul 18 13:38:44 UTC 2026
# Rebuild triggered at Sat Jul 18 15:32:06 UTC 2026

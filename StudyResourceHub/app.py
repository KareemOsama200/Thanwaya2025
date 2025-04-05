import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
import dotenv

# Load environment variables from .env file if present
dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize app
app = Flask(__name__)

# Configure database based on environment
# Check for DATABASE_URL (used by Vercel/Heroku) or fallback to SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku/Vercel uses 'postgres://' which SQLAlchemy no longer accepts
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.logger.info("Using PostgreSQL database")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.logger.info("Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder based on environment (Vercel or local)
is_vercel = os.environ.get('VERCEL', False)
if is_vercel:
    # On Vercel, use /tmp for file uploads (the only writable directory)
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.logger.info("Running on Vercel - using /tmp for uploads")
else:
    # Local development
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.logger.info("Running locally - using ./uploads for uploads")

app.secret_key = os.environ.get("SESSION_SECRET", "your_fallback_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add a context processor to make the current date available to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.admin_login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى لوحة التحكم'

# Import routes after initializing app and db to avoid circular imports
from models import Admin
from admin import admin_routes
import utils

# Register blueprints
app.register_blueprint(admin_routes)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    from flask import render_template
    from models import Subject
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

# Subject route
@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    from flask import render_template, abort
    from models import Subject, Section
    subject = Subject.query.get_or_404(subject_id)
    sections = Section.query.filter_by(subject_id=subject_id).all()
    return render_template('subject.html', subject=subject, sections=sections)

# Section route
@app.route('/section/<int:section_id>')
def section(section_id):
    from flask import render_template, abort
    from models import Section, File
    section = Section.query.get_or_404(section_id)
    files = File.query.filter_by(section_id=section_id).all()
    return render_template('section.html', section=section, files=files)

# Download file route
@app.route('/download/<int:file_id>')
def download_file(file_id):
    from flask import send_from_directory, abort
    from models import File
    file_record = File.query.get_or_404(file_id)
    
    # Increment download count
    file_record.download_count += 1
    db.session.commit()
    
    # Generate path for the file
    file_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        str(file_record.section.subject.id),
        str(file_record.section.id)
    )
    
    return send_from_directory(file_path, file_record.filename, as_attachment=True)

# Initialize database tables
with app.app_context():
    db.create_all()
    
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin = Admin(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Default admin account created.")

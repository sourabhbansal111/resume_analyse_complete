from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from database import Database
from config import Config
from auth import hash_password, verify_password, generate_token, verify_token, require_auth, require_admin

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)

# Configuration
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
MAX_FILE_SIZE = Config.MAX_CONTENT_LENGTH

# Set upload folder relative to project root
upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = upload_path
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize components
db = Database()
resume_parser = ResumeParser()
skill_extractor = SkillExtractor()
job_matcher = JobMatcher()

# Ensure upload directory exists
os.makedirs(upload_path, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Resume Analyzer API is running'})

# Authentication endpoints
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'user')
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Check if user exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        try:
            user_id = db.create_user(email, password_hash, name, role)
            token = generate_token(user_id, role)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'role': role
                },
                'message': 'User created successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user
        user = db.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user['id'], user['role'])
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    try:
        user_id = request.current_user['user_id']
        user = db.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Upload and parse resume PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse resume
        resume_text = resume_parser.parse_pdf(filepath)
        
        # Extract skills
        skills = skill_extractor.extract_skills(resume_text)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'skills': skills,
            'skill_count': len(skills),
            'message': 'Resume uploaded and parsed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """Analyze resume and match with jobs"""
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename required'}), 400
    
    filename = data['filename']
    company_id = data.get('company_id')  # None means all companies
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Parse resume
        resume_text = resume_parser.parse_pdf(filepath)
        
        # Extract skills
        skills = skill_extractor.extract_skills(resume_text)
        
        # Get jobs (filtered by company if specified)
        jobs = db.get_all_jobs(company_id=company_id)
        
        if not jobs:
            return jsonify({
                'error': f'No jobs found{" for selected company" if company_id else ""}. Please add jobs in the Admin Panel.'
            }), 404
        
        # Match with jobs
        matches = job_matcher.match_with_all_jobs(skills, jobs)
        
        # Add improvement tips and company info to each match
        for match in matches:
            missing_skills = match['missing_required_skills'] + match['missing_preferred_skills']
            match['improvement_tips'] = job_matcher.generate_improvement_tips(
                missing_skills, match['job_title']
            )
            # Add company info from job data
            job_data = next((j for j in jobs if j['id'] == match['job_id']), None)
            if job_data:
                match['company_name'] = job_data.get('company_name', 'Unknown')
                match['company_logo'] = job_data.get('company_logo')
                match['company_website'] = job_data.get('company_website')
        
        # Save analysis
        analysis_result = {
            'skills': skills,
            'matches': matches,
            'total_jobs': len(jobs),
            'company_id': company_id
        }
        db.save_analysis(filename, skills, analysis_result)
        
        return jsonify({
            'success': True,
            'extracted_skills': skills,
            'matches': matches,
            'total_jobs_analyzed': len(jobs)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Company endpoints (public - anyone can view)
@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    try:
        companies = db.get_all_companies()
        return jsonify({
            'success': True,
            'companies': companies,
            'count': len(companies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies', methods=['POST'])
@require_admin
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        company_id = db.add_company(
            name=data.get('name'),
            description=data.get('description'),
            logo_url=data.get('logo_url'),
            website=data.get('website')
        )
        return jsonify({
            'success': True,
            'company_id': company_id,
            'message': 'Company created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get specific company by ID"""
    try:
        company = db.get_company_by_id(company_id)
        if company:
            return jsonify({
                'success': True,
                'company': company
            })
        else:
            return jsonify({'error': 'Company not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['PUT'])
@require_admin
def update_company(company_id):
    """Update a company"""
    try:
        data = request.get_json()
        db.update_company(
            company_id=company_id,
            name=data.get('name'),
            description=data.get('description'),
            logo_url=data.get('logo_url'),
            website=data.get('website')
        )
        return jsonify({
            'success': True,
            'message': 'Company updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['DELETE'])
@require_admin
def delete_company(company_id):
    """Delete a company"""
    try:
        db.delete_company(company_id)
        return jsonify({
            'success': True,
            'message': 'Company deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Job endpoints
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all available job roles, optionally filtered by company"""
    try:
        company_id = request.args.get('company_id', type=int)
        jobs = db.get_all_jobs(company_id=company_id)
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
@require_admin
def create_job():
    """Create a new job role"""
    try:
        data = request.get_json()
        job_id = db.add_job_role(
            company_id=data.get('company_id'),
            title=data.get('title'),
            description=data.get('description'),
            required_skills=data.get('required_skills', []),
            preferred_skills=data.get('preferred_skills', []),
            experience_level=data.get('experience_level', 'Mid'),
            location=data.get('location'),
            salary_range=data.get('salary_range')
        )
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Job created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get specific job role by ID"""
    try:
        job = db.get_job_by_id(job_id)
        if job:
            return jsonify({
                'success': True,
                'job': job
            })
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@require_admin
def update_job(job_id):
    """Update a job role"""
    try:
        data = request.get_json()
        db.update_job(
            job_id=job_id,
            title=data.get('title'),
            description=data.get('description'),
            required_skills=data.get('required_skills'),
            preferred_skills=data.get('preferred_skills'),
            experience_level=data.get('experience_level'),
            location=data.get('location'),
            salary_range=data.get('salary_range')
        )
        return jsonify({
            'success': True,
            'message': 'Job updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@require_admin
def delete_job(job_id):
    """Delete a job role"""
    try:
        db.delete_job(job_id)
        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting AI Resume Analyzer API...")
    print("Note: SpaCy is optional. Skill extraction works without it, but NLP features are enhanced if SpaCy is installed.")
    app.run(debug=True, port=5000)


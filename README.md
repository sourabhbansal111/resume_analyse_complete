# AI Resume Analyzer + Job Matcher

A powerful full-stack application that analyzes resumes, extracts skills using NLP, and matches them with job roles using machine learning. Features secure authentication, company management, and a professional admin panel.

## Features

- 🔐 **Secure Authentication**: Login/Signup system with JWT tokens
- 👤 **User Management**: Separate user and admin roles
- 🏢 **Company Management**: Multi-company support with company selection
- 📄 **Resume Upload**: Upload PDF resumes for analysis
- 🤖 **AI Skill Extraction**: Automatically extracts skills from resumes
- 🎯 **Job Matching**: Matches resumes with job roles using ML
- 💡 **Improvement Tips**: Provides missing skills and improvement recommendations
- 📊 **Detailed Analysis**: Shows skill match percentage and gap analysis
- 🔒 **Admin Panel**: Secure admin panel for managing companies and jobs (admin only)

## Tech Stack

- **Frontend**: React, HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Authentication**: JWT (PyJWT) + bcrypt
- **ML**: Pattern-based matching (Scikit-learn optional for advanced TF-IDF)
- **NLP**: Pattern-based (SpaCy optional for enhanced features)
- **Database**: SQLite
- **Resume Parsing**: pdfplumber

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python backend/init_db.py
```

This creates the database schema and adds sample companies and jobs.

### 3. Create Admin User

```bash
python backend/create_admin.py
```

Enter admin credentials when prompted. **Only one admin user is allowed.** This admin will have access to the admin panel.

### 4. (Optional) Install Enhanced ML/NLP Libraries

The app works with basic pattern matching. For enhanced features, you can optionally install:

**Scikit-learn** (for advanced TF-IDF matching):
```bash
pip install scikit-learn
```

**SpaCy** (for enhanced NLP - requires Visual C++ Build Tools on Windows):
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Note**: Both are optional. The app works perfectly without them using pattern-based matching.

### 5. Run Backend Server

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`

### 6. Run Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### For Regular Users

1. **Sign Up**: Create a new account
2. **Login**: Sign in with your credentials
3. **Upload Resume**: Upload your PDF resume
4. **Select Company**: Choose a company or "All Companies"
5. **View Matches**: See job matches with detailed analysis

### For Admin Users

1. **Login**: Sign in with admin credentials
2. **Access Admin Panel**: Click "Admin Panel" button in navigation
3. **Manage Companies**: Add, edit, or delete companies
4. **Manage Jobs**: Add, edit, or delete job postings
5. **View Analysis**: Regular users can analyze resumes against your jobs

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Role-Based Access**: Admin panel only accessible to admin users
- **Single Admin**: Only one admin user allowed in the system
- **Protected Routes**: Admin endpoints require authentication

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User signup
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user (requires auth)

### Public Endpoints
- `POST /api/upload` - Upload resume PDF
- `POST /api/analyze` - Analyze resume and match with jobs
- `GET /api/jobs` - Get all available job roles
- `GET /api/jobs/<id>` - Get specific job details
- `GET /api/companies` - Get all companies

### Admin Endpoints (Require Admin Role)
- `POST /api/companies` - Create company
- `PUT /api/companies/<id>` - Update company
- `DELETE /api/companies/<id>` - Delete company
- `POST /api/jobs` - Create job
- `PUT /api/jobs/<id>` - Update job
- `DELETE /api/jobs/<id>` - Delete job

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask application
│   ├── auth.py             # Authentication utilities
│   ├── resume_parser.py    # PDF parsing
│   ├── skill_extractor.py # NLP skill extraction
│   ├── job_matcher.py      # ML job matching
│   ├── database.py         # Database operations
│   ├── init_db.py          # Initialize database
│   └── create_admin.py     # Create admin user
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   └── App.css         # Styles
│   └── package.json
└── uploads/                # Resume uploads directory
```

## Default Admin Setup

After running `python backend/create_admin.py`, you'll have one admin user who can:
- Access the admin panel
- Manage companies and jobs
- View all user analyses

Regular users can:
- Sign up and login
- Upload and analyze resumes
- View job matches
- Cannot access admin panel

## Troubleshooting

### Admin Panel Not Showing
- Make sure you're logged in as an admin user
- Check browser console for authentication errors
- Verify token is stored in localStorage

### Authentication Errors
- Check if backend is running
- Verify JWT token is being sent in requests
- Clear localStorage and login again

### Database Errors
- Run `python backend/init_db.py` to reinitialize
- Delete `backend/resume_analyzer.db` and reinitialize
- Check database file permissions

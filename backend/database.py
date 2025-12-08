import sqlite3
import json
import os
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path='resume_analyzer.db'):
        # Store database in backend directory
        if not os.path.dirname(db_path):
            db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                logo_url TEXT,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Job roles table (now linked to companies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                required_skills TEXT,
                preferred_skills TEXT,
                experience_level TEXT,
                location TEXT,
                salary_range TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Resume analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                extracted_skills TEXT,
                analysis_result TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_company(self, name: str, description: str = None, logo_url: str = None, website: str = None):
        """Add a new company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO companies (name, description, logo_url, website)
            VALUES (?, ?, ?, ?)
        ''', (name, description, logo_url, website))
        
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        return company_id
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM companies ORDER BY name')
        rows = cursor.fetchall()
        
        companies = []
        for row in rows:
            companies.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'logo_url': row[3],
                'website': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return companies
    
    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """Get a specific company by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
        row = cursor.fetchone()
        
        if row:
            company = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'logo_url': row[3],
                'website': row[4],
                'created_at': row[5]
            }
            conn.close()
            return company
        
        conn.close()
        return None
    
    def update_company(self, company_id: int, name: str = None, description: str = None, 
                       logo_url: str = None, website: str = None):
        """Update a company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if name is not None:
            updates.append('name = ?')
            values.append(name)
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if logo_url is not None:
            updates.append('logo_url = ?')
            values.append(logo_url)
        if website is not None:
            updates.append('website = ?')
            values.append(website)
        
        if updates:
            values.append(company_id)
            cursor.execute(f'UPDATE companies SET {", ".join(updates)} WHERE id = ?', values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_company(self, company_id: int):
        """Delete a company (cascades to jobs)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
        conn.commit()
        conn.close()
        return True
    
    def add_job_role(self, company_id: int, title: str, description: str, required_skills: List[str], 
                     preferred_skills: List[str] = None, experience_level: str = "Mid", 
                     location: str = None, salary_range: str = None):
        """Add a new job role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_roles (company_id, title, description, required_skills, preferred_skills, experience_level, location, salary_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, title, description, json.dumps(required_skills), 
              json.dumps(preferred_skills or []), experience_level, location, salary_range))
        
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return job_id
    
    def get_all_jobs(self, company_id: int = None) -> List[Dict]:
        """Get all job roles, optionally filtered by company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if company_id:
            cursor.execute('''
                SELECT j.*, c.name as company_name, c.logo_url as company_logo, c.website as company_website
                FROM job_roles j
                JOIN companies c ON j.company_id = c.id
                WHERE j.company_id = ?
                ORDER BY j.created_at DESC
            ''', (company_id,))
        else:
            cursor.execute('''
                SELECT j.*, c.name as company_name, c.logo_url as company_logo, c.website as company_website
                FROM job_roles j
                JOIN companies c ON j.company_id = c.id
                ORDER BY j.created_at DESC
            ''')
        
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            jobs.append({
                'id': row[0],
                'company_id': row[1],
                'title': row[2],
                'description': row[3],
                'required_skills': json.loads(row[4]) if row[4] else [],
                'preferred_skills': json.loads(row[5]) if row[5] else [],
                'experience_level': row[6],
                'location': row[7],
                'salary_range': row[8],
                'created_at': row[9],
                'company_name': row[10],
                'company_logo': row[11],
                'company_website': row[12]
            })
        
        conn.close()
        return jobs
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict]:
        """Get a specific job role by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT j.*, c.name as company_name, c.logo_url as company_logo, c.website as company_website
            FROM job_roles j
            JOIN companies c ON j.company_id = c.id
            WHERE j.id = ?
        ''', (job_id,))
        row = cursor.fetchone()
        
        if row:
            job = {
                'id': row[0],
                'company_id': row[1],
                'title': row[2],
                'description': row[3],
                'required_skills': json.loads(row[4]) if row[4] else [],
                'preferred_skills': json.loads(row[5]) if row[5] else [],
                'experience_level': row[6],
                'location': row[7],
                'salary_range': row[8],
                'created_at': row[9],
                'company_name': row[10],
                'company_logo': row[11],
                'company_website': row[12]
            }
            conn.close()
            return job
        
        conn.close()
        return None
    
    def update_job(self, job_id: int, title: str = None, description: str = None,
                   required_skills: List[str] = None, preferred_skills: List[str] = None,
                   experience_level: str = None, location: str = None, salary_range: str = None):
        """Update a job role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if required_skills is not None:
            updates.append('required_skills = ?')
            values.append(json.dumps(required_skills))
        if preferred_skills is not None:
            updates.append('preferred_skills = ?')
            values.append(json.dumps(preferred_skills))
        if experience_level is not None:
            updates.append('experience_level = ?')
            values.append(experience_level)
        if location is not None:
            updates.append('location = ?')
            values.append(location)
        if salary_range is not None:
            updates.append('salary_range = ?')
            values.append(salary_range)
        
        if updates:
            values.append(job_id)
            cursor.execute(f'UPDATE job_roles SET {", ".join(updates)} WHERE id = ?', values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_job(self, job_id: int):
        """Delete a job role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM job_roles WHERE id = ?', (job_id,))
        conn.commit()
        conn.close()
        return True
    
    def save_analysis(self, filename: str, extracted_skills: List[str], analysis_result: Dict, user_id: int = None):
        """Save resume analysis result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resume_analyses (filename, extracted_skills, analysis_result, user_id)
            VALUES (?, ?, ?, ?)
        ''', (filename, json.dumps(extracted_skills), json.dumps(analysis_result), user_id))
        
        conn.commit()
        analysis_id = cursor.lastrowid
        conn.close()
        return analysis_id
    
    def create_user(self, email: str, password_hash: str, name: str, role: str = 'user'):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if admin already exists
        if role == 'admin':
            cursor.execute('SELECT id FROM users WHERE role = ?', ('admin',))
            if cursor.fetchone():
                conn.close()
                raise Exception('Admin user already exists. Only one admin is allowed.')
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, name, role)
            VALUES (?, ?, ?, ?)
        ''', (email, password_hash, name, role))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            user = {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2],
                'name': row[3],
                'role': row[4],
                'created_at': row[5]
            }
            conn.close()
            return user
        
        conn.close()
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, name, role, created_at FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            user = {
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'role': row[3],
                'created_at': row[4]
            }
            conn.close()
            return user
        
        conn.close()
        return None


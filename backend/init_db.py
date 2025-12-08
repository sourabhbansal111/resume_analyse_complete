"""
Initialize database with sample companies and job roles
"""
from database import Database

def init_sample_data():
    """Add sample companies and job roles to the database"""
    db = Database()
    
    # Sample companies
    companies = [
        {
            'name': 'TechCorp',
            'description': 'Leading technology company specializing in software solutions',
            'logo_url': '',
            'website': 'https://techcorp.com'
        },
        {
            'name': 'DataFlow Inc',
            'description': 'Data analytics and machine learning solutions provider',
            'logo_url': '',
            'website': 'https://dataflow.com'
        },
        {
            'name': 'CloudSystems',
            'description': 'Cloud infrastructure and DevOps services',
            'logo_url': '',
            'website': 'https://cloudsystems.com'
        },
        {
            'name': 'WebDev Studio',
            'description': 'Full-stack web development agency',
            'logo_url': '',
            'website': 'https://webdevstudio.com'
        }
    ]
    
    # Sample jobs
    jobs = [
        {
            'company_name': 'TechCorp',
            'title': 'Python Developer',
            'description': 'Develop and maintain Python applications, work with APIs, and collaborate with cross-functional teams.',
            'required_skills': ['python', 'sql', 'git', 'rest api', 'flask', 'django'],
            'preferred_skills': ['docker', 'aws', 'react', 'postgresql', 'mongodb', 'kubernetes'],
            'experience_level': 'Mid',
            'location': 'San Francisco, CA',
            'salary_range': '$90k - $120k'
        },
        {
            'company_name': 'WebDev Studio',
            'title': 'Full Stack Developer',
            'description': 'Build end-to-end web applications using modern frameworks and technologies.',
            'required_skills': ['javascript', 'react', 'node.js', 'html', 'css', 'sql', 'git'],
            'preferred_skills': ['typescript', 'angular', 'vue', 'aws', 'docker', 'mongodb', 'express'],
            'experience_level': 'Mid',
            'location': 'New York, NY',
            'salary_range': '$85k - $115k'
        },
        {
            'company_name': 'DataFlow Inc',
            'title': 'Data Scientist',
            'description': 'Analyze complex data sets, build ML models, and provide data-driven insights.',
            'required_skills': ['python', 'machine learning', 'pandas', 'numpy', 'data analysis', 'sql'],
            'preferred_skills': ['tensorflow', 'pytorch', 'scikit-learn', 'jupyter', 'deep learning', 'nlp'],
            'experience_level': 'Senior',
            'location': 'Seattle, WA',
            'salary_range': '$120k - $150k'
        },
        {
            'company_name': 'CloudSystems',
            'title': 'DevOps Engineer',
            'description': 'Manage infrastructure, automate deployments, and ensure system reliability.',
            'required_skills': ['docker', 'kubernetes', 'aws', 'linux', 'git', 'ci/cd'],
            'preferred_skills': ['jenkins', 'terraform', 'ansible', 'azure', 'gcp', 'monitoring'],
            'experience_level': 'Mid',
            'location': 'Austin, TX',
            'salary_range': '$100k - $130k'
        },
        {
            'company_name': 'WebDev Studio',
            'title': 'Frontend Developer',
            'description': 'Create responsive and interactive user interfaces using modern web technologies.',
            'required_skills': ['javascript', 'react', 'html', 'css', 'git'],
            'preferred_skills': ['typescript', 'angular', 'vue', 'next.js', 'redux', 'webpack'],
            'experience_level': 'Junior',
            'location': 'Remote',
            'salary_range': '$60k - $80k'
        },
        {
            'company_name': 'TechCorp',
            'title': 'Backend Developer',
            'description': 'Design and implement server-side logic, APIs, and database solutions.',
            'required_skills': ['python', 'sql', 'rest api', 'git', 'linux'],
            'preferred_skills': ['java', 'node.js', 'docker', 'aws', 'postgresql', 'mongodb', 'microservices'],
            'experience_level': 'Mid',
            'location': 'Boston, MA',
            'salary_range': '$95k - $125k'
        },
        {
            'company_name': 'DataFlow Inc',
            'title': 'ML Engineer',
            'description': 'Build and deploy machine learning models at scale.',
            'required_skills': ['python', 'machine learning', 'tensorflow', 'pytorch', 'scikit-learn'],
            'preferred_skills': ['deep learning', 'nlp', 'computer vision', 'aws', 'docker', 'kubernetes'],
            'experience_level': 'Senior',
            'location': 'Palo Alto, CA',
            'salary_range': '$130k - $160k'
        },
        {
            'company_name': 'CloudSystems',
            'title': 'Software Engineer',
            'description': 'Design, develop, and maintain software applications.',
            'required_skills': ['python', 'java', 'git', 'sql', 'problem solving'],
            'preferred_skills': ['javascript', 'docker', 'aws', 'agile', 'microservices', 'rest api'],
            'experience_level': 'Mid',
            'location': 'Denver, CO',
            'salary_range': '$90k - $120k'
        }
    ]
    
    print("Initializing database with sample data...")
    
    # Create companies
    company_map = {}
    for company_data in companies:
        company_id = db.add_company(
            name=company_data['name'],
            description=company_data['description'],
            logo_url=company_data['logo_url'],
            website=company_data['website']
        )
        company_map[company_data['name']] = company_id
        print(f"Added company: {company_data['name']} (ID: {company_id})")
    
    # Create jobs
    for job_data in jobs:
        company_id = company_map.get(job_data['company_name'])
        if company_id:
            job_id = db.add_job_role(
                company_id=company_id,
                title=job_data['title'],
                description=job_data['description'],
                required_skills=job_data['required_skills'],
                preferred_skills=job_data['preferred_skills'],
                experience_level=job_data['experience_level'],
                location=job_data.get('location'),
                salary_range=job_data.get('salary_range')
            )
            print(f"Added job: {job_data['title']} at {job_data['company_name']} (ID: {job_id})")
    
    print(f"\nSuccessfully added {len(companies)} companies and {len(jobs)} job roles!")
    print("Database initialization complete.")

if __name__ == '__main__':
    init_sample_data()

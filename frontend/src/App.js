import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const API_BASE_URL = 'https://resume-analyse-backend.onrender.com/api';

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [skills, setSkills] = useState([]);
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState('upload'); // auth, upload, company-select, results
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminMode, setAdminMode] = useState('companies');
  
  // Auth states
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'signup'
  const [authForm, setAuthForm] = useState({ email: '', password: '', name: '' });
  const [authError, setAuthError] = useState('');

  // Admin form states
  const [companyForm, setCompanyForm] = useState({ name: '', description: '', logo_url: '', website: '' });
  const [jobForm, setJobForm] = useState({ 
    company_id: '', title: '', description: '', location: '', salary_range: '',
    experience_level: 'Mid', required_skills: '', preferred_skills: ''
  });
  const [editingCompany, setEditingCompany] = useState(null);
  const [editingJob, setEditingJob] = useState(null);
  const [jobs, setJobs] = useState([]);

  // Set up axios interceptor for auth token
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      (async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/auth/me`);
          if (response.data.success) {
            setIsAuthenticated(true);
            setUser(response.data.user);
            setCurrentStep('upload');
          }
        } catch (err) {
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
          setIsAuthenticated(false);
          setUser(null);
        }
      })();
    }
  }, []);

  useEffect(() => {
    loadCompanies();
    loadJobs();
  }, []);

  

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: authForm.email,
        password: authForm.password
      });

      if (response.data.success) {
        localStorage.setItem('token', response.data.token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
        setIsAuthenticated(true);
        setUser(response.data.user);
        setCurrentStep('upload');
        loadCompanies();
        loadJobs();
      }
    } catch (err) {
      setAuthError(err.response?.data?.error || 'Login failed. Please try again.');
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthError('');
    
    if (!authForm.name || !authForm.email || !authForm.password) {
      setAuthError('All fields are required');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
        email: authForm.email,
        password: authForm.password,
        name: authForm.name,
        role: 'user'
      });

      if (response.data.success) {
        localStorage.setItem('token', response.data.token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
        setIsAuthenticated(true);
        setUser(response.data.user);
        setCurrentStep('upload');
        loadCompanies();
        loadJobs();
      }
    } catch (err) {
      setAuthError(err.response?.data?.error || 'Signup failed. Please try again.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    setCurrentStep('upload');
    setShowAdmin(false);
    setFile(null);
    setSkills([]);
    setMatches([]);
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadCompanies();
      loadJobs();
    }
  }, [isAuthenticated]);

  const loadCompanies = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/companies`);
      if (response.data.success) {
        setCompanies(response.data.companies);
      }
    } catch (err) {
      console.error('Failed to load companies:', err);
    }
  };

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs`);
      if (response.data.success) {
        setJobs(response.data.jobs);
      }
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        setSkills(response.data.skills);
        setCurrentStep('company-select');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('No file selected');
      return;
    }

    setAnalyzing(true);
    setError('');

    try {
      console.log('Analyzing with:', { filename: file.name, company_id: selectedCompany });
      
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        filename: file.name,
        company_id: selectedCompany || null
      });

      console.log('Analysis response:', response.data);

      if (response.data.success) {
        setMatches(response.data.matches || []);
        setCurrentStep('results');
      } else {
        setError(response.data.error || 'Analysis failed. Please try again.');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Analysis failed. Please try again.';
      setError(errorMessage);
      alert(`Error: ${errorMessage}\n\nMake sure:\n1. Backend server is running\n2. Database is initialized (run: python backend/init_db.py)\n3. File was uploaded successfully`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setSkills([]);
    setMatches([]);
    setError('');
    setSelectedCompany(null);
    setCurrentStep('upload');
  };

  // Admin functions
  const handleCreateCompany = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/companies`, companyForm);
      setCompanyForm({ name: '', description: '', logo_url: '', website: '' });
      loadCompanies();
      alert('Company created successfully!');
    } catch (err) {
      alert('Failed to create company: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleUpdateCompany = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API_BASE_URL}/companies/${editingCompany.id}`, companyForm);
      setEditingCompany(null);
      setCompanyForm({ name: '', description: '', logo_url: '', website: '' });
      loadCompanies();
      alert('Company updated successfully!');
    } catch (err) {
      alert('Failed to update company: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleDeleteCompany = async (id) => {
    if (window.confirm('Are you sure you want to delete this company? All jobs will be deleted too.')) {
      try {
        await axios.delete(`${API_BASE_URL}/companies/${id}`);
        loadCompanies();
        loadJobs();
        alert('Company deleted successfully!');
      } catch (err) {
        alert('Failed to delete company: ' + (err.response?.data?.error || err.message));
      }
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    try {
      const jobData = {
        ...jobForm,
        company_id: parseInt(jobForm.company_id),
        required_skills: jobForm.required_skills.split(',').map(s => s.trim()).filter(s => s),
        preferred_skills: jobForm.preferred_skills.split(',').map(s => s.trim()).filter(s => s)
      };
      await axios.post(`${API_BASE_URL}/jobs`, jobData);
      setJobForm({ 
        company_id: '', title: '', description: '', location: '', salary_range: '',
        experience_level: 'Mid', required_skills: '', preferred_skills: ''
      });
      loadJobs();
      alert('Job created successfully!');
    } catch (err) {
      alert('Failed to create job: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleUpdateJob = async (e) => {
    e.preventDefault();
    try {
      const jobData = {
        ...jobForm,
        company_id: parseInt(jobForm.company_id),
        required_skills: jobForm.required_skills.split(',').map(s => s.trim()).filter(s => s),
        preferred_skills: jobForm.preferred_skills.split(',').map(s => s.trim()).filter(s => s)
      };
      await axios.put(`${API_BASE_URL}/jobs/${editingJob.id}`, jobData);
      setEditingJob(null);
      setJobForm({ 
        company_id: '', title: '', description: '', location: '', salary_range: '',
        experience_level: 'Mid', required_skills: '', preferred_skills: ''
      });
      loadJobs();
      alert('Job updated successfully!');
    } catch (err) {
      alert('Failed to update job: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleDeleteJob = async (id) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await axios.delete(`${API_BASE_URL}/jobs/${id}`);
        loadJobs();
        alert('Job deleted successfully!');
      } catch (err) {
        alert('Failed to delete job: ' + (err.response?.data?.error || err.message));
      }
    }
  };

  const startEditCompany = (company) => {
    setEditingCompany(company);
    setCompanyForm({
      name: company.name,
      description: company.description || '',
      logo_url: company.logo_url || '',
      website: company.website || ''
    });
  };

  const startEditJob = (job) => {
    setEditingJob(job);
    setJobForm({
      company_id: job.company_id.toString(),
      title: job.title,
      description: job.description || '',
      location: job.location || '',
      salary_range: job.salary_range || '',
      experience_level: job.experience_level || 'Mid',
      required_skills: (job.required_skills || []).join(', '),
      preferred_skills: (job.preferred_skills || []).join(', ')
    });
  };

  // Show auth screen if not authenticated
  if (!isAuthenticated && currentStep === 'auth') {
    return (
      <div className="App dark">
        <nav className="navbar">
          <div className="nav-container">
            <div className="nav-brand">
              <span className="brand-icon"><img src="/logo.ico" width={80} alt="📊" /></span>
              <span className="brand-text">Clever CV</span>
            </div>
          </div>
        </nav>

        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-header">
              <h1>{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</h1>
              <p>{authMode === 'login' ? 'Sign in to continue' : 'Get started with Clever CV'}</p>
            </div>

            {authError && <div className="error-message">{authError}</div>}

            <form onSubmit={authMode === 'login' ? handleLogin : handleSignup} className="auth-form">
              {authMode === 'signup' && (
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={authForm.name}
                    onChange={(e) => setAuthForm({...authForm, name: e.target.value})}
                    placeholder="Enter your name"
                    required
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  placeholder="Enter your email"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                  placeholder="Enter your password"
                  required
                  minLength={6}
                />
              </div>

              <button type="submit" className="btn btn-primary btn-large btn-block">
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                {authMode === 'login' ? "Don't have an account? " : "Already have an account? "}
                <button 
                  type="button"
                  className="link-button"
                  onClick={() => {
                    setAuthMode(authMode === 'login' ? 'signup' : 'login');
                    setAuthError('');
                    setAuthForm({ email: '', password: '', name: '' });
                  }}
                >
                  {authMode === 'login' ? 'Sign Up' : 'Sign In'}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App dark">
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-icon"><img src="/logo.ico" width={80} alt="📊" /></span>
            <span className="brand-text">Clever CV</span>
          </div>
          <div className="nav-actions">
            {user && (
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                {user.role === 'admin' && (
                  <button 
                    className={`nav-btn ${showAdmin ? 'active' : ''}`}
                    onClick={() => setShowAdmin(!showAdmin)}
                  >
                    {showAdmin ? '← Back to Analysis' : 'Admin Panel'}
                  </button>
                )}
                <button className="nav-btn" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            )}
            {!user && (
              <button className="nav-btn" onClick={() => setCurrentStep('auth')}>
                Login
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="container">
        {!showAdmin ? (
          <>
            {currentStep === 'upload' && (
              <div className="hero-section">
                <div className="hero-content">
                  <h1 className="hero-title">Find Your Perfect Job Match</h1>
                  <p className="hero-subtitle">AI-powered resume analysis matches you with the best opportunities</p>
                  
                  <div className="upload-card">
                    <div className="upload-icon-large">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                      </svg>
                    </div>
                    <h3>Upload Your Resume</h3>
                    <p className="upload-hint">PDF format, max 10MB</p>
                    
                    {error && <div className="error-message">{error}</div>}
                    
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      id="file-input"
                      style={{ display: 'none' }}
                    />
                    <label htmlFor="file-input" className="upload-button">
                      <span>{file ? file.name : 'Choose File'}</span>
                    </label>
                    
                    {file && (
                      <button onClick={handleUpload} className="btn btn-primary btn-large" disabled={uploading}>
                        {uploading ? (
                          <>
                            <span className="spinner"></span>
                            Processing...
                          </>
                        ) : (
                          <>
                            <span>Analyze Resume</span>
                            <span className="btn-arrow">→</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'company-select' && (
              <div className="company-select-section">
                <div className="section-card">
                  <h2>Select Company</h2>
                  <p className="section-description">Choose a company to analyze for, or analyze for all companies</p>
                  
                  {error && <div className="error-message">{error}</div>}
                  
                  <div className="company-grid">
                    <div 
                      className={`company-card ${selectedCompany === null ? 'selected' : ''}`}
                      onClick={() => setSelectedCompany(null)}
                    >
                      <div className="company-card-icon">🌐</div>
                      <h3>All Companies</h3>
                      <p>Analyze across all available companies</p>
                    </div>
                    
                    {companies.map(company => (
                      <div
                        key={company.id}
                        className={`company-card ${selectedCompany === company.id ? 'selected' : ''}`}
                        onClick={() => setSelectedCompany(company.id)}
                      >
                        {company.logo_url ? (
                          <img src={company.logo_url} alt={company.name} className="company-logo" />
                        ) : (
                          <div className="company-card-icon">{company.name.charAt(0).toUpperCase()}</div>
                        )}
                        <h3>{company.name}</h3>
                        <p>{company.description || 'No description'}</p>
                      </div>
                    ))}
                  </div>

                  <div className="skills-preview">
                    <h3>Extracted Skills ({skills.length})</h3>
                    <div className="skills-grid">
                      {skills.map((skill, index) => (
                        <span key={index} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>

                  <div className="action-buttons">
                    <button onClick={handleAnalyze} className="btn btn-primary btn-large" disabled={analyzing}>
                      {analyzing ? (
                        <>
                          <span className="spinner"></span>
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <span>Find Matches</span>
                          <span className="btn-arrow">→</span>
                        </>
                      )}
                    </button>
                    <button onClick={handleReset} className="btn btn-secondary">Upload Different Resume</button>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'results' && (
              <div className="results-section">
                <div className="results-header">
                  <div>
                    <h2>Job Matches</h2>
                    <p className="results-subtitle">{matches.length} opportunities found</p>
                  </div>
                  <button onClick={handleReset} className="btn btn-secondary">Analyze Another Resume</button>
                </div>

                {matches.length === 0 ? (
                  <div className="no-results">No job matches found.</div>
                ) : (
                  <div className="matches-grid">
                    {matches.map((match, index) => (
                      <div key={index} className="match-card">
                        <div className="match-card-header">
                          <div className="company-info">
                            {match.company_logo ? (
                              <img src={match.company_logo} alt={match.company_name} className="company-logo-small" />
                            ) : (
                              <div className="company-logo-placeholder">{match.company_name.charAt(0)}</div>
                            )}
                            <div>
                              <div className="company-name">{match.company_name}</div>
                              <div className="job-title">{match.job_title}</div>
                            </div>
                          </div>
                          <div className="match-score-badge">
                            <span className="score-value">{match.match_score.toFixed(0)}%</span>
                            <span className="score-label">Match</span>
                          </div>
                        </div>

                        <p className="job-description">{match.job_description}</p>

                        {match.location && (
                          <div className="job-meta">
                            <span className="meta-item">📍 {match.location}</span>
                            {match.salary_range && <span className="meta-item">💰 {match.salary_range}</span>}
                            <span className="meta-item">📊 {match.experience_level}</span>
                          </div>
                        )}

                        <div className="match-stats">
                          <div className="stat-item">
                            <span className="stat-label">Required Skills</span>
                            <span className="stat-value">{match.matched_required_count}/{match.total_required_skills}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Preferred Skills</span>
                            <span className="stat-value">{match.matched_preferred_count}/{match.total_preferred_skills}</span>
                          </div>
                        </div>

                        {match.matching_required_skills.length > 0 && (
                          <div className="skills-group">
                            <div className="skills-group-header">
                              <span className="skills-icon matching">✓</span>
                              <h4>Matching Skills</h4>
                            </div>
                            <div className="skills-list">
                              {[...match.matching_required_skills, ...match.matching_preferred_skills].map((skill, i) => (
                                <span key={i} className="skill-tag skill-match">{skill}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {match.missing_required_skills.length > 0 && (
                          <div className="skills-group">
                            <div className="skills-group-header">
                              <span className="skills-icon missing">!</span>
                              <h4>Missing Required Skills</h4>
                            </div>
                            <div className="skills-list">
                              {match.missing_required_skills.map((skill, i) => (
                                <span key={i} className="skill-tag skill-missing">{skill}</span>
                              ))}
                            </div>
                          </div>
                        )}

                        {match.improvement_tips && match.improvement_tips.length > 0 && (
                          <div className="improvement-tips">
                            <div className="tips-header">
                              <span className="tips-icon">💡</span>
                              <h4>Recommendations</h4>
                            </div>
                            <ul>
                              {match.improvement_tips.map((tip, i) => (
                                <li key={i}>{tip}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          user?.role === 'admin' ? (
            <div className="admin-panel">
              <div className="admin-tabs">
                <button 
                  className={`admin-tab ${adminMode === 'companies' ? 'active' : ''}`}
                  onClick={() => setAdminMode('companies')}
                >
                  Companies
                </button>
                <button 
                  className={`admin-tab ${adminMode === 'jobs' ? 'active' : ''}`}
                  onClick={() => setAdminMode('jobs')}
                >
                  Jobs
                </button>
              </div>

              {adminMode === 'companies' && (
                <div className="admin-content">
                  <div className="admin-form-card">
                    <h3>{editingCompany ? 'Edit Company' : 'Add New Company'}</h3>
                    <form onSubmit={editingCompany ? handleUpdateCompany : handleCreateCompany}>
                      <div className="form-group">
                        <label>Company Name *</label>
                        <input
                          type="text"
                          value={companyForm.name}
                          onChange={(e) => setCompanyForm({...companyForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Description</label>
                        <textarea
                          value={companyForm.description}
                          onChange={(e) => setCompanyForm({...companyForm, description: e.target.value})}
                          rows="3"
                        />
                      </div>
                      <div className="form-group">
                        <label>Logo URL</label>
                        <input
                          type="url"
                          value={companyForm.logo_url}
                          onChange={(e) => setCompanyForm({...companyForm, logo_url: e.target.value})}
                        />
                      </div>
                      <div className="form-group">
                        <label>Website</label>
                        <input
                          type="url"
                          value={companyForm.website}
                          onChange={(e) => setCompanyForm({...companyForm, website: e.target.value})}
                        />
                      </div>
                      <div className="form-actions">
                        <button type="submit" className="btn btn-primary">
                          {editingCompany ? 'Update' : 'Create'} Company
                        </button>
                        {editingCompany && (
                          <button 
                            type="button" 
                            className="btn btn-secondary"
                            onClick={() => {
                              setEditingCompany(null);
                              setCompanyForm({ name: '', description: '', logo_url: '', website: '' });
                            }}
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </form>
                  </div>

                  <div className="admin-list">
                    <h3>All Companies ({companies.length})</h3>
                    <div className="companies-list">
                      {companies.map(company => (
                        <div key={company.id} className="admin-item">
                          <div className="admin-item-content">
                            {company.logo_url ? (
                              <img src={company.logo_url} alt={company.name} className="admin-logo" />
                            ) : (
                              <div className="admin-logo-placeholder">{company.name.charAt(0)}</div>
                            )}
                            <div>
                              <h4>{company.name}</h4>
                              <p>{company.description || 'No description'}</p>
                            </div>
                          </div>
                          <div className="admin-item-actions">
                            <button onClick={() => startEditCompany(company)} className="btn-icon">✏️</button>
                            <button onClick={() => handleDeleteCompany(company.id)} className="btn-icon">🗑️</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {adminMode === 'jobs' && (
                <div className="admin-content">
                  <div className="admin-form-card">
                    <h3>{editingJob ? 'Edit Job' : 'Add New Job'}</h3>
                    <form onSubmit={editingJob ? handleUpdateJob : handleCreateJob}>
                      <div className="form-group">
                        <label>Company *</label>
                        <select
                          value={jobForm.company_id}
                          onChange={(e) => setJobForm({...jobForm, company_id: e.target.value})}
                          required
                        >
                          <option value="">Select Company</option>
                          {companies.map(c => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group">
                        <label>Job Title *</label>
                        <input
                          type="text"
                          value={jobForm.title}
                          onChange={(e) => setJobForm({...jobForm, title: e.target.value})}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Description</label>
                        <textarea
                          value={jobForm.description}
                          onChange={(e) => setJobForm({...jobForm, description: e.target.value})}
                          rows="3"
                        />
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Location</label>
                          <input
                            type="text"
                            value={jobForm.location}
                            onChange={(e) => setJobForm({...jobForm, location: e.target.value})}
                          />
                        </div>
                        <div className="form-group">
                          <label>Salary Range</label>
                          <input
                            type="text"
                            value={jobForm.salary_range}
                            onChange={(e) => setJobForm({...jobForm, salary_range: e.target.value})}
                          />
                        </div>
                        <div className="form-group">
                          <label>Experience Level</label>
                          <select
                            value={jobForm.experience_level}
                            onChange={(e) => setJobForm({...jobForm, experience_level: e.target.value})}
                          >
                            <option value="Junior">Junior</option>
                            <option value="Mid">Mid</option>
                            <option value="Senior">Senior</option>
                          </select>
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Required Skills (comma-separated)</label>
                        <input
                          type="text"
                          value={jobForm.required_skills}
                          onChange={(e) => setJobForm({...jobForm, required_skills: e.target.value})}
                          placeholder="python, javascript, react"
                        />
                      </div>
                      <div className="form-group">
                        <label>Preferred Skills (comma-separated)</label>
                        <input
                          type="text"
                          value={jobForm.preferred_skills}
                          onChange={(e) => setJobForm({...jobForm, preferred_skills: e.target.value})}
                          placeholder="docker, aws, kubernetes"
                        />
                      </div>
                      <div className="form-actions">
                        <button type="submit" className="btn btn-primary">
                          {editingJob ? 'Update' : 'Create'} Job
                        </button>
                        {editingJob && (
                          <button 
                            type="button" 
                            className="btn btn-secondary"
                            onClick={() => {
                              setEditingJob(null);
                              setJobForm({ 
                                company_id: '', title: '', description: '', location: '', salary_range: '',
                                experience_level: 'Mid', required_skills: '', preferred_skills: ''
                              });
                            }}
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </form>
                  </div>

                  <div className="admin-list">
                    <h3>All Jobs ({jobs.length})</h3>
                    <div className="jobs-list">
                      {jobs.map(job => (
                        <div key={job.id} className="admin-item">
                          <div className="admin-item-content">
                            <div>
                              <h4>{job.title}</h4>
                              <p className="job-company-name">{job.company_name}</p>
                              <p>{job.description || 'No description'}</p>
                              <div className="job-tags">
                                {job.location && <span className="job-tag">📍 {job.location}</span>}
                                {job.experience_level && <span className="job-tag">📊 {job.experience_level}</span>}
                              </div>
                            </div>
                          </div>
                          <div className="admin-item-actions">
                            <button onClick={() => startEditJob(job)} className="btn-icon">✏️</button>
                            <button onClick={() => handleDeleteJob(job.id)} className="btn-icon">🗑️</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="no-access">
              <h2>Access Denied</h2>
              <p>You don't have permission to access the admin panel.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}

export default App;

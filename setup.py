"""
Setup script for AI Resume Analyzer
"""
import subprocess
import sys
import os

def run_command(command_list, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Step: {description}")
    print(f"Command: {' '.join(command_list)}")
    print(f"{'='*50}\n")
    
    try:
        result = subprocess.run(command_list, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode == 0:
            # Some commands output to stderr even on success (like pip)
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr if e.stderr else e.stdout}")
        return False

def main():
    print("="*60)
    print("AI Resume Analyzer - Setup Script")
    print("="*60)
    
    # Step 1: Install Python dependencies
    print("\n[1/4] Installing Python dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installing Python packages"):
        print("Failed to install Python dependencies. Please run manually:")
        print("pip install -r requirements.txt")
        return
    
    # Step 2: Skip SpaCy (optional - requires Visual C++ Build Tools)
    print("\n[2/4] Skipping SpaCy installation (optional)...")
    print("Note: SpaCy requires Visual C++ Build Tools on Windows.")
    print("The application works without SpaCy using pattern-based skill extraction.")
    print("To install SpaCy later (optional): pip install spacy && python -m spacy download en_core_web_sm")
    
    # Step 3: Initialize database
    print("\n[3/4] Initializing database with sample jobs...")
    if not run_command([sys.executable, "backend/init_db.py"], 
                      "Initializing database"):
        print("Failed to initialize database. Please run manually:")
        print("python backend/init_db.py")
        return
    
    # Step 4: Create uploads directory
    print("\n[4/4] Creating uploads directory...")
    os.makedirs('uploads', exist_ok=True)
    print("✓ Uploads directory created")
    
    print("\n" + "="*60)
    print("Setup Complete! ✓")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python app.py")
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm install")
    print("   npm start")
    print("\n3. Open http://localhost:3000 in your browser")
    print("="*60)

if __name__ == '__main__':
    main()


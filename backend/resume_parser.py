import pdfplumber
import re
from typing import Optional

class ResumeParser:
    def __init__(self):
        self.text = ""
    
    def parse_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF resume
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from the resume
        """
        try:
            text = ""
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Clean up the text
            text = self._clean_text(text)
            self.text = text
            return text
        
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep common punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)]', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def get_sections(self) -> dict:
        """Extract common resume sections"""
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': ''
        }
        
        text_lower = self.text.lower()
        
        # Try to find sections by common headers
        section_patterns = {
            'contact': r'(contact|phone|email|address)',
            'summary': r'(summary|objective|profile|about)',
            'experience': r'(experience|work history|employment|professional experience)',
            'education': r'(education|academic|qualifications)',
            'skills': r'(skills|technical skills|competencies|proficiencies)'
        }
        
        lines = self.text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            for section, pattern in section_patterns.items():
                if re.search(pattern, line_lower) and len(line) < 50:
                    current_section = section
                    break
            
            # Add line to current section
            if current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def get_text(self) -> str:
        """Get the full extracted text"""
        return self.text


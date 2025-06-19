#!/usr/bin/env python
"""
Book AI Tutor Usage Example Script
---------------------------------
This script demonstrates how to upload a PDF and extract its content
using the Book AI Tutor API.

Usage:
    python upload_and_extract.py path/to/your.pdf

Requirements:
    - requests library (pip install requests)
    - A running Book AI Tutor Django server
"""

import sys
import os
import requests
import json
from urllib.parse import urljoin

# Configuration
API_BASE_URL = "http://localhost:8000/api/"
DOCUMENTS_ENDPOINT = urljoin(API_BASE_URL, "documents/")


def upload_pdf(pdf_path):
    """Upload a PDF file to the Book AI Tutor system"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return None
    
    filename = os.path.basename(pdf_path)
    title = os.path.splitext(filename)[0].replace("_", " ").title()
    
    with open(pdf_path, 'rb') as pdf_file:
        files = {'pdf_file': (filename, pdf_file)}
        data = {
            'title': title,
            'description': f"Uploaded from script on {os.path.basename(__file__)}"
        }
        
        try:
            response = requests.post(DOCUMENTS_ENDPOINT, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error uploading PDF: {e}")
            return None


def extract_content(document_id):
    """Extract content from the PDF"""
    extract_endpoint = urljoin(DOCUMENTS_ENDPOINT, f"{document_id}/extract-content/")
    
    try:
        response = requests.post(extract_endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error extracting content: {e}")
        return None


def get_preview_url(document_id):
    """Get the URL for the HTML preview"""
    return urljoin(DOCUMENTS_ENDPOINT, f"{document_id}/preview/?format=html")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} path/to/your.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Upload the PDF
    print(f"Uploading {pdf_path}...")
    document = upload_pdf(pdf_path)
    
    if not document:
        print("Failed to upload document")
        sys.exit(1)
    
    document_id = document['id']
    print(f"Document uploaded successfully with ID: {document_id}")
    
    # Extract content
    print("Extracting content...")
    result = extract_content(document_id)
    
    if not result:
        print("Failed to extract content")
        sys.exit(1)
    
    print(f"Content extracted successfully: {result['message']}")
    
    # Get preview URL
    preview_url = get_preview_url(document_id)
    print(f"\nPreview your document at: {preview_url}")
    print("(make sure the Django server is running)")


if __name__ == "__main__":
    main()

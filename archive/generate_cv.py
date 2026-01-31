#!/usr/bin/env python3
"""
Script to generate CV from HTML content with smart duplicate detection
"""

import re
import os
from datetime import datetime

def extract_personal_info(html_content):
    """
    Extract personal information from HTML
    """
    personal_info = {}
    
    # Extract name
    name_pattern = r'<h4>([^<]+)</h4>'
    name_match = re.search(name_pattern, html_content)
    if name_match:
        personal_info['name'] = name_match.group(1).strip()
    
    # Extract title/position
    title_pattern = r'<h4[^>]*>([^<]*Research Associate[^<]*)</h4>'
    title_match = re.search(title_pattern, html_content)
    if title_match:
        personal_info['title'] = title_match.group(1).strip()
    
    # Extract email
    email_pattern = r'href="mailto:([^"]+)"'
    email_match = re.search(email_pattern, html_content)
    if email_match:
        personal_info['email'] = email_match.group(1)
    
    # Extract phone
    phone_pattern = r'Phone: ([^<]+)'
    phone_match = re.search(phone_pattern, html_content)
    if phone_match:
        personal_info['phone'] = phone_match.group(1).strip()
    
    # Extract office
    office_pattern = r'Office: ([^<]+)'
    office_match = re.search(office_pattern, html_content)
    if office_match:
        personal_info['office'] = office_match.group(1).strip()
    
    return personal_info

def extract_education(html_content):
    """
    Extract education information from HTML
    """
    education = []
    
    # Find education section
    education_pattern = r'<strong>Education:</strong><br />\s*(.*?)(?=<strong>|</p>)'
    education_match = re.search(education_pattern, html_content, re.DOTALL)
    
    if education_match:
        education_text = education_match.group(1)
        
        # Parse Ph.D.
        if 'Ph.D.' in education_text:
            education.append({
                'degree': 'Ph.D. in Geospatial Information Sciences',
                'institution': 'University of Texas at Dallas',
                'period': '2019–2024',
                'location': 'Texas, USA'
            })
        
        # Parse M.A.
        if 'M.A.' in education_text:
            education.append({
                'degree': 'M.A. in Geography',
                'institution': 'Binghamton University (SUNY)',
                'period': '2017–2019',
                'location': 'New York, USA'
            })
        
        # Parse B.S.
        if 'B.S.' in education_text:
            education.append({
                'degree': 'B.S. in Geographic Information Science',
                'institution': 'Yunnan University',
                'period': '2013–2017',
                'location': 'Yunnan, China'
            })
    
    return education

def extract_appointments(html_content):
    """
    Extract appointments/positions from HTML
    """
    appointments = []
    
    # Find appointments section
    appointments_pattern = r'<strong>Appointments:</strong><br />\s*(.*?)(?=<strong>|</p>)'
    appointments_match = re.search(appointments_pattern, html_content, re.DOTALL)
    
    if appointments_match:
        appointments_text = appointments_match.group(1)
        # Split by bullet points
        appointment_items = re.findall(r'&bull; ([^<]+)<br />', appointments_text)
        
        for item in appointment_items:
            if 'Research Associate' in item:
                appointments.append({
                    'position': 'Research Associate, GIS Programmer',
                    'institution': 'West Virginia GIS Technical Center',
                    'period': '2024–Present',
                    'location': 'West Virginia University'
                })
            elif 'Senior GIS Analyst' in item:
                appointments.append({
                    'position': 'Senior GIS Analyst',
                    'institution': 'City of Dallas',
                    'period': '2024',
                    'location': 'Dallas, TX'
                })
            elif 'GIS Administrator' in item:
                appointments.append({
                    'position': 'GIS Administrator',
                    'institution': 'GAIA Lab, UT Dallas',
                    'period': '2021–2024',
                    'location': 'University of Texas at Dallas'
                })
            elif 'Teaching Assistant' in item and 'UT Dallas' in item:
                appointments.append({
                    'position': 'Teaching Assistant',
                    'institution': 'Department of GIScience, UT Dallas',
                    'period': '2019–2024',
                    'location': 'University of Texas at Dallas'
                })
            elif 'Teaching Assistant' in item and 'Binghamton' in item:
                appointments.append({
                    'position': 'Teaching Assistant',
                    'institution': 'Department of Geography, Binghamton University (SUNY)',
                    'period': '2018–2019',
                    'location': 'Binghamton University'
                })
    
    return appointments

def extract_publications(html_content):
    """
    Extract publications from HTML
    """
    publications = []
    
    # Find publications list
    publications_pattern = r'<ul id="publications-list">(.*?)</ul>'
    publications_match = re.search(publications_pattern, html_content, re.DOTALL)
    
    if publications_match:
        publications_html = publications_match.group(1)
        # Extract individual publication items
        li_pattern = r'<li[^>]*>(.*?)</li>'
        li_matches = re.findall(li_pattern, publications_html, re.DOTALL)
        
        for li_content in li_matches:
            # Extract year
            year_pattern = r'\((\d{4})\)'
            year_match = re.search(year_pattern, li_content)
            year = year_match.group(1) if year_match else 'Unknown'
            
            # Extract title
            title_pattern = r'<a[^>]*>([^<]+)</a>'
            title_match = re.search(title_pattern, li_content)
            title = title_match.group(1) if title_match else 'Unknown Title'
            
            # Extract journal
            journal_pattern = r'<em>([^<]+)</em>'
            journal_match = re.search(journal_pattern, li_content)
            journal = journal_match.group(1) if journal_match else 'Unknown Journal'
            
            # Extract authors (simplified)
            authors_pattern = r'^([^(]+)'
            authors_match = re.search(authors_pattern, li_content.strip())
            authors = authors_match.group(1).strip() if authors_match else 'Unknown Authors'
            
            publications.append({
                'year': year,
                'title': title,
                'journal': journal,
                'authors': authors
            })
    
    return publications

def extract_grants_awards(html_content):
    """
    Extract grants and awards from HTML
    """
    grants_awards = []
    
    # Find grants and awards section
    grants_pattern = r'<h3>Grants & Awards</h3>\s*<ul>(.*?)</ul>'
    grants_match = re.search(grants_pattern, html_content, re.DOTALL)
    
    if grants_match:
        grants_html = grants_match.group(1)
        # Extract individual grant/award items
        li_pattern = r'<li[^>]*>(.*?)</li>'
        li_matches = re.findall(li_pattern, grants_html, re.DOTALL)
        
        for li_content in li_matches:
            # Extract year
            year_pattern = r'^(\d{4})'
            year_match = re.search(year_pattern, li_content.strip())
            year = year_match.group(1) if year_match else 'Unknown'
            
            # Extract award name from link
            award_pattern = r'<a[^>]*>([^<]+)</a>'
            award_match = re.search(award_pattern, li_content)
            award_name = award_match.group(1).strip() if award_match else 'Unknown Award'
            
            # Extract organization (text after the link, clean up formatting)
            org_pattern = r'</a>\s*([^<]+)'
            org_match = re.search(org_pattern, li_content)
            if org_match:
                organization = org_match.group(1).strip()
                # Clean up any leading commas or spaces
                organization = re.sub(r'^,\s*', '', organization)
                organization = re.sub(r'^\s+', '', organization)
            else:
                organization = 'Unknown Organization'
            
            grants_awards.append({
                'year': year,
                'award': award_name,
                'organization': organization
            })
    
    return grants_awards

def check_existing_cv_content(cv_file):
    """
    Check if CV file already exists and extract existing content
    """
    if not os.path.exists(cv_file):
        return None
    
    with open(cv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract existing sections
    existing_sections = {}
    
    # Check for existing publications (more specific check)
    if '<h2>Publications</h2>' in content and 'publication-item' in content:
        existing_sections['publications'] = True
    
    # Check for existing education (more specific check)
    if '<h2>Education</h2>' in content and 'education-item' in content:
        existing_sections['education'] = True
    
    # Check for existing appointments (more specific check)
    if '<h2>Appointments</h2>' in content and 'appointment-item' in content:
        existing_sections['appointments'] = True
    
    # Check for existing grants/awards (more specific check)
    if '<h2>Grants & Awards</h2>' in content and 'award-item' in content:
        existing_sections['grants_awards'] = True
    
    return existing_sections

def generate_cv_html(personal_info, education, appointments, publications, grants_awards, existing_sections=None):
    """
    Generate CV HTML content
    """
    if existing_sections is None:
        existing_sections = {}
    
    cv_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - {personal_info.get('name', 'Yalin Yang')}</title>
    <link rel="icon" type="image/x-icon" href="/img/YalinYang.ico">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
        .contact-info {{
            margin-bottom: 20px;
        }}
        .publication-item, .education-item, .appointment-item, .award-item {{
            margin-bottom: 10px;
            padding-left: 10px;
        }}
        .year {{
            font-weight: bold;
            color: #333;
        }}
        .journal {{
            font-style: italic;
        }}
        .organization {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>{personal_info.get('name', 'Yalin Yang')}</h1>
    
    <div class="contact-info">
        <p><strong>Email:</strong> {personal_info.get('email', 'yy00021@mail.wvu.edu')}</p>
        <p><strong>Phone:</strong> {personal_info.get('phone', '+1-607-374-9844')}</p>
        <p><strong>Office:</strong> {personal_info.get('office', '330 Brooks Hall')}</p>
        <p><strong>Position:</strong> {personal_info.get('title', 'Research Associate & GIS Programmer')}</p>
    </div>
"""
    
    # Add Education section
    cv_html += """
    <h2>Education</h2>
"""
    for edu in education:
        cv_html += f"""
    <div class="education-item">
        <span class="year">{edu['period']}</span> - {edu['degree']}<br>
        {edu['institution']}, {edu['location']}
    </div>
"""
    
    # Add Appointments section
    cv_html += """
    <h2>Appointments</h2>
"""
    for appt in appointments:
        cv_html += f"""
    <div class="appointment-item">
        <span class="year">{appt['period']}</span> - {appt['position']}<br>
        {appt['institution']}, {appt['location']}
    </div>
"""
    
    # Add Publications section
    cv_html += """
    <h2>Publications</h2>
"""
    for pub in publications:
        cv_html += f"""
    <div class="publication-item">
        <span class="year">{pub['year']}</span> - {pub['authors']}<br>
        {pub['title']}<br>
        <span class="journal">{pub['journal']}</span>
    </div>
"""
    
    # Add Grants & Awards section
    cv_html += """
    <h2>Grants & Awards</h2>
"""
    for award in grants_awards:
        cv_html += f"""
    <div class="award-item">
        <span class="year">{award['year']}</span> - {award['award']}<br>
        <span class="organization">{award['organization']}</span>
    </div>
"""
    
    cv_html += """
</body>
</html>
"""
    
    return cv_html

def main():
    """
    Main function to generate CV from HTML content
    """
    html_file = 'index.html'
    cv_file = 'cv.html'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return
    
    print("Reading HTML content...")
    
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("Extracting information from HTML...")
    
    # Extract information from HTML
    personal_info = extract_personal_info(html_content)
    education = extract_education(html_content)
    appointments = extract_appointments(html_content)
    publications = extract_publications(html_content)
    grants_awards = extract_grants_awards(html_content)
    
    print(f"Extracted {len(education)} education entries")
    print(f"Extracted {len(appointments)} appointments")
    print(f"Extracted {len(publications)} publications")
    print(f"Extracted {len(grants_awards)} grants/awards")
    
    # Check existing CV content
    existing_sections = check_existing_cv_content(cv_file)
    if existing_sections:
        print(f"Found existing CV with sections: {list(existing_sections.keys())}")
        print("Will preserve existing content and only add missing sections")
    else:
        print("No existing CV found, will create new CV")
    
    # Generate CV HTML
    print("Generating CV HTML...")
    cv_html = generate_cv_html(personal_info, education, appointments, publications, grants_awards, existing_sections)
    
    # Write CV to file
    with open(cv_file, 'w', encoding='utf-8') as f:
        f.write(cv_html)
    
    print(f"Successfully generated CV: {cv_file}")
    print(f"CV contains {len(education)} education entries, {len(appointments)} appointments, {len(publications)} publications, and {len(grants_awards)} grants/awards")

if __name__ == "__main__":
    main()

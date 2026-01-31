#!/usr/bin/env python3
"""
Script to generate a professional CV from HTML content
"""

import re
import os
from bs4 import BeautifulSoup
from datetime import datetime

def extract_info_from_html(html_file):
    """
    Extract structured information from index.html using BeautifulSoup
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    info = {
        'name': "Yalin Yang",
        'title': "Research Associate & GIS Programmer",
        'contact': {
            'email': "yy00021@mail.wvu.edu",
            'phone': "+1-607-374-9844",
            'office': "330 Brooks Hall",
            'location': "Morgantown, WV 26506",
            'website': "https://gisyaliny.github.io/"
        },
        'education': [],
        'appointments': [],
        'publications': [],
        'awards': [],
    }
    
    # --- Extract basic info if available (overwriting defaults) ---
    # (We keep defaults as fallbacks because scraping specific tags might ideally be more robust, 
    # but the defaults are correct for now based on previous files)

    # --- Extract Education ---
    # Locate "Education" section text
    # In index.html, it's usually under a <p> or similar. 
    # We'll search for the text "Education:" and parse siblings/children.
    # The structure in index.html is: <p class="large"><strong>Education:</strong><br />... text ... </p>
    
    # We can try to find the "Education:" text and then parse the parent
    edu_header = soup.find(string=re.compile("Education:"))
    if edu_header:
        parent_p = edu_header.parent.parent # strong -> p
        # Get text and split by bullets? 
        # The text structure is: &bull; Year ... Ph.D... <br>
        # Let's just get the text and use regex to parse the lines starting with bullet char or year
        text = parent_p.get_text("\n")
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Look for years pattern like 2019-2024
            if re.search(r'\d{4}.*\d{4}', line):
                info['education'].append(line.replace("•", "").replace("&bull;", "").strip())

    # --- Extract Appointments ---
    appt_header = soup.find(string=re.compile("Appointments:"))
    if appt_header:
        parent_p = appt_header.parent.parent
        text = parent_p.get_text("\n")
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if re.search(r'\d{4}.*\d{4}|\d{4}.*Present', line):
                 info['appointments'].append(line.replace("•", "").replace("&bull;", "").strip())

    # --- Extract Publications ---
    pub_ul = soup.find('ul', id='publications-list')
    if pub_ul:
        for li in pub_ul.find_all('li'):
            # Parse publication details for better styling
            # We want: Year, Citation, and maybe highlight Author
            # But plain text citation is often standard for CVs.
            # However, we can highlight the year if we want columns.
            
            pub_html = str(li)
            text = li.get_text(" ", strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            # Extract Year
            year_match = re.search(r'\((\d{4})\)', text)
            year = year_match.group(1) if year_match else "Unknown"
            
            # Clean text specifically for CV (maybe remove links text wrapper?)
            # Actually, keeping the citation as is, is usually fine.
            # We will store raw HTML to preserve bolding <b>Yang, Y.</b>
            # BeautifulSoup converts tags to text, losing bolding.
            # let's reconstruct it or use innerHTML.
            
            # Simplified approach: just keep the full HTML of the li content
            # But removing the <li> tag itself.
            content_html = "".join([str(x) for x in li.contents])
            
            info['publications'].append({
                'year': year,
                'content': content_html,
                'text': text
            })

    # --- Extract Awards ---
    # Find headers with "Grants & Awards"
    for header in soup.find_all(['h2', 'h3']):
        if "Grants & Awards" in header.get_text():
            next_ul = header.find_next('ul')
            if next_ul:
                for li in next_ul.find_all('li'):
                    text = li.get_text(" ", strip=True)
                    text = re.sub(r'\s+', ' ', text)
                    
                    # Extract Year
                    year_match = re.search(r'^(\d{4})', text)
                    year = year_match.group(1) if year_match else "Unknown"
                    
                    # Store
                    info['awards'].append({
                        'year': year,
                        'text': text
                    })
            break
            
    return info

def generate_cv_html(info):
    """
    Generate the HTML for the CV
    """
    
    # CSS Styles
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400&family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');
        
        body {
            font-family: 'Open Sans', Helvetica, Arial, sans-serif;
            color: #333;
            line-height: 1.5;
            max-width: 850px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #f9f9f9;
        }
        
        .cv-container {
            background-color: white;
            padding: 50px;
            box-shadow: 0 0 15px rgba(0,0,0,0.05);
            border-top: 5px solid #2c3e50;
        }
        
        a {
            color: #2980b9;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        header {
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        h1 {
            font-family: 'Merriweather', serif;
            font-size: 32px;
            color: #2c3e50;
            margin: 0 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .title {
            font-size: 18px;
            color: #7f8c8d;
            font-weight: 300;
            margin: 0;
        }
        
        .contact-info {
            text-align: right;
            font-size: 14px;
            color: #555;
        }
        
        .contact-info p {
            margin: 3px 0;
        }
        
        section {
            margin-bottom: 30px;
        }
        
        h2 {
            font-family: 'Merriweather', serif;
            font-size: 20px;
            color: #2c3e50;
            border-bottom: 3px solid #f1f1f1;
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 20px;
            text-transform: uppercase;
            display: inline-block;
            border-bottom-color: #3498db;
        }
        
        .item {
            margin-bottom: 15px;
            display: flex;
        }
        
        .item-year {
            flex: 0 0 120px;
            font-weight: bold;
            color: #7f8c8d;
            font-size: 14px;
            padding-top: 2px;
        }
        
        .item-content {
            flex: 1;
        }
        
        .publication-item {
            margin-bottom: 12px;
            padding-left: 15px;
            border-left: 3px solid #eee;
        }
        
        .publication-item:hover {
            border-left-color: #3498db;
        }
        
        .appointment-item, .education-item {
            margin-bottom: 15px;
        }
        
        @media print {
            body {
                background-color: white;
                margin: 0;
            }
            .cv-container {
                box-shadow: none;
                padding: 0;
                border: none;
            }
            a {
                color: #000;
                text-decoration: none;
            }
        }
    </style>
    """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{info['name']} - Curriculum Vitae</title>
    {css}
</head>
<body>

<div class="cv-container">
    <header>
        <div>
            <h1>{info['name']}</h1>
            <h3 class="title">{info['title']}</h3>
            <p>West Virginia GIS Technical Center<br>West Virginia University</p>
        </div>
        <div class="contact-info">
            <p>{info['contact']['email']}</p>
            <p>{info['contact']['phone']}</p>
            <p>{info['contact']['office']}</p>
            <p>{info['contact']['location']}</p>
            <p><a href="{info['contact']['website']}">{info['contact']['website']}</a></p>
        </div>
    </header>

    <section>
        <h2>Education</h2>
"""
    # Parse Education strings to separate Year from Content if possible
    # Strings format: "2019–2024: Ph.D. ..."
    for edu in info['education']:
        # Try to split by first colon or common separator
        parts = edu.split(':', 1)
        if len(parts) == 2:
            year = parts[0].strip()
            desc = parts[1].strip()
        else:
            year = ""
            desc = edu
            
        html += f"""
        <div class="item">
            <div class="item-year">{year}</div>
            <div class="item-content">{desc}</div>
        </div>
        """

    html += """
    </section>

    <section>
        <h2>Academic Appointments</h2>
"""
    for appt in info['appointments']:
        parts = appt.split(':', 1)
        if len(parts) == 2:
            year = parts[0].strip()
            desc = parts[1].strip()
        else:
            year = ""
            desc = appt
            
        html += f"""
        <div class="item">
            <div class="item-year">{year}</div>
            <div class="item-content">{desc}</div>
        </div>
        """

    html += """
    </section>

    <section>
        <h2>Publications</h2>
"""
    for pub in info['publications']:
        html += f"""
        <div class="item">
            <div class="item-year">{pub['year']}</div>
            <div class="item-content publication-item">
                {pub['content']}
            </div>
        </div>
        """

    html += """
    </section>
    
    <section>
        <h2>Grants & Awards</h2>
"""
    for award in info['awards']:
        # Try to separate Year from text
        # Text format: "2024 Award Name..."
        # Regex to find first space after year
        match = re.match(r'^(\d{4})\s*(.*)', award['text'])
        if match:
            year = match.group(1)
            desc = match.group(2)
        else:
            year = ""
            desc = award['text']
            
        html += f"""
        <div class="item">
            <div class="item-year">{year}</div>
            <div class="item-content">{desc}</div>
        </div>
        """

    html += """
    </section>
    
    <footer>
        <p style="text-align: center; color: #999; font-size: 12px; margin-top: 50px;">
            Last updated: """ + datetime.now().strftime('%B %Y') + """
        </p>
    </footer>

</div>

</body>
</html>
"""
    return html

def main():
    print("Generating Professional CV...")
    info = extract_info_from_html("index.html")
    
    print(f"Extracted: {len(info['education'])} Education, {len(info['appointments'])} Appointments, {len(info['publications'])} Publications")
    
    cv_html = generate_cv_html(info)
    
    with open("cv.html", "w", encoding='utf-8') as f:
        f.write(cv_html)
        
    print("✅ Successfully generated cv.html")

if __name__ == "__main__":
    main()

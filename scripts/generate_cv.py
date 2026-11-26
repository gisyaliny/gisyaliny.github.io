#!/usr/bin/env python3
"""
Generate `cv.html` from `index.html`.

This was moved from the repository root into `scripts/`.
"""

from __future__ import annotations

from html import escape
import yaml
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


def extract_info_from_html(html_file: str) -> dict:
    """
    Extract structured information from index.html using BeautifulSoup.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    info = {
        "name": "Yalin Yang",
        "title": "Research Scientist & GIS Programmer",
        "contact": {
            "email": "yy00021@mail.wvu.edu",
            "phone": "+1-607-374-9844",
            "office": "330 Brooks Hall",
            "location": "Morgantown, WV 26506",
            "website": "https://gisyaliny.github.io/",
        },
        "education": [],
        "appointments": [],
        "publications": [],
        "awards": [],
        "projects": [],
    }

    for row in soup.select(".education-strip .record-list > li"):
        degree = row.select_one("strong")
        info["education"].append(f"{row.time.get_text(strip=True)}: {degree.get_text(strip=True)}, {row.br.next_sibling.strip()}")

    for row in soup.select("#appointments li"):
        dates = row.select_one(".tenure").get_text(strip=True).removeprefix("Current · ")
        info["appointments"].append(f"{dates}: {row.h3.get_text(strip=True)}, {row.p.get_text(strip=True)}")

    lead = soup.select_one("#projects .lead-copy")
    info["projects"].append((lead.h3.get_text(strip=True), lead.a["href"], lead.p.get_text(strip=True)))
    for card in soup.select("#work .engineering-card"):
        info["projects"].append((card.h4.get_text(strip=True), card["href"], card.select_one(".card-summary").get_text(strip=True)))

    for group in soup.select("#papers .pub-year"):
        for entry in group.select("li"):
            info["publications"].append({"year": group.h3.get_text(strip=True), "content": entry.decode_contents()})

    awards_file = REPO_ROOT / "_data" / "awards.yml"
    for award in yaml.safe_load(awards_file.read_text(encoding="utf-8")):
        info["awards"].append(f"{award['year']} {award['title']}, {award['organization']}")

    return info


def generate_cv_html(info: dict) -> str:
    """
    Generate the HTML for the CV.
    """
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
        
        .publication-item p { margin: .25em 0 0; }
        @media (max-width: 600px) {
            body { margin: 0 auto; padding: 0; }
            .cv-container { padding: 24px; }
            header, .item { display: block; }
            .contact-info { text-align: left; }
        }
        @media print {
            .item { break-inside: avoid; }
            h2 { break-after: avoid; }
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

    for edu in info["education"]:
        parts = edu.split(":", 1)
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
        <h2>Appointments</h2>
"""

    for appt in info["appointments"]:
        parts = appt.split(":", 1)
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
        <h2>Selected GIS &amp; GeoAI projects</h2>
"""
    for title, url, description in info["projects"]:
        html += f'<p><strong><a href="{escape(url, quote=True)}">{escape(title)}</a></strong><br>{escape(description)}</p>'

    html += """
    </section>

    <section>
        <h2>Publications</h2>
"""

    for pub in info["publications"]:
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

    for award in info["awards"]:
        match = re.match(r"^(\d{4})\s*(.*)", award)
        if match:
            year = match.group(1)
            desc = match.group(2)
        else:
            year = ""
            desc = award

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
            Last updated: """ + datetime.now().strftime("%B %Y") + """
        </p>
    </footer>

</div>

</body>
</html>
"""
    return html


def main() -> None:
    print("Generating Professional CV...")

    html_path = REPO_ROOT / "index.html"
    cv_path = REPO_ROOT / "cv.html"

    if not html_path.exists():
        print(f"Error: {html_path} not found!")
        sys.exit(1)

    info = extract_info_from_html(str(html_path))
    print(
        f"Extracted: {len(info['education'])} Education, {len(info['appointments'])} Appointments, {len(info['publications'])} Publications"
    )

    cv_html = generate_cv_html(info)

    with open(cv_path, "w", encoding="utf-8") as f:
        f.write(cv_html)

    print(f"✅ Successfully generated {cv_path.name}")


if __name__ == "__main__":
    main()


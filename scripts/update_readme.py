#!/usr/bin/env python3
"""
Update `README.md` based on `index.html` content.

This was moved from the repository root into `scripts/`.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


def extract_info_from_html(html_file: str) -> dict:
    """Extract key information from index.html."""
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    name = "Yalin Yang"
    title = "Research Associate & GIS Programmer"
    institution = "West Virginia University"
    center = "West Virginia GIS Technical Center"

    email_match = re.search(r"mailto:([^\"]+)", content)
    email = email_match.group(1) if email_match else "yy00021@mail.wvu.edu"

    website_match = re.search(r"https://gisyaliny\.github\.io/", content)
    website = "https://gisyaliny.github.io/" if website_match else "https://gisyaliny.github.io/"

    social_links = {}
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if "scholar.google.com" in href:
            social_links["Google Scholar"] = href
        elif "github.com" in href:
            social_links["GitHub"] = href
        elif "linkedin.com" in href:
            social_links["LinkedIn"] = href

    research_interests = [
        "Geographic Information Science (GIS)",
        "Urban Environment and Human Networks Modeling",
        "Big Geospatial Data Analytics",
        "GIS Programming",
        "Android Development",
        "AWS Cloud Computing",
        "Python, JavaScript, Java, R Programming",
    ]

    education = [
        "2019–2024: Ph.D. in Geospatial Information Sciences, University of Texas at Dallas",
        "2017–2019: M.A. in Geography, Binghamton University (SUNY)",
        "2013–2017: B.S. in Geographic Information Science, Yunnan University",
    ]

    appointments = [
        "2024–Present: Research Associate, GIS Programmer, West Virginia GIS Technical Center",
        "2024: Senior GIS Analyst, City of Dallas",
        "2021–2024: GIS Administrator, GAIA Lab, UT Dallas",
        "2019–2024: Teaching Assistant, Department of GIScience, UT Dallas",
        "2018–2019: Teaching Assistant, Department of Geography, Binghamton University (SUNY)",
    ]

    publications = []
    pub_ul = soup.find("ul", id="publications-list")
    if pub_ul:
        for li in pub_ul.find_all("li"):
            text = li.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            publications.append(text)

    awards = []
    for header in soup.find_all(["h2", "h3"]):
        if "Grants & Awards" in header.get_text():
            next_ul = header.find_next("ul")
            if next_ul:
                for li in next_ul.find_all("li"):
                    text = li.get_text(" ", strip=True)
                    text = re.sub(r"\s+", " ", text)
                    awards.append(text)
            break

    return {
        "name": name,
        "title": title,
        "institution": institution,
        "center": center,
        "email": email,
        "website": website,
        "social_links": social_links,
        "research_interests": research_interests,
        "education": education,
        "appointments": appointments,
        "publications": publications,
        "awards": awards,
    }


def generate_readme(info: dict) -> str:
    """Generate README.md content based on extracted information."""
    readme_content = f"""# {info['name']}'s Academic Website

This is the personal academic website of {info['name']}, a {info['title']} at the {info['center']}, {info['institution']}. The website showcases research, teaching experience, awards, and professional activities.

## About

{info['name']} is a {info['title']} at the [{info['center']}](https://wvgis.wvu.edu/) at {info['institution']}. {info['name']} holds a Ph.D. in Geospatial Information Sciences from the University of Texas at Dallas and specializes in Geographic Information Science (GIS), Urban Environment, and Human Networks Modeling.

### Research Interests

{info['name']} focuses on applying geospatial big data, machine learning, and cloud computing (AWS) to study:
- Built environments and social events
- Semantic segmentation of urban landscapes  
- Navigation with map matching
- Human networks modeling
- Big geospatial data analytics

### Technical Skills

- **Programming Languages**: Python, JavaScript, Java, R
- **GIS & Spatial Analysis**: ArcGIS, QGIS, Spatial Statistics, WebGIS
- **Cloud Computing**: AWS (Lambda, API Gateway, DynamoDB)
- **Mobile Development**: Android Development
- **Data Science**: Machine Learning, Deep Learning, Natural Language Processing

## Education

"""

    for edu in info["education"]:
        readme_content += f"- {edu}\n"

    readme_content += f"""
## Current Position

{info['appointments'][0]}

## Professional Experience
"""
    for appointment in info["appointments"][1:]:
        readme_content += f"- {appointment}\n"

    readme_content += f"""
## Recent Publications
"""
    for pub in info["publications"][:10]:
        readme_content += f"- {pub}\n"

    readme_content += f"""
## Awards & Grants
"""
    for award in info["awards"][:12]:
        readme_content += f"- {award}\n"

    readme_content += f"""
## Contact

- **Email**: [{info['email']}](mailto:{info['email']})
- **Website**: [{info['website']}]({info['website']})
- **Google Scholar**: [{info['name']}]({info['social_links'].get('Google Scholar', '#')})
- **GitHub**: [gisyaliny]({info['social_links'].get('GitHub', '#')})
- **LinkedIn**: [{info['name']}]({info['social_links'].get('LinkedIn', '#')})

---
*This README is automatically generated from the website content. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return readme_content


def main() -> None:
    html_path = REPO_ROOT / "index.html"
    readme_path = REPO_ROOT / "README.md"

    if not html_path.exists():
        print(f"Error: {html_path} not found!")
        sys.exit(1)

    print("Extracting information from index.html...")
    info = extract_info_from_html(str(html_path))

    print("Generating README.md content...")
    readme_content = generate_readme(info)

    print(f"Writing updated content to {readme_path}...")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ Successfully updated {readme_path.name}")
    print(f"📊 Extracted {len(info['publications'])} publications")
    print(f"🏆 Extracted {len(info['awards'])} awards")
    print(f"🎓 Extracted {len(info['education'])} education entries")
    print(f"💼 Extracted {len(info['appointments'])} appointments")


if __name__ == "__main__":
    main()


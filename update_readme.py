#!/usr/bin/env python3
"""
Script to update README.md based on content from index.html
Extracts key information from the academic website and generates an updated README
"""

import re
from bs4 import BeautifulSoup
from datetime import datetime
import os

def extract_info_from_html(html_file):
    """Extract key information from index.html"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract basic info
    name = "Yalin Yang"
    title = "Research Associate & GIS Programmer"
    institution = "West Virginia University"
    center = "West Virginia GIS Technical Center"
    
    # Extract email
    email_match = re.search(r'mailto:([^"]+)', content)
    email = email_match.group(1) if email_match else "yy00021@mail.wvu.edu"
    
    # Extract website URL
    website_match = re.search(r'https://gisyaliny\.github\.io/', content)
    website = "https://gisyaliny.github.io/" if website_match else "https://gisyaliny.github.io/"
    
    # Extract social links
    social_links = {}
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if 'scholar.google.com' in href:
            social_links['Google Scholar'] = href
        elif 'github.com' in href:
            social_links['GitHub'] = href
        elif 'linkedin.com' in href:
            social_links['LinkedIn'] = href
    
    # Extract research interests
    research_interests = [
        "Geographic Information Science (GIS)",
        "Urban Environment and Human Networks Modeling", 
        "Big Geospatial Data Analytics",
        "GIS Programming",
        "Android Development",
        "AWS Cloud Computing",
        "Python, JavaScript, Java, R Programming"
    ]
    
    # Extract education
    education = [
        "2019–2024: Ph.D. in Geospatial Information Sciences, University of Texas at Dallas",
        "2017–2019: M.A. in Geography, Binghamton University (SUNY)",
        "2013–2017: B.S. in Geographic Information Science, Yunnan University"
    ]
    
    # Extract current appointments
    appointments = [
        "2024–Present: Research Associate, GIS Programmer, West Virginia GIS Technical Center",
        "2024: Senior GIS Analyst, City of Dallas",
        "2021–2024: GIS Administrator, GAIA Lab, UT Dallas",
        "2019–2024: Teaching Assistant, Department of GIScience, UT Dallas",
        "2018–2019: Teaching Assistant, Department of Geography, Binghamton University (SUNY)"
    ]
    
    # Extract recent publications (from the publications section)
    publications = [
        "Griffith, D. A., Conway, C., Gamarra, A., Hutchison, M., Kim, D., & Yang, Y. (2025). Political Districts Versus Customized Polygons: Implementing Geographic Tessellation Stratified Random Sampling. Transactions in GIS, 29(2), e70019.",
        "Maxwell, A. E., Farhadpour, S., Das, S., & Yang, Y. (2024). geodl: An R package for geospatial deep learning semantic segmentation using torch and terra. PLoS One, 19(12), e0315127.",
        "Yang, Y., Wu, Y., & Yuan, M. (2024). What Local Environments Drive Opportunities for Social Events? A New Approach Based on Bayesian Modeling in Dallas, Texas, USA. ISPRS International Journal of Geo-Information, 13(3), 81.",
        "Wu, Y., Yang, Y., & Yuan, M. (2024). Location Analytics of Routine Occurrences (LARO) to Identify Locations with Regularly Occurring Events with a Case Study on Traffic Accidents. Information, 15(2), 107."
    ]
    
    # Extract awards and grants
    awards = [
        "2024: Geospatial Cyberinfrastructure Workshop Scholarship, National Science Foundation",
        "2024: Betty and Gifford Travel Award, University of Texas at Dallas",
        "2023: AAG Student Travel Grants, American Association of Geographers (AAG)",
        "2023: I-GUIDE Summer School Travel Award, National Science Foundation",
        "2023: Pioneer Student Research Grants, University of Texas at Dallas",
        "2022: ICA Scholarship, International Cartographic Association (ICA)",
        "2022: Esri EIP Student of the Year Award, ESRI",
        "2021: Ph.D. Research Small Award, University of Texas at Dallas",
        "2019: Pioneer Student Research Grants, University of Texas at Dallas",
        "2019: AAG-UCGIS Summer School Travel Award, University Consortium for Geographic Information Science (UCGIS)"
    ]
    
    return {
        'name': name,
        'title': title,
        'institution': institution,
        'center': center,
        'email': email,
        'website': website,
        'social_links': social_links,
        'research_interests': research_interests,
        'education': education,
        'appointments': appointments,
        'publications': publications,
        'awards': awards
    }

def generate_readme(info):
    """Generate README.md content based on extracted information"""
    
    current_year = datetime.now().year
    
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
    
    for edu in info['education']:
        readme_content += f"- {edu}\n"
    
    readme_content += f"""
## Current Position

{info['appointments'][0]}

## Professional Experience

"""
    
    for appointment in info['appointments'][1:]:
        readme_content += f"- {appointment}\n"
    
    readme_content += f"""
## Recent Publications

"""
    
    for pub in info['publications'][:4]:  # Show top 4 recent publications
        readme_content += f"- {pub}\n"
    
    readme_content += f"""
## Awards & Grants

"""
    
    for award in info['awards'][:6]:  # Show top 6 recent awards
        readme_content += f"- {award}\n"
    
    readme_content += f"""
## Website Features

- Responsive design using Bootstrap
- Modern UI with custom styling
- Interactive research portfolio with modal windows
- Contact form functionality
- Integration with academic profiles (Google Scholar, GitHub, LinkedIn)
- Multi-language support (English and Chinese)

## Technical Stack

- HTML5
- CSS3
- JavaScript
- Bootstrap Framework
- jQuery
- Font Awesome Icons
- Google Fonts

## Website Sections

The website is organized into several main sections:
- **About Me**: Professional background and education
- **Research**: Interactive portfolio showcasing research projects
- **Publications**: Academic publications and research output
- **Awards**: Grants, scholarships, and recognition
- **Teaching**: Teaching experience and course materials
- **Contact**: Contact information and form

## Development

The website is hosted on GitHub Pages and can be accessed at [{info['website']}]({info['website']}).

### Local Development

To run the website locally:
1. Clone the repository: `git clone https://github.com/gisyaliny/gisyaliny.github.io.git`
2. Open `index.html` in a web browser
3. Or serve locally using a simple HTTP server: `python -m http.server 8000`

## Contact

- **Email**: [{info['email']}](mailto:{info['email']})
- **Website**: [{info['website']}]({info['website']})
- **Google Scholar**: [{info['name']}]({info['social_links'].get('Google Scholar', '#')})
- **GitHub**: [gisyaliny]({info['social_links'].get('GitHub', '#')})
- **LinkedIn**: [{info['name']}]({info['social_links'].get('LinkedIn', '#')})

## License

All rights reserved. Copyright © {current_year} {info['name']}.

---

*This README is automatically generated from the website content. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return readme_content

def main():
    """Main function to update README.md"""
    
    html_file = 'index.html'
    readme_file = 'README.md'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return
    
    print("Extracting information from index.html...")
    info = extract_info_from_html(html_file)
    
    print("Generating README.md content...")
    readme_content = generate_readme(info)
    
    print(f"Writing updated content to {readme_file}...")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Successfully updated {readme_file}")
    print(f"📊 Extracted {len(info['publications'])} publications")
    print(f"🏆 Extracted {len(info['awards'])} awards")
    print(f"🎓 Extracted {len(info['education'])} education entries")
    print(f"💼 Extracted {len(info['appointments'])} appointments")

if __name__ == "__main__":
    main()

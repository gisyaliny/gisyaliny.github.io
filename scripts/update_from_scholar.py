import yaml
from scholarly import scholarly
import sys
import os

# Configuration
CONFIG_FILE = '_config.yml'
DATA_FILE = '_data/publications.yml'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def fetch_publications(scholar_id):
    print(f"Fetching publications for Google Scholar ID: {scholar_id}...")
    try:
        author = scholarly.search_author_id(scholar_id)
        scholarly.fill(author, sections=['publications'])
    except Exception as e:
        print(f"Error fetching from Google Scholar: {e}")
        sys.exit(1)
    
    publications = []
    print(f"Found {len(author['publications'])} publications.")
    
    for pub in author['publications']:
        scholarly.fill(pub)
        bib = pub['bib']
        
        # Extract fields
        title = bib.get('title', 'Untitled')
        year = bib.get('pub_year', 'Unknown')
        
        # Authors
        # Google Scholar returns authors as a string sometimes, let's keep it simple
        authors = bib.get('author', 'Unknown')
        # Bold current user (simplified logic, user might need to adjust name matching)
        authors = authors.replace('Yalin Yang', '**Yalin Yang**').replace('Y Yang', '**Y Yang**')

        # Journal / Venue
        journal = bib.get('journal') or bib.get('conference') or bib.get('publisher') or 'Preprint'
        volume = bib.get('volume')
        number = bib.get('number')
        pages = bib.get('pages')
        
        journal_full = journal
        if volume:
            journal_full += f", {volume}"
            if number:
                journal_full += f"({number})"
        if pages:
            journal_full += f", {pages}"
            
        link = pub.get('pub_url')
        
        entry = {
            'title': title,
            'authors': authors,
            'year': int(year) if str(year).isdigit() else year,
            'journal': journal_full,
            'link': link
        }
        publications.append(entry)
        
    return publications

def save_yaml(publications):
    # Sort by year descending
    publications.sort(key=lambda x: str(x['year']), reverse=True)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(publications, f, sort_keys=False, allow_unicode=True, width=1000)
    print(f"Saved {len(publications)} publications to {DATA_FILE}")

def main():
    config = load_config()
    scholar_id = config.get('google_scholar_id')
    
    if not scholar_id:
        print("Error: 'google_scholar_id' not found in _config.yml")
        sys.exit(1)
        
    pubs = fetch_publications(scholar_id)
    save_yaml(pubs)

if __name__ == "__main__":
    main()

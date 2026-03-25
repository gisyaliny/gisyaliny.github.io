#!/usr/bin/env python3
"""
Helper utilities to render and update the publications <ul> section in index.html.

This was originally implemented in `archive/update_publications.py`.
The functions here are used by `scripts/update_from_scholar.py`.
"""

import re
import os


def parse_publication(publication_text):
    """
    Parse a publication entry and extract components.
    Handles both journal articles and thesis formats.
    """
    text = publication_text.strip()

    # Pattern 1: Journal articles with volume, issue, pages
    # Format: Authors (Year). Title. Journal, Volume(Issue), Pages.
    journal_pattern = r"^(.+?)\s+\((\d{4})\)\.\s+(.+?)\.\s+(.+?),\s+(\d+)(?:\((\d+)\))?,\s+(.+?)\.$"

    # Pattern 2: Thesis format
    # Format: Authors (Year). Title (Master's thesis, Institution).
    thesis_pattern = r"^(.+?)\s+\((\d{4})\)\.\s+(.+?)\s+\(Master\'s thesis,\s+(.+?)\)\.$"

    # Try journal article pattern first
    match = re.match(journal_pattern, text)
    if match:
        authors, year, title, journal, volume, issue, pages = match.groups()

        # Bold Yang, Y. in authors list
        authors_bold = re.sub(r"\bYang, Y\.", "<b>Yang, Y.</b>", authors)

        # Create DOI URL if it's a DOI format
        doi_url = None
        if "e" in pages and pages.startswith("e"):
            # This looks like a DOI
            doi_url = f"https://doi.org/{pages}"

        return {
            "authors": authors_bold,
            "year": int(year),
            "title": title,
            "journal": journal,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "doi_url": doi_url,
            "type": "journal",
        }

    # Try thesis pattern
    match = re.match(thesis_pattern, text)
    if match:
        authors, year, title, institution = match.groups()

        # Bold Yang, Y. in authors list
        authors_bold = re.sub(r"\bYang, Y\.", "<b>Yang, Y.</b>", authors)

        return {
            "authors": authors_bold,
            "year": int(year),
            "title": title,
            "journal": f"Master's thesis, {institution}",
            "volume": None,
            "issue": None,
            "pages": None,
            "doi_url": None,
            "type": "thesis",
        }

    print(f"Warning: Could not parse publication: {publication_text}")
    return None


def generate_html_li(publication_data):
    """
    Generate HTML list item for a publication.
    """
    authors = publication_data["authors"]
    year = publication_data["year"]
    title = publication_data["title"]
    journal = publication_data["journal"]
    volume = publication_data["volume"]
    issue = publication_data["issue"]
    pages = publication_data["pages"]
    doi_url = publication_data["doi_url"]
    pub_type = publication_data.get("type", "journal")

    # Always add link to paper title (use DOI URL if available, otherwise placeholder)
    if doi_url:
        title_with_link = f'<a href="{doi_url}" target="_blank">{title}</a>'
    else:
        # Use placeholder link if no DOI available
        title_with_link = f'<a href="#" target="_blank">{title}</a>'

    # Format the citation based on type
    if pub_type == "thesis":
        citation = f"{authors} ({year}). {title_with_link}. <em>{journal}</em>."
    else:
        # For journal articles: Authors (Year). Title. Journal, Volume(Issue), Pages.
        citation = f"{authors} ({year}). {title_with_link}. <em>{journal}</em>"

        if volume:
            if issue:
                citation += f", {volume}({issue})"
            else:
                citation += f", {volume}"

        if pages:
            citation += f", {pages}."
        else:
            citation += "."

    return f'<li style="margin: 10px">{citation}</li>'


def extract_existing_publications(html_content):
    """
    Extract existing publication titles from the publications HTML.
    Returns a list of titles (the <a> text inside each <li>).
    """
    existing_titles = []

    ul_start = html_content.find("<ul id=\"publications-list\">")
    if ul_start == -1:
        return existing_titles

    ul_end = html_content.find("</ul>", ul_start)
    if ul_end == -1:
        return existing_titles

    # Extract the content between <ul> and </ul>
    ul_content = html_content[ul_start:ul_end]

    li_pattern = r"<li[^>]*>(.*?)</li>"
    li_matches = re.findall(li_pattern, ul_content, re.DOTALL)

    for li_content in li_matches:
        title_pattern = r"<a[^>]*>([^<]+)</a>"
        title_match = re.search(title_pattern, li_content)
        if title_match:
            title = title_match.group(1).strip()
            existing_titles.append(title)

    return existing_titles


def parse_existing_publication_html(li_html):
    """
    Parse an existing publication <li> to extract year for sorting.
    """
    year_pattern = r"\((\d{4})\)"
    year_match = re.search(year_pattern, li_html)
    if year_match:
        return int(year_match.group(1))
    return 0


def update_html_file(html_file, publications_list, existing_publications_html):
    """
    Update the HTML file with new publications list, preserving existing ones and maintaining chronological order.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    start_pattern = r"<ul id=\"publications-list\">"
    end_pattern = r"</ul>"

    start_match = re.search(start_pattern, content)
    if not start_match:
        print("Error: Could not find publications list in HTML file")
        return False

    # Find the end of the publications list
    start_pos = start_match.start()
    ul_start = content.find("<ul id=\"publications-list\">", start_pos)
    ul_end = content.find("</ul>", ul_start)

    if ul_start == -1 or ul_end == -1:
        print("Error: Could not find publications list boundaries")
        return False

    # Parse existing publications and extract their HTML with years
    existing_publications_with_years = []
    if existing_publications_html:
        li_pattern = r"<li[^>]*>.*?</li>"
        existing_li_matches = re.findall(li_pattern, existing_publications_html, re.DOTALL)

        for li_html in existing_li_matches:
            year = parse_existing_publication_html(li_html)
            existing_publications_with_years.append((year, li_html))

    # Combine all publications (existing + new) and sort by year (newest first)
    all_publications = []
    for year, li_html in existing_publications_with_years:
        all_publications.append((year, li_html))

    for pub_html in publications_list:
        year = parse_existing_publication_html(pub_html)
        all_publications.append((year, pub_html))

    all_publications.sort(key=lambda x: x[0], reverse=True)

    new_publications_html = "<ul id=\"publications-list\">\n"
    for year, li_html in all_publications:
        new_publications_html += f"                            {li_html}\n"
    new_publications_html += "                        </ul>"

    # Replace the old publications list with the new one
    new_content = content[:ul_start] + new_publications_html + content[ul_end + 5 :]

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


# Legacy main: update from publications.txt
def main():
    """
    Main function to read publications.txt and update index.html.
    """
    publications_file = "publications.txt"
    html_file = "index.html"

    if not os.path.exists(publications_file):
        print(f"Error: {publications_file} not found!")
        return

    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return

    print("Reading existing publications from HTML...")
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    existing_titles = extract_existing_publications(html_content)
    print(f"Found {len(existing_titles)} existing publications in HTML")

    # Extract existing publications HTML to preserve them
    existing_publications_html = ""
    ul_start = html_content.find("<ul id=\"publications-list\">")
    if ul_start != -1:
        ul_end = html_content.find("</ul>", ul_start)
        if ul_end != -1:
            existing_publications_html = html_content[
                ul_start + len("<ul id=\"publications-list\">") : ul_end
            ]

    print("Reading publications from publications.txt...")
    with open(publications_file, "r", encoding="utf-8") as f:
        publications = f.readlines()

    publications_data = []
    new_publications_count = 0

    for i, pub_text in enumerate(publications, 1):
        pub_text = pub_text.strip()
        if not pub_text:
            continue

        print(f"Processing publication {i}: {pub_text[:50]}...")
        pub_data = parse_publication(pub_text)
        if pub_data:
            title = pub_data["title"]
            if title in existing_titles:
                print(f"  → Publication already exists in HTML, skipping: {title[:50]}...")
                continue

            print(f"  → New publication, will add: {title[:50]}...")
            publications_data.append(pub_data)
            new_publications_count += 1
        else:
            print(f"Failed to parse publication {i}")

    if new_publications_count == 0:
        print("\nNo new publications to add. All publications from publications.txt already exist in HTML.")
        print("Re-sorting existing publications by year...")
        if update_html_file(html_file, [], existing_publications_html):
            print(f"Successfully re-sorted publications in {html_file}")
        else:
            print("Failed to re-sort HTML file")
        return

    publications_data.sort(key=lambda x: x["year"], reverse=True)
    print(f"\nSorted {new_publications_count} new publications by year (newest first)")

    html_items = []
    for pub_data in publications_data:
        html_li = generate_html_li(pub_data)
        html_items.append(html_li)

    print(f"Generated {len(html_items)} new HTML list items")

    if update_html_file(html_file, html_items, existing_publications_html):
        print(f"Successfully updated {html_file} with {new_publications_count} new publications")
    else:
        print("Failed to update HTML file")

    print(f"\nTotal new publications added: {new_publications_count}")
    print(f"Total existing publications preserved: {len(existing_titles)}")


if __name__ == "__main__":
    main()


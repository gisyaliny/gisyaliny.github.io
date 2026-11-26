#!/usr/bin/env python3
"""
Fetch publications from Google Scholar and update `index.html` directly.

This fixes the previous implementation that only wrote `_data/publications.yml`
(which your current `index.html` does not consume).
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from html import unescape
from scholarly import scholarly

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Ensure we can import `scripts/update_publications.py` when running this file
sys.path.insert(0, str(SCRIPT_DIR))
from update_publications import (  # noqa: E402
    extract_existing_publications,
    generate_html_li,
    update_html_file,
)


CONFIG_FILE = REPO_ROOT / "_config.yml"
HTML_FILE = REPO_ROOT / "index.html"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Error: {CONFIG_FILE} not found.")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize_title(title: str) -> str:
    """
    Normalize a title for duplicate detection.
    This is intentionally simple: lowercasing + removing punctuation.
    """
    if not title:
        return ""
    t = re.sub(r"\s+", " ", str(title)).strip().lower()
    # Remove punctuation but keep spaces/word chars.
    t = re.sub(r"[^\w\s]", "", t)
    return t


def fetch_and_parse_publications(scholar_id: str, delay_s: float = 1.0) -> list[dict]:
    """
    Fetch publications from Google Scholar and transform them into the format
    expected by `scripts/update_publications.py::generate_html_li`.
    """
    print(f"Searching for author with ID: {scholar_id}")

    author = scholarly.search_author_id(scholar_id)
    try:
        # Fill author to get the publications list (still might be slow).
        scholarly.fill(author, sections=["publications"])
    except Exception as e:
        raise RuntimeError(f"Error fetching from Google Scholar: {e}") from e

    pub_list = author.get("publications", [])
    print(f"Found {len(pub_list)} publications. Fetching details...")

    publications_data: list[dict] = []
    for idx, pub in enumerate(pub_list, start=1):
        bib = pub.get("bib", {}) if isinstance(pub, dict) else {}
        title = bib.get("title")
        pub_year = bib.get("pub_year")

        if not title:
            continue

        try:
            filled_pub = scholarly.fill(pub)
            filled_bib = filled_pub.get("bib", {}) if isinstance(filled_pub, dict) else {}

            # Authors: scholarly usually returns something like "Last, F." already.
            authors_raw = filled_bib.get("author") or bib.get("author") or "Unknown"
            authors_raw = str(authors_raw).replace("&", "&amp;")

            # Bold Yang, Y. and common variants.
            # (If Yang appears differently, the un-bolded version will still render correctly.)
            authors_final = re.sub(
                r"\b(Yang,\s*Y\.[-]?[A-Z]?\.?)\b", "<b>Yang, Y.</b>", authors_raw, flags=re.IGNORECASE
            )

            journal = (
                filled_bib.get("journal")
                or filled_bib.get("conference")
                or filled_bib.get("publisher")
                or "Preprint"
            )
            volume = filled_bib.get("volume")
            issue = filled_bib.get("number") or filled_bib.get("issue")
            pages = filled_bib.get("pages")

            pub_url = filled_pub.get("pub_url")
            doi_url = pub_url if pub_url else None

            # Determine type for citation formatting
            title_l = str(title).lower()
            journal_l = str(journal).lower()
            pub_type = "thesis" if "thesis" in title_l or "thesis" in journal_l else "journal"

            year_val = filled_bib.get("pub_year", pub_year)
            year_int = int(year_val) if year_val and str(year_val).isdigit() else 0

            publications_data.append(
                {
                    "authors": authors_final,
                    "year": year_int,
                    "title": title,
                    "journal": journal,
                    "volume": volume,
                    "issue": issue,
                    "pages": pages,
                    "doi_url": doi_url,
                    "type": pub_type,
                }
            )

            print(f"  [{idx}/{len(pub_list)}] Processed: {str(title)[:60]}...")

            time.sleep(delay_s)
        except Exception as e:
            print(f"  [{idx}/{len(pub_list)}] Error processing '{str(title)[:40]}...': {e}")
            continue

    return publications_data


def update_year_groups(html, publications):
    start = html.index('<div id="papers">')
    end = html.index('</section>', start)
    soup = BeautifulSoup(html[start:end], "html.parser")
    papers = soup.select_one("#papers")
    groups = {int(group.h3.get_text(strip=True)): group for group in papers.select(".pub-year")}
    seen = {normalize_title(title.get_text(" ", strip=True)) for title in papers.select("li > a, li > span")}
    added = 0
    for pub in publications:
        year, title = pub["year"], pub["title"]
        key = normalize_title(title)
        if not year or not key or key in seen:
            continue
        seen.add(key)
        if year not in groups:
            group = soup.new_tag("div", attrs={"class": "pub-year"})
            group.append(soup.new_tag("h3"))
            group.h3.string = str(year)
            group.append(soup.new_tag("ul"))
            older = [y for y in groups if y < year]
            archive = papers.select_one(".older-pubs")
            parent = archive if archive and year <= max(int(h.text) for h in archive.select("h3")) else papers
            sibling = next((groups[y] for y in sorted(older, reverse=True) if groups[y].parent is parent), None)
            if sibling:
                sibling.insert_before(group)
            elif parent is papers and archive:
                archive.insert_before(group)
            else:
                parent.append(group)
            groups[year] = group
        item = soup.new_tag("li")
        url = pub.get("doi_url") or ""
        link = soup.new_tag("a", href=url) if url.startswith(("https://", "http://")) else soup.new_tag("span")
        link.string = title
        item.append(link)
        details = soup.new_tag("p")
        authors = BeautifulSoup(unescape(pub["authors"]), "html.parser").get_text(" ", strip=True)
        location = str(pub.get("volume") or "")
        if pub.get("issue"):
            location += f"({pub['issue']})"
        details.string = " · ".join(str(v) for v in (authors, pub["journal"], location, pub.get("pages")) if v)
        item.append(details)
        groups[year].ul.insert(0, item)
        added += 1
    if not added:
        return html
    archive = papers.select_one(".older-pubs")
    if archive:
        years = [int(h.text) for h in archive.select("h3")]
        archive.summary.span.string = f"{min(years)}–{max(years)} · {len(archive.select('li'))} works"
    return html[:start] + str(papers) + html[end:]


def main():
    config = load_config()
    scholar_id = config.get("google_scholar_id")
    if not scholar_id:
        print("Error: 'google_scholar_id' not found in _config.yml")
        sys.exit(1)

    if not HTML_FILE.exists():
        print(f"Error: {HTML_FILE} not found.")
        sys.exit(1)

    publications_data = fetch_and_parse_publications(str(scholar_id))
    if not publications_data:
        print("No publications found or error occurred.")
        return

    publications_data.sort(key=lambda x: x.get("year", 0), reverse=True)
    print(f"Collected {len(publications_data)} publications from Scholar.")

    html_content = HTML_FILE.read_text(encoding="utf-8")
    if '<div id="papers">' in html_content:
        updated = update_year_groups(html_content, publications_data)
        if updated != html_content:
            HTML_FILE.write_text(updated, encoding="utf-8")
        return
    existing_titles = extract_existing_publications(html_content)
    existing_titles_norm = {normalize_title(t) for t in existing_titles}
    print(f"Found {len(existing_titles)} existing publications in index.html.")

    new_publications_data = [
        pub for pub in publications_data if normalize_title(pub.get("title")) not in existing_titles_norm
    ]
    print(f"Found {len(new_publications_data)} NEW publications to add.")

    # Extract existing <li> HTML so we can preserve them and just re-sort/merge.
    ul_start = html_content.find('<ul id="publications-list">')
    existing_publications_html = ""
    if ul_start != -1:
        ul_end = html_content.find("</ul>", ul_start)
        if ul_end != -1:
            existing_publications_html = html_content[
                ul_start + len('<ul id="publications-list">') : ul_end
            ]

    html_items = [generate_html_li(pub_data) for pub_data in new_publications_data]

    ok = update_html_file(str(HTML_FILE), html_items, existing_publications_html)
    if ok:
        print("Successfully updated index.html publications.")
    else:
        print("Failed to update index.html publications.")


if __name__ == "__main__":
    main()

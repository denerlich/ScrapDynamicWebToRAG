import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import streamlit as st

st.set_page_config(layout="wide")
st.title("Interactive Website Crawler for RAG")
st.markdown(
    """
This tool recursively maps and extracts accessible internal links from given website domains.
All found content is saved in a single Markdown file suitable for ChatGPT or other RAG systems.
"""
)

start_urls_input = st.text_area(
    "Enter starting URLs (one per line):",
    "https://example.com",
)
max_depth = st.slider("Maximum crawl depth:", min_value=1, max_value=5, value=2)
use_playwright = st.checkbox(
    "Use Playwright for JavaScript-rendered pages", value=False
)
run_crawl = st.button("Start Crawling and Extracting")

def clean_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)[:80]

def fetch_page(url, use_browser=False):
    if not use_browser:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()
        browser.close()
    return html

def crawl_sites(start_urls, depth, use_browser=False):
    visited = set()
    queue = [(url, 0) for url in start_urls]
    results = []
    while queue:
        url, current_depth = queue.pop(0)
        if url in visited or current_depth > depth:
            continue
        visited.add(url)
        try:
            html = fetch_page(url, use_browser)
            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string.strip() if soup.title else url
            paragraphs = soup.find_all(["p", "h1", "h2", "h3", "li"])
            text = "\n".join(
                p.get_text().strip() for p in paragraphs if p.get_text().strip()
            )
            results.append(
                {"url": url, "title": title, "depth": current_depth, "text": text}
            )
            base_domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if link.startswith(base_domain):
                    queue.append((link, current_depth + 1))
        except Exception as e:
            st.warning(f"Failed to retrieve {url}: {e}")
            continue
    return results

def save_to_markdown(pages, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"# {page['title']}\n")
            f.write(f"**URL:** {page['url']}\n")
            f.write(f"**Depth:** {page['depth']}\n\n")
            f.write("## Page Content\n\n")
            f.write(page["text"] + "\n\n")
            f.write("---\n\n")

start_urls = [u.strip() for u in start_urls_input.splitlines() if u.strip()]

if run_crawl and start_urls:
    st.info(f"Starting crawl for {len(start_urls)} starting URL(s) (up to depth {max_depth})...")
    pages = crawl_sites(start_urls, max_depth, use_playwright)
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file = "output/combined_site_map.md"
    save_to_markdown(pages, output_file)
    st.success("Crawling completed. Download the compiled Markdown below.")
    with open(output_file, "rb") as f:
        st.download_button("Download Markdown File", f, file_name=os.path.basename(output_file))

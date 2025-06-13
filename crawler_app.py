import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import streamlit as st

st.set_page_config(layout="wide")
st.title("Interactive Website Crawler for RAG")
st.markdown("""
This tool recursively maps and extracts all accessible internal links from a given website domain.  
All found content is saved in a single Markdown file suitable for ChatGPT or other RAG systems.
""")

start_url = st.text_input("Enter the starting URL:", value="https://example.com")
max_depth = st.slider("Maximum crawl depth:", min_value=1, max_value=5, value=2)
run_crawl = st.button("Start Crawling and Extracting")

def clean_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)[:80]

def crawl_site(base_url, depth):
    visited = set()
    queue = [(base_url, 0)]
    results = []
    while queue:
        url, current_depth = queue.pop(0)
        if url in visited or current_depth > depth:
            continue
        visited.add(url)
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title else url
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            results.append({"url": url, "title": title, "depth": current_depth, "text": text})
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if link.startswith(base_url):
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

if run_crawl and start_url:
    parsed_url = urlparse(start_url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    st.info(f"Starting crawl from {start_url} (up to depth {max_depth})...")
    pages = crawl_site(domain, max_depth)
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file = f"output/{clean_filename(domain)}_site_map.md"
    save_to_markdown(pages, output_file)
    st.success("Crawling completed. Download the compiled Markdown below.")
    with open(output_file, "rb") as f:
        st.download_button("Download Markdown File", f, file_name=os.path.basename(output_file))

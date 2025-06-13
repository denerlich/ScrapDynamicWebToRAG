# ScrapDynamicWebToRAG

This project contains a Streamlit application that recursively crawls one or more
websites and compiles the text content into a single Markdown file. The output is
useful for retrieval augmented generation (RAG) workflows.

## Usage

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   # Only required if using the Playwright option
   playwright install
   ```

2. Run the app:

   ```bash
   streamlit run crawler_app.py
   ```

3. Enter one or more starting URLs (one per line), choose the crawl depth, and
   optionally enable Playwright for pages that rely on JavaScript. When the crawl
   completes a Markdown file will be written to the `output` directory.

diff --git a/README.md b/README.md
index 4655e602d9f001c6d9d4fe72846a7f34d7eba5e5..b8a02a6e1a625a85c4127e89f08b034483fbe1e7 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,25 @@
-# ScrapDynamicWebToRAG
+# ScrapDynamicWebToRAG
+
+This project contains a Streamlit application that recursively crawls one or more
+websites and compiles the text content into a single Markdown file. The output is
+useful for retrieval augmented generation (RAG) workflows.
+
+## Usage
+
+1. Install the dependencies:
+
+   ```bash
+   pip install -r requirements.txt
+   # Only required if using the Playwright option
+   playwright install
+   ```
+
+2. Run the app:
+
+   ```bash
+   streamlit run crawler_app.py
+   ```
+
+3. Enter one or more starting URLs (one per line), choose the crawl depth, and
+   optionally enable Playwright for pages that rely on JavaScript. When the crawl
+   completes a Markdown file will be written to the `output` directory.

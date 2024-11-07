
# Fitness Revolucionario Knowledge Base

## Prerequisites

1. **Python**: Ensure you have Python 3.12 installed.
2. **Required Python Packages**: Install the dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **wkhtmltopdf**: The script uses `pdfkit`, which requires `wkhtmltopdf` as a backend. Install `wkhtmltopdf` and ensure it is accessible in your system PATH.

## download_webpage

This script downloads web pages as PDF files and saves them to a specified directory. It supports three different modes for downloading:
1. A single webpage URL
2. A list of webpage URLs from a file
3. All pages listed in a sitemap XML file

### Usage

#### Command-Line Options

- `-p, --page` : Download a single webpage as PDF.
- `-s, --sitemap` : Download all pages listed in a sitemap XML file.
- `-l, --page_list` : Download all pages listed in a file, where each line contains one webpage URL.
- `-d, --directory` : (Required) Directory to save the PDF files.

#### Examples

##### 1. Download a Single Webpage as PDF

To download a single webpage:
```bash
python download_sitemap_pdfs.py -p https://example.com -d /path/to/target_directory
```

##### 2. Download Multiple Pages from a Sitemap XML

To download all pages listed in a `sitemap.xml` file:
```bash
python download_sitemap_pdfs.py -s /path/to/sitemap.xml -d /path/to/target_directory
```

##### 3. Download Multiple Pages from a List File

To download multiple pages from a file (`page_list.txt`) where each line contains a URL:
```bash
python download_sitemap_pdfs.py -l /path/to/page_list.txt -d /path/to/target_directory
```

#### Notes

- Each PDF file will be named based on the URL, with special characters like `/` replaced by underscores.
- Ensure `wkhtmltopdf` is installed and accessible in your system PATH.


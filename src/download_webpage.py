from pathlib import Path
import pdfkit
import requests
import argparse
import xml.etree.ElementTree as ET

def download_webpage_as_pdf(url: str, target_path: str) -> None:
    """
    Downloads a web page as a PDF and saves it to the specified target path.

    Parameters:
        url (str): The URL of the webpage to download.
        target_path (str): The path where the PDF should be saved.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    pdfkit.from_string(response.text, target_path)
    print(f"PDF saved to {target_path}")

def download_sitemap_as_pdfs(sitemap_path: str, target_dir: str) -> None:
    """
    Downloads all pages listed in a sitemap XML file as PDFs and saves them in the target directory.

    Parameters:
        sitemap_path (str): Path to the sitemap XML file.
        target_dir (str): Directory where PDFs should be saved.
    """
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [url_elem.text for url_elem in root.findall("ns:url/ns:loc", namespaces=namespace)]

    for url in urls:
        filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
        target_path = target_dir_path / filename

        try:
            download_webpage_as_pdf(url, str(target_path))
        except Exception as e:
            print(f"Failed to download {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download pages from a sitemap XML or a single webpage as a PDF.")
    parser.add_argument("-s", "--sitemap", type=str, help="Path to the sitemap XML file")
    parser.add_argument("-d", "--directory", type=str, required=True, help="Directory to save the PDF files")
    parser.add_argument("-p", "--page", type=str, help="URL of a single webpage to download as PDF")

    args = parser.parse_args()

    if args.page:
        # If a single page URL is provided, download it directly
        target_dir_path = Path(args.directory)
        target_dir_path.mkdir(parents=True, exist_ok=True)

        filename = f"{args.page.replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
        target_path = target_dir_path / filename
        try:
            download_webpage_as_pdf(args.page, str(target_path))
        except Exception as e:
            print(f"Failed to download {args.page}: {e}")
    elif args.sitemap:
        # If a sitemap is provided, download all pages listed in the sitemap
        download_sitemap_as_pdfs(args.sitemap, args.directory)
    else:
        print("Error: Either --sitemap or --page must be provided.")
        parser.print_help()

if __name__ == "__main__":
    main()

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
import pdfkit


def download_webpage_as_pdf(url: str, target_path: str) -> None:
    """
    Downloads a web page as a PDF and saves it to the specified target path.

    Parameters:
        url (str): The URL of the webpage to download.
        target_path (str): The path where the PDF should be saved.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        pdfkit.from_string(response.text, target_path)
        print(f"PDF saved to {target_path}")
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {url}: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")


def download_sitemap_as_pdfs(sitemap_path: str, target_dir: str) -> None:
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        url_elem.text
        for url_elem in root.findall("ns:url/ns:loc", namespaces=namespace)
    ]

    for url in urls:
        filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
        target_path = target_dir_path / filename

        try:
            download_webpage_as_pdf(url, str(target_path))
        except Exception as e:
            print(f"Failed to download {url}: {e}")


def download_pages_from_list(page_list_path: str, target_dir: str) -> None:
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True, exist_ok=True)

    with open(page_list_path, "r") as file:
        urls = file.read().splitlines()

    for url in urls:
        filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
        target_path = target_dir_path / filename

        try:
            download_webpage_as_pdf(url, str(target_path))
        except Exception as e:
            print(f"Failed to download {url}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download pages from a sitemap XML, a list of pages, or a single webpage as a PDF."
    )
    parser.add_argument(
        "-s", "--sitemap", type=str, help="Path to the sitemap XML file"
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        required=True,
        help="Directory to save the PDF files",
    )
    parser.add_argument(
        "-p", "--page", type=str, help="URL of a single webpage to download as PDF"
    )
    parser.add_argument(
        "-l",
        "--page_list",
        type=str,
        help="Path to a file containing a list of webpage URLs to download as PDFs",
    )

    args = parser.parse_args()

    if args.page:
        target_dir_path = Path(args.directory)
        target_dir_path.mkdir(parents=True, exist_ok=True)

        filename = f"{args.page.replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
        target_path = target_dir_path / filename
        try:
            download_webpage_as_pdf(args.page, str(target_path))
        except Exception as e:
            print(f"Failed to download {args.page}: {e}")
    elif args.sitemap:
        download_sitemap_as_pdfs(args.sitemap, args.directory)
    elif args.page_list:
        download_pages_from_list(args.page_list, args.directory)
    else:
        print("Error: You must provide either --sitemap, --page, or --page_list.")
        parser.print_help()


if __name__ == "__main__":
    main()

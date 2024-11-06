import argparse
import asyncio
from pathlib import Path

import httpx

# Limit the number of concurrent downloads
CONCURRENT_DOWNLOADS = 5  # Adjust this number based on your system's capabilities
semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)


async def download_file(url: str, target_folder: Path):
    """Download a file from a URL to the target folder, skipping if 404 error occurs."""
    filename = url.split("/")[-1]  # Get the file name from the URL
    filepath = target_folder / filename

    async with semaphore:  # Limit the concurrency
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, follow_redirects=True
                )  # Follow redirects
                response.raise_for_status()
                filepath.write_bytes(response.content)
                print(f"Downloaded {filename} to {target_folder}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    print(f"Skipped {filename}: 404 Not Found")
                else:
                    print(f"Failed to download {filename}: {e}")


async def main(lower_bound: int, upper_bound: int, target_folder: str):
    """Main function to download audio files in the specified range to target folder."""
    target_folder_path = Path(target_folder)
    target_folder_path.mkdir(parents=True, exist_ok=True)  # Ensure target folder exists

    urls = [
        f"https://traffic.libsyn.com/secure/fitnessrevolucionario/Episodio{n}.mp3"
        for n in range(lower_bound, upper_bound + 1)
    ]

    # Start asynchronous downloads with a concurrency limit
    download_tasks = [download_file(url, target_folder_path) for url in urls]
    await asyncio.gather(*download_tasks)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download a range of episodes.")
    parser.add_argument(
        "lower_bound", type=int, help="The lower bound of episode numbers"
    )
    parser.add_argument(
        "upper_bound", type=int, help="The upper bound of episode numbers"
    )
    parser.add_argument(
        "target_folder", type=str, help="The folder to save downloaded files"
    )

    args = parser.parse_args()

    # Run the main function in an asyncio event loop
    asyncio.run(main(args.lower_bound, args.upper_bound, args.target_folder))

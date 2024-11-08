
# Fitness Revolucionario Knowledge Base

## Prerequisites

1. **Python**: Ensure you have Python 3.12 installed.
2. **Required Python Packages**: Install the dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **wkhtmltopdf**: The script uses `pdfkit`, which requires `wkhtmltopdf` as a backend. Install `wkhtmltopdf` and ensure it is accessible in your system PATH.

## Folder Structure

The project is organized as follows:

```
project-root/
│
├── bin/
│   └── extract_transcript        # Bash script to convert the output of AWS Transcribe in JSON to txt  
│
├── src/
│   └── download_episodes.py      # Script to download fitness revolucionario podcast episodes
│   └── download_webpage.py       # Script to download web pages as PDFs
│   └── transcribe.py             # Script to generate transcriptions using AWS Transcribe
├── tests/
│   └── test_download_episodes.py # Placeholder for tests
│
├── requirements.txt              # Dependencies for the project
├── requirements-dev.txt          # Development dependencies
├── Makefile                      # Makefile for common commands
├── README.md                     # Project documentation
└── .gitignore                    # Git ignore file to exclude unnecessary files
```

## Makefile

1. **Install dependencies**:
   ```bash
   make install
   ```

2. **Lint the code**:
   ```bash
   make lint
   ```

3. **Format the code**:
   ```bash
   make format
   ```

4. **Run tests**:
   ```bash
   make test
   ```

## download_webpage.py

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
python download_webpage.py -p https://example.com -d /path/to/target_directory
```

##### 2. Download Multiple Pages from a Sitemap XML

To download all pages listed in a `sitemap.xml` file:
```bash
python download_webpage.py -s /path/to/sitemap.xml -d /path/to/target_directory
```

##### 3. Download Multiple Pages from a List File

To download multiple pages from a file (`page_list.txt`) where each line contains a URL:
```bash
python download_webpage.py -l /path/to/page_list.txt -d /path/to/target_directory
```

#### Notes

- Each PDF file will be named based on the URL, with special characters like `/` replaced by underscores.
- Ensure `wkhtmltopdf` is installed and accessible in your system PATH.

## download_episodes.py

### Usage

The main script, `download_episodes.py`, is located in the `src` directory and can be used in multiple ways.

#### Basic Usage

Run the script with the command-line interface to specify the episode range and target folder:

```bash
python src/download_episodes.py <lower_bound> <upper_bound> <target_folder>
```

For example, to download episodes from 1 to 10 into a folder named `downloads`:

```bash
python src/download_episodes.py 1 10 downloads
```

#### Using the Makefile

The project includes a `Makefile` with commands for convenience:

1. **Run the download script with bounds and folder**:
   ```bash
   make run lower=1 upper=10 folder=downloads
   ```
### Command-Line Arguments

- `lower_bound`: The starting episode number to download.
- `upper_bound`: The ending episode number to download.
- `target_folder`: The directory where the episodes will be saved.

The script will attempt to download each episode in the specified range. If an episode is missing (404 error), it will be skipped, and a message will be logged.

## transcribe.py

This script uploads audio files to an AWS S3 bucket, initiates transcription jobs in AWS Transcribe, downloads the transcriptions to a specified local directory, and manages concurrent transcriptions. It also checks if a transcription job already exists for a file and skips it if so, saving processing time.

### Usage

The script can be used to process a single file or all files in a directory, with a configurable limit on the number of concurrent transcriptions.

#### Command-Line Arguments

- `--input_file`: Path to a single input file to transcribe.
- `--dir`: Path to a directory containing multiple files to transcribe. The script processes all files in the directory.
- `language`: Language code for transcription (e.g., `en-US`).
- `target_dir`: Directory to save downloaded transcriptions.
- `--concurrent`: Maximum number of concurrent transcription jobs (default is `5`).

> **Note**: Either `--input_file` or `--dir` must be provided, not both.

#### Examples

1. **Transcribing a Single File**

   ```bash
   python transcribe_script.py --input_file /path/to/file.mp4 en-US /path/to/target_dir
   ```

   This command will:
   - Upload `/path/to/file.mp4` to the `ldeltoro-input` S3 bucket.
   - Start a transcription job with `en-US` as the language code.
   - Download the resulting transcription to `/path/to/target_dir`.

2. **Transcribing Multiple Files in a Directory**

   ```bash
   python transcribe_script.py --dir /path/to/directory en-US /path/to/target_dir --concurrent 5
   ```

   This command will:
   - Process all files in `/path/to/directory`.
   - Transcribe each file concurrently, up to a maximum of 5 jobs at a time.
   - Download each transcription result to `/path/to/target_dir`.
   - Skip any files that already have existing transcription jobs.
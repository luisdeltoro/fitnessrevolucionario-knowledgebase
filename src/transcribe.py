import argparse
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

# Hardcoded bucket names
INPUT_BUCKET = "ldeltoro-input"
OUTPUT_BUCKET = "ldeltoro-output"

# Initialize boto3 clients with specific profile and region
session = boto3.Session(profile_name="ldeltoro", region_name="us-east-1")
s3_client = session.client("s3")
transcribe_client = session.client("transcribe")


def upload_file_to_s3(input_file: str, bucket: str) -> str:
    """
    Uploads a file to an S3 bucket and returns the S3 URI.
    """
    try:
        file_name = input_file.split("/")[-1]  # Get only the file name from path
        s3_client.upload_file(input_file, bucket, file_name)
        s3_uri = f"s3://{bucket}/{file_name}"
        print(f"File uploaded to {s3_uri}")
        return s3_uri
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        raise


def start_transcription_job(job_name: str, s3_uri: str, language_code: str) -> str:
    """
    Starts a transcription job in AWS Transcribe and returns the job name.
    """
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat="mp4",  # Assume mp4, change if needed
            LanguageCode=language_code,
            OutputBucketName=OUTPUT_BUCKET,
        )
        print(f"Transcription job '{job_name}' started.")
        return job_name
    except ClientError as e:
        print(f"Error starting transcription job: {e}")
        raise


def check_transcription_job(job_name: str) -> dict:
    """
    Polls the status of the transcription job until it completes.
    """
    print(f"Checking transcription job status for '{job_name}'...")
    while True:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        status = response["TranscriptionJob"]["TranscriptionJobStatus"]
        if status in ["COMPLETED", "FAILED"]:
            print(f"Transcription job '{job_name}' finished with status: {status}")
            return response
        print("Transcription job in progress...")
        time.sleep(5)


def delete_file_from_s3(bucket: str, file_name: str):
    """
    Deletes a file from an S3 bucket.
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=file_name)
        print(f"Deleted '{file_name}' from bucket '{bucket}'.")
    except ClientError as e:
        print(f"Error deleting file from S3: {e}")
        raise


def download_transcription_file(target_dir: str, transcript_uri: str):
    """
    Downloads the transcription file from S3 to the specified local directory.
    """
    # Extract only the object key part from the full S3 URI
    object_key = transcript_uri.split(f"{OUTPUT_BUCKET}/")[-1]

    # Wait briefly to ensure the file is fully available
    time.sleep(5)

    try:
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Define the local path to save the transcription file
        local_file_path = os.path.join(target_dir, os.path.basename(object_key))

        # Check if the file exists and download it
        s3_client.head_object(Bucket=OUTPUT_BUCKET, Key=object_key)
        s3_client.download_file(OUTPUT_BUCKET, object_key, local_file_path)

        print(f"Transcription file downloaded to: {local_file_path}")
    except ClientError as e:
        print(f"Error downloading transcription file: {e}")
        raise


def process_file(input_file: str, language: str, target_dir: str):
    """
    Process a single file: upload, transcribe, delete from S3, and download output.
    """
    job_name = f"transcription-{input_file.split('/')[-1].split('.')[0]}"
    file_name = input_file.split("/")[-1]

    # Step 1: Upload file to input S3 bucket
    s3_uri = upload_file_to_s3(input_file, INPUT_BUCKET)

    # Step 2: Start transcription job
    start_transcription_job(job_name, s3_uri, language)

    # Step 3: Check transcription job status
    response = check_transcription_job(job_name)

    # Step 4: Delete the input file from the input bucket
    delete_file_from_s3(INPUT_BUCKET, file_name)

    # Step 5: Download the transcription output to target directory
    if response["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        download_transcription_file(target_dir, transcript_uri)
        print(f"Transcription completed and file downloaded to {target_dir}")
    else:
        print("Transcription job did not complete successfully.")


def main(
    input_file: str,
    language: str,
    target_dir: str,
    directory: str = None,
    concurrent: int = 5,
):
    # If a directory is provided, process all files in that directory
    files_to_process = (
        [input_file]
        if input_file
        else [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    )

    # Process files with concurrency limit
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [
            executor.submit(process_file, file, language, target_dir)
            for file in files_to_process
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload files and start AWS transcription jobs."
    )
    parser.add_argument("--input_file", type=str, help="Path to a single input file.")
    parser.add_argument(
        "--dir", type=str, help="Path to a directory containing files to transcribe."
    )
    parser.add_argument(
        "language", type=str, help="Language code for transcription (e.g., 'en-US')."
    )
    parser.add_argument(
        "target_dir", type=str, help="Directory to save the downloaded transcriptions."
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=5,
        help="Max number of concurrent transcriptions.",
    )

    args = parser.parse_args()

    if not (args.input_file or args.dir):
        print("Error: Either --input_file or --dir must be provided.")
    else:
        main(args.input_file, args.language, args.target_dir, args.dir, args.concurrent)

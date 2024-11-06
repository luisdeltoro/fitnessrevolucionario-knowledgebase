import argparse
import time
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


def main(input_file: str, language: str):
    # Generate a unique job name using the file name
    job_name = f"transcription-{input_file.split('/')[-1].split('.')[0]}"

    # Step 1: Upload file to input S3 bucket
    s3_uri = upload_file_to_s3(input_file, INPUT_BUCKET)

    # Step 2: Start transcription job
    start_transcription_job(job_name, s3_uri, language)

    # Step 3: Check transcription job status
    response = check_transcription_job(job_name)

    # Step 4: Handle final output (result is automatically saved to OUTPUT_BUCKET)
    if response["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        parsed_uri = urlparse(transcript_uri)
        print(f"Transcription completed. Output available at: {parsed_uri.geturl()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload a file and start AWS transcription."
    )
    parser.add_argument("input_file", type=str, help="Path to the input file.")
    parser.add_argument(
        "language", type=str, help="Language code for transcription (e.g., 'en-US')."
    )

    args = parser.parse_args()
    main(args.input_file, args.language)

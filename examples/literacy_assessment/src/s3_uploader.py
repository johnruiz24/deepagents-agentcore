"""
S3 uploader for assessment files.

This module provides functionality to upload generated assessment files (JSON and Markdown)
to AWS S3 for durable storage and cross-system accessibility.
"""

import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, List, Literal
import json
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed

from examples.literacy_assessment.src.config import LiteracyAssessmentConfig
from examples.literacy_assessment.src.models import Assessment
from examples.literacy_assessment.src.questions import format_assessment_as_markdown
import logging

logger = logging.getLogger(__name__)


def retry_with_backoff(max_attempts=3, backoff_seconds=None):
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default 3)
        backoff_seconds: List of sleep times between retries (default [1, 2, 4])

    Returns:
        Decorated function with retry logic
    """
    if backoff_seconds is None:
        backoff_seconds = [1, 2, 4]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')

                    # Permanent errors - don't retry
                    if error_code in ['NoSuchBucket', 'AccessDenied', 'InvalidBucketName']:
                        print(f"Permanent S3 error ({error_code}): {e}")
                        raise

                    # Transient errors - retry with backoff
                    if error_code in ['Throttling', 'ServiceUnavailable', 'RequestTimeout', 'RequestTimeTooSkewed']:
                        if attempt < max_attempts - 1:
                            sleep_time = backoff_seconds[attempt] if attempt < len(backoff_seconds) else backoff_seconds[-1]
                            print(f"S3 transient error ({error_code}), retry {attempt + 1}/{max_attempts} after {sleep_time}s")
                            time.sleep(sleep_time)
                            continue

                    # Unknown error or max retries exceeded
                    print(f"S3 error ({error_code}): {e}")
                    raise

            raise RuntimeError(f"Max retries ({max_attempts}) exceeded for S3 operation")

        return wrapper
    return decorator


class S3UploaderClient:
    """
    Client for uploading assessment files to S3.

    Uses boto3 S3 client with the same authentication pattern as KB tools.
    Includes retry logic with exponential backoff for transient errors.
    """

    def __init__(
        self,
        bucket_name: str = None,
        prefix: str = None,
        region: str = None,
        profile: str = None
    ):
        """
        Initialize S3 uploader with boto3 session.

        Args:
            bucket_name: S3 bucket name (defaults to config)
            prefix: S3 key prefix (defaults to config)
            region: AWS region (defaults to config)
            profile: AWS profile name (defaults to config)
        """
        self.bucket_name = bucket_name or LiteracyAssessmentConfig.S3_BUCKET_NAME
        self.prefix = prefix or LiteracyAssessmentConfig.S3_PREFIX
        self.region = region or LiteracyAssessmentConfig.S3_REGION
        self.profile = profile or LiteracyAssessmentConfig.AWS_PROFILE

        # Create boto3 session (with profile if specified, otherwise uses IAM role)
        if self.profile:
            session = boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
        else:
            session = boto3.Session(region_name=self.region)

        # Initialize S3 client
        self.s3_client = session.client('s3')

    def _generate_s3_key(self, level: int, timestamp: datetime, file_format: str) -> str:
        """
        Generate S3 key for assessment file.

        Args:
            level: Literacy level (1-4)
            timestamp: Assessment generation timestamp
            file_format: 'json' or 'markdown'

        Returns:
            S3 key string (e.g., 'learning_path/assessments/level_1/level_1_20251105_120000.json')
        """
        # Format timestamp as YYYYMMDD_HHMMSS
        ts_str = timestamp.strftime('%Y%m%d_%H%M%S')

        # Determine file extension
        ext = 'json' if file_format == 'json' else 'md'

        # Build key with hierarchical structure
        key = f"{self.prefix}/level_{level}/level_{level}_{ts_str}.{ext}"

        return key

    def _format_s3_uri(self, key: str) -> str:
        """
        Format S3 URI from bucket and key.

        Args:
            key: S3 object key

        Returns:
            S3 URI (s3://bucket/key)
        """
        return f"s3://{self.bucket_name}/{key}"

    def _prepare_assessment_content(self, assessment: Assessment, file_format: str) -> tuple[str, str]:
        """
        Prepare assessment content and content type for upload.

        Args:
            assessment: Assessment object to convert
            file_format: 'json' or 'markdown'

        Returns:
            Tuple of (content_string, content_type)
        """
        if file_format == 'json':
            # Convert assessment to JSON string using Pydantic's model_dump_json
            content = assessment.model_dump_json(indent=2)
            content_type = 'application/json'
        else:  # markdown
            # Convert assessment to markdown format
            content = format_assessment_as_markdown(assessment)
            content_type = 'text/markdown'

        return content, content_type

    def _generate_metadata(self, assessment: Assessment, file_format: str) -> Dict[str, str]:
        """
        Generate S3 object metadata from assessment.

        Args:
            assessment: Assessment object
            file_format: 'json' or 'markdown'

        Returns:
            Dict of metadata key-value pairs
        """
        # Note: All values must be strings, keys will be lowercased by AWS
        metadata = {
            'generation-time': datetime.now().isoformat(),
            'user-background-hash': str(hash(assessment.user_background)),
            'modules-count': str(len(assessment.modules_covered)),
            'literacy-level': str(assessment.level),
            'question-count': str(len(assessment.multiple_choice_questions) + len(assessment.open_ended_questions)),
            'format': file_format
        }

        return metadata

    @retry_with_backoff(max_attempts=3, backoff_seconds=[1, 2, 4])
    def _upload_with_retry(self, key: str, body: str, content_type: str, metadata: Dict[str, str]) -> dict:
        """
        Internal method to upload object with retry logic.

        Args:
            key: S3 object key
            body: Content to upload
            content_type: MIME type
            metadata: Object metadata

        Returns:
            S3 put_object response

        Raises:
            ClientError: On permanent S3 errors
            RuntimeError: After max retries exhausted
        """
        return self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body.encode('utf-8'),
            ContentType=content_type,
            Metadata=metadata
        )

    def upload_assessment(
        self,
        assessment: Assessment,
        file_format: Literal["json", "markdown"],
        timestamp: datetime = None
    ) -> str:
        """
        Upload assessment file to S3.

        Args:
            assessment: Assessment object to upload
            file_format: 'json' or 'markdown'
            timestamp: Optional timestamp (defaults to now)

        Returns:
            S3 URI (s3://bucket/key)

        Raises:
            ClientError: On permanent S3 errors (AccessDenied, NoSuchBucket)
            RuntimeError: After max retry attempts exhausted
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Generate S3 key
        key = self._generate_s3_key(assessment.level, timestamp, file_format)

        # Prepare content and metadata
        content, content_type = self._prepare_assessment_content(assessment, file_format)
        metadata = self._generate_metadata(assessment, file_format)

        # Upload to S3 with retry logic
        try:
            self._upload_with_retry(key, content, content_type, metadata)
            s3_uri = self._format_s3_uri(key)
            print(f"✓ Uploaded assessment to S3: {s3_uri}")
            return s3_uri

        except Exception as e:
            print(f"✗ Failed to upload assessment to S3: {e}")
            raise

    def upload_multiple_assessments(
        self,
        assessments: List[Assessment],
        formats: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Upload multiple assessments concurrently using ThreadPoolExecutor.

        Args:
            assessments: List of Assessment objects to upload
            formats: List of formats to upload (default: ["json", "markdown"])

        Returns:
            Dict mapping assessment level to list of S3 URIs

        Example:
            {
                'level_1': ['s3://bucket/.../level_1_...json', 's3://bucket/.../level_1_...md'],
                'level_2': ['s3://bucket/.../level_2_...json', 's3://bucket/.../level_2_...md'],
            }
        """
        if formats is None:
            formats = ["json", "markdown"]

        results = {}
        timestamp = datetime.now()

        # Use ThreadPoolExecutor for concurrent uploads (max 5 workers)
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all upload tasks
            future_to_assessment = {}
            for assessment in assessments:
                for fmt in formats:
                    future = executor.submit(
                        self.upload_assessment,
                        assessment,
                        fmt,
                        timestamp
                    )
                    future_to_assessment[future] = (assessment.level, fmt)

            # Collect results as they complete
            for future in as_completed(future_to_assessment):
                level, fmt = future_to_assessment[future]
                key = f"level_{level}"

                try:
                    s3_uri = future.result()
                    if key not in results:
                        results[key] = []
                    results[key].append(s3_uri)
                except Exception as e:
                    print(f"✗ Upload failed for level {level} ({fmt}): {e}")
                    # Continue with other uploads

        return results

    def verify_bucket_access(self) -> bool:
        """
        Verify S3 bucket exists and is accessible.

        Returns:
            True if bucket is accessible, False otherwise
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"✗ S3 bucket access check failed ({error_code}): {e}")
            return False


# =============================================================================
# Tool Function for Subagents
# =============================================================================

def upload_assessment_to_s3(assessment_json: str, level: int) -> dict:
    """
    Upload assessment to S3 in both JSON and markdown formats (tool function for subagents).

    Args:
        assessment_json: Complete assessment as JSON string
        level: Literacy level (1-4)

    Returns:
        Dict with status, s3_uris (JSON and markdown), and upload details

    Example:
        result = upload_assessment_to_s3(assessment_json, level=2)
        # Returns: {
        #   "status": "success",
        #   "s3_uri_json": "s3://bucket/path/level_2_20251106_120000.json",
        #   "s3_uri_markdown": "s3://bucket/path/level_2_20251106_120000.md",
        #   "level": 2,
        #   "timestamp": "2025-11-06T12:00:00"
        # }
    """
    try:
        # Parse assessment JSON
        assessment_dict = json.loads(assessment_json)
        assessment = Assessment(**assessment_dict)

        # Initialize S3 uploader
        uploader = S3UploaderClient()

        # Upload both JSON and markdown formats with same timestamp
        timestamp = datetime.now()
        s3_uri_json = uploader.upload_assessment(assessment, "json", timestamp)
        s3_uri_markdown = uploader.upload_assessment(assessment, "markdown", timestamp)

        logger.info(f"Assessment uploaded successfully: JSON={s3_uri_json}, Markdown={s3_uri_markdown}")

        return {
            "status": "success",
            "s3_uri_json": s3_uri_json,
            "s3_uri_markdown": s3_uri_markdown,
            "level": level,
            "timestamp": timestamp.isoformat(),
            "bucket": uploader.bucket_name,
            "prefix": uploader.prefix
        }

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {e}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "level": level
        }

    except Exception as e:
        error_msg = f"S3 upload failed: {e}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "level": level
        }

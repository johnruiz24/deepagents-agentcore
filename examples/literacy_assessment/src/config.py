"""
Configuration management for the Literacy Level Assessment System.

This module handles loading and validating configuration from environment variables,
including AWS Bedrock Knowledge Base IDs and AWS credentials.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class LiteracyAssessmentConfig:
    """
    Configuration for literacy assessment system.

    Manages AWS Bedrock Knowledge Base IDs, AWS credentials, and system settings.
    All values are loaded from environment variables with sensible defaults.
    """

    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-central-1")
    AWS_PROFILE: Optional[str] = os.getenv("AWS_PROFILE", None)  # None in AgentCore (uses IAM roles)

    # Knowledge Base IDs (one per literacy level)
    # These are pre-configured AWS Bedrock Knowledge Bases in eu-central-1
    KB_LEVEL_1_ID: str = os.getenv("KB_LEVEL_1_ID", "QADZTSAPWX")
    KB_LEVEL_2_ID: str = os.getenv("KB_LEVEL_2_ID", "KGGD2PTQ2N")
    KB_LEVEL_3_ID: str = os.getenv("KB_LEVEL_3_ID", "7MGFSODDVI")
    KB_LEVEL_4_ID: str = os.getenv("KB_LEVEL_4_ID", "CHYWO1H6OM")  # Level 4 Expert KB

    # Assessment Configuration
    ASSESSMENT_TIMEOUT: int = int(os.getenv("ASSESSMENT_TIMEOUT", "60"))  # seconds
    KB_MAX_RESULTS: int = int(os.getenv("KB_MAX_RESULTS", "10"))  # results per query
    MIN_MODULES_COVERED: int = int(os.getenv("MIN_MODULES_COVERED", "5"))  # minimum modules

    # Bedrock API Timeout Configuration (for boto3 client)
    # Increased from default 60s to handle KB queries + question generation
    BEDROCK_READ_TIMEOUT: int = int(os.getenv("BEDROCK_READ_TIMEOUT", "300"))  # 5 minutes
    BEDROCK_CONNECT_TIMEOUT: int = int(os.getenv("BEDROCK_CONNECT_TIMEOUT", "60"))  # 60 seconds

    # LLM Configuration
    # Using AWS Bedrock model IDs (EU region)
    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "8192"))  # Increased from 4096 to allow full assessment generation

    # Fast model for simple tasks (EU region)
    LLM_FAST_MODEL_ID: str = os.getenv("LLM_FAST_MODEL_ID", "eu.anthropic.claude-haiku-4-5-20251001-v1:0")

    # Fallback models (to avoid throttling)
    # Sonnet 4 fallback (for regular/hard/complex questions)
    LLM_FALLBACK_MODEL_ID: str = os.getenv("LLM_FALLBACK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")

    # Claude 3.7 Sonnet fallback (for simple questions)
    LLM_FALLBACK_FAST_MODEL_ID: str = os.getenv("LLM_FALLBACK_FAST_MODEL_ID", "eu.anthropic.claude-3-7-sonnet-20250219-v1:0")

    # S3 Upload Configuration
    S3_BUCKET_NAME: str = os.getenv(
        "S3_BUCKET_NAME",
        "literacy-framework-development-961105418118-eu-central-1"
    )
    S3_PREFIX: str = os.getenv("S3_PREFIX", "learning_path/assessments")
    S3_REGION: str = os.getenv("S3_REGION", AWS_REGION)  # Inherit from AWS_REGION
    ENABLE_S3_UPLOAD: bool = os.getenv("ENABLE_S3_UPLOAD", "true").lower() == "true"

    @classmethod
    def get_kb_id(cls, level: int) -> str:
        """
        Get knowledge base ID for specified literacy level.

        Args:
            level: Literacy level (1-4)

        Returns:
            Knowledge base ID string

        Raises:
            ValueError: If level is not 1-4 or KB ID not configured
        """
        if level not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid literacy level: {level}. Must be 1-4.")

        kb_map: Dict[int, str] = {
            1: cls.KB_LEVEL_1_ID,
            2: cls.KB_LEVEL_2_ID,
            3: cls.KB_LEVEL_3_ID,
            4: cls.KB_LEVEL_4_ID,
        }

        kb_id = kb_map.get(level)
        if not kb_id:
            raise ValueError(f"Knowledge base ID not configured for level {level}")

        return kb_id

    @classmethod
    def get_all_kb_ids(cls) -> Dict[int, str]:
        """
        Get all knowledge base IDs as a dictionary.

        Returns:
            Dict mapping level (1-4) to KB ID
        """
        return {
            1: cls.KB_LEVEL_1_ID,
            2: cls.KB_LEVEL_2_ID,
            3: cls.KB_LEVEL_3_ID,
            4: cls.KB_LEVEL_4_ID,
        }

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            True if all required config present, False otherwise
        """
        required_ids = [
            cls.KB_LEVEL_1_ID,
            cls.KB_LEVEL_2_ID,
            cls.KB_LEVEL_3_ID,
            cls.KB_LEVEL_4_ID,
        ]

        # Check all KB IDs are non-empty
        if not all(required_ids):
            return False

        # Check AWS region and profile are set
        if not cls.AWS_REGION or not cls.AWS_PROFILE:
            return False

        return True

    @classmethod
    def validate_s3_config(cls) -> bool:
        """
        Validate S3 bucket is accessible.

        Returns:
            True if bucket accessible and writable, False otherwise
        """
        import boto3
        from botocore.exceptions import ClientError

        try:
            # Create boto3 session (with profile if specified, otherwise uses IAM role)
            if cls.AWS_PROFILE:
                session = boto3.Session(
                    profile_name=cls.AWS_PROFILE,
                    region_name=cls.S3_REGION
                )
            else:
                session = boto3.Session(region_name=cls.S3_REGION)
            s3_client = session.client('s3')

            # Check if bucket exists (HeadBucket)
            s3_client.head_bucket(Bucket=cls.S3_BUCKET_NAME)

            # Test write permission with a test object
            test_key = f"{cls.S3_PREFIX}/.test_access"
            s3_client.put_object(
                Bucket=cls.S3_BUCKET_NAME,
                Key=test_key,
                Body=b'test'
            )

            # Clean up test object
            s3_client.delete_object(
                Bucket=cls.S3_BUCKET_NAME,
                Key=test_key
            )

            return True

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"S3 validation failed ({error_code}): {e}")
            return False
        except Exception as e:
            print(f"S3 validation error: {e}")
            return False

    @classmethod
    def get_config_summary(cls) -> Dict[str, any]:
        """
        Get a summary of current configuration for display/debugging.

        Returns:
            Dict containing configuration summary
        """
        return {
            "aws_region": cls.AWS_REGION,
            "aws_profile": cls.AWS_PROFILE,
            "knowledge_bases": {
                "level_1": cls.KB_LEVEL_1_ID,
                "level_2": cls.KB_LEVEL_2_ID,
                "level_3": cls.KB_LEVEL_3_ID,
                "level_4": cls.KB_LEVEL_4_ID,
            },
            "s3": {
                "bucket_name": cls.S3_BUCKET_NAME,
                "prefix": cls.S3_PREFIX,
                "region": cls.S3_REGION,
                "upload_enabled": cls.ENABLE_S3_UPLOAD,
            },
            "settings": {
                "assessment_timeout": cls.ASSESSMENT_TIMEOUT,
                "kb_max_results": cls.KB_MAX_RESULTS,
                "min_modules_covered": cls.MIN_MODULES_COVERED,
                "llm_model_id": cls.LLM_MODEL_ID,
            },
            "validation": {
                "all_kb_ids_configured": cls.validate(),
            }
        }

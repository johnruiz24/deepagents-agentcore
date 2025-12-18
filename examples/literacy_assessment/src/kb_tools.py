"""
AWS Bedrock Knowledge Base tools for retrieving curriculum content.

This module provides functions and classes for querying AWS Bedrock Knowledge Bases
to retrieve curriculum content for assessment generation.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional
import json

from examples.literacy_assessment.src.config import LiteracyAssessmentConfig


class KnowledgeBaseClient:
    """
    Client for interacting with AWS Bedrock Knowledge Bases.

    Handles authentication, querying, and error handling for KB operations.
    """

    def __init__(
        self,
        knowledge_base_id: str,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None
    ):
        """
        Initialize KB client with AWS credentials.

        Args:
            knowledge_base_id: AWS Bedrock Knowledge Base ID
            region_name: AWS region (defaults to config)
            profile_name: AWS profile name (defaults to config)
        """
        self.kb_id = knowledge_base_id
        self.region = region_name or LiteracyAssessmentConfig.AWS_REGION
        self.profile = profile_name or LiteracyAssessmentConfig.AWS_PROFILE

        # Create boto3 session (with profile if specified, otherwise uses IAM role)
        if self.profile:
            session = boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
        else:
            session = boto3.Session(region_name=self.region)

        # Initialize bedrock-agent-runtime client for retrieval
        self.client = session.client('bedrock-agent-runtime')

    def query(
        self,
        query_text: str,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Query the knowledge base for relevant content.

        Args:
            query_text: Natural language query
            max_results: Maximum number of results to return (defaults to config)

        Returns:
            List of retrieval results with content and metadata

        Raises:
            ClientError: If KB access fails
        """
        max_results = max_results or LiteracyAssessmentConfig.KB_MAX_RESULTS

        try:
            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={'text': query_text},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )

            return response.get('retrievalResults', [])

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))

            if error_code == 'ResourceNotFoundException':
                raise ValueError(f"Knowledge base not found: {self.kb_id}")
            elif error_code == 'AccessDeniedException':
                raise PermissionError(f"Access denied to knowledge base: {self.kb_id}")
            else:
                raise RuntimeError(f"KB query failed ({error_code}): {error_msg}")

    def extract_content_text(self, results: List[Dict]) -> List[str]:
        """
        Extract text content from retrieval results.

        Args:
            results: Raw retrieval results from query()

        Returns:
            List of content text strings
        """
        content_list = []
        for result in results:
            # Extract text from content field
            content = result.get('content', {}).get('text', '')
            if content.strip():
                content_list.append(content)

        return content_list

    def extract_metadata(self, results: List[Dict]) -> List[Dict]:
        """
        Extract metadata from retrieval results.

        Args:
            results: Raw retrieval results from query()

        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        for result in results:
            metadata = result.get('metadata', {})
            location = result.get('location', {})

            # Combine metadata and location info
            combined = {
                **metadata,
                'location': location
            }
            metadata_list.append(combined)

        return metadata_list


def gather_diverse_content(
    kb_client: KnowledgeBaseClient,
    level: int,
    target_module_count: int = 6
) -> Dict[str, List[Dict]]:
    """
    Query KB multiple times to gather content from diverse modules.

    Uses a multi-query strategy:
    1. Query for curriculum overview to discover modules
    2. Query each module individually for detailed content

    Args:
        kb_client: Initialized KnowledgeBaseClient
        level: Literacy level (1-4)
        target_module_count: Target number of modules to query (default 6 for 5+ coverage buffer)

    Returns:
        Dict mapping module names to content results
    """
    # Step 1: Get curriculum overview
    overview_query = f"List the main modules, courses, and topics in Level {level} literacy curriculum"
    overview_results = kb_client.query(overview_query, max_results=8)

    # Step 2: Extract module information from overview
    modules = extract_modules_from_overview(overview_results, level)

    # Step 3: Query each module for detailed content
    module_content = {}
    for i, module_name in enumerate(modules[:target_module_count]):
        # Query for specific module content
        module_query = f"Detailed content, concepts, and examples for {module_name} in Level {level} curriculum"
        module_results = kb_client.query(module_query, max_results=3)

        if module_results:
            module_content[module_name] = module_results

    return module_content


def extract_modules_from_overview(
    overview_results: List[Dict],
    level: int
) -> List[str]:
    """
    Extract module/course names from overview query results.

    Args:
        overview_results: Results from curriculum overview query
        level: Literacy level (for default fallback)

    Returns:
        List of module names
    """
    # Extract content text
    content_texts = []
    for result in overview_results:
        text = result.get('content', {}).get('text', '')
        if text.strip():
            content_texts.append(text)

    # Parse module names from content
    # Look for common patterns: "Module X:", "Course X:", numbered/bulleted lists
    modules = []
    for text in content_texts:
        # Try to extract structured module names
        lines = text.split('\n')
        for line in lines:
            line = line.strip()

            # Match patterns like "Module 1:", "Course 01:", etc.
            if any(keyword in line.lower() for keyword in ['module', 'course', 'unit', 'chapter']):
                # Extract the module/course identifier
                # Simple heuristic: take the line up to first colon or period
                module_name = line.split(':')[0].split('.')[0].strip()
                if module_name and len(module_name) < 100:  # Sanity check
                    modules.append(module_name)

    # Deduplicate while preserving order
    seen = set()
    unique_modules = []
    for module in modules:
        if module.lower() not in seen:
            seen.add(module.lower())
            unique_modules.append(module)

    # If we didn't extract enough modules, generate generic names
    if len(unique_modules) < 6:
        # Fallback: Generate generic module names based on level
        for i in range(len(unique_modules), 6):
            unique_modules.append(f"Level {level} Module {i+1}")

    return unique_modules


# Tool functions for each literacy level (used by subagents)

def query_level_1_kb(query: str, max_results: int = 10) -> dict:
    """
    Query Level 1 knowledge base.

    Args:
        query: Natural language query
        max_results: Maximum results to return

    Returns:
        Dict with content, metadata, and document sources
    """
    kb_id = LiteracyAssessmentConfig.get_kb_id(1)
    client = KnowledgeBaseClient(kb_id)

    results = client.query(query, max_results)
    content_texts = client.extract_content_text(results)
    metadata = client.extract_metadata(results)

    # Extract document sources (PDF names, S3 URIs)
    document_sources = []
    for result in results:
        location = result.get('location', {})
        s3_location = location.get('s3Location', {})
        if s3_location:
            uri = s3_location.get('uri', '')
            # Extract filename from S3 URI
            if uri:
                filename = uri.split('/')[-1] if '/' in uri else uri
                document_sources.append({
                    "filename": filename,
                    "s3_uri": uri
                })

    return {
        "level": 1,
        "query": query,
        "content": content_texts,
        "metadata": metadata,
        "document_sources": document_sources,
        "result_count": len(results)
    }


def query_level_2_kb(query: str, max_results: int = 10) -> dict:
    """
    Query Level 2 knowledge base.

    Args:
        query: Natural language query
        max_results: Maximum results to return

    Returns:
        Dict with content, metadata, and document sources
    """
    kb_id = LiteracyAssessmentConfig.get_kb_id(2)
    client = KnowledgeBaseClient(kb_id)

    results = client.query(query, max_results)
    content_texts = client.extract_content_text(results)
    metadata = client.extract_metadata(results)

    # Extract document sources
    document_sources = []
    for result in results:
        location = result.get('location', {})
        s3_location = location.get('s3Location', {})
        if s3_location:
            uri = s3_location.get('uri', '')
            if uri:
                filename = uri.split('/')[-1] if '/' in uri else uri
                document_sources.append({
                    "filename": filename,
                    "s3_uri": uri
                })

    return {
        "level": 2,
        "query": query,
        "content": content_texts,
        "metadata": metadata,
        "document_sources": document_sources,
        "result_count": len(results)
    }


def query_level_3_kb(query: str, max_results: int = 10) -> dict:
    """
    Query Level 3 knowledge base.

    Args:
        query: Natural language query
        max_results: Maximum results to return

    Returns:
        Dict with content, metadata, and document sources
    """
    kb_id = LiteracyAssessmentConfig.get_kb_id(3)
    client = KnowledgeBaseClient(kb_id)

    results = client.query(query, max_results)
    content_texts = client.extract_content_text(results)
    metadata = client.extract_metadata(results)

    # Extract document sources
    document_sources = []
    for result in results:
        location = result.get('location', {})
        s3_location = location.get('s3Location', {})
        if s3_location:
            uri = s3_location.get('uri', '')
            if uri:
                filename = uri.split('/')[-1] if '/' in uri else uri
                document_sources.append({
                    "filename": filename,
                    "s3_uri": uri
                })

    return {
        "level": 3,
        "query": query,
        "content": content_texts,
        "metadata": metadata,
        "document_sources": document_sources,
        "result_count": len(results)
    }


def query_level_4_kb(query: str, max_results: int = 10) -> dict:
    """
    Query Level 4 knowledge base.

    Note: Level 4 has its own dedicated expert-level KB (YOUR_LEVEL_4_KB_ID).

    Args:
        query: Natural language query
        max_results: Maximum results to return

    Returns:
        Dict with content, metadata, and document sources
    """
    kb_id = LiteracyAssessmentConfig.get_kb_id(4)
    client = KnowledgeBaseClient(kb_id)

    results = client.query(query, max_results)
    content_texts = client.extract_content_text(results)
    metadata = client.extract_metadata(results)

    # Extract document sources
    document_sources = []
    for result in results:
        location = result.get('location', {})
        s3_location = location.get('s3Location', {})
        if s3_location:
            uri = s3_location.get('uri', '')
            if uri:
                filename = uri.split('/')[-1] if '/' in uri else uri
                document_sources.append({
                    "filename": filename,
                    "s3_uri": uri
                })

    return {
        "level": 4,
        "query": query,
        "content": content_texts,
        "metadata": metadata,
        "document_sources": document_sources,
        "result_count": len(results)
    }


def gather_content_for_assessment(level: int) -> Dict[str, List[Dict]]:
    """
    Gather diverse content for assessment generation.

    High-level function that creates a KB client and gathers content
    from multiple modules for the specified level.

    Args:
        level: Literacy level (1-4)

    Returns:
        Dict mapping module names to content results
    """
    kb_id = LiteracyAssessmentConfig.get_kb_id(level)
    client = KnowledgeBaseClient(kb_id)

    return gather_diverse_content(client, level, target_module_count=6)

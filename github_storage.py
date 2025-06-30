"""
GitHub Storage Module for SMIF Dashboard
Handles private repository storage for Excel files
"""
import base64
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, List
import streamlit as st
from github import Github, GithubException, UnknownObjectException
import io

logger = logging.getLogger(__name__)


class GitHubStorage:
    """
    Manages data storage in a private GitHub repository.
    Provides upload, download, and version history functionality.
    """
    
    def __init__(self, token: str, repo_name: str):
        """
        Initialize GitHub storage client.
        
        Args:
            token: GitHub personal access token with repo scope
            repo_name: Repository name in format "username/repo-name"
        """
        self.token = token
        self.repo_name = repo_name
        self.github = Github(token)
        
        try:
            self.repo = self.github.get_repo(repo_name)
            logger.info(f"Connected to GitHub repository: {repo_name}")
        except Exception as e:
            logger.error(f"Failed to connect to repository {repo_name}: {e}")
            raise
    
    def _ensure_directory_structure(self):
        """Ensure the required directory structure exists in the repo."""
        try:
            # Check if data/current directory exists
            try:
                self.repo.get_contents("data/current")
            except UnknownObjectException:
                # Create directory structure with README files
                self.repo.create_file(
                    "data/current/README.md",
                    "Initialize current data directory",
                    "# Current Data\nThis directory contains the latest uploaded files.",
                    branch="main"
                )
                logger.info("Created data/current directory")
            
            # Check if data/archive directory exists
            try:
                self.repo.get_contents("data/archive")
            except UnknownObjectException:
                self.repo.create_file(
                    "data/archive/README.md",
                    "Initialize archive directory",
                    "# Archive\nThis directory contains historical uploads.",
                    branch="main"
                )
                logger.info("Created data/archive directory")
                
        except Exception as e:
            logger.error(f"Error ensuring directory structure: {e}")
            raise
    
    def upload_files(self, transaction_data: bytes, income_data: bytes, 
                    uploader_email: str) -> bool:
        """
        Upload Excel files to the private repository.
        
        Args:
            transaction_data: Transaction Excel file as bytes
            income_data: Income Excel file as bytes
            uploader_email: Email of the user uploading
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory structure exists
            self._ensure_directory_structure()
            
            # Archive current files if they exist
            self._archive_current_files()
            
            # Prepare file contents
            transaction_content = base64.b64encode(transaction_data).decode('utf-8')
            income_content = base64.b64encode(income_data).decode('utf-8')
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Upload SMIF data - {timestamp}\n\nUploaded by: {uploader_email}"
            
            # Upload transaction file
            transaction_path = "data/current/transaction_data.xlsx"
            try:
                # Try to update existing file
                file = self.repo.get_contents(transaction_path)
                self.repo.update_file(
                    transaction_path,
                    commit_message,
                    transaction_content,
                    file.sha,
                    branch="main"
                )
            except UnknownObjectException:
                # Create new file if it doesn't exist
                self.repo.create_file(
                    transaction_path,
                    commit_message,
                    transaction_content,
                    branch="main"
                )
            
            # Upload income file
            income_path = "data/current/income_data.xlsx"
            try:
                file = self.repo.get_contents(income_path)
                self.repo.update_file(
                    income_path,
                    commit_message,
                    income_content,
                    file.sha,
                    branch="main"
                )
            except UnknownObjectException:
                self.repo.create_file(
                    income_path,
                    commit_message,
                    income_content,
                    branch="main"
                )
            
            # Update metadata
            self._update_metadata(uploader_email, timestamp)
            
            logger.info(f"Successfully uploaded files at {timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
            return False
    
    def download_files(self) -> Tuple[Optional[bytes], Optional[bytes], Optional[Dict]]:
        """
        Download the latest Excel files from the repository.
        
        Returns:
            tuple: (transaction_data, income_data, metadata)
                   Returns (None, None, None) if files don't exist
        """
        try:
            # Download transaction file
            transaction_path = "data/current/transaction_data.xlsx"
            try:
                transaction_file = self.repo.get_contents(transaction_path)
                transaction_data = base64.b64decode(transaction_file.content)
            except UnknownObjectException:
                logger.warning(f"Transaction file not found: {transaction_path}")
                transaction_data = None
            
            # Download income file
            income_path = "data/current/income_data.xlsx"
            try:
                income_file = self.repo.get_contents(income_path)
                income_data = base64.b64decode(income_file.content)
            except UnknownObjectException:
                logger.warning(f"Income file not found: {income_path}")
                income_data = None
            
            # Download metadata
            metadata = self._get_metadata()
            
            if transaction_data and income_data:
                logger.info("Successfully downloaded files from GitHub")
            
            return transaction_data, income_data, metadata
            
        except Exception as e:
            logger.error(f"Error downloading files: {e}")
            return None, None, None
    
    def get_file_history(self, limit: int = 10) -> List[Dict]:
        """
        Get upload history with timestamps and uploaders.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            list: History entries with timestamp, uploader, commit hash
        """
        try:
            history = []
            
            # Get commits for the data/current directory
            commits = self.repo.get_commits(path="data/current")
            
            count = 0
            for commit in commits:
                if count >= limit:
                    break
                    
                # Parse commit message for upload info
                if "Upload SMIF data" in commit.commit.message:
                    lines = commit.commit.message.split('\n')
                    timestamp = lines[0].replace("Upload SMIF data - ", "")
                    uploader = "Unknown"
                    
                    for line in lines:
                        if "Uploaded by:" in line:
                            uploader = line.replace("Uploaded by:", "").strip()
                            break
                    
                    history.append({
                        'timestamp': timestamp,
                        'uploader': uploader,
                        'commit_sha': commit.sha,
                        'commit_date': commit.commit.author.date.isoformat()
                    })
                    count += 1
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting file history: {e}")
            return []
    
    def _archive_current_files(self) -> bool:
        """
        Move current files to archive before uploading new ones.
        
        Returns:
            bool: True if successful or no files to archive
        """
        try:
            # Check if current files exist
            try:
                transaction_file = self.repo.get_contents("data/current/transaction_data.xlsx")
                income_file = self.repo.get_contents("data/current/income_data.xlsx")
            except UnknownObjectException:
                # No files to archive
                return True
            
            # Create archive directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = f"data/archive/{timestamp}"
            
            # Get file contents
            transaction_content = transaction_file.content
            income_content = income_file.content
            
            # Create archived files
            self.repo.create_file(
                f"{archive_dir}/transaction_data.xlsx",
                f"Archive files - {timestamp}",
                transaction_content,
                branch="main"
            )
            
            self.repo.create_file(
                f"{archive_dir}/income_data.xlsx",
                f"Archive files - {timestamp}",
                income_content,
                branch="main"
            )
            
            logger.info(f"Archived current files to {archive_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error archiving files: {e}")
            return False
    
    def _update_metadata(self, uploader_email: str, timestamp: str):
        """Update metadata.json with latest upload information."""
        try:
            metadata = {
                "last_upload": {
                    "timestamp": timestamp,
                    "uploader": uploader_email,
                    "updated_at": datetime.now().isoformat()
                },
                "repository": self.repo_name,
                "version": "1.0"
            }
            
            metadata_content = json.dumps(metadata, indent=2)
            metadata_path = "metadata.json"
            
            try:
                # Update existing file
                file = self.repo.get_contents(metadata_path)
                self.repo.update_file(
                    metadata_path,
                    f"Update metadata - {timestamp}",
                    metadata_content,
                    file.sha,
                    branch="main"
                )
            except UnknownObjectException:
                # Create new file
                self.repo.create_file(
                    metadata_path,
                    f"Create metadata - {timestamp}",
                    metadata_content,
                    branch="main"
                )
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
    
    def _get_metadata(self) -> Optional[Dict]:
        """Get metadata from repository."""
        try:
            metadata_file = self.repo.get_contents("metadata.json")
            metadata_content = base64.b64decode(metadata_file.content).decode('utf-8')
            return json.loads(metadata_content)
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test if the connection to the repository is working.
        
        Returns:
            bool: True if connection is successful
        """
        try:
            # Try to get repository info
            _ = self.repo.full_name
            _ = self.repo.private  # This will fail if no access
            logger.info(f"Successfully connected to {self.repo_name}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Streamlit-specific helper functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_data_from_github(token: str, repo_name: str) -> Tuple[Optional[bytes], Optional[bytes], Optional[Dict]]:
    """
    Get data from GitHub with caching.
    
    Args:
        token: GitHub token
        repo_name: Repository name
        
    Returns:
        tuple: (transaction_data, income_data, metadata)
    """
    try:
        storage = GitHubStorage(token, repo_name)
        return storage.download_files()
    except Exception as e:
        st.error(f"Error connecting to GitHub: {str(e)}")
        return None, None, None


def clear_github_cache():
    """Clear the GitHub data cache."""
    get_cached_data_from_github.clear()
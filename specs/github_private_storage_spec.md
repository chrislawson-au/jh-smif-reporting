# GitHub Private Storage Implementation Specification

## Overview
This specification outlines the implementation of a GitHub-based private storage solution for the SMIF Dashboard to enable persistent data storage while maintaining data privacy and security.

## Problem Statement
- Current Streamlit deployment loses data when the app goes to sleep
- Need persistent storage for Excel files uploaded by administrators
- Data must remain private (financial information)
- Solution must be free or minimal cost
- Must maintain user-friendly interface for non-technical students

## Solution Architecture

### High-Level Design
```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Public GitHub  │     │  Streamlit App   │     │ Private GitHub   │
│  Repository     │────▶│  (Cloud Hosted)  │────▶│  Repository      │
│  (Code Only)    │     │                  │     │  (Data Only)     │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                               │                           │
                               │                           │
                               ▼                           ▼
                        ┌──────────────┐           ┌──────────────┐
                        │   Students   │           │ Excel Files  │
                        │   (Users)    │           │ (.xlsx)      │
                        └──────────────┘           └──────────────┘
```

### Components

1. **Public Repository** (existing)
   - Contains all application code
   - Deployment configuration
   - Documentation
   - NO data files

2. **Private Repository** (new)
   - Stores uploaded Excel files
   - Maintains version history
   - Accessible only via GitHub token
   - Repository name: `smif-private-data` (configurable)

3. **Streamlit Application**
   - Hosted on Streamlit Community Cloud
   - Accesses private repo via GitHub API
   - Caches data in session state
   - Maintains existing authentication

## Implementation Details

### 1. Private Repository Structure
```
smif-private-data/
├── README.md
├── data/
│   ├── current/
│   │   ├── transaction_data.xlsx
│   │   └── income_data.xlsx
│   └── archive/
│       ├── 2024-01-15_120000/
│       │   ├── transaction_data.xlsx
│       │   └── income_data.xlsx
│       └── ...
└── metadata.json
```

### 2. GitHub Storage Module (`github_storage.py`)

```python
class GitHubStorage:
    """
    Handles all interactions with the private GitHub repository
    for data storage and retrieval.
    """
    
    def __init__(self, token: str, repo: str):
        """
        Initialize GitHub storage client.
        
        Args:
            token: GitHub personal access token with repo scope
            repo: Repository name in format "username/repo-name"
        """
        
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
        
    def download_files(self) -> tuple[bytes, bytes, dict]:
        """
        Download the latest Excel files from the repository.
        
        Returns:
            tuple: (transaction_data, income_data, metadata)
        """
        
    def get_file_history(self, limit: int = 10) -> list[dict]:
        """
        Get upload history with timestamps and uploaders.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            list: History entries with timestamp, uploader, commit hash
        """
        
    def archive_current_files(self) -> bool:
        """
        Move current files to archive before uploading new ones.
        
        Returns:
            bool: True if successful
        """
```

### 3. Security Configuration

#### Streamlit Secrets (`.streamlit/secrets.toml`)
```toml
[github]
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"  # Personal access token
DATA_REPO = "username/smif-private-data"   # Private repo name

[emails]
ALLOWED_EMAILS = ["admin1@jhu.edu", "admin2@jhu.edu"]

[passwords]
CLASS_PASSWORD = "secure_password_here"
```

#### Required GitHub Token Permissions
- `repo` scope (full control of private repositories)
- Token should be generated specifically for this application
- Consider using fine-grained personal access tokens for better security

### 4. Integration Points

#### Modified Upload Flow
1. Admin uploads Excel files through Streamlit UI
2. Files are validated (format, size, content)
3. Current files are archived with timestamp
4. New files are uploaded to `data/current/`
5. Metadata is updated with upload info
6. Commit is created with descriptive message
7. Success/failure is reported to user

#### Modified Data Loading Flow
1. On app startup, check for cached data in session state
2. If no cache or cache expired (>1 hour):
   - Download latest files from GitHub
   - Process data as normal
   - Cache in session state
3. Display last update timestamp to users
4. Provide manual refresh button for admins

### 5. Error Handling

- **GitHub API Rate Limits**: Implement exponential backoff
- **Network Failures**: Fall back to cached data with warning
- **Invalid Files**: Validate before upload, show clear errors
- **Token Issues**: Clear error messages without exposing token

### 6. Performance Optimizations

- Use `st.cache_data` for processed data
- Cache GitHub file downloads for 1 hour
- Implement lazy loading for historical data
- Use GitHub's conditional requests (ETags)

## Migration Plan

### Phase 1: Setup (Day 1)
1. Create private GitHub repository
2. Generate personal access token
3. Add secrets to Streamlit Cloud
4. Deploy github_storage.py module

### Phase 2: Integration (Day 2)
1. Modify data upload flow
2. Modify data loading flow
3. Add error handling
4. Test with sample data

### Phase 3: Migration (Day 3)
1. Upload current data to private repo
2. Update production app
3. Monitor for issues
4. Document for administrators

## Benefits

1. **Zero Cost**: GitHub free tier includes unlimited private repos
2. **Data Privacy**: Financial data never exposed publicly
3. **Version Control**: Full history of all uploads
4. **Reliability**: GitHub's infrastructure
5. **Simplicity**: No new services to manage
6. **Familiar Tools**: Uses existing GitHub knowledge

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|---------|------------|
| GitHub API rate limits | App becomes temporarily unavailable | Implement caching and rate limit handling |
| Token exposure | Data breach | Store in Streamlit secrets, never in code |
| Large file sizes | Upload failures | Implement file size limits (50MB) |
| GitHub outage | App cannot access data | Cache last known good data |

## Success Criteria

1. Data persists between Streamlit app restarts
2. Upload/download operations complete in <5 seconds
3. No data exposed in public repository
4. Existing user experience maintained
5. Zero monthly costs
6. Admin audit trail via commit history

## Future Enhancements

1. Automated daily backups to another service
2. Data validation before upload
3. Email notifications for uploads
4. API for external data consumers
5. Automated data archival after semester end

## Appendix

### Alternative Solutions Considered

1. **Firebase**: More complex, potential costs
2. **AWS S3**: Requires AWS account, potential costs
3. **Google Sheets**: File size limitations
4. **Supabase**: Another service to manage
5. **Local SQLite**: No good free hosting with persistent disk

### Decision Matrix

| Solution | Cost | Complexity | Privacy | Persistence | Reliability |
|----------|------|------------|---------|-------------|-------------|
| GitHub Private Repo | Free | Low | High | Permanent | High |
| Firebase | Free tier | Medium | High | Permanent | High |
| AWS S3 | Pay as you go | High | High | Permanent | High |
| Google Sheets | Free | Low | Medium | Permanent | Medium |
| Current (No persistence) | Free | None | High | None | Low |

GitHub Private Repository scored highest on our requirements.
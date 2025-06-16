# SMIF Dashboard Setup Guide

## Quick Setup for Each Semester

### 1. Update Student Email List

Edit `config.py` and add your class roster:

```python
ALLOWED_EMAILS = [
    # Professor/Instructor emails
    "your.email@university.edu",
    
    # Student emails - Add your class roster here
    "student1@university.edu",
    "student2@university.edu", 
    "student3@university.edu",
    # ... add all student emails
]

# Change password each semester
CLASS_PASSWORD = "smif2025spring!"
```

### 2. Deploy to Streamlit Cloud

1. **Update GitHub:**
   ```bash
   git add config.py
   git commit -m "Update class roster for [semester]"
   git push origin main
   ```

2. **Deploy:** App will auto-update on Streamlit Cloud

### 3. Share with Students

**App URL:** `https://your-app.streamlit.app`

**Instructions for students:**
- Use your university email address
- Use class password: `[your class password]`
- Any student can upload Excel files and view results

## Usage Workflow

1. **Students download** brokerage reports from broker portal
2. **Any student uploads** the 2 Excel files via web app
3. **App processes** data automatically 
4. **All students view** interactive dashboard results
5. **Students download** CSV reports as needed

## Security Features

- ✅ Only students with university emails can access
- ✅ Password changes each semester  
- ✅ No permanent file storage (data processed in memory)
- ✅ HTTPS encryption via Streamlit Cloud

## Configuration Options

Edit `config.py` to customize:
- `ALLOWED_EMAILS`: List of permitted email addresses
- `CLASS_PASSWORD`: Access password for the semester
- `APP_TITLE`: Dashboard title
- `INITIAL_PORTFOLIO_VALUE`: Starting portfolio value

## Troubleshooting

**Student can't log in:**
- Check email spelling in `config.py`
- Verify password is correct
- Email must be lowercase in config

**Upload fails:**
- Check Excel file format matches expected columns
- File size limit is 200MB

**Performance issues:**
- Yahoo Finance has rate limits for market data
- Try uploading during off-peak hours
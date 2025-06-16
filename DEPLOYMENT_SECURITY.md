# 🔒 SMIF Dashboard - Secure Deployment Guide

## ⚠️ **CRITICAL SECURITY STEPS**

### **1. Repository Privacy Settings**
**🔐 KEEP REPOSITORY PRIVATE**
- ✅ **Private repo recommended** for production use
- ✅ Contains authentication logic and email management
- ✅ Prevents unauthorized access to codebase
- ❌ **Never make public** with real student emails or passwords

### **2. Sensitive Data Cleanup** ✅ COMPLETED
The following files have been secured:
- ✅ Added comprehensive `.gitignore`
- ✅ Removed real Excel files with portfolio data
- ✅ Removed `config.py` with actual emails/passwords
- ✅ Created `config_template.py` for safe configuration
- ✅ Removed processed data directory

---

## 🚀 **Deployment Steps**

### **Step 1: Configure Your App**
```bash
# Copy template and add your real class information
cp config_template.py config.py

# Edit config.py with your actual:
# - Student email addresses
# - Secure class password
# - App title
```

### **Step 2: Security Review**
✅ **Verify these files are NOT in your repo:**
- `config.py` (your real configuration)
- `*.xlsx` (real portfolio data files)
- `data/` (processed results)
- `.env` files
- Any files with real passwords or emails

### **Step 3: Deploy to Streamlit Cloud**

#### **Option A: Private Repository (Recommended)**
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Secure SMIF dashboard for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your **private** GitHub repository
   - Set main file: `streamlit_app.py`
   - **Important:** Add your real configuration via Streamlit Secrets

3. **Configure Streamlit Secrets:**
   - In Streamlit Cloud app settings
   - Add secrets in TOML format:
   ```toml
   [passwords]
   CLASS_PASSWORD = "your_actual_password"
   
   [emails]
   ALLOWED_EMAILS = [
       "your.email@university.edu",
       "student1@university.edu",
       "student2@university.edu"
   ]
   
   [settings]
   APP_TITLE = "Your Class SMIF Dashboard"
   INITIAL_PORTFOLIO_VALUE = 338400
   ```

#### **Option B: Public Repository (Less Secure)**
If you must use a public repo:
1. **Never commit** real emails or passwords
2. **Use environment variables** for all sensitive data
3. **Add security warnings** in README
4. **Monitor access** regularly

---

## 🔑 **Password Security Best Practices**

### **Strong Password Requirements:**
- ✅ **12+ characters** minimum
- ✅ **Mix of letters, numbers, symbols**
- ✅ **Unique per semester**
- ✅ **Not related to course/university name**

### **Examples:**
- ❌ Bad: `smif2024`, `finance123`, `university`
- ✅ Good: `Qx7!mK9pL2#w`, `3nVest$2024!`, `F1n@nc3_C1@ss!`

### **Password Distribution:**
- ✅ **Share securely** via email or course management system
- ✅ **Change each semester**
- ✅ **Don't include in any documentation**

---

## 👥 **User Management**

### **Adding Students:**
1. **Edit `config.py`** (never commit to GitHub)
2. **Or use Streamlit Secrets** for production
3. **Redeploy app** to update access list

### **Example Configuration:**
```python
ALLOWED_EMAILS = [
    # Instructors
    "prof.smith@university.edu",
    "ta.jones@university.edu",
    
    # Fall 2024 SMIF Class
    "john.doe@university.edu",
    "jane.smith@university.edu",
    "alex.wilson@university.edu",
    # ... continue for all students
]

CLASS_PASSWORD = "Your_Secure_Password_2024!"
```

---

## 🛡️ **Security Features Built-In**

### **Authentication:**
- ✅ **Email-based access control**
- ✅ **University domain verification**
- ✅ **Session management**
- ✅ **Automatic logout**

### **Data Protection:**
- ✅ **No permanent file storage on server**
- ✅ **In-memory processing only**
- ✅ **HTTPS encryption** (via Streamlit Cloud)
- ✅ **No data sharing between deployments**

### **Access Logging:**
- ✅ **Upload tracking** (who uploaded when)
- ✅ **Session state management**
- ✅ **Activity metadata**

---

## 🔍 **Monitoring & Maintenance**

### **Regular Security Tasks:**
1. **Review access logs** monthly
2. **Update student email list** each semester
3. **Change passwords** each semester
4. **Monitor for unauthorized access**
5. **Update dependencies** regularly

### **Semester Transition:**
1. **Clear saved data** (use "Clear Saved Data" button)
2. **Update email list** with new students
3. **Change password**
4. **Test with new class**

---

## 🆘 **Security Incident Response**

### **If Password is Compromised:**
1. **Immediately change** `CLASS_PASSWORD` in config
2. **Redeploy app** to update
3. **Clear all saved data**
4. **Notify students** of new password
5. **Review access logs**

### **If Email List is Exposed:**
1. **Rotate password** immediately
2. **Review who had access**
3. **Consider new email requirements**
4. **Update configuration**

---

## ✅ **Pre-Deployment Checklist**

### **Security Review:**
- [ ] Repository is private
- [ ] No real emails in committed files
- [ ] No passwords in committed files
- [ ] `.gitignore` properly configured
- [ ] Real Excel files removed
- [ ] Processed data directory removed

### **Configuration:**
- [ ] `config.py` created with real class info
- [ ] Strong password selected
- [ ] All student emails added
- [ ] App title customized

### **Testing:**
- [ ] Local testing completed
- [ ] Authentication working
- [ ] File upload/processing working
- [ ] Export features tested
- [ ] Data persistence working

### **Deployment:**
- [ ] Streamlit Cloud account ready
- [ ] Repository connected
- [ ] Secrets configured (if using)
- [ ] App deployed successfully
- [ ] URL shared with students

---

## 📋 **Student Instructions Template**

```
SMIF Dashboard Access Instructions

1. Visit: https://your-app.streamlit.app
2. Login with:
   - Email: [your university email]
   - Password: [provided separately]

3. Upload Excel files from broker
4. View analysis and export data
5. Use Jupyter templates for advanced analysis

Security: Never share login credentials.
Support: Contact [instructor email] for issues.
```

---

Your app is now ready for secure deployment! The key is keeping the repository private and managing credentials properly.
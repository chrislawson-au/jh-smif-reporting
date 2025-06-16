# 📊 SMIF Performance Dashboard

A comprehensive web-based portfolio analysis tool for Student-Managed Investment Funds (SMIF) with Jupyter/Colab integration.

## 🎯 Features

- **📈 Web Dashboard**: Interactive portfolio performance analysis
- **🔒 Secure Authentication**: Email-based access control
- **💾 Data Persistence**: Results saved between sessions
- **📊 Multi-Format Export**: Excel, CSV, JSON, Python pickle
- **🐍 Jupyter Integration**: Pre-built analysis notebooks
- **🔬 Google Colab Support**: Cloud-based advanced analysis
- **📱 Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### For Instructors (First-Time Setup)

1. **Clone and Configure:**
   ```bash
   git clone [your-repo-url]
   cd jh-smif-reporting
   cp config_template.py config.py
   # Edit config.py with your class emails and password
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```

3. **Streamlit Cloud Setup:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your **private** GitHub repository
   - Set main file: `streamlit_app.py`
   - Deploy and share URL with students

### For Students

1. **Access Dashboard:** Visit your class dashboard URL
2. **Login:** Use your university email + class password
3. **Upload Data:** Upload Excel files from brokerage account
4. **Analyze:** View interactive charts and performance metrics
5. **Export:** Download data for advanced analysis in Jupyter/Excel

## 📋 Requirements

- Python 3.8+
- University email addresses for access control
- Excel files from brokerage account:
  - `Investment_Transaction_Detail_-_Customizable.xlsx`
  - `Income_and_Expense_Detail_Base_by_Account.xlsx`

## 🔒 Security

- ✅ **Private Repository Recommended**
- ✅ **Email-based Access Control**
- ✅ **No Permanent Data Storage**
- ✅ **HTTPS Encryption** (via Streamlit Cloud)
- ✅ **Session Management**

⚠️ **IMPORTANT**: Never commit real student emails, passwords, or portfolio data to GitHub.

## 📚 Documentation

- **[Deployment Security Guide](DEPLOYMENT_SECURITY.md)** - Secure setup instructions
- **[Integration Guide](INTEGRATION_GUIDE.md)** - Jupyter/Colab usage
- **[Setup Guide](SETUP_GUIDE.md)** - Semester configuration
- **[CLAUDE.md](CLAUDE.md)** - Technical architecture

## 🛠️ Advanced Analysis

### Jupyter Notebook Integration
1. Download Jupyter template from dashboard
2. Export data as pickle file
3. Upload both to Jupyter environment
4. Run advanced portfolio analysis

### Google Colab Integration
1. Copy setup code from dashboard
2. Upload data file to Colab
3. Run pre-built analysis functions
4. Extend with custom analysis

## 📊 Data Exports

- **📗 Excel Workbook**: Multi-sheet analysis file
- **📦 CSV Package**: Separate files for each dataset
- **🥒 Python Pickle**: Direct Python objects
- **📄 JSON**: Structured data for APIs

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create configuration
cp config_template.py config.py
# Edit config.py with test data

# Run locally
streamlit run streamlit_app.py
```

## 📈 Architecture

- **Frontend**: Streamlit web application
- **Data Processing**: Pandas, NumPy for analysis
- **Market Data**: Yahoo Finance API
- **Statistics**: Statsmodels for regression analysis
- **Persistence**: Local file system with JSON/pickle
- **Authentication**: Email validation with session management

## 🆘 Support

- **Security Issues**: See [DEPLOYMENT_SECURITY.md](DEPLOYMENT_SECURITY.md)
- **Technical Issues**: Check [CLAUDE.md](CLAUDE.md) for architecture
- **Integration Help**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

## 📄 License

Educational use only. Not for commercial distribution.

---

**Built for academic portfolio management education** 🎓
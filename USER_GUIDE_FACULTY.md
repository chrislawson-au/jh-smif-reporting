# SMIF Dashboard - Faculty & Teaching Staff Guide

## Overview

The SMIF (Student-Managed Investment Fund) Dashboard is a web-based analytics platform that transforms brokerage transaction data into comprehensive performance reports. This guide helps faculty and teaching staff understand, manage, and integrate the dashboard into their curriculum.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Dashboard Features](#dashboard-features)
3. [Class Management](#class-management)
4. [Educational Integration](#educational-integration)
5. [Data Security](#data-security)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Accessing the Dashboard
- **URL**: `https://[your-app-name].streamlit.app`
- **Login**: Use your university email + class password
- **Requirements**: Any modern web browser, internet connection

### First Time Setup
1. **Student Access**: Provide students with:
   - Dashboard URL
   - Their university email addresses (must be pre-authorized)
   - Class password (distribute securely)

2. **Data Upload**: Any authorized user can upload Excel files:
   - Investment Transaction Detail (from brokerage)
   - Income and Expense Detail (from brokerage)

---

## Dashboard Features

### 📊 Performance Analytics
- **Benchmark Comparison**: SMIF portfolio vs VTI (total stock market)
- **Key Metrics**: Annual returns, volatility, Sharpe ratio, maximum drawdown
- **Regression Analysis**: Alpha and beta calculations with statistical significance
- **Visual Charts**: Interactive performance charts and scatter plots

### 🥧 Portfolio Analysis
- **Current Allocation**: Pie charts and detailed breakdowns
- **Position Tracking**: Real-time market values and weights
- **Historical Performance**: Cumulative returns over time
- **Risk Assessment**: Drawdown analysis and volatility measures

### 📈 Data Export Capabilities
- **Excel Workbooks**: Complete analysis in spreadsheet format
- **CSV Packages**: Individual datasets for further analysis
- **Jupyter Integration**: Pre-built notebooks for advanced analysis
- **JSON/Pickle**: Raw data for custom programming projects

### 🔄 Real-Time Processing
- **Instant Analysis**: Reports generated immediately after upload
- **Market Data**: Live pricing from Yahoo Finance
- **Split Adjustments**: Automatic handling of stock splits
- **No Storage**: Data processed in memory only (privacy-focused)

---

## Class Management

### Student Access Control

#### Adding Students
1. Contact your IT administrator or dashboard maintainer
2. Provide list of student university email addresses
3. Students gain immediate access once emails are added
4. No individual account creation required

#### Removing Students
- Remove email addresses from authorization list
- Changes take effect immediately
- Students lose access at next login attempt

#### Password Management
- **Change Each Semester**: Recommend updating class password for security
- **Distribution**: Share password securely (email, LMS, in-person)
- **Strength**: Use complex passwords (8+ characters, mixed case, numbers, symbols)

### Class Workflow Recommendations

#### Option 1: Instructor-Led Analysis
1. **Instructor uploads** brokerage files during class
2. **Live demonstration** of dashboard features
3. **Class discussion** of results and implications
4. **Students access** same data independently for assignments

#### Option 2: Student-Led Analysis
1. **Designated students** upload new data weekly/monthly
2. **Rotating responsibility** for data updates
3. **Peer presentation** of findings to class
4. **Collaborative analysis** and discussion

#### Option 3: Assignment-Based
1. **Students access** pre-uploaded data
2. **Individual analysis** using export features
3. **Research projects** using Jupyter notebooks
4. **Comparative studies** across time periods

---

## Educational Integration

### Learning Objectives Supported

#### Finance Concepts
- **Portfolio Performance**: Understanding returns, risk, and benchmarking
- **Risk Management**: Volatility, drawdowns, and risk-adjusted returns
- **Asset Allocation**: Diversification and portfolio construction
- **Market Analysis**: Alpha, beta, and factor analysis

#### Quantitative Skills
- **Statistical Analysis**: Regression, correlation, hypothesis testing
- **Data Visualization**: Chart interpretation and presentation
- **Excel Proficiency**: Advanced spreadsheet analysis
- **Programming**: Python/Jupyter for advanced students

### Assignment Ideas

#### Basic Assignments
1. **Performance Report**: Compare SMIF vs benchmark over specific period
2. **Risk Analysis**: Calculate and interpret risk metrics
3. **Allocation Review**: Analyze current portfolio composition
4. **Recommendation Report**: Suggest portfolio improvements

#### Advanced Projects
1. **Factor Analysis**: Identify sources of alpha using exported data
2. **Optimization Study**: Propose alternative allocations
3. **Peer Comparison**: Compare with other student investment funds
4. **Research Project**: Custom analysis using Jupyter notebooks

#### Group Projects
1. **Investment Committee**: Rotating roles analyzing performance
2. **Presentation Series**: Students present findings to class
3. **Case Study**: Deep dive into specific time periods or events
4. **Benchmarking**: Compare against multiple indices

### Integration with Curriculum

#### Course Alignment
- **Investments**: Portfolio theory and performance measurement
- **Corporate Finance**: Risk and return concepts
- **Quantitative Methods**: Statistical analysis and regression
- **Capstone**: Real-world application of finance concepts

#### Assessment Opportunities
- **Regular Quizzes**: Based on current portfolio performance
- **Midterm Projects**: Comprehensive performance analysis
- **Final Presentations**: Semester-long portfolio evaluation
- **Peer Evaluations**: Group analysis and recommendations

---

## Data Security

### Privacy Protection
- **No Permanent Storage**: Data processed in memory only
- **Secure Authentication**: Email-based access control
- **HTTPS Encryption**: All data transmission secured
- **No Personal Information**: Only portfolio data analyzed

### Compliance Considerations
- **FERPA**: Student email addresses protected in authorization system
- **University Policies**: Compliant with institutional data governance
- **Brokerage Data**: Treated as educational material, not personal financial data

### Best Practices
1. **Regular Password Updates**: Change class password each semester
2. **Access Reviews**: Periodically review authorized student list
3. **Secure Distribution**: Share passwords through secure channels only
4. **Monitor Usage**: Review dashboard access patterns if available

---

## Troubleshooting

### Common Issues

#### Students Can't Access
- **Check Email**: Verify exact email address is authorized
- **Password Issues**: Confirm correct class password
- **Browser Problems**: Try different browser or clear cache
- **University Network**: Some networks may block external sites

#### Data Upload Problems
- **File Format**: Ensure Excel files (.xlsx) with correct structure
- **File Size**: Large files may timeout (contact IT if persistent)
- **Column Names**: Files must match expected brokerage report format
- **Data Quality**: Ensure transaction dates and amounts are valid

#### Performance Issues
- **Slow Loading**: Yahoo Finance API may have delays
- **Chart Problems**: Try refreshing browser or different device
- **Export Failures**: Check internet connection and file permissions

### Getting Help

#### For Technical Issues
1. **Check Error Messages**: Note exact error text for IT support
2. **Browser Compatibility**: Try Chrome, Firefox, Safari, or Edge
3. **Network Issues**: Test from different internet connection
4. **Device Problems**: Try from different computer or mobile device

#### For Educational Support
1. **Dashboard Features**: Refer to student user guide
2. **Financial Concepts**: Use traditional finance textbooks and resources
3. **Statistical Methods**: Consult quantitative methods resources
4. **Programming Help**: Python/pandas documentation for advanced users

---

## Benefits for Faculty

### Time Savings
- **Automated Analysis**: No manual calculations required
- **Instant Updates**: Real-time performance tracking
- **Ready-Made Reports**: Professional-quality visualizations
- **Export Flexibility**: Data in multiple formats for assignments

### Enhanced Learning
- **Real Data**: Actual student investment performance
- **Visual Learning**: Interactive charts and graphs
- **Hands-On Experience**: Students work with professional tools
- **Current Events**: Connect classroom theory to real market performance

### Professional Development
- **Industry Tools**: Exposure to modern analytics platforms
- **Data Literacy**: Students learn data analysis skills
- **Technology Integration**: Blend traditional finance with modern tools
- **Research Opportunities**: Access to rich dataset for academic research

---

## Support and Resources

### Documentation
- **Student User Guide**: Detailed instructions for student users
- **Quick Reference**: Common tasks and shortcuts
- **Technical Documentation**: For IT support and administrators

### Updates and Maintenance
- **Automatic Updates**: Dashboard updates automatically from code repository
- **Feature Requests**: Contact maintainer for new functionality
- **Bug Reports**: Report issues through appropriate channels

### Community
- **Best Practices**: Share successful integration strategies
- **Lesson Plans**: Collaborate on educational content
- **Assessment Tools**: Develop rubrics and evaluation criteria

---

**Questions or need additional support?** Contact your IT department or the dashboard maintainer for technical assistance.
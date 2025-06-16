# SMIF Dashboard - Student User Guide

## Welcome to the SMIF Performance Dashboard! 📈

This guide will help you navigate and use the Student-Managed Investment Fund (SMIF) dashboard to analyze your portfolio's performance, understand investment concepts, and complete assignments.

## 🚀 Getting Started

### What You Need
- **Dashboard URL**: Provided by your instructor
- **University Email**: Your official university email address
- **Class Password**: Shared by your instructor (keep it secure!)
- **Web Browser**: Chrome, Firefox, Safari, or Edge

### First Login
1. **Open the Dashboard**: Click the link provided by your instructor
2. **Enter Your Email**: Use your full university email address (case-sensitive)
3. **Enter Password**: Type the class password exactly as provided
4. **Click Login**: You should see the main dashboard

> 💡 **Tip**: Bookmark the dashboard URL for easy access throughout the semester!

---

## 📊 Dashboard Overview

When you first log in, you'll see several main sections:

### Navigation Bar
- **Welcome Message**: Shows your email and login status
- **Logout Button**: Click to securely log out

### Data Overview Section
- **Last Updated**: When data was last uploaded
- **Portfolio Positions**: Number of different stocks/investments
- **Uploaded By**: Who uploaded the most recent data
- **File Details**: Information about the Excel files used

### Upload Section
- **File Upload Area**: Where you can upload new Excel files
- **Generate Reports Button**: Processes uploaded data

### Analysis Tabs
- **📊 Performance**: Charts comparing SMIF to market benchmark
- **🥧 Allocation**: Portfolio composition and weights
- **📉 Drawdown**: Risk analysis and loss periods
- **📋 Data**: Export options for further analysis

---

## 📁 Uploading Data

### Required Files
You need two Excel files from your brokerage account:

1. **Investment Transaction Detail File**
   - Shows all buy/sell transactions
   - Usually named something like "Investment_Transaction_Detail_-_Customizable.xlsx"

2. **Income and Expense Detail File**
   - Shows dividends, fees, and other income
   - Usually named something like "Income_and_Expense_Detail_Base_by_Account.xlsx"

### Upload Process
1. **Locate Upload Section**: Scroll to "Upload Files" area
2. **Select Transaction File**: Click first upload button, choose your transaction file
3. **Select Income File**: Click second upload button, choose your income file
4. **Generate Reports**: Click the blue "🚀 Generate Reports" button
5. **Wait for Processing**: You'll see a progress bar - this takes 30-60 seconds
6. **View Results**: New analysis will appear in the tabs below

> ⚠️ **Important**: Files are processed in memory only - they're not permanently stored on any server.

---

## 📈 Understanding the Performance Tab

### Key Metrics (Top Row)
- **SMIF Annual Return**: Your portfolio's yearly return percentage
- **SMIF Volatility**: How much your portfolio value fluctuates (risk measure)
- **SMIF Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Max Drawdown**: Largest peak-to-trough loss (lower is better)

### Performance Chart
- **Blue Line (SMIF)**: Your portfolio's cumulative performance
- **Orange Line (VTI)**: Benchmark (total stock market) performance
- **X-Axis**: Date timeline
- **Y-Axis**: Cumulative return (starting at 1.0 = 100%)

> 📚 **Learning Tip**: If your SMIF line is above VTI, you're outperforming the market!

### Scatter Plot
- **Each Dot**: Represents one day's returns
- **X-Axis**: VTI (market) daily returns
- **Y-Axis**: SMIF daily returns
- **Red Line**: Regression line showing relationship
- **Alpha**: Excess return beyond what market movements explain
- **Beta**: How much your portfolio moves relative to the market
- **R-squared**: How closely your returns follow the market (0-1 scale)

### Key Concepts
- **Alpha > 0**: Portfolio generating excess returns (good!)
- **Beta > 1**: More volatile than market
- **Beta < 1**: Less volatile than market
- **Beta = 1**: Moves exactly with market

---

## 🥧 Understanding the Allocation Tab

### Portfolio Pie Chart
- **Each Slice**: Represents one stock/investment
- **Size**: Proportional to percentage of total portfolio
- **Colors**: Different for each holding
- **Percentages**: Shown as labels on each slice

### Allocation Table
- **Ticker**: Stock symbol (e.g., AAPL, MSFT)
- **Weight**: Percentage of total portfolio
- **Market Value**: Dollar amount invested in each position

### What to Look For
- **Concentration**: Are you too heavily invested in one stock?
- **Diversification**: Do you have a good spread across different companies?
- **Sector Balance**: Are you concentrated in one industry?

> 📚 **Assignment Tip**: Compare your allocation to recommended diversification principles from class!

---

## 📉 Understanding the Drawdown Tab

### Drawdown Chart
- **X-Axis**: Date timeline
- **Y-Axis**: Percentage loss from peak value
- **Blue Line (SMIF)**: Your portfolio's drawdowns
- **Orange Line (VTI)**: Market benchmark drawdowns

### Key Concepts
- **Drawdown**: Temporary loss from a previous high point
- **Recovery**: When the line returns to zero (new high achieved)
- **Maximum Drawdown**: The deepest loss experienced

### What This Tells You
- **Risk Assessment**: How much money you could lose in bad periods
- **Volatility Comparison**: How your risk compares to the overall market
- **Recovery Time**: How long it takes to recover from losses

---

## 📋 Data Export & Advanced Analysis

### Export Options

#### For Excel Analysis
- **📗 Excel Workbook**: Complete dataset with multiple sheets
- **📦 CSV Package**: Individual CSV files in a ZIP folder

#### For Programming Projects
- **🥒 Python Pickle**: Raw data for Jupyter notebooks
- **📄 JSON Data**: Structured data for web applications

### Jupyter Notebook Integration

#### Getting Started with Jupyter
1. **Download Template**: Click "📓 Download Jupyter Notebook Template"
2. **Download Data**: Click "🥒 Download Python Data (Pickle)"
3. **Upload to Jupyter**: Use JupyterHub, Google Colab, or local installation
4. **Run Analysis**: Execute the pre-built code cells

#### Google Colab Option
1. **Copy Code**: From the "Google Colab" tab
2. **Open Colab**: Go to colab.research.google.com
3. **Create Notebook**: Paste the code into a new notebook
4. **Upload Data**: Use the file upload feature in Colab
5. **Run Analysis**: Execute the cells for advanced analytics

### Data Preview
Use the "Quick Data Preview" tabs to:
- **Returns**: See daily return percentages
- **Positions**: View number of shares held
- **Weights**: Check portfolio allocation percentages
- **Summary**: Review portfolio value and costs

---

## 💡 Tips for Success

### Best Practices
1. **Regular Updates**: Upload new data weekly or monthly
2. **Compare Periods**: Look at different time ranges for trends
3. **Document Changes**: Note when major trades were made
4. **Ask Questions**: Use data to generate discussion topics for class

### Common Analysis Tasks

#### For Assignments
- **Performance Comparison**: How does SMIF compare to VTI?
- **Risk Analysis**: What's the risk-return tradeoff?
- **Allocation Review**: Is the portfolio well-diversified?
- **Trend Identification**: Are there patterns over time?

#### For Presentations
- **Export Charts**: Use screenshot tools to capture visualizations
- **Key Metrics**: Focus on the most important numbers
- **Story Telling**: Explain what the data means in plain language
- **Recommendations**: Suggest improvements based on analysis

### Academic Applications
- **Research Projects**: Use exported data for detailed analysis
- **Comparative Studies**: Compare different time periods
- **Statistical Analysis**: Calculate additional metrics using raw data
- **Peer Collaboration**: Share insights with classmates

---

## 🆘 Troubleshooting

### Login Issues
**Problem**: "Invalid email or password"
- **Check Email**: Ensure you're using your complete university email
- **Check Password**: Verify you have the correct class password
- **Case Sensitivity**: Email addresses are case-sensitive
- **Clear Browser**: Try clearing browser cache or use incognito mode

**Problem**: "Configuration not found"
- **Demo Mode**: System will show demo login (use demo@university.edu / demo123)
- **Contact Instructor**: This usually means setup isn't complete

### Upload Issues
**Problem**: Upload fails or times out
- **File Format**: Ensure files are .xlsx (Excel format)
- **File Size**: Very large files may timeout
- **Internet Connection**: Check your internet connectivity
- **Try Again**: Sometimes temporary issues resolve on retry

**Problem**: "Error processing data"
- **File Content**: Make sure files have the expected column structure
- **Data Quality**: Check for missing dates or invalid entries
- **File Source**: Ensure files are from the correct brokerage reports

### Performance Issues
**Problem**: Charts not loading
- **Browser Compatibility**: Try a different browser
- **JavaScript**: Ensure JavaScript is enabled
- **Internet Speed**: Slow connections may cause issues
- **Device Performance**: Try on a different device

**Problem**: Data seems incorrect
- **Market Data**: Yahoo Finance occasionally has delays
- **Calculation Errors**: Cross-check with manual calculations
- **Date Ranges**: Verify the time period you're analyzing

### Getting Help
1. **Read Error Messages**: They often contain helpful information
2. **Try Different Browser**: Chrome usually works best
3. **Ask Classmates**: Others may have encountered similar issues
4. **Contact Instructor**: For persistent technical problems
5. **Use Demo Mode**: If login fails, try the demo for practice

---

## 📚 Learning Resources

### Finance Concepts
- **Portfolio Theory**: Understanding risk and return
- **Benchmarking**: Comparing performance to market indices
- **Risk Metrics**: Volatility, Sharpe ratio, drawdowns
- **Alpha and Beta**: Market-relative performance measures

### Technical Skills
- **Excel Analysis**: Using downloaded data for custom calculations
- **Python Programming**: Jupyter notebooks for advanced analysis
- **Data Visualization**: Creating charts and graphs
- **Statistical Analysis**: Regression and correlation concepts

### Assignment Ideas
- **Weekly Reports**: Track and explain weekly performance
- **Sector Analysis**: Examine allocation by industry
- **Risk Assessment**: Evaluate portfolio risk profile
- **Benchmarking Study**: Compare against different indices
- **Optimization Project**: Suggest portfolio improvements

---

## 🎯 Quick Reference

### Common Tasks
- **Login**: URL → Email → Password → Enter
- **Upload**: Files → Both Excel files → Generate Reports
- **Export Data**: Data tab → Choose format → Download
- **View Performance**: Performance tab → Check metrics and charts
- **Check Allocation**: Allocation tab → Review pie chart and table

### Key Numbers to Track
- **Annual Return**: Higher is better
- **Sharpe Ratio**: Higher is better (risk-adjusted return)
- **Maximum Drawdown**: Lower is better (less risk)
- **Alpha**: Positive means outperforming expectations
- **Beta**: Around 1.0 means similar risk to market

### Important Features
- **Real-time Processing**: Data analyzed instantly
- **No Permanent Storage**: Your data isn't saved on servers
- **Export Flexibility**: Multiple formats for different uses
- **Interactive Charts**: Hover for detailed information

---

**Happy analyzing! 📊 Use this dashboard to deepen your understanding of investments and apply classroom concepts to real portfolio performance.**

---

*Questions about the dashboard? Ask your instructor or refer to the troubleshooting section above.*
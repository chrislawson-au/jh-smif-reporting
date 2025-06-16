# SMIF Dashboard - Troubleshooting Guide

## 🔧 Quick Diagnosis

### Is the problem with...?
- **🔐 Login/Access**: [Jump to Login Issues](#login--access-issues)
- **📁 File Upload**: [Jump to Upload Issues](#file-upload-issues)
- **📊 Charts/Display**: [Jump to Display Issues](#charts--display-issues)
- **📉 Data/Calculations**: [Jump to Data Issues](#data--calculation-issues)
- **📱 Mobile/Browser**: [Jump to Browser Issues](#browser--device-issues)

---

## 🔐 Login & Access Issues

### Problem: "Invalid email or password"

**Common Causes:**
- Email address typos or formatting
- Incorrect password
- Case sensitivity issues
- Browser cache problems

**Solutions:**
1. **Double-check email**: Use your complete university email (e.g., `student@university.edu`)
2. **Verify password**: Ensure you have the current class password
3. **Check case sensitivity**: Email addresses are case-sensitive
4. **Clear browser cache**: 
   - Chrome: Ctrl+Shift+Delete → Clear browsing data
   - Firefox: Ctrl+Shift+Delete → Clear recent history
   - Safari: Develop menu → Empty caches
5. **Try incognito/private mode**: Ctrl+Shift+N (Chrome) or Ctrl+Shift+P (Firefox)

**Still not working?**
- Contact your instructor to verify your email is authorized
- Try from a different device or network
- Check if there's a maintenance announcement

---

### Problem: "Configuration not found" or Demo Mode

**What this means:**
The dashboard can't find its configuration settings.

**Immediate solution:**
Use demo credentials to test:
- Email: `demo@university.edu`
- Password: `demo123`

**Long-term fix:**
This usually means the dashboard setup is incomplete. Contact your instructor or IT support.

---

### Problem: Can't access dashboard URL

**Troubleshooting steps:**
1. **Check URL**: Ensure you have the correct web address
2. **Internet connection**: Test with other websites
3. **University network**: Some campus networks block external sites
4. **VPN issues**: Try disconnecting VPN if using one
5. **Firewall**: Check if institutional firewall is blocking access

**Alternative access methods:**
- Try from personal device with mobile data
- Use different network (home, café, library)
- Contact IT to whitelist the dashboard domain

---

## 📁 File Upload Issues

### Problem: "File upload failed" or upload button not working

**File format checklist:**
- ✅ Files must be `.xlsx` (Excel format)
- ✅ Files must be from your brokerage reports
- ❌ Don't use `.xls`, `.csv`, or other formats

**File size issues:**
- Large files (>50MB) may timeout
- Try uploading during off-peak hours
- Check internet connection stability

**Browser-specific fixes:**
1. **Chrome**: Check if file uploads are blocked in settings
2. **Firefox**: Ensure cookies and JavaScript are enabled
3. **Safari**: Try disabling popup blockers
4. **Edge**: Clear browser cache and try again

---

### Problem: "Error processing data" after successful upload

**Data quality issues:**
1. **Column headers**: Ensure Excel files have expected column names
2. **Date formats**: Dates should be in standard format (YYYY-MM-DD or MM/DD/YYYY)
3. **Numeric data**: Amounts should be numbers, not text with symbols
4. **Empty rows**: Remove any completely empty rows

**File structure verification:**
- **Transaction file** should have columns like: Date, Ticker, Shares, Price, Amount
- **Income file** should have columns like: Date, Description, Amount, Account

**Quick fixes:**
1. Re-download files from brokerage
2. Open in Excel and check for obvious errors
3. Try uploading one file at a time to isolate the problem
4. Save files with different names to avoid caching issues

---

### Problem: Upload takes too long or times out

**Network optimization:**
1. **Stable connection**: Use wired connection if possible
2. **Close other tabs**: Reduce bandwidth usage
3. **Optimal timing**: Upload during low-traffic periods
4. **File size**: Consider splitting large date ranges

**Retry strategies:**
- Wait 5 minutes before retrying
- Refresh the page completely
- Try from different device/network
- Upload during off-peak hours (early morning, late evening)

---

## 📊 Charts & Display Issues

### Problem: Charts not loading or appearing blank

**Browser compatibility:**
1. **JavaScript enabled**: Ensure JavaScript is not blocked
2. **Ad blockers**: Temporarily disable ad blockers
3. **Browser updates**: Ensure browser is up-to-date
4. **Compatibility mode**: Disable IE compatibility mode

**Display fixes:**
1. **Refresh page**: Simple F5 or Ctrl+R refresh
2. **Hard refresh**: Ctrl+Shift+R (Chrome) or Cmd+Shift+R (Mac)
3. **Zoom level**: Try different zoom levels (90%, 100%, 110%)
4. **Window size**: Resize browser window

**Alternative browsers to try:**
- Chrome (recommended)
- Firefox
- Safari
- Edge

---

### Problem: Charts show wrong data or outdated information

**Data refresh issues:**
1. **Check last updated**: Look for "Last Updated" date on dashboard
2. **Browser cache**: Clear cache and refresh
3. **Upload timing**: Ensure you clicked "Generate Reports" after upload
4. **Processing time**: Wait for processing to complete (progress bar)

**Verification steps:**
1. **Scroll to top**: Check if upload section shows new files
2. **Data tab**: Verify exported data matches expectations
3. **Comparison**: Cross-check with known values from Excel files

---

### Problem: Performance metrics seem incorrect

**Common calculation issues:**
1. **Date range**: Metrics calculated from first available date
2. **Market data**: Yahoo Finance occasionally has delays or errors
3. **Weekends/holidays**: Returns calculated on business days only
4. **Stock splits**: Automatic adjustments may affect historical data

**Verification methods:**
1. **Export data**: Download Excel file to verify calculations
2. **Manual check**: Compare key dates and values with source files
3. **Benchmark comparison**: VTI data should match market performance
4. **Time period**: Ensure you're analyzing the expected date range

---

## 📉 Data & Calculation Issues

### Problem: Portfolio positions don't match brokerage account

**Common causes:**
1. **Partial data**: Missing recent transactions
2. **Stock splits**: Automatic adjustments may create discrepancies
3. **Date alignment**: Positions calculated as of last business day
4. **Dividend reinvestment**: May affect share counts

**Debugging steps:**
1. **Check dates**: Verify data covers expected time period
2. **Export positions**: Download position data to Excel for analysis
3. **Compare totals**: Check if total portfolio value matches
4. **Recent trades**: Ensure latest transactions are included

---

### Problem: Returns calculations seem wrong

**Calculation methodology:**
- Returns based on daily NAV changes
- Includes dividends and transaction costs
- Compared to VTI total return (includes dividends)
- Annualized using 252 trading days

**Common issues:**
1. **Cash flows**: Large deposits/withdrawals affect returns
2. **Timing**: Returns calculated from first available date
3. **Benchmark**: Ensure comparing to appropriate index
4. **Fees**: Transaction costs included in calculations

**Verification approach:**
1. **Export returns**: Download daily returns data
2. **Spot check**: Verify a few specific dates manually
3. **Cumulative check**: Ensure cumulative returns make sense
4. **Benchmark verification**: Compare VTI returns to external sources

---

## 📱 Browser & Device Issues

### Problem: Dashboard doesn't work on mobile device

**Mobile limitations:**
- File uploads may not work on mobile browsers
- Charts may not display properly on small screens
- Touch interactions limited compared to desktop

**Mobile-friendly alternatives:**
1. **View only**: Use mobile for viewing metrics and charts
2. **Export data**: Download files for offline analysis
3. **Desktop required**: Use desktop/laptop for uploads and detailed analysis

**Mobile troubleshooting:**
1. **Landscape mode**: Rotate device for better chart viewing
2. **Zoom out**: Pinch to zoom out for full dashboard view
3. **Scroll thoroughly**: Some content may be hidden
4. **Browser choice**: Safari (iOS) or Chrome (Android) work best

---

### Problem: Browser crashes or freezes

**Memory management:**
1. **Close other tabs**: Reduce memory usage
2. **Restart browser**: Fresh start often helps
3. **Clear cache**: Remove stored data
4. **Update browser**: Ensure latest version

**System resources:**
- Dashboard requires decent processing power for chart rendering
- Yahoo Finance API calls may be intensive
- Large datasets can consume significant memory

**Alternative solutions:**
1. **Different device**: Try on more powerful computer
2. **Reduce load**: Close unnecessary applications
3. **Wired connection**: More stable than WiFi
4. **Peak hours**: Avoid busy network times

---

## 🔍 Specific Error Messages

### "Yahoo Finance API Error"
**Meaning**: Can't retrieve market data
**Solutions**: 
- Wait 10-15 minutes and try again
- Check if specific tickers are causing issues
- Try during different market hours

### "File format not supported"
**Meaning**: Uploaded file isn't .xlsx format
**Solutions**:
- Save Excel file as .xlsx (not .xls)
- Don't upload CSV or other formats
- Ensure file isn't corrupted

### "Processing timeout"
**Meaning**: Analysis taking too long
**Solutions**:
- Smaller file size (fewer transactions)
- Better internet connection
- Try during off-peak hours

### "Authentication failed"
**Meaning**: Login credentials invalid
**Solutions**:
- Verify email and password
- Check with instructor for access
- Try demo mode to test system

---

## 🆘 When to Get Help

### Try self-help first:
1. **Read error messages carefully**
2. **Check this troubleshooting guide**
3. **Try basic solutions** (refresh, different browser)
4. **Wait and retry** (temporary issues often resolve)

### Contact support when:
- Same error persists after multiple attempts
- Error messages are unclear or technical
- Dashboard features are completely broken
- Authentication issues that can't be resolved

### Information to provide:
1. **Exact error message** (screenshot if possible)
2. **Steps to reproduce** the problem
3. **Browser and device** being used
4. **Time when error occurred**
5. **Whether it worked before** or is first attempt

---

## 🔄 Maintenance & Updates

### Dashboard updates:
- **Automatic**: Updates deploy automatically from code repository
- **No downtime**: Updates usually seamless
- **Feature additions**: New capabilities added regularly

### Planned maintenance:
- Usually announced in advance
- Typically brief (5-15 minutes)
- Access temporarily unavailable

### Emergency fixes:
- May happen without notice
- Usually resolve critical issues quickly
- Temporary workarounds provided when possible

---

## 📚 Additional Resources

### Documentation:
- **User Guide (Students)**: Comprehensive how-to guide
- **User Guide (Faculty)**: Instructor-focused documentation
- **Quick Reference**: Common tasks and shortcuts

### Technical Support:
- **Instructor**: First contact for dashboard issues
- **IT Department**: Technical problems and access issues
- **Classmates**: Peer support and troubleshooting

### External Resources:
- **Browser help**: Chrome/Firefox/Safari support sites
- **Excel help**: Microsoft Office support
- **University IT**: Campus technology support

---

**Remember**: Most issues are temporary and resolve with basic troubleshooting. When in doubt, try the simple solutions first! 🔧✨
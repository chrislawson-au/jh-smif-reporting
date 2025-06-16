# Data Persistence in SMIF Dashboard

## How Data Persistence Works

### ✅ What Gets Saved:
- **Processed portfolio data** (positions, returns, performance metrics)
- **Upload metadata** (who uploaded, when, file names)
- **Portfolio holdings** (ticker symbols, date ranges)
- **All charts and analysis results**

### 📁 Where Data is Stored:
- **Local Development**: `data/` folder in your project
- **Streamlit Cloud**: Persistent storage in the cloud app instance

### 🔄 Data Lifecycle:
1. **Student uploads** Excel files
2. **App processes** data and saves to `data/` folder
3. **All users** can view saved results immediately
4. **Data persists** between app restarts and user sessions
5. **New uploads** overwrite previous data

### 💾 Streamlit Cloud Persistence:
- Data **WILL persist** between user sessions
- Data **WILL persist** when app restarts
- Data **WILL persist** when you redeploy the app
- Data only gets cleared when:
  - User clicks "Clear Saved Data" button
  - You manually delete files from the repository
  - Streamlit Cloud resets (rare, usually with major platform updates)

### 🔐 Security:
- Each deployment has its own isolated data storage
- Data is not shared between different Streamlit apps
- Only users with valid email access can view/upload data

### 📊 What Students See:
- **Current data overview** with last upload info
- **Portfolio holdings** and performance charts
- **Who uploaded** the data and when
- **File details** (names, sizes)
- **Data freshness** indicators

### 🆕 Updating Data:
- Any authorized user can upload new files
- New uploads automatically replace old data
- App shows who uploaded the latest data
- Students can see when data was last refreshed

## Usage Workflow:

1. **Students log in** → See existing data (if any)
2. **Student uploads** new files → Data gets saved
3. **Other students log in** → See the new data immediately
4. **Data remains available** for the entire semester
5. **At semester end** → Clear data for next class
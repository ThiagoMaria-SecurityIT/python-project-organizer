# 🐍 Python Project Organizer

A visual tool to organize and manage your Python projects across multiple folders. Get a complete overview of your project portfolio with health scoring, status tracking, and analytics.

**Note**: This project is designed for a single main folder containing all your Python projects, where each subfolder represents an individual project.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-plastic&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-plastic&logo=python&logoColor=white)  

<img width="1833" height="770" alt="image" src="https://github.com/user-attachments/assets/b8f8fbf6-b82c-4808-8abb-de621d68c359" />


## ✨ Features

### 📊 **Dashboard & Analytics**
- **Project Health Scoring**: Automatic health assessment (0-100) based on project quality
- **Advanced Metrics**: Portfolio overview, completion rates, project statistics
- **Visual Analytics**: Interactive charts and status distribution
- **Project Comparison**: Side-by-side project analysis

### 🗂️ **Project Management**
- **Single Folder Structure**: Designed for one main folder with project subfolders
- **Status Tracking**: Track project status (Development, Complete, Need Fix, etc.)
- **Smart Detection**: Automatically identifies Python projects
- **Bulk Operations**: Update multiple projects simultaneously

### 🎯 **Status System**
- 🟢 **Under Development** - Active development
- 🟡 **Under Update** - Maintenance and updates  
- 🔴 **Need Fix** - Requires bug fixes
- 🟣 **Not Working** - Broken or needs major work
- ⚫ **Dropped** - Abandoned projects
- ✅ **Complete** - Finished projects
- ⚪ **Not Set** - Needs status assignment

## 🚀 Quick Start

### Method 1: One-Click Launcher (Recommended for Windows)
1. Download the project files
2. Double-click `launch.bat`
3. The app opens automatically in your browser at `http://localhost:8501`

### Method 2: Manual Setup
```bash
# Install dependencies
pip install streamlit pandas plotly

# Run the application
streamlit run optimized_project_organizer.py
```

## 📋 Requirements

- Python 3.7+
- Streamlit
- Pandas
- Plotly

## 🏗️ Folder Structure

This tool is designed for this specific folder structure:
```
YourMainProjectsFolder/
├── project_1/                 # Your Python project
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── project_2/                 # Another project
│   ├── app.py
│   └── utils.py
├── data_science_project/      # Data science project
│   ├── analysis.ipynb
│   └── requirements.txt
└── web_app/                   # Web application
    ├── app.py
    ├── templates/
    └── requirements.txt
```

## 🎮 How to Use

### 1. **First Setup**
- Open the app and navigate to the sidebar
- Enter the path to your main projects folder in "Scan folder"
- Example: `C:/Users/YourName/PythonProjects` or `/home/username/MyProjects`

### 2. **Scan Projects**
- Click "🚀 Scan Projects" to analyze your main folder
- The app automatically detects Python projects (subfolders with .py files or requirements.txt)

### 3. **Manage Projects**
- Use the **Dashboard** to see overview and health scores
- Go to **Project Explorer** to update individual project status
- Use **Status Manager** for bulk operations across multiple projects

### 4. **Set Project Status**
For each project, you can:
- Set development status (Under Development, Complete, etc.)
- Add notes and reminders
- Track last modification dates
- Monitor project health scores

## 📊 Health Scoring System

Projects are automatically scored (0-100) based on:

| Factor | Points | Description |
|--------|--------|-------------|
| **Base Score** | 50 | Starting point for all projects |
| **Requirements** | +15 | Has requirements.txt file |
| **README** | +15 | Has README.md documentation |
| **Python Files** | +20 | Number of .py files (capped) |
| **Status Bonus** | ±30 | Based on project status |

**Health Categories:**
- 🟢 **Excellent (80-100)**: Well-maintained projects
- 🟡 **Good (60-79)**: Solid projects with minor issues
- 🟠 **Fair (40-59)**: Needs attention
- 🔴 **Poor (0-39)**: Requires immediate action

## 🗂️ Navigation Guide

### 🏠 Dashboard
- **Overview Tab**: Basic metrics and status distribution
- **Advanced Metrics**: Health scoring and portfolio analytics  
- **Project Comparison**: Compare and prioritize projects

### 📂 Project Explorer
- Browse all projects with filtering and grouping
- Update individual project status and notes
- Group by: Status, Requirements, File Count, Size

### 🎯 Status Manager
- Bulk status updates across multiple projects
- Quick actions and automated workflows
- Status distribution overview

### ⚙️ Settings & Paths
- Manage saved project folders
- Export/import data
- Application configuration

## 💾 Data Management

- **Auto-Save**: All project statuses and notes saved automatically
- **Local Storage**: Data stored in `project_data.json` and `saved_paths.json`
- **Export**: Download your project data as JSON
- **Multiple Sessions**: Your work persists between app restarts

## 🆘 Troubleshooting

### Common Issues

**❌ "Path not found" error**
- Check that your main projects folder path is correct
- Use forward slashes: `C:/Users/Name/Projects` or `C:\\Users\\Name\\Projects`
- Ensure the folder exists and you have read permissions

**❌ No projects detected**
- Ensure your main folder contains subfolders (not loose files)
- Projects need either `.py` files or `requirements.txt` in their subfolder
- Check that subfolders are actual Python projects

**❌ App won't start**
- Ensure Python is installed: `python --version`
- Install required packages: `pip install streamlit pandas plotly`
- Check firewall isn't blocking port 8501

### Example Setup

If your projects are organized like this:
```
C:/
└── Users/
    └── YourName/
        └── PythonProjects/          # ← Your MAIN folder
            ├── web_app/             # Project 1
            ├── data_analysis/       # Project 2  
            ├── machine_learning/    # Project 3
            └── automation_scripts/  # Project 4
```

Enter this path in the app: `C:/Users/YourName/PythonProjects`

## 🚀 What's Next?

- Set up your main projects folder path
- Scan to discover all your projects  
- Start tracking project status and health
- Use the dashboard to prioritize your work

---

**Happy Organizing!** 🐍✨

*Perfect for developers managing multiple Python projects in a single main folder structure.*

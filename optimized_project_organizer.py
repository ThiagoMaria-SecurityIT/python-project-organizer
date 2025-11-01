# optimized_project_organizer.py
import streamlit as st
import pandas as pd
from pathlib import Path
import json
import os
from datetime import datetime
import time
import plotly.express as px  # ADD THIS IMPORT

# Page configuration
st.set_page_config(
    page_title="🐍 Python Project Organizer",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ProjectManager:
    def __init__(self):
        self.data_file = "project_data.json"
        self.saved_paths_file = "saved_paths.json"
        self.load_data()
    
    def load_data(self):
        """Load saved data or initialize empty"""
        try:
            # Load saved paths
            if Path(self.saved_paths_file).exists():
                with open(self.saved_paths_file, 'r') as f:
                    self.saved_paths = json.load(f)
            else:
                self.saved_paths = []
            
            # Load project statuses
            if Path(self.data_file).exists():
                with open(self.data_file, 'r') as f:
                    self.project_data = json.load(f)
            else:
                self.project_data = {}
        except Exception as e:
            st.error(f"Error loading data: {e}")
            self.saved_paths = []
            self.project_data = {}
    
    def save_data(self):
        """Save all data to JSON files"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.project_data, f, indent=2)
            with open(self.saved_paths_file, 'w') as f:
                json.dump(self.saved_paths, f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def add_saved_path(self, path):
        """Add a new path to saved paths"""
        if path and path not in self.saved_paths:
            self.saved_paths.append(path)
            self.save_data()
            return True
        return False
    
    def remove_saved_path(self, path):
        """Remove a path from saved paths"""
        if path in self.saved_paths:
            self.saved_paths.remove(path)
            self.save_data()
            return True
        return False
    
    def update_project_status(self, project_path, status, notes=""):
        """Update status for a project"""
        self.project_data[project_path] = {
            "status": status,
            "notes": notes,
            "last_updated": datetime.now().isoformat()
        }
        self.save_data()
    
    def get_project_status(self, project_path):
        """Get status for a project"""
        return self.project_data.get(project_path, {
            "status": "Not Set",
            "notes": "",
            "last_updated": None
        })
    
    def get_projects_by_status(self):
        """Get counts of projects by status"""
        status_counts = {}
        for project_path, data in self.project_data.items():
            status = data['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
        # Add these methods to the ProjectManager class
    def calculate_project_health(self, project):
        """Calculate project health score (0-100)"""
        score = 50  # Base score
        
        # Positive factors
        if project['has_requirements']:
            score += 15
        if project['has_readme']:
            score += 15
        if project['python_files'] > 0:
            score += min(project['python_files'] * 2, 20)
        
        # Status-based scoring
        status_score = {
            "Complete": 20,
            "Under Development": 10,
            "Under Update": 5,
            "Need Fix": -10,
            "Not Working": -20,
            "Dropped": -30,
            "Not Set": -5
        }
        project_status = self.get_project_status(project['path'])
        score += status_score.get(project_status['status'], 0)
        
        return max(0, min(100, score))

    def get_health_emoji(self, score):
        """Get health indicator emoji"""
        if score >= 80: return "🟢"
        elif score >= 60: return "🟡"
        elif score >= 40: return "🟠"
        else: return "🔴"

    def get_health_description(self, score):
        """Get health description"""
        if score >= 80: return "Excellent"
        elif score >= 60: return "Good"
        elif score >= 40: return "Fair"
        else: return "Poor"

def scan_projects_folder(folder_path):
    """Scan folder for Python projects with error handling and caching"""
    try:
        path = Path(folder_path)
        if not path.exists():
            return None, f"❌ Path not found: {folder_path}"
        
        projects = []
        for item in path.iterdir():
            if item.is_dir():
                # Quick check for Python projects
                try:
                    # Check for common Python project indicators
                    py_files = list(item.glob("*.py"))  # Only root level for speed
                    if not py_files:
                        # Check one level deeper if no .py files in root
                        py_files = list(item.glob("*/*.py"))[:1]  # Limit for performance
                    
                    requirements = (item / "requirements.txt").exists()
                    readme = (item / "README.md").exists()
                    
                    if py_files or requirements:
                        projects.append({
                            'name': item.name,
                            'path': str(item),
                            'python_files': len(py_files),
                            'has_requirements': requirements,
                            'has_readme': readme,
                            'last_modified': datetime.fromtimestamp(
                                item.stat().st_mtime
                            ).strftime("%Y-%m-%d"),
                            'size_mb': round(sum(
                                f.stat().st_size for f in item.glob('*') 
                                if f.is_file()
                            ) / 1024 / 1024, 2)
                        })
                except (PermissionError, OSError):
                    continue  # Skip directories we can't access
        
        return projects, None
        
    except PermissionError:
        return None, f"❌ Permission denied: {folder_path}"
    except Exception as e:
        return None, f"❌ Error scanning path: {str(e)}"

def setup_navigation():
    """Setup the main navigation sidebar"""
    st.sidebar.header("🧭 Navigation")
    
    # Main navigation options
    nav_options = [
        "🏠 Dashboard",
        "📂 Project Explorer", 
        "🎯 Status Manager",
        "⚙️ Settings & Paths"
    ]
    
    selected_nav = st.sidebar.radio("Go to:", nav_options)
    
    # Quick stats in sidebar
    if 'scanned_projects' in st.session_state and st.session_state.scanned_projects:
        projects = st.session_state.scanned_projects
        total_projects = len(projects)
        
        # Calculate some quick stats
        not_set_count = sum(1 for p in projects if st.session_state.pm.get_project_status(p['path'])['status'] == "Not Set")
        health_scores = [st.session_state.pm.calculate_project_health(p) for p in projects]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 Quick Stats")
        st.sidebar.metric("Total Projects", total_projects)
        st.sidebar.metric("Need Status", not_set_count)
        st.sidebar.metric("Avg Health", f"{avg_health:.1f}")
    
    st.sidebar.markdown("---")
    return selected_nav

def setup_quick_actions():
    """Setup quick actions in sidebar"""
    st.sidebar.subheader("🚀 Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Rescan", use_container_width=True):
            st.session_state.force_scan = True
            st.rerun()
    with col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            if 'scanned_projects' in st.session_state:
                del st.session_state.scanned_projects
            st.rerun()
    
    st.sidebar.markdown("---")

def setup_path_management(pm):
    """Setup path management section"""
    st.sidebar.subheader("📁 Project Paths")
    
    # Current path input
    current_path = st.sidebar.text_input(
        "Scan folder:",
        value=st.session_state.get('current_path', ''),
        placeholder="C:/path/to/your/projects",
        key="nav_current_path"
    )
    
    if st.sidebar.button("🚀 Scan Projects", type="primary", use_container_width=True):
        st.session_state.current_path = current_path
        st.session_state.force_scan = True
        st.rerun()
    
    # Quick select from saved paths
    if pm.saved_paths:
        st.sidebar.write("**Quick Select:**")
        selected_saved_path = st.sidebar.selectbox(
            "Saved paths:",
            pm.saved_paths,
            key="saved_path_select",
            label_visibility="collapsed"
        )
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Use", key="use_saved"):
                st.session_state.current_path = selected_saved_path
                st.session_state.force_scan = True
                st.rerun()
        with col2:
            if st.button("Remove", key="remove_saved"):
                pm.remove_saved_path(selected_saved_path)
                st.rerun()

def setup_grouping_filters():
    """Setup grouping and filtering options"""
    st.sidebar.subheader("📊 View Options")
    
    group_by = st.sidebar.selectbox(
        "Group by:",
        ["None", "Status", "Has Requirements", "Python Files Count", "Size"],
        key="group_by"
    )
    
    status_options = ["All", "Not Set", "Under Development", "Under Update", 
                     "Need Fix", "Not Working", "Dropped", "Complete"]
    selected_status = st.sidebar.selectbox(
        "Filter by status:",
        status_options,
        key="status_filter"
    )
    
    st.sidebar.markdown("---")
    return group_by, selected_status

def show_dashboard(pm):
    """Display the enhanced dashboard page"""
    st.header("🏠 Project Dashboard")
    
    if 'current_path' not in st.session_state or not st.session_state.current_path:
        st.info("👆 Please set a project path in the sidebar to get started!")
        return
    
    # Scan projects if needed
    if 'scanned_projects' not in st.session_state or st.session_state.get('force_scan', False):
        with st.spinner("🔄 Scanning projects..."):
            projects, error = scan_projects_folder(st.session_state.current_path)
            if error:
                st.error(error)
                return
            st.session_state.scanned_projects = projects
            st.session_state.force_scan = False
    
    projects = st.session_state.scanned_projects
    
    if not projects:
        st.warning("No Python projects found in the selected folder.")
        return
    
    # Create tabs for different dashboard views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Advanced Metrics", "🔍 Project Comparison"])
    
    with tab1:
        show_basic_overview(pm, projects)
    
    with tab2:
        show_advanced_metrics(pm, projects)
    
    with tab3:
        show_project_comparison(pm, projects)

def show_basic_overview(pm, projects):
    """Show basic overview in the first tab"""
    # Basic metrics
    st.subheader("📈 Basic Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_projects = len(projects)
        st.metric("Total Projects", total_projects)
    with col2:
        total_py_files = sum(p['python_files'] for p in projects)
        st.metric("Python Files", total_py_files)
    with col3:
        with_req = sum(1 for p in projects if p['has_requirements'])
        st.metric("With Requirements", with_req)
    with col4:
        with_readme = sum(1 for p in projects if p['has_readme'])
        st.metric("With README", with_readme)
    with col5:
        not_set_count = sum(1 for p in projects if pm.get_project_status(p['path'])['status'] == "Not Set")
        st.metric("Not Set Status", not_set_count, delta=f"{not_set_count} need attention")
    
    # Status distribution
    st.subheader("🎯 Project Status Distribution")
    
    status_counts = {}
    for project in projects:
        status = pm.get_project_status(project['path'])['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Status Overview:**")
            status_order = ["Not Set", "Under Development", "Under Update", "Need Fix", "Not Working", "Dropped", "Complete"]
            
            for status in status_order:
                count = status_counts.get(status, 0)
                emoji = {
                    "Not Set": "⚪",
                    "Under Development": "🟢", 
                    "Under Update": "🟡",
                    "Need Fix": "🔴",
                    "Not Working": "🟣",
                    "Dropped": "⚫",
                    "Complete": "✅"
                }.get(status, "⚪")
                
                if status == "Not Set" and count > 0:
                    st.warning(f"{emoji} **{status}:** {count} projects")
                else:
                    st.write(f"{emoji} {status}: {count} projects")
        
        with col2:
            if status_counts:
                status_df = pd.DataFrame({
                    'Status': status_order,
                    'Count': [status_counts.get(status, 0) for status in status_order]
                })
                status_df = status_df[status_df['Count'] > 0]
                
                if not status_df.empty:
                    st.bar_chart(status_df.set_index('Status'))
                else:
                    st.info("No status data available")
    
    # Enhanced Projects Table with Health Scores
    st.subheader("📋 All Projects Overview")
    
    # Prepare enhanced data for the table
    table_data = []
    for i, project in enumerate(projects, 1):
        project_status = pm.get_project_status(project['path'])
        health_score = pm.calculate_project_health(project)
        
        table_data.append({
            'Project Number': i,
            'Project Name': project['name'],
            'Health': f"{pm.get_health_emoji(health_score)} {health_score}",
            'Status': project_status['status'],
            'Python Files': project['python_files'],
            'Requirements': '✅' if project['has_requirements'] else '❌',
            'README': '✅' if project['has_readme'] else '❌',
            'Size (MB)': project['size_mb'],
            'Last Modified': project['last_modified'],
            'Notes': project_status['notes'][:50] + "..." if project_status['notes'] and len(project_status['notes']) > 50 else project_status['notes']
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display the enhanced table
    st.dataframe(
        df,
        use_container_width=True,
        height=400,
        column_config={
            'Project Number': st.column_config.NumberColumn('Project Number', width='small'),
            'Project Name': st.column_config.TextColumn('Project Name', width='medium'),
            'Health': st.column_config.TextColumn('Health', width='small'),
            'Status': st.column_config.TextColumn('Status', width='medium'),
            'Python Files': st.column_config.NumberColumn('Python Files', width='small'),
            'Requirements': st.column_config.TextColumn('Req', width='small'),
            'README': st.column_config.TextColumn('README', width='small'),
            'Size (MB)': st.column_config.NumberColumn('Size (MB)', width='small'),
            'Last Modified': st.column_config.TextColumn('Last Modified', width='medium'),
            'Notes': st.column_config.TextColumn('Notes', width='large')
        }
    )
    
    # Summary information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Size", f"{sum(p['size_mb'] for p in projects):.1f} MB")
    with col2:
        avg_files = sum(p['python_files'] for p in projects) / len(projects) if projects else 0
        st.metric("Avg Python Files", f"{avg_files:.1f}")
    with col3:
        projects_with_notes = sum(1 for p in projects if pm.get_project_status(p['path'])['notes'])
        st.metric("Projects with Notes", projects_with_notes)
        
        
def show_advanced_metrics(pm, projects):
    """Show professional metrics and KPIs"""
    st.subheader("📊 Advanced Metrics")
    
    if not projects:
        st.info("No projects to display metrics.")
        return
    
    # Calculate advanced metrics
    total_size_gb = sum(p['size_mb'] for p in projects) / 1024
    health_scores = [pm.calculate_project_health(p) for p in projects]
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
    
    # Count projects by health category
    excellent = len([s for s in health_scores if s >= 80])
    good = len([s for s in health_scores if s >= 60 and s < 80])
    fair = len([s for s in health_scores if s >= 40 and s < 60])
    poor = len([s for s in health_scores if s < 40])
    
    # Stale projects (older than 6 months)
    stale_count = 0
    for project in projects:
        last_modified = datetime.strptime(project['last_modified'], "%Y-%m-%d")
        days_since_mod = (datetime.now() - last_modified).days
        if days_since_mod > 180:  # 6 months
            stale_count += 1
    
    # Completion rate
    completed = len([p for p in projects if pm.get_project_status(p['path'])['status'] == "Complete"])
    completion_rate = (completed / len(projects)) * 100 if projects else 0
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Size", 
            f"{total_size_gb:.2f} GB",
            help="Total size of all projects"
        )
    
    with col2:
        st.metric(
            "Avg Health Score", 
            f"{avg_health:.1f}",
            f"{pm.get_health_emoji(avg_health)} {pm.get_health_description(avg_health)}",
            help="Average health score across all projects"
        )
    
    with col3:
        st.metric(
            "Stale Projects", 
            stale_count,
            delta=f"{stale_count} need review" if stale_count > 0 else None,
            delta_color="inverse" if stale_count > 0 else "normal",
            help="Projects not modified in 6+ months"
        )
    
    with col4:
        st.metric(
            "Completion Rate", 
            f"{completion_rate:.1f}%",
            help="Percentage of projects marked as Complete"
        )
    
    # Health distribution chart
    st.subheader("🏥 Project Health Distribution")
    
    health_data = {
        'Excellent (80-100)': excellent,
        'Good (60-79)': good,
        'Fair (40-59)': fair,
        'Poor (0-39)': poor
    }
    
    # Create two columns for health overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Health distribution bar chart
        health_df = pd.DataFrame({
            'Health Category': list(health_data.keys()),
            'Count': list(health_data.values())
        })
        
        # Create a colored bar chart
        fig = px.bar(
            health_df, 
            x='Health Category', 
            y='Count',
            color='Health Category',
            color_discrete_map={
                'Excellent (80-100)': '#00ff00',
                'Good (60-79)': '#ffff00', 
                'Fair (40-59)': '#ffa500',
                'Poor (0-39)': '#ff0000'
            },
            title="Project Health Distribution"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Health summary
        st.write("**Health Summary:**")
        st.write(f"🟢 Excellent: {excellent} projects")
        st.write(f"🟡 Good: {good} projects")
        st.write(f"🟠 Fair: {fair} projects")
        st.write(f"🔴 Poor: {poor} projects")
        
        # Overall health indicator
        st.markdown("---")
        st.write("**Overall Portfolio Health:**")
        overall_health = pm.get_health_description(avg_health)
        overall_emoji = pm.get_health_emoji(avg_health)
        st.markdown(f"### {overall_emoji} {overall_health}")
        st.progress(avg_health / 100)

def show_project_comparison(pm, projects):
    """Show project comparison for decision making"""
    st.subheader("📈 Project Comparison")
    
    if not projects:
        st.info("No projects to compare.")
        return
    
    # Let user select projects to compare
    project_names = [p['name'] for p in projects]
    selected_projects = st.multiselect(
        "Select projects to compare:",
        project_names,
        default=project_names[:min(5, len(project_names))],
        key="project_comparison"
    )
    
    if selected_projects:
        # Create comparison data
        comparison_data = []
        for project_name in selected_projects:
            project = next((p for p in projects if p['name'] == project_name), None)
            if project:
                health = pm.calculate_project_health(project)
                status = pm.get_project_status(project['path'])
                last_modified = datetime.strptime(project['last_modified'], "%Y-%m-%d")
                days_since_mod = (datetime.now() - last_modified).days
                
                comparison_data.append({
                    'Project': project['name'],
                    'Health Score': health,
                    'Health': f"{pm.get_health_emoji(health)} {health}",
                    'Status': status['status'],
                    'Python Files': project['python_files'],
                    'Requirements': '✅' if project['has_requirements'] else '❌',
                    'README': '✅' if project['has_readme'] else '❌',
                    'Size (MB)': project['size_mb'],
                    'Days Since Modified': days_since_mod,
                    'Last Updated': project['last_modified']
                })
        
        df = pd.DataFrame(comparison_data)
        
        # Display comparison table with styling
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                'Project': st.column_config.TextColumn('Project', width='medium'),
                'Health Score': st.column_config.NumberColumn('Health', width='small'),
                'Health': st.column_config.TextColumn('Health', width='small'),
                'Status': st.column_config.TextColumn('Status', width='medium'),
                'Python Files': st.column_config.NumberColumn('Files', width='small'),
                'Requirements': st.column_config.TextColumn('Req', width='small'),
                'README': st.column_config.TextColumn('README', width='small'),
                'Size (MB)': st.column_config.NumberColumn('Size', width='small'),
                'Days Since Modified': st.column_config.NumberColumn('Days Old', width='small'),
                'Last Updated': st.column_config.TextColumn('Last Updated', width='medium')
            }
        )
        
        # Add some insights
        st.subheader("💡 Comparison Insights")
        
        # Find best and worst health
        if comparison_data:
            best_project = max(comparison_data, key=lambda x: x['Health Score'])
            worst_project = min(comparison_data, key=lambda x: x['Health Score'])
            oldest_project = max(comparison_data, key=lambda x: x['Days Since Modified'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Best Health", 
                    best_project['Project'],
                    f"Score: {best_project['Health Score']}"
                )
            
            with col2:
                st.metric(
                    "Needs Most Attention", 
                    worst_project['Project'],
                    f"Score: {worst_project['Health Score']}",
                    delta_color="inverse"
                )
            
            with col3:
                st.metric(
                    "Most Stale", 
                    oldest_project['Project'],
                    f"{oldest_project['Days Since Modified']} days old",
                    delta_color="inverse"
                )


def get_status_emoji(status):
    """Helper function to get status emoji"""
    status_emojis = {
        "Not Set": "⚪",
        "Under Development": "🟢",
        "Under Update": "🟡",
        "Need Fix": "🔴",
        "Not Working": "🟣",
        "Dropped": "⚫",
        "Complete": "✅"
    }
    return status_emojis.get(status, "⚪")

def display_project_card(project, pm, index):
    """Display a single project card with optimized form handling"""
    project_status = pm.get_project_status(project['path'])
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Project header with emoji based on status
            status_emoji = {
                "Not Set": "⚪",
                "Under Development": "🟢",
                "Under Update": "🟡",
                "Need Fix": "🔴",
                "Not Working": "🟣",
                "Dropped": "⚫",
                "Complete": "✅"
            }.get(project_status['status'], "⚪")
            
            st.write(f"### {status_emoji} {project['name']}")
            st.write(f"**Path:** `{project['path']}`")
            st.write(f"**Python Files:** {project['python_files']} | "
                    f"**Last Modified:** {project['last_modified']}")
            st.write(f"**Size:** {project['size_mb']} MB | "
                    f"**Requirements:** {'✅' if project['has_requirements'] else '❌'} | "
                    f"**README:** {'✅' if project['has_readme'] else '❌'}")
            
            if project_status['notes']:
                st.info(f"📝 **Notes:** {project_status['notes']}")
        
        with col2:
            # Quick status info
            st.write("**Current Status:**")
            st.write(f"**{project_status['status']}**")
            
            if project_status['last_updated']:
                try:
                    last_update = datetime.fromisoformat(
                        project_status['last_updated']
                    ).strftime("%m/%d/%Y")
                    st.write(f"*Updated: {last_update}*")
                except:
                    st.write("*Updated: Unknown*")
        
        with col3:
            # Status management form - using a unique key based on project path
            form_key = f"status_form_{project['path'].replace('/', '_').replace(':', '')}"
            
            with st.form(key=form_key):
                status_options = ["Not Set", "Under Development", "Under Update", 
                                "Need Fix", "Not Working", "Dropped", "Complete"]
                
                current_status_index = status_options.index(project_status['status']) if project_status['status'] in status_options else 0
                
                new_status = st.selectbox(
                    "Update Status:",
                    status_options,
                    key=f"status_{form_key}",
                    index=current_status_index
                )
                notes = st.text_area(
                    "Notes:",
                    value=project_status['notes'],
                    key=f"notes_{form_key}",
                    placeholder="Add project notes...",
                    height=80
                )
                
                if st.form_submit_button("💾 Update Status"):
                    pm.update_project_status(project['path'], new_status, notes)
                    st.success("Status updated!")
                    time.sleep(0.5)
                    st.rerun()

def show_project_explorer(pm, group_by, selected_status):
    """Display the project explorer page"""
    st.header("📂 Project Explorer")
    
    if 'current_path' not in st.session_state or not st.session_state.current_path:
        st.info("👆 Please set a project path in the sidebar to get started!")
        return
    
    # Scan projects if needed
    if 'scanned_projects' not in st.session_state or st.session_state.get('force_scan', False):
        with st.spinner("🔄 Scanning projects..."):
            projects, error = scan_projects_folder(st.session_state.current_path)
            if error:
                st.error(error)
                st.info("💡 **Tips:**")
                st.write("- Check if the path exists")
                st.write("- Ensure you have permission to access the folder")
                st.write("- Try using a different path format")
                return
            st.session_state.scanned_projects = projects
            st.session_state.force_scan = False
    
    projects = st.session_state.scanned_projects
    
    if not projects:
        st.warning("🤷 No Python projects found in this folder.")
        st.info("""
        A Python project is detected if it contains:
        - `.py` files, OR
        - `requirements.txt` file
        """)
        return
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(projects))
    with col2:
        st.metric("Python Files", sum(p['python_files'] for p in projects))
    with col3:
        st.metric("With Requirements", 
                 sum(1 for p in projects if p['has_requirements']))
    with col4:
        st.metric("With README", 
                 sum(1 for p in projects if p['has_readme']))
    
    st.markdown("---")
    
    # Apply status filter
    filtered_projects = []
    for project in projects:
        project_status = pm.get_project_status(project['path'])
        if selected_status == "All" or project_status['status'] == selected_status:
            filtered_projects.append(project)
    
    # Group projects
    grouped_projects = group_projects(filtered_projects, group_by, pm)
    
    # Display grouped projects
    for group_name, group_items in grouped_projects.items():
        if not group_items:
            continue
            
        st.subheader(f"{group_name} ({len(group_items)} projects)")
        
        for i, project in enumerate(group_items):
            display_project_card(project, pm, i)
            st.markdown("---")
    
    # Show message if no projects match filter
    if not filtered_projects:
        st.warning(f"No projects with status: {selected_status}")

def group_projects(projects, group_by, pm):
    """Group projects based on selected criteria"""
    if group_by == "None":
        return {"All Projects": projects}
    
    elif group_by == "Status":
        grouped = {}
        for project in projects:
            status = pm.get_project_status(project['path'])['status']
            if status not in grouped:
                grouped[status] = []
            grouped[status].append(project)
        return grouped
    
    elif group_by == "Has Requirements":
        grouped = {
            "With Requirements": [],
            "Without Requirements": []
        }
        for project in projects:
            if project['has_requirements']:
                grouped["With Requirements"].append(project)
            else:
                grouped["Without Requirements"].append(project)
        return {k: v for k, v in grouped.items() if v}
    
    elif group_by == "Python Files Count":
        grouped = {
            "No Python Files": [],
            "1-5 Files": [],
            "6-20 Files": [],
            "20+ Files": []
        }
        for project in projects:
            count = project['python_files']
            if count == 0:
                grouped["No Python Files"].append(project)
            elif 1 <= count <= 5:
                grouped["1-5 Files"].append(project)
            elif 6 <= count <= 20:
                grouped["6-20 Files"].append(project)
            else:
                grouped["20+ Files"].append(project)
        return {k: v for k, v in grouped.items() if v}
    
    elif group_by == "Size":
        grouped = {
            "Small (< 10 MB)": [],
            "Medium (10-100 MB)": [],
            "Large (> 100 MB)": []
        }
        for project in projects:
            size = project['size_mb']
            if size < 10:
                grouped["Small (< 10 MB)"].append(project)
            elif 10 <= size <= 100:
                grouped["Medium (10-100 MB)"].append(project)
            else:
                grouped["Large (> 100 MB)"].append(project)
        return {k: v for k, v in grouped.items() if v}

def show_status_manager(pm):
    """Display the status manager page for bulk operations"""
    st.header("🎯 Status Manager")
    
    if 'current_path' not in st.session_state or not st.session_state.current_path:
        st.info("👆 Please set a project path in the sidebar to get started!")
        return
    
    # Scan projects if needed
    if 'scanned_projects' not in st.session_state or st.session_state.get('force_scan', False):
        with st.spinner("🔄 Scanning projects..."):
            projects, error = scan_projects_folder(st.session_state.current_path)
            if error:
                st.error(error)
                return
            st.session_state.scanned_projects = projects
            st.session_state.force_scan = False
    
    projects = st.session_state.scanned_projects
    
    if not projects:
        st.warning("No Python projects found in the selected folder.")
        return
    
    # Bulk status operations
    st.subheader("🔄 Bulk Status Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Update Multiple Projects**")
        selected_projects = st.multiselect(
            "Select projects to update:",
            [p['name'] for p in projects],
            key="bulk_select"
        )
        
        new_status = st.selectbox(
            "Set status to:",
            ["Not Set", "Under Development", "Under Update", "Need Fix", "Not Working", "Dropped", "Complete"],
            key="bulk_status"
        )
        
        bulk_notes = st.text_area(
            "Notes (optional):",
            key="bulk_notes",
            placeholder="Add notes for selected projects..."
        )
        
        if st.button("💾 Apply to Selected", type="primary", use_container_width=True):
            if selected_projects:
                updated_count = 0
                for project_name in selected_projects:
                    project = next((p for p in projects if p['name'] == project_name), None)
                    if project:
                        pm.update_project_status(project['path'], new_status, bulk_notes)
                        updated_count += 1
                
                st.success(f"Updated status for {updated_count} projects!")
                st.rerun()
            else:
                st.warning("Please select at least one project.")
    
    with col2:
        st.write("**Quick Actions**")
        
        if st.button("🔄 Set All to 'Under Development'", use_container_width=True):
            for project in projects:
                pm.update_project_status(project['path'], "Under Development", "Bulk updated")
            st.success("All projects set to 'Under Development'!")
            st.rerun()
        
        if st.button("📊 Generate Status Report", use_container_width=True):
            generate_status_report(pm, projects)
        
        if st.button("🧹 Clear All Notes", use_container_width=True):
            for project in projects:
                current_status = pm.get_project_status(project['path'])
                pm.update_project_status(project['path'], current_status['status'], "")
            st.success("All notes cleared!")
            st.rerun()
    
    st.markdown("---")
    
    # Status overview
    st.subheader("📈 Status Overview")
    
    # Calculate status distribution
    status_counts = {}
    for project in projects:
        status = pm.get_project_status(project['path'])['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display status cards
    cols = st.columns(4)
    status_emojis = {
        "Not Set": "⚪",
        "Under Development": "🟢",
        "Under Update": "🟡",
        "Need Fix": "🔴",
        "Not Working": "🟣",
        "Dropped": "⚫",
        "Complete": "✅"
    }
    
    for i, (status, count) in enumerate(status_counts.items()):
        with cols[i % 4]:
            emoji = status_emojis.get(status, "⚪")
            st.metric(f"{emoji} {status}", count)
    
    st.markdown("---")
    
    # Projects by status
    st.subheader("📋 Projects by Status")
    
    for status in ["Not Set", "Under Development", "Under Update", "Need Fix", "Not Working", "Dropped", "Complete"]:
        status_projects = [p for p in projects if pm.get_project_status(p['path'])['status'] == status]
        if status_projects:
            with st.expander(f"{status_emojis.get(status, '⚪')} {status} ({len(status_projects)} projects)"):
                for project in status_projects:
                    project_status = pm.get_project_status(project['path'])
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{project['name']}**")
                    with col2:
                        st.write(f"Files: {project['python_files']}")
                    with col3:
                        if st.button("Edit", key=f"edit_{project['path']}"):
                            st.session_state.editing_project = project['path']
                            st.rerun()
                    
                    if project_status['notes']:
                        st.caption(f"Notes: {project_status['notes']}")
                    st.markdown("---")

def generate_status_report(pm, projects):
    """Generate a comprehensive status report"""
    st.subheader("📊 Status Report")
    
    # Calculate statistics
    total_projects = len(projects)
    status_counts = {}
    total_python_files = 0
    projects_with_requirements = 0
    projects_with_readme = 0
    
    for project in projects:
        status = pm.get_project_status(project['path'])['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        total_python_files += project['python_files']
        if project['has_requirements']:
            projects_with_requirements += 1
        if project['has_readme']:
            projects_with_readme += 1
    
    # Display report
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📈 Project Statistics**")
        st.write(f"Total Projects: {total_projects}")
        st.write(f"Total Python Files: {total_python_files}")
        st.write(f"Projects with Requirements: {projects_with_requirements}")
        st.write(f"Projects with README: {projects_with_readme}")
    
    with col2:
        st.write("**🎯 Status Distribution**")
        for status, count in status_counts.items():
            percentage = (count / total_projects) * 100
            emoji = {
                "Not Set": "⚪",
                "Under Development": "🟢",
                "Under Update": "🟡",
                "Need Fix": "🔴",
                "Not Working": "🟣",
                "Dropped": "⚫",
                "Complete": "✅"
            }.get(status, "⚪")
            st.write(f"{emoji} {status}: {count} ({percentage:.1f}%)")
    
    # Export options
    st.markdown("---")
    st.write("**📤 Export Report**")
    
    if st.button("📋 Copy to Clipboard"):
        report_text = f"Python Projects Status Report\n"
        report_text += f"Total Projects: {total_projects}\n"
        report_text += f"Total Python Files: {total_python_files}\n"
        report_text += "Status Distribution:\n"
        for status, count in status_counts.items():
            percentage = (count / total_projects) * 100
            report_text += f"  - {status}: {count} ({percentage:.1f}%)\n"
        
        # For Streamlit Cloud, we can't directly copy to clipboard
        st.code(report_text)
        st.success("Report generated! Copy the text above.")

def show_settings(pm):
    """Display the settings and paths management page"""
    st.header("⚙️ Settings & Path Management")
    
    # Path Management
    st.subheader("📁 Saved Paths")
    
    # Add new path
    with st.form("add_path_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_path = st.text_input(
                "Add new project path:",
                placeholder="C:/Users/YourName/PythonProjects"
            )
        with col2:
            if st.form_submit_button("💾 Add Path", use_container_width=True):
                if new_path:
                    if pm.add_saved_path(new_path):
                        st.success(f"Path saved: {new_path}")
                        st.rerun()
                    else:
                        st.warning("Path already exists or is invalid")
                else:
                    st.warning("Please enter a valid path")
    
    # Manage existing paths
    if pm.saved_paths:
        st.write("**Current Saved Paths:**")
        for i, path in enumerate(pm.saved_paths):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"`{path}`")
            with col2:
                if st.button("Use", key=f"use_{i}"):
                    st.session_state.current_path = path
                    st.session_state.force_scan = True
                    st.rerun()
            with col3:
                if st.button("Remove", key=f"remove_{i}"):
                    pm.remove_saved_path(path)
                    st.success("Path removed!")
                    st.rerun()
    else:
        st.info("No saved paths yet. Add a path above to get started!")
    
    st.markdown("---")
    
    # Data Management
    st.subheader("💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Data**")
        if st.button("📤 Export Project Data", use_container_width=True):
            export_project_data(pm)
        
        if st.button("📤 Export Settings", use_container_width=True):
            export_settings(pm)
    
    with col2:
        st.write("**Maintenance**")
        if st.button("🧹 Clear All Data", use_container_width=True):
            if st.checkbox("I'm sure I want to clear all data"):
                clear_all_data(pm)
                st.rerun()
        
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Application Info
    st.subheader("ℹ️ Application Information")
    
    st.write("**About Python Project Organizer**")
    st.write("A tool to help you organize and manage your Python projects with status tracking and visual overview.")
    
    st.write("**Data Storage**")
    st.write(f"Project data: `{pm.data_file}`")
    st.write(f"Saved paths: `{pm.saved_paths_file}`")
    
    if st.button("📁 Show Data Files"):
        show_data_files(pm)

def export_project_data(pm):
    """Export project data to a downloadable file"""
    if pm.project_data:
        # Convert to downloadable format
        export_data = {
            "export_date": datetime.now().isoformat(),
            "projects": pm.project_data
        }
        
        st.download_button(
            label="📥 Download Project Data",
            data=json.dumps(export_data, indent=2),
            file_name=f"project_organizer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.warning("No project data to export.")

def export_settings(pm):
    """Export settings to a downloadable file"""
    export_data = {
        "export_date": datetime.now().isoformat(),
        "saved_paths": pm.saved_paths,
        "settings": {
            "version": "1.0",
            "exported_from": "Python Project Organizer"
        }
    }
    
    st.download_button(
        label="📥 Download Settings",
        data=json.dumps(export_data, indent=2),
        file_name=f"organizer_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def clear_all_data(pm):
    """Clear all application data"""
    try:
        # Clear session state
        for key in list(st.session_state.keys()):
            if key != 'pm':
                del st.session_state[key]
        
        # Clear data files
        if Path(pm.data_file).exists():
            Path(pm.data_file).unlink()
        if Path(pm.saved_paths_file).exists():
            Path(pm.saved_paths_file).unlink()
        
        # Reset project manager
        pm.saved_paths = []
        pm.project_data = {}
        
        st.success("All data cleared successfully!")
    except Exception as e:
        st.error(f"Error clearing data: {e}")

def show_data_files(pm):
    """Display current data file contents"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Project Data**")
        if Path(pm.data_file).exists():
            with open(pm.data_file, 'r') as f:
                data = json.load(f)
            st.json(data)
        else:
            st.info("No project data file exists yet.")
    
    with col2:
        st.write("**Saved Paths**")
        if Path(pm.saved_paths_file).exists():
            with open(pm.saved_paths_file, 'r') as f:
                data = json.load(f)
            st.write(data)
        else:
            st.info("No saved paths file exists yet.")

def main():
    st.title("🐍 Python Project Organizer")
    st.markdown("---")
    
    # Initialize project manager
    if 'pm' not in st.session_state:
        st.session_state.pm = ProjectManager()
    
    pm = st.session_state.pm
    
    # Setup navigation
    selected_nav = setup_navigation()
    
    # Setup quick actions
    setup_quick_actions()
    
    # Setup path management
    setup_path_management(pm)
    
    # Setup grouping and filters (returns values we need for Project Explorer)
    group_by, selected_status = setup_grouping_filters()
    
    # Display status legend
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Status Legend")
    st.sidebar.info("""
    - 🟢 Under Development
    - 🟡 Under Update  
    - 🔴 Need Fix
    - 🟣 Not Working
    - ⚫ Dropped
    - ✅ Complete
    - ⚪ Not Set
    """)
    
    # Route to selected page
    if selected_nav == "🏠 Dashboard":
        show_dashboard(pm)
    elif selected_nav == "📂 Project Explorer":
        show_project_explorer(pm, group_by, selected_status)
    elif selected_nav == "🎯 Status Manager":
        show_status_manager(pm)
    elif selected_nav == "⚙️ Settings & Paths":
        show_settings(pm)

if __name__ == "__main__":
    main()

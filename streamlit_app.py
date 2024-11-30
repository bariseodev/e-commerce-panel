import streamlit as st
import os

# Ensure the selected project path is available in session state
if "selected_project" not in st.session_state:
    st.error("No project selected. Please select a project in the sidebar.")
else:
    project_path = st.session_state["project_path"]

# Define the projects directory
PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)  # Ensure the directory exists

# Fetch all projects from the projects directory
projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]

if not projects:
    st.error("No projects found! Please add projects to the /projects folder.")
else:
    if "selected_project" not in st.session_state:
        st.session_state["selected_project"] = projects[0]

    # Sidebar project selection
    selected_project = st.sidebar.selectbox(
        "Proje Seç Hcm ", options=projects, index=projects.index(st.session_state["selected_project"])
    )
    st.session_state["selected_project"] = selected_project

    # Display selected project info
    project_path = os.path.join(PROJECTS_DIR, selected_project)
    st.sidebar.write(f"**Seçtiğin Proje:** {selected_project}")

    st.title(f"Proje: {selected_project}")

    # List files in the selected project's folder
    project_files = os.listdir(project_path)
    st.subheader("Project Dosyaları")
    if project_files:
        st.markdown("\n".join([f"- {file}" for file in project_files]))
    else:
        st.write("Henüz Bir Proje Dosyası Yok Demekki.")

    # Pass project-specific context to session state
    st.session_state["project_path"] = project_path

# Sidebar menu for script selection
script_pages = ["e_commerce_scraper_page", "stock_control", "telegram_scrape_page"]

# Sidebar radio for selecting which script to run
selected_script = st.sidebar.radio("Modül Seç Hcm", script_pages)

# Import and run the corresponding script based on the selected option
if selected_script == "telegram_scrape_page":
    from pages.telegram_scrape_page import show_telegram_scraper_page
    show_telegram_scraper_page()
elif selected_script == "e_commerce_scraper_page":
    from pages.e_commerce_scraper_page import show_ecommerce_scraper_page
    show_ecommerce_scraper_page()
    pass
elif selected_script == "stock_control":
    # Import and run stock_control page script
    # Assuming a function like show_stock_control_page exists
    pass

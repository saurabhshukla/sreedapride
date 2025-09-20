"""
Streamlit Cloud entry point for flat-level water consumption analysis.
This file imports and runs the main app from the src directory.
"""

import sys
from pathlib import Path
import importlib.util

def import_app_main():
    """Import the main function from src/app.py"""
    src_path = Path(__file__).parent / "src" / "app.py"

    # Add src to path for all imports
    sys.path.insert(0, str(Path(__file__).parent / "src"))

    # Load the app module
    spec = importlib.util.spec_from_file_location("app", src_path)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)

    return app_module.main

# Get the main function
main = import_app_main()

if __name__ == "__main__":
    # Set page config
    import streamlit as st

    st.set_page_config(
        page_title="Apartment Water Billing System",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    main()
"""
Analysis Tab
Contains the existing water consumption analysis functionality.
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure the src directory is in the path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from data_processor import FlatDataProcessor, FlatAnalyzer
    from ui_components import FlatAnalysisUI
    from components import FileUploadComponent, HeaderComponent
except ImportError:
    # Fallback for import issues
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from data_processor import FlatDataProcessor, FlatAnalyzer
    from ui_components import FlatAnalysisUI
    from components import FileUploadComponent, HeaderComponent


def show_analysis_tab():
    """Display the analysis tab content with existing functionality."""
    # Initialize components
    data_processor = FlatDataProcessor()
    analyzer = FlatAnalyzer()
    ui = FlatAnalysisUI()
    file_upload = FileUploadComponent()

    # Show tab header
    HeaderComponent.show_tab_header(
        "Water Consumption Analysis",
        "Analyze and compare monthly water consumption across apartments",
        "📊"
    )

    st.info("🏠 **Individual Flat Analysis**: This tool analyzes consumption at the apartment level.")

    # File upload section using reusable component
    st.subheader("📁 Upload Analysis Files")
    last_month_file, this_month_file = file_upload.show_dual_file_upload(
        first_label="Upload Last Month File",
        second_label="Upload This Month File",
        help_text="Upload Excel files containing water consumption data for comparison analysis"
    )

    if last_month_file and this_month_file:
        try:
            with st.spinner("🔄 Processing multi-sheet Excel files..."):
                # Process both files
                df_last = data_processor.load_flat_data(last_month_file)
                df_this = data_processor.load_flat_data(this_month_file)

            # Show processing status
            ui.show_processing_status(df_last is not None, df_this is not None)

            if df_last is not None and df_this is not None:

                # Show data summary
                ui.show_data_summary(df_last, df_this)

                # Analyze the data
                analysis_results = analyzer.analyze_consumption_changes(df_last, df_this)

                # Display main analytics dashboard
                st.header("📈 Advanced Analytics Dashboard")

                # Show key metrics
                ui.show_key_metrics(analysis_results["metrics"])

                # Show detailed analysis in tabs
                ui.show_analysis_tabs(analysis_results["categories"])

                # Create block summary for executive summary
                block_summary = analyzer.create_block_summary(analysis_results["merged_data"])

                # Show executive summary
                ui.show_executive_summary(
                    analysis_results["metrics"],
                    analysis_results["categories"],
                    block_summary
                )

                # Download section
                ui.show_download_section(
                    analysis_results["merged_data"],
                    analysis_results["categories"],
                    analysis_results["metrics"],
                    block_summary
                )

            else:
                ui.show_error_message("Could not extract flat data from one or both files")

        except Exception as e:
            ui.show_error_message(f"Error processing files: {str(e)}")
"""
Billing Management Tab
This tab will contain all billing-related functionality.
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
    from components import FileUploadComponent, HeaderComponent
except ImportError:
    # Fallback for import issues
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from components import FileUploadComponent, HeaderComponent


def show_billing_tab():
    """Display the billing management tab content."""
    # Initialize components
    file_upload = FileUploadComponent()

    # Show tab header
    HeaderComponent.show_tab_header(
        "Billing Management",
        "Generate and manage apartment billing statements",
        "💰"
    )

    # Placeholder content for billing functionality
    st.info("🚧 **Billing Management System Coming Soon!**")

    st.write("""
    This section will include:
    - **Bill Generation**: Create monthly billing statements for all apartments
    - **Payment Tracking**: Monitor payment status and outstanding amounts
    - **Rate Management**: Configure water rates and other charges
    - **Invoice Templates**: Customize billing templates and formats
    - **Payment Reports**: Generate payment summary and collection reports
    """)

    # Add file upload section for future billing functionality
    st.subheader("📁 Upload Billing Data")
    st.write("When ready, you'll be able to upload billing data files here:")

    # Example of using the reusable file upload component
    billing_files = file_upload.show_multiple_file_upload(
        label="Upload Billing Files",
        help_text="Select Excel files containing billing data",
        key_suffix="billing"
    )

    if billing_files:
        st.success(f"✅ {len(billing_files)} file(s) uploaded successfully!")
        for file in billing_files:
            st.write(f"- {file.name}")

    # Placeholder sections for future features
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧾 Quick Actions")
        if st.button("Generate Monthly Bills", disabled=True):
            st.info("This feature will be available soon!")

        if st.button("Send Payment Reminders", disabled=True):
            st.info("This feature will be available soon!")

    with col2:
        st.subheader("📊 Billing Overview")
        st.metric("Total Outstanding", "₹0", help="Total amount pending collection")
        st.metric("Bills Generated", "0", help="Number of bills generated this month")
        st.metric("Payment Rate", "0%", help="Percentage of bills paid on time")

    # Coming soon features
    with st.expander("🔮 Upcoming Features"):
        st.write("""
        **Phase 1 - Basic Billing:**
        - Import resident data and consumption readings
        - Generate standardized bill formats
        - Export bills as PDF or Excel

        **Phase 2 - Advanced Features:**
        - Automated payment tracking
        - SMS/Email notifications
        - Online payment integration

        **Phase 3 - Analytics:**
        - Revenue forecasting
        - Collection efficiency reports
        - Seasonal consumption analysis
        """)
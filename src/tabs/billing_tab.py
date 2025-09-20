"""
Billing Management Tab
Complete billing workflow from WeGot data to Adda template generation.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Ensure the src directory is in the path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from components import FileUploadComponent, HeaderComponent
    from billing_processor import BillingWorkflowManager
except ImportError:
    # Fallback for import issues
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from components import FileUploadComponent, HeaderComponent
    from billing_processor import BillingWorkflowManager


def show_billing_tab():
    """Display the complete billing management functionality with step-by-step progression."""
    # Initialize components
    file_upload = FileUploadComponent()

    # Initialize session state for workflow
    if 'billing_workflow' not in st.session_state:
        st.session_state.billing_workflow = BillingWorkflowManager()
    if 'workflow_completed' not in st.session_state:
        st.session_state.workflow_completed = False
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None

    # Initialize step progression
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'files_uploaded' not in st.session_state:
        st.session_state.files_uploaded = False
    if 'data_copied' not in st.session_state:
        st.session_state.data_copied = False
    if 'selected_month' not in st.session_state:
        st.session_state.selected_month = None
    if 'bwssb_reading' not in st.session_state:
        st.session_state.bwssb_reading = 0.0
    if 'tanker_reading' not in st.session_state:
        st.session_state.tanker_reading = 0.0

    # Show tab header
    HeaderComponent.show_tab_header(
        "WeGot to Adda Billing Processor",
        "Step-by-step billing workflow from WeGot data to Adda template generation",
        "💰"
    )

    # Accordion-based Step-by-Step Interface
    # Step 1: File Uploads
    step1_status = "✅ Completed" if st.session_state.current_step > 1 else "📁 Upload Files"
    with st.expander(f"**Step 1: {step1_status}**", expanded=(st.session_state.current_step == 1)):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**WeGot All Blocks File**")
            st.info("📊 Upload the 'All Blocks DD-MM-YYYY.xlsx' file downloaded from WeGot")
            wegot_file = file_upload.show_single_file_upload(
                label="Upload WeGot All Blocks File",
                key_suffix="wegot"
            )

        with col2:
            st.write("**Monthly Billing Template**")
            st.info("📋 Upload the 'BillingAll_Blocks_Month-YYYY.xlsx' template file")
            billing_file = file_upload.show_single_file_upload(
                label="Upload Billing Template File",
                key_suffix="billing_template"
            )

        with col3:
            st.write("**Adda Template File**")
            st.info("🎯 Upload the 'Adda_Template_DD-MM-YY.xlsx' template file")
            adda_template_file = file_upload.show_single_file_upload(
                label="Upload Adda Template File",
                key_suffix="adda_template"
            )

        # Check if all files are uploaded
        files_ready = (wegot_file is not None and
                      billing_file is not None and
                      adda_template_file is not None)

        # CTA for Step 1
        st.markdown("---")

        # Create flexbox container using columns
        st.markdown('<div class="button-warning-container">', unsafe_allow_html=True)

        btn_col, warn_col = st.columns([1, 2])

        with btn_col:
            # Always show button but disabled when requirements not met
            button_clicked = st.button("📊 Copy WeGot Data & Proceed to Step 2",
                        disabled=not files_ready or st.session_state.files_uploaded,
                        help="Upload all files to copy WeGot data" if not files_ready else ("Already completed" if st.session_state.files_uploaded else "Click to copy WeGot data and proceed to step 2"),
                        key="step1_cta")

        with warn_col:
            # Show status or requirements next to button
            if files_ready and st.session_state.files_uploaded:
                st.success("✅ Files uploaded and WeGot data copied to billing template")
            elif not files_ready:
                missing = []
                if wegot_file is None: missing.append("WeGot file")
                if billing_file is None: missing.append("Billing template")
                if adda_template_file is None: missing.append("Adda template")
                st.warning(f"⚠️ Please upload: {', '.join(missing)}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Handle button click
        if button_clicked:
                with st.spinner("Copying WeGot data to WeGot Report sheet..."):
                    try:
                        # Load WeGot data
                        wegot_data = st.session_state.billing_workflow.wegot_processor.load_wegot_data(wegot_file)

                        # Load billing template
                        billing_sheets = st.session_state.billing_workflow.wegot_processor.load_billing_template(billing_file)

                        # BLIND REPLACEMENT: Copy WeGot data to WeGot Report sheet
                        if 'WeGot report' in billing_sheets:
                            billing_sheets['WeGot report'] = wegot_data.copy()
                            st.session_state.billing_workflow.wegot_processor.billing_template = billing_sheets
                            st.session_state.files_uploaded = True
                            st.session_state.current_step = 2
                            st.success(f"✅ WeGot data copied! {len(wegot_data)} rows replaced in WeGot Report sheet")
                            st.rerun()
                        else:
                            st.error("❌ WeGot Report sheet not found in billing template")
                    except Exception as e:
                        st.error(f"❌ Error copying data: {str(e)}")

    # Step 2: Enter BWSSB and Tanker details
    step2_status = "✅ Completed" if st.session_state.current_step > 2 else "⚙️ Enter BWSSB and Tanker details"
    step2_enabled = st.session_state.current_step >= 2
    with st.expander(f"**Step 2: {step2_status}**", expanded=(st.session_state.current_step == 2)):
        if step2_enabled:
            col1, col2, col3 = st.columns(3)

            with col1:
                # Month selector instead of text input
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                # Default to previous month
                previous_month_index = (datetime.now().month - 2) % 12
                month = st.selectbox("📅 Billing Month",
                                   options=months,
                                   index=previous_month_index,
                                   help="Select the month for billing")
                st.session_state.selected_month = month

            with col2:
                bwssb_reading = st.number_input("💧 Cauvery Water Bill",
                                               min_value=0.0, value=st.session_state.bwssb_reading, step=1.0,
                                               help="Enter the Cauvery water bill amount")
                st.session_state.bwssb_reading = bwssb_reading

            with col3:
                tanker_reading = st.number_input("🚛 Tanker Water Reading",
                                               min_value=0.0, value=st.session_state.tanker_reading, step=1.0,
                                               help="Enter the water tanker reading")
                st.session_state.tanker_reading = tanker_reading

            # CTA for Step 2
            st.markdown("---")
            params_ready = (month is not None and
                           bwssb_reading > 0 and
                           tanker_reading > 0)

            # Create flexbox container using columns
            st.markdown('<div class="button-warning-container">', unsafe_allow_html=True)

            btn_col2, warn_col2 = st.columns([1, 2])

            with btn_col2:
                # Always show button but disabled when requirements not met
                button_clicked2 = st.button("🚀 Generate Billing Data & Proceed to Results",
                            disabled=not params_ready,
                            help="Enter all parameters to generate billing data" if not params_ready else "Click to generate billing data and proceed to results",
                            key="step2_cta")

            with warn_col2:
                # Show requirements if not met next to button
                if not params_ready:
                    missing = []
                    if bwssb_reading <= 0: missing.append("Cauvery water bill")
                    if tanker_reading <= 0: missing.append("Tanker reading")
                    if missing:
                        st.warning(f"⚠️ Please provide: {', '.join(missing)}")

            st.markdown('</div>', unsafe_allow_html=True)

            # Handle button click
            if button_clicked2:
                    with st.spinner("Processing billing data and generating templates..."):
                        try:
                            # Use the billing processor to update the template properly
                            wegot_data = st.session_state.billing_workflow.wegot_processor.wegot_data
                            billing_sheets = st.session_state.billing_workflow.wegot_processor.billing_template

                            # Update billing template with WeGot data and readings
                            updated_sheets = st.session_state.billing_workflow._update_billing_template_with_wegot_data(
                                wegot_data, billing_sheets, month, bwssb_reading, tanker_reading)

                            # Store the updated template
                            st.session_state.billing_workflow.updated_billing_template = updated_sheets
                            st.session_state.billing_workflow.wegot_processor.billing_template = updated_sheets

                            # Extract final allocation data
                            final_allocation = st.session_state.billing_workflow.wegot_processor.extract_final_allocation_data()

                            # Generate Adda template using the uploaded template file
                            adda_template_file = st.session_state.get("upload_adda_template_file_uploader_adda_template", None)
                            if adda_template_file:
                                adda_template = st.session_state.billing_workflow._generate_adda_template_from_file(
                                    final_allocation, adda_template_file, month)
                                # Store the generated template in the adda_generator
                                st.session_state.billing_workflow.adda_generator.dues_template = adda_template

                            # Store results
                            total_amount = final_allocation['To_Be_Billed'].sum()
                            apartment_count = len(final_allocation)
                            avg_amount = total_amount / apartment_count if apartment_count > 0 else 0

                            st.session_state.workflow_results = {
                                'status': 'success',
                                'total_billing_amount': total_amount,
                                'apartment_count': apartment_count,
                                'average_amount_per_flat': avg_amount,
                                'month': month,
                                'final_allocation': final_allocation,
                                'adda_template': adda_template
                            }

                            st.session_state.workflow_completed = True
                            st.session_state.current_step = 3
                            st.success("🎉 Billing processing completed successfully!")

                            # Show allocation update info
                            if month == 'Aug':
                                st.info(f"📍 Allocation sheet updated: {month} → Row 15 (C15: {bwssb_reading}, D15: {tanker_reading})")
                            elif month == 'Sep':
                                st.info(f"📍 Allocation sheet updated: {month} → Row 16 (C16: {bwssb_reading}, D16: {tanker_reading})")
                            else:
                                st.info(f"📍 Allocation sheet updated for month: {month}")

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Processing failed: {str(e)}")
        else:
            st.info("⏳ Complete Step 1 to unlock this section")

    # Step 3: Results and Downloads
    step3_status = "✅ Completed" if st.session_state.workflow_completed else "📊 Results & Downloads"
    step3_enabled = st.session_state.current_step >= 3 and st.session_state.workflow_completed

    with st.expander(f"**Step 3: {step3_status}**", expanded=(st.session_state.current_step == 3 and step3_enabled)):
        if step3_enabled:
            results = st.session_state.workflow_results

            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Billing Amount",
                         f"₹{results.get('total_billing_amount', 0):,.0f}",
                         help="Total amount to be billed across all apartments")

            with col2:
                st.metric("Total Apartments",
                         results.get('apartment_count', 0),
                         help="Number of apartments processed")

            with col3:
                st.metric("Average per Flat",
                         f"₹{results.get('average_amount_per_flat', 0):.0f}",
                         help="Average billing amount per apartment")

            with col4:
                st.metric("Processing Month",
                         results.get('month', 'N/A'),
                         help="Month for which billing was processed")

            # Workflow Status
            with st.expander("🔍 View Workflow Status"):
                workflow_status = results.get('workflow_status', {})
                for step, status in workflow_status.items():
                    status_icon = "✅" if status else "❌"
                    st.write(f"{status_icon} {step.replace('_', ' ').title()}")

            # Download Section
            st.subheader("📥 Download Generated Files")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Download Updated Billing Template (for emailing)
                st.write("**📧 For Email Distribution**")
                try:
                    updated_billing_bytes = st.session_state.billing_workflow.get_updated_billing_template_download()

                    st.download_button(
                        label="📧 Download Updated Billing File",
                        data=updated_billing_bytes,
                        file_name=f"BillingAll_Blocks_{month}-{datetime.now().year}_{datetime.now().strftime('%d%m%Y')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download the updated billing file with WeGot data for emailing to residents"
                    )
                except Exception as e:
                    st.error(f"Error generating billing file: {str(e)}")

            with col2:
                # Download Adda Template
                st.write("**🎯 For Adda Upload**")
                try:
                    adda_template_bytes = st.session_state.billing_workflow.get_adda_template_download()

                    st.download_button(
                        label="📊 Download Adda Template",
                        data=adda_template_bytes,
                        file_name=f"adda_dues_template_{month}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download the Excel template ready for Adda upload"
                    )
                except Exception as e:
                    st.error(f"Error generating Adda template: {str(e)}")

            with col3:
                # Preview Final Allocation Data
                st.write("**👁️ Data Preview**")
                if st.button("Preview Final Allocation Data"):
                    try:
                        final_allocation = st.session_state.billing_workflow.get_final_allocation_data()
                        st.dataframe(final_allocation, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying data: {str(e)}")

            # Workflow explanation
            st.info("""
            **📋 Three Output Files Generated:**

            1. **📧 Updated Billing File**: Contains WeGot data integrated with your billing template - send this to residents via email
            2. **🎯 Adda Template**: Ready-to-upload format for Adda platform with calculated amounts
            3. **👁️ Data Preview**: View the processed data before downloading
            """)
        else:
            st.info("⏳ Complete Step 2 to unlock this section")


    # Reset workflow button
    if st.session_state.workflow_completed:
        if st.button("🔄 Start New Billing Workflow"):
            # Reset all workflow-related session state
            st.session_state.billing_workflow = BillingWorkflowManager()
            st.session_state.workflow_completed = False
            st.session_state.workflow_results = None
            st.session_state.current_step = 1
            st.session_state.files_uploaded = False
            st.session_state.data_copied = False
            st.session_state.selected_month = None
            st.session_state.bwssb_reading = 0.0
            st.session_state.tanker_reading = 0.0
            st.rerun()
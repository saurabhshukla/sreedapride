"""
File Upload Component
Reusable file upload widgets for the billing management system.
"""

import streamlit as st
from typing import Tuple, Optional, List, Any


class FileUploadComponent:
    """Reusable file upload component that can be used across different tabs."""

    def __init__(self):
        self.supported_formats = ["xls", "xlsx"]

    def show_dual_file_upload(self,
                             first_label: str = "Upload First File",
                             second_label: str = "Upload Second File",
                             help_text: Optional[str] = None) -> Tuple[Any, Any]:
        """
        Display two file upload widgets side by side.

        Args:
            first_label: Label for the first file uploader
            second_label: Label for the second file uploader
            help_text: Optional help text to display above the uploaders

        Returns:
            Tuple of uploaded files (first_file, second_file)
        """
        if help_text:
            st.info(help_text)

        col1, col2 = st.columns(2)
        with col1:
            first_file = st.file_uploader(
                first_label,
                type=self.supported_formats,
                key=f"{first_label.lower().replace(' ', '_')}_uploader"
            )
        with col2:
            second_file = st.file_uploader(
                second_label,
                type=self.supported_formats,
                key=f"{second_label.lower().replace(' ', '_')}_uploader"
            )

        return first_file, second_file

    def show_single_file_upload(self,
                               label: str = "Upload File",
                               help_text: Optional[str] = None,
                               key_suffix: str = "") -> Any:
        """
        Display a single file upload widget.

        Args:
            label: Label for the file uploader
            help_text: Optional help text to display above the uploader
            key_suffix: Suffix to add to the key to avoid conflicts

        Returns:
            Uploaded file or None
        """
        if help_text:
            st.info(help_text)

        return st.file_uploader(
            label,
            type=self.supported_formats,
            key=f"{label.lower().replace(' ', '_')}_uploader_{key_suffix}"
        )

    def show_multiple_file_upload(self,
                                 label: str = "Upload Files",
                                 help_text: Optional[str] = None,
                                 accept_multiple: bool = True,
                                 key_suffix: str = "") -> List[Any]:
        """
        Display a file upload widget that can accept multiple files.

        Args:
            label: Label for the file uploader
            help_text: Optional help text to display above the uploader
            accept_multiple: Whether to accept multiple files
            key_suffix: Suffix to add to the key to avoid conflicts

        Returns:
            List of uploaded files
        """
        if help_text:
            st.info(help_text)

        uploaded_files = st.file_uploader(
            label,
            type=self.supported_formats,
            accept_multiple_files=accept_multiple,
            key=f"{label.lower().replace(' ', '_')}_uploader_{key_suffix}"
        )

        if uploaded_files is None:
            return []
        elif not accept_multiple:
            return [uploaded_files] if uploaded_files else []
        else:
            return uploaded_files
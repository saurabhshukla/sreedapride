import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Apartment Water Consumption Insights 💧")
st.write("Upload **last month** and **this month** Excel files to compare water consumption across all sheets.")

# --- Function to load multi-sheet Excel ---
def load_multi_sheet_excel(file):
    try:
        # Get all sheet names
        xl_file = pd.ExcelFile(file)
        sheet_names = xl_file.sheet_names
        
        st.write(f"**📋 Found {len(sheet_names)} sheets:**")
        for i, sheet in enumerate(sheet_names):
            st.write(f"  {i+1}. {sheet}")
        
        all_data = {}
        apartment_data = None
        
        # Try to find apartment data in each sheet
        for sheet_name in sheet_names:
            try:
                st.write(f"\n**🔍 Analyzing sheet: '{sheet_name}'**")
                
                # Load sheet data
                raw = pd.read_excel(file, sheet_name=sheet_name, header=None)
                
                if raw.empty:
                    st.write(f"  ⚠️ Sheet '{sheet_name}' is empty")
                    continue
                
                # Show preview
                st.write(f"  📊 Sheet size: {raw.shape[0]} rows × {raw.shape[1]} columns")
                
                # Look for apartment-related data
                apartment_keywords = ["apartment", "apartm", "flat", "unit", "block", "serial"]
                billing_keywords = ["billed", "total", "consumption", "amount", "bill", "to be", "dues"]
                
                header_row = None
                
                # Search for header row in first 20 rows
                for i in range(min(20, len(raw))):
                    row = raw.iloc[i]
                    row_str = row.astype(str).str.lower()
                    row_text = ' '.join(row_str.values)
                    
                    has_apartment = any(keyword in row_text for keyword in apartment_keywords)
                    has_billing = any(keyword in row_text for keyword in billing_keywords)
                    
                    if has_apartment and has_billing:
                        header_row = i
                        st.write(f"  ✅ Found apartment data at row {i + 1}")
                        break
                
                if header_row is not None:
                    # Load with proper header
                    df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)
                    
                    # Clean column names
                    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', ' ') for c in df.columns]
                    
                    # Find apartment column
                    flat_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(keyword in col_lower for keyword in apartment_keywords):
                            flat_col = col
                            break
                    
                    # Find billing column
                    billed_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(keyword in col_lower for keyword in billing_keywords):
                            billed_col = col
                            break
                    
                    # If no keyword match, find rightmost numeric column
                    if flat_col and not billed_col:
                        numeric_cols = []
                        for col in df.columns:
                            try:
                                numeric_data = pd.to_numeric(df[col], errors='coerce')
                                if numeric_data.notna().sum() > len(df) * 0.3:
                                    numeric_cols.append(col)
                            except:
                                pass
                        
                        if numeric_cols:
                            billed_col = numeric_cols[-1]
                    
                    if flat_col and billed_col:
                        # Clean and process data
                        df_clean = df[[flat_col, billed_col]].copy()
                        df_clean.columns = ["Flat", "Consumption"]
                        
                        # Clean data
                        df_clean["Flat"] = df_clean["Flat"].astype(str).str.strip()
                        df_clean["Consumption"] = pd.to_numeric(df_clean["Consumption"], errors='coerce').fillna(0)
                        
                        # Remove invalid rows
                        df_clean = df_clean[
                            df_clean["Flat"].notna() & 
                            (df_clean["Flat"] != "") & 
                            (df_clean["Flat"] != "nan") &
                            (df_clean["Flat"] != "None") &
                            (~df_clean["Flat"].str.lower().str.contains("total|sum|grand", na=False))
                        ]
                        
                        # Store data with sheet info
                        df_clean["Sheet"] = sheet_name
                        all_data[sheet_name] = df_clean
                        
                        st.write(f"  ✅ Extracted {len(df_clean)} apartment records")
                        st.write(f"  🏠 Apartment column: '{flat_col}'")
                        st.write(f"  💰 Billing column: '{billed_col}'")
                        
                        # Use the sheet with most data as primary
                        if apartment_data is None or len(df_clean) > len(apartment_data):
                            apartment_data = df_clean[["Flat", "Consumption"]].copy()
                            st.write(f"  🎯 Using '{sheet_name}' as primary data source")
                    
                    else:
                        st.write(f"  ⚠️ Could not find both apartment and billing columns in '{sheet_name}'")
                        st.write(f"      Available columns: {list(df.columns)}")
                
                else:
                    st.write(f"  ⚠️ No apartment data found in sheet '{sheet_name}'")
            
            except Exception as e:
                st.write(f"  ❌ Error processing sheet '{sheet_name}': {str(e)}")
                continue
        
        if apartment_data is not None:
            st.success(f"✅ Successfully loaded apartment data with {len(apartment_data)} records")
            return apartment_data, all_data
        else:
            st.error("❌ No apartment consumption data found in any sheet")
            return None, all_data
            
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None, {}

# --- File uploaders ---
col1, col2 = st.columns(2)
with col1:
    last_month_file = st.file_uploader("Upload Last Month File", type=["xls", "xlsx"])
with col2:
    this_month_file = st.file_uploader("Upload This Month File", type=["xls", "xlsx"])

if last_month_file and this_month_file:
    try:
        with st.spinner("🔄 Processing multi-sheet Excel files..."):
            df_last, last_sheets = load_multi_sheet_excel(last_month_file)
            df_this, this_sheets = load_multi_sheet_excel(this_month_file)

        if df_last is not None and df_this is not None:
            st.success("✅ Both files processed successfully!")
            
            # Show data summary
            with st.expander("📊 Data Summary"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Last Month:**")
                    st.write(f"- Total apartments: {len(df_last)}")
                    st.write(f"- Total consumption: ₹{df_last['Consumption'].sum():,.0f}")
                    st.write(f"- Average per apartment: ₹{df_last['Consumption'].mean():.0f}")
                    st.dataframe(df_last.head())
                
                with col2:
                    st.write("**This Month:**")
                    st.write(f"- Total apartments: {len(df_this)}")
                    st.write(f"- Total consumption: ₹{df_this['Consumption'].sum():,.0f}")
                    st.write(f"- Average per apartment: ₹{df_this['Consumption'].mean():.0f}")
                    st.dataframe(df_this.head())

            # Merge and analyze
            merged = pd.merge(df_last, df_this, on="Flat", how="outer", suffixes=("_last", "_this"))
            merged = merged.fillna(0)

            # Calculate changes
            merged["Change"] = merged["Consumption_this"] - merged["Consumption_last"]
            merged["Change_Percent"] = np.where(
                merged["Consumption_last"] > 0,
                (merged["Change"] / merged["Consumption_last"]) * 100,
                np.where(merged["Consumption_this"] > 0, 100, 0)
            )

            # Advanced Analytics
            st.header("📈 Advanced Analytics Dashboard")
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            total_change = merged["Change"].sum()
            avg_change = merged["Change"].mean()
            active_flats = len(merged[merged["Consumption_this"] > 0])
            zero_usage = len(merged[merged["Consumption_this"] == 0])
            
            with col1:
                st.metric("Total Flats", len(merged))
            with col2:
                st.metric("Active Flats", active_flats, f"{(active_flats/len(merged)*100):.1f}%")
            with col3:
                st.metric("Total Revenue Change", f"₹{total_change:,.0f}")
            with col4:
                st.metric("Zero Usage Flats", zero_usage, f"{(zero_usage/len(merged)*100):.1f}%")

            # Detailed Analysis
            st.subheader("🔍 Detailed Analysis")
            
            # Significant increases (>₹200 or >25% increase)
            major_increases = merged[
                ((merged["Change"] > 200) | (merged["Change_Percent"] > 25)) & 
                (merged["Change"] > 0)
            ].sort_values("Change", ascending=False)

            # Significant decreases (>₹200 decrease or >25% decrease)
            major_decreases = merged[
                ((merged["Change"] < -200) | (merged["Change_Percent"] < -25)) & 
                (merged["Change"] < 0)
            ].sort_values("Change")

            # Zero consumption (previously active)
            zero_consumption = merged[
                (merged["Consumption_this"] == 0) & 
                (merged["Consumption_last"] > 0)
            ].sort_values("Consumption_last", ascending=False)

            # New consumers
            new_consumers = merged[
                (merged["Consumption_last"] == 0) & 
                (merged["Consumption_this"] > 0)
            ].sort_values("Consumption_this", ascending=False)

            # High consumers (top 10%)
            high_threshold = merged["Consumption_this"].quantile(0.9)
            high_consumers = merged[
                merged["Consumption_this"] >= high_threshold
            ].sort_values("Consumption_this", ascending=False)

            # Display results in tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Major Increases", "📉 Major Decreases", "⭕ Zero Usage", 
                "🆕 New Consumers", "🏆 High Consumers"
            ])

            with tab1:
                if not major_increases.empty:
                    st.write(f"**{len(major_increases)} apartments with significant increases:**")
                    display_cols = ["Flat", "Consumption_last", "Consumption_this", "Change", "Change_Percent"]
                    st.dataframe(
                        major_increases[display_cols].style.format({
                            "Consumption_last": "₹{:.0f}",
                            "Consumption_this": "₹{:.0f}",
                            "Change": "₹{:.0f}",
                            "Change_Percent": "{:.1f}%"
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("No significant increases found")

            with tab2:
                if not major_decreases.empty:
                    st.write(f"**{len(major_decreases)} apartments with significant decreases:**")
                    st.dataframe(
                        major_decreases[display_cols].style.format({
                            "Consumption_last": "₹{:.0f}",
                            "Consumption_this": "₹{:.0f}",
                            "Change": "₹{:.0f}",
                            "Change_Percent": "{:.1f}%"
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("No significant decreases found")

            with tab3:
                if not zero_consumption.empty:
                    st.write(f"**{len(zero_consumption)} apartments went from active to zero usage:**")
                    st.dataframe(
                        zero_consumption[["Flat", "Consumption_last", "Change"]].style.format({
                            "Consumption_last": "₹{:.0f}",
                            "Change": "₹{:.0f}"
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("No apartments went from active to zero usage")

            with tab4:
                if not new_consumers.empty:
                    st.write(f"**{len(new_consumers)} new active apartments:**")
                    st.dataframe(
                        new_consumers[["Flat", "Consumption_this", "Change"]].style.format({
                            "Consumption_this": "₹{:.0f}",
                            "Change": "₹{:.0f}"
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("No new consumers found")

            with tab5:
                if not high_consumers.empty:
                    st.write(f"**Top 10% consumers (≥₹{high_threshold:.0f}):**")
                    st.dataframe(
                        high_consumers[["Flat", "Consumption_this", "Change", "Change_Percent"]].style.format({
                            "Consumption_this": "₹{:.0f}",
                            "Change": "₹{:.0f}",
                            "Change_Percent": "{:.1f}%"
                        }),
                        use_container_width=True
                    )

            # Executive Summary
            st.header("📋 Executive Summary")
            
            summary_text = f"""
            **Monthly Water Consumption Analysis Summary**
            
            **Overall Trends:**
            - Total apartments analyzed: {len(merged)}
            - Active apartments this month: {active_flats} ({(active_flats/len(merged)*100):.1f}%)
            - Total revenue change: ₹{total_change:,.0f} ({'+' if total_change >= 0 else ''}{(total_change/df_last['Consumption'].sum()*100):.1f}%)
            - Average change per apartment: ₹{avg_change:.0f}
            
            **Key Findings:**
            - {len(major_increases)} apartments had significant consumption increases
            - {len(major_decreases)} apartments had significant consumption decreases  
            - {len(zero_consumption)} apartments went from active to zero usage
            - {len(new_consumers)} apartments became newly active
            - {len(high_consumers)} apartments are in the top 10% of consumers
            
            **Action Items:**
            - Follow up on {len(zero_consumption)} apartments with zero usage for vacancy status
            - Investigate {len(major_increases)} apartments with major increases for potential leaks
            - Verify meter readings for apartments with >100% consumption changes
            - Welcome {len(new_consumers)} new active residents
            """
            
            st.markdown(summary_text)

            # Download comprehensive report
            st.header("📥 Download Complete Analysis")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Main comparison
                export_merged = merged.round(2)
                export_merged.to_excel(writer, sheet_name="Full Analysis", index=False)
                
                # Individual analyses
                if not major_increases.empty:
                    major_increases.round(2).to_excel(writer, sheet_name="Major Increases", index=False)
                if not major_decreases.empty:
                    major_decreases.round(2).to_excel(writer, sheet_name="Major Decreases", index=False)
                if not zero_consumption.empty:
                    zero_consumption.round(2).to_excel(writer, sheet_name="Zero Usage", index=False)
                if not new_consumers.empty:
                    new_consumers.round(2).to_excel(writer, sheet_name="New Consumers", index=False)
                if not high_consumers.empty:
                    high_consumers.round(2).to_excel(writer, sheet_name="High Consumers", index=False)
                
                # Summary sheet
                summary_df = pd.DataFrame({
                    "Metric": ["Total Apartments", "Active Apartments", "Zero Usage", "New Consumers", 
                              "Major Increases", "Major Decreases", "Total Revenue Change", "Average Change"],
                    "Value": [len(merged), active_flats, len(zero_consumption), len(new_consumers),
                             len(major_increases), len(major_decreases), f"₹{total_change:,.0f}", f"₹{avg_change:.0f}"]
                })
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

            st.download_button(
                label="📥 Download Comprehensive Analysis Report",
                data=output.getvalue(),
                file_name=f"water_consumption_comprehensive_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.error("❌ Could not extract apartment data from one or both files")

    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        st.write("**Troubleshooting:**")
        st.write("1. Ensure your Excel files contain apartment/flat data")
        st.write("2. Check that billing amounts are in numeric format")
        st.write("3. Verify that apartment identifiers are consistent between files")

# Instructions
with st.expander("📖 How to Use This Multi-Sheet Analyzer"):
    st.write("""
    **This enhanced version:**
    - 🔍 **Scans all sheets** in your Excel files automatically
    - 📊 **Finds apartment data** wherever it exists in the workbook
    - 🎯 **Uses the sheet with most data** as the primary source
    - 📈 **Provides advanced analytics** with multiple analysis categories
    - 📋 **Generates comprehensive reports** with executive summary
    
    **Perfect for complex Excel files with:**
    - Multiple worksheets (Charts, Allocations, Reports, etc.)
    - Different data formats across sheets
    - Various column naming conventions
    - Mixed data types and layouts
    
    **The analyzer will automatically:**
    1. Scan all sheets for apartment/consumption data
    2. Find the best data source in each file
    3. Clean and standardize the data
    4. Perform comprehensive comparison analysis
    5. Generate actionable insights and reports
    """)
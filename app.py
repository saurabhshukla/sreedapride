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
        
        # Store logs for debugging
        processing_logs = []
        processing_logs.append(f"📋 Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
        
        all_data = {}
        apartment_data = None
        
        # Try to find apartment data in each sheet
        for sheet_name in sheet_names:
            try:
                processing_logs.append(f"\n🔍 Analyzing sheet: '{sheet_name}'")
                
                # Load sheet data
                raw = pd.read_excel(file, sheet_name=sheet_name, header=None)
                
                if raw.empty:
                    processing_logs.append(f"  ⚠️ Sheet '{sheet_name}' is empty")
                    continue
                
                processing_logs.append(f"  📊 Sheet size: {raw.shape[0]} rows × {raw.shape[1]} columns")
                
                # Look for apartment-related data (using Apartment as primary, not Block)
                apartment_keywords = ["apartment", "apartm", "flat", "unit", "serial"]
                billing_keywords = ["billed", "total", "consumption", "amount", "bill", "to be", "dues"]
                
                header_row = None
                
                # Search for header row in first 20 rows
                for i in range(min(20, len(raw))):
                    row = raw.iloc[i]
                    row_str = row.astype(str).str.lower()
                    row_text = ' '.join(row_str.values)
                    
                    has_apartment = any(keyword in row_text for keyword in apartment_keywords)
                    has_billing = any(keyword in row_text for keyword in billing_keywords)
                    
                    processing_logs.append(f"    Row {i+1}: apartment={has_apartment}, billing={has_billing}")
                    
                    if has_apartment and has_billing:
                        header_row = i
                        processing_logs.append(f"  ✅ Found apartment data at row {i + 1}")
                        processing_logs.append(f"     Header content: {row.tolist()}")
                        break
                
                if header_row is not None:
                    # Load with proper header
                    df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)
                    
                    # Clean column names
                    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', ' ') for c in df.columns]
                    processing_logs.append(f"  📝 Available columns: {list(df.columns)}")
                    
                    # Find apartment column (prioritize 'Apartment' over 'Block')
                    flat_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(keyword in col_lower for keyword in apartment_keywords):
                            flat_col = col
                            processing_logs.append(f"  🏠 Found apartment column: '{flat_col}'")
                            break
                    
                    # Find billing column
                    billed_col = None
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(keyword in col_lower for keyword in billing_keywords):
                            billed_col = col
                            processing_logs.append(f"  💰 Found billing column: '{billed_col}'")
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
                            processing_logs.append(f"  💰 Using rightmost numeric column: '{billed_col}'")
                    
                    if flat_col and billed_col:
                        # Clean and process data
                        df_clean = df[[flat_col, billed_col]].copy()
                        df_clean.columns = ["Flat", "Consumption"]
                        
                        processing_logs.append(f"  🧹 Raw data sample: {df_clean.head(3).to_dict('records')}")
                        
                        # Clean data
                        df_clean["Flat"] = df_clean["Flat"].astype(str).str.strip()
                        df_clean["Consumption"] = pd.to_numeric(df_clean["Consumption"], errors='coerce').fillna(0)
                        
                        # Remove invalid rows
                        before_count = len(df_clean)
                        df_clean = df_clean[
                            df_clean["Flat"].notna() & 
                            (df_clean["Flat"] != "") & 
                            (df_clean["Flat"] != "nan") &
                            (df_clean["Flat"] != "None") &
                            (~df_clean["Flat"].str.lower().str.contains("total|sum|grand", na=False))
                        ]
                        after_count = len(df_clean)
                        
                        # Store data with sheet info
                        df_clean["Sheet"] = sheet_name
                        all_data[sheet_name] = df_clean
                        
                        processing_logs.append(f"  ✅ Extracted {after_count} apartment records (removed {before_count - after_count} invalid rows)")
                        processing_logs.append(f"  📈 Consumption range: ₹{df_clean['Consumption'].min():.0f} - ₹{df_clean['Consumption'].max():.0f}")
                        
                        # Use the sheet with most data as primary
                        if apartment_data is None or len(df_clean) > len(apartment_data):
                            apartment_data = df_clean[["Flat", "Consumption"]].copy()
                            processing_logs.append(f"  🎯 Using '{sheet_name}' as primary data source ({len(df_clean)} records)")
                    
                    else:
                        missing_cols = []
                        if not flat_col:
                            missing_cols.append("apartment")
                        if not billed_col:
                            missing_cols.append("billing")
                        processing_logs.append(f"  ⚠️ Missing {', '.join(missing_cols)} columns in '{sheet_name}'")
                        processing_logs.append(f"      Available columns: {list(df.columns)}")
                
                else:
                    processing_logs.append(f"  ⚠️ No apartment data found in sheet '{sheet_name}'")
            
            except Exception as e:
                processing_logs.append(f"  ❌ Error processing sheet '{sheet_name}': {str(e)}")
                continue
        
        # Display processing logs in collapsible section
        with st.expander("🔍 Processing Logs (Click to expand)"):
            for log in processing_logs:
                st.text(log)
        
        if apartment_data is not None:
            st.success(f"✅ Successfully loaded apartment data with {len(apartment_data)} records")
            st.info(f"📊 Primary data source: {len([k for k, v in all_data.items() if len(v) == len(apartment_data)])} sheet(s) with {len(apartment_data)} records")
            return apartment_data, all_data
        else:
            st.error("❌ No apartment consumption data found in any sheet")
            st.error("🔍 Looking for sheets with both 'Apartment' columns AND billing/consumption columns")
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
                
                # Summary sheet with flat-level statistics
                summary_data = {
                    "Metric": ["Total Flats", "Active Flats", "Zero Usage", "New Consumers", 
                              "Major Increases", "Major Decreases", "Total Revenue Change", "Average Change per Flat"],
                    "Value": [len(merged), active_flats, len(zero_consumption), len(new_consumers),
                             len(major_increases), len(major_decreases), f"₹{total_change:,.0f}", f"₹{avg_change:.0f}"]
                }
                
                # Add block-wise summary
                if len(merged) > 0:
                    merged_with_blocks = merged.copy()
                    merged_with_blocks["Block"] = merged_with_blocks["Flat"].str[:1]
                    block_stats = merged_with_blocks.groupby("Block").agg({
                        "Consumption_this": ["count", "sum", "mean"],
                        "Change": "sum"
                    }).round(0)
                    block_stats.columns = ["Flats_Count", "Total_Consumption", "Avg_Consumption", "Total_Change"]
                    block_stats = block_stats.reset_index()
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)
                    block_stats.to_excel(writer, sheet_name="Block Summary", index=False)
                else:
                    summary_df = pd.DataFrame(summary_data)
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
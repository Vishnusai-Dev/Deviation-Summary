import pandas as pd
import streamlit as st
from io import BytesIO

def normalize_value(val):
    """Convert NaN/None to empty string and strip spaces."""
    if pd.isna(val):
        return ""
    return str(val).strip()

def find_deviations(df_input, df_output):
    deviations = []

    # Ensure column alignment
    common_headers = [h for h in df_input.columns if h in df_output.columns]

    if "Vendor SKU Code" not in df_input.columns:
        st.error("❌ 'Vendor SKU Code' column not found in Input sheet.")
        return None

    for idx, row in df_input.iterrows():
        row_output = df_output.loc[idx] if idx < len(df_output) else None
        if row_output is None:
            continue

        row_diff = {
            "Row Number": idx + 2,  # Excel-style row number
            "sku": row.get("Vendor SKU Code", ""),
            "Deviation Count": 0,
            "Missing Filled Count": 0,
            "Modified Count": 0
        }

        diffs = {}
        for col in common_headers:
            val_in = normalize_value(row[col])
            val_out = normalize_value(row_output[col])

            if val_in != val_out:
                diffs[col] = f"Old: {val_in} → New: {val_out}"
                row_diff["Deviation Count"] += 1
                if val_in == "" and val_out != "":
                    row_diff["Missing Filled Count"] += 1
                elif val_in != "" and val_out != "":
                    row_diff["Modified Count"] += 1

        if row_diff["Deviation Count"] > 0:
            row_diff.update(diffs)
            deviations.append(row_diff)

    return pd.DataFrame(deviations)

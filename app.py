import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Deviation Checker", layout="wide")

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
            "Row Number": idx + 2,  # +2 to match Excel row numbers (header + index offset)
            "sku": row["Vendor SKU Code"],
            "Deviation Count": 0,
            "Missing Filled Count": 0,
            "Modified Count": 0
        }

        diffs = {}
        for col in common_headers:
            val_in = str(row[col]).strip()
            val_out = str(row_output[col]).strip()

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


st.title("📊 Excel Deviation Checker")
st.write("Upload Input and Output Excel files to compare deviations.")

# Upload files
file_input = st.file_uploader("Upload Input Excel", type=["xlsx"])
file_output = st.file_uploader("Upload Output Excel", type=["xlsx"])

if file_input and file_output:
    # Read Excel sheets
    df_input = pd.read_excel(file_input, sheet_name="Input")
    df_output = pd.read_excel(file_output, sheet_name="Output")

    deviations_df = find_deviations(df_input, df_output)

    if deviations_df is not None and not deviations_df.empty:
        st.success(f"✅ Found {deviations_df['Deviation Count'].sum()} deviations.")
        st.dataframe(deviations_df, use_container_width=True)

        # Download deviations as Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            deviations_df.to_excel(writer, index=False, sheet_name="Deviations")

        st.download_button(
            label="📥 Download Deviations Report",
            data=output.getvalue(),
            file_name="deviations.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No deviations found ✅")

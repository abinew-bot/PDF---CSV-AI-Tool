import streamlit as st
import pdfplumber
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="PDF → CSV (AI)", page_icon="📄")
st.title("📄 PDF → CSV Converter (AI-ready)")
st.write("Upload any PDF and convert tables into clean CSV files.")

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded:
    with pdfplumber.open(uploaded) as pdf:
        all_tables = []
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                df["Page"] = i + 1
                all_tables.append(df)

        if all_tables:
            if len(all_tables) == 1:
                csv = all_tables[0].to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", csv, "output.csv", "text/csv")
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for idx, df in enumerate(all_tables):
                        zf.writestr(f"table_{idx+1}.csv", df.to_csv(index=False))
                st.download_button("⬇️ Download All Tables (ZIP)", zip_buffer.getvalue(), "tables.zip")
        else:
            st.warning("No tables found in PDF.")
else:
    st.info("Please upload a PDF file to begin.")
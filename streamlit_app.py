import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io
import re

st.set_page_config(page_title="PDF → CSV Converter", page_icon="📄")
st.title("📄 PDF → CSV Converter (Smart Cleanup)")

st.write(
    "Upload a PDF and convert it into structured CSV. "
    "Optionally use Smart Cleanup for better formatting."
)

# Sidebar
st.sidebar.header("Settings")
use_ai = st.sidebar.toggle("🧠 Smart Cleanup", value=True)

uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

def clean_text_rows(rows):
    # Remove empty lines and normalize spaces
    cleaned = []
    for row in rows:
        row = [re.sub(r"\s+", " ", c.strip()) for c in row if c.strip()]
        if row:
            cleaned.append(row)

    # Try to fix inconsistent column lengths
    max_len = max(len(r) for r in cleaned)
    fixed = [r + [""] * (max_len - len(r)) for r in cleaned]

    df = pd.DataFrame(fixed)

    # Auto-detect column names if patterns found
    header_candidates = ["date", "amount", "name", "desc", "id", "txn"]
    headers = []
    for i, col in enumerate(df.columns):
        sample = " ".join(df[col].astype(str).head(5)).lower()
        for h in header_candidates:
            if h in sample:
                headers.append(h.capitalize())
                break
        else:
            headers.append(f"Column_{i+1}")
    df.columns = headers

    return df

if uploaded:
    reader = PdfReader(uploaded)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    rows = [re.split(r"\s{2,}", line.strip()) for line in text.split("\n") if line.strip()]
    df = pd.DataFrame(rows)

    if use_ai:
        st.info("✨ Applying Smart Cleanup...")
        df = clean_text_rows(rows)
        st.success("✅ Smart cleanup complete!")

    st.dataframe(df.head(20))
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "output.csv", "text/csv")

else:
    st.info("📂 Please upload a PDF file to begin.")

import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io
import re
from openai import OpenAI

st.set_page_config(page_title="PDF → CSV Converter (AI)", page_icon="📄")
st.title("📄 PDF → CSV Converter (AI-Powered)")
st.write("Upload a PDF and convert it into clean CSV data. You can optionally use AI cleanup for better formatting.")

# Sidebar options
st.sidebar.header("Settings")
use_ai = st.sidebar.toggle("🧠 Use AI cleanup", value=False)

uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded:
    reader = PdfReader(uploaded)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    rows = [re.split(r"\s{2,}", line.strip()) for line in text.split("\n") if line.strip()]
    df = pd.DataFrame(rows)

    if use_ai:
        st.info("🧠 Cleaning table with AI... please wait")
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at formatting messy text data into clean CSV tables."},
                    {"role": "user", "content": f"Clean and format this data as a CSV table with headers:\n{text[:6000]}"}
                ],
                temperature=0
            )
            cleaned_csv = response.choices[0].message.content
            st.download_button("⬇️ Download Cleaned CSV (AI)", cleaned_csv, "cleaned_output.csv", "text/csv")
            st.success("✅ AI cleanup done!")
        except Exception as e:
            st.error(f"AI cleanup failed: {e}")
    else:
        st.dataframe(df.head(20))
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Raw CSV", csv, "output.csv", "text/csv")

else:
    st.info("Please upload a PDF file to begin.")

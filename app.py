import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
import google.generativeai as genai

# ✅ Your Gemini API Key
API_KEY = "AIzaSyD8AEZfTsb1HvMDIEJSYpCmyu-t5krXJ-M"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
    return text.strip()

def extract_text_from_docx(docx_file):
    text = ""
    try:
        doc = Document(docx_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {e}")
    return text.strip()

def extract_resume_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        st.error("❌ Unsupported file type. Only .pdf and .docx are supported.")
        return ""

def get_resume_score(resume_text, job_description):
    prompt = f"""
You are an AI recruitment assistant.

Compare the following resume with the given job description. Extract the candidate's:
- Technical Skills
- Years of Experience
- Educational Qualifications

Then rate the match as a percentage (0% to 100%) and explain why.

Job Description:
{job_description}

Resume:
{resume_text}

Return the output in the following format:
1. Extracted Technical Skills:
2. Years of Experience:
3. Educational Qualifications:
4. Resume Match Score (in %):
5. Reasoning:
"""
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---
st.set_page_config(page_title="Resume Match Analyzer", page_icon="📄", layout="centered")

# Custom CSS for dark theme
dark_grey = "#23272f"
css = f"""
<style>
body {{ background-color: {dark_grey}; }}
[data-testid="stAppViewContainer"] {{ background: {dark_grey}; }}
[data-testid="stHeader"] {{ background: {dark_grey}; }}
[data-testid="stSidebar"] {{ background: #181a20; }}
.stTextInput, .stTextArea, .stFileUploader {{ background: #2c2f36; color: #fff; }}
.stButton>button {{ background: #444654; color: #fff; border-radius: 8px; }}
.stMarkdown, .stText, .stTitle, .stHeader {{ color: #fff; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.title("📄 Resume Match Analyzer")
st.markdown("""
Upload a resume (**PDF** or **DOCX**) and paste the job description below. Get an instant AI-powered match analysis!
""")

uploaded_file = st.file_uploader("Upload Resume (.pdf or .docx)", type=["pdf", "docx"])
job_description = st.text_area("Paste Job Description", height=200)

if st.button("Analyze Resume"):
    if uploaded_file and job_description.strip():
        with st.spinner("Extracting resume text..."):
            resume_text = extract_resume_text(uploaded_file)
        if resume_text:
            st.success("Resume text extracted.")
            with st.spinner("Analyzing with Gemini..."):
                result = get_resume_score(resume_text, job_description)
            st.markdown("---")
            st.subheader("✅ Resume Match Analysis:")
            st.markdown(f"<div style='white-space: pre-wrap;'>{result}</div>", unsafe_allow_html=True)
    else:
        st.warning("Please upload a resume and enter a job description.")

import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
import google.generativeai as genai

# Load environment variables from .env (for local development)
load_dotenv()

API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not API_KEY:
    st.error("API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()
genai.configure(api_key=API_KEY)
# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")


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

# Custom CSS for dark theme and modern card UI
dark_grey = "#23272f"
css = f"""
<style>
body {{ background-color: {dark_grey}; }}
[data-testid="stAppViewContainer"] {{ background: {dark_grey}; }}
[data-testid="stHeader"] {{ background: {dark_grey}; }}
[data-testid="stSidebar"] {{ background: #181a20; }}

.main-card {{
    background: #262a32;
    border-radius: 18px;
    box-shadow: 0 4px 32px 0 rgba(0,0,0,0.25);
    padding: 2.5rem 2rem 2rem 2rem;
    max-width: 520px;
    margin: 2.5rem auto 2rem auto;
}}
.stTextInput, .stTextArea, .stFileUploader {{ background: #2c2f36 !important; color: #fff !important; border-radius: 8px; border: 1px solid #444654; }}
.stButton>button {{ background: linear-gradient(90deg, #444654 0%, #23272f 100%); color: #fff; border-radius: 8px; font-size: 1.1rem; padding: 0.6rem 1.5rem; border: none; }}
.stButton>button:hover {{ background: #5a5d6a; }}
.stMarkdown, .stText, .stTitle, .stHeader {{ color: #fff; }}
.result-box {{
    background: #23272f;
    border-radius: 12px;
    border: 1px solid #444654;
    padding: 1.5rem;
    margin-top: 1.5rem;
    font-size: 1.1rem;
    color: #fff;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.15);
}}
.stSpinner > div > div {{ color: #fff !important; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align:center; font-size:2.5rem; font-weight:700; margin-bottom:0.5rem;'>📄 Resume Match Analyzer</h1>
<p style='text-align:center; color:#b0b3b8; font-size:1.1rem;'>Upload a resume (<b>PDF</b> or <b>DOCX</b>) and paste the job description below.<br>Get an instant <span style='color:#00bfae;'>AI-powered</span> match analysis!</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Resume (.pdf or .docx)", type=["pdf", "docx"])
job_description = st.text_area("Paste Job Description", height=200)

analyze_btn = st.button("Analyze Resume")

if analyze_btn:
    if uploaded_file and job_description.strip():
        with st.spinner("Extracting resume text..."):
            resume_text = extract_resume_text(uploaded_file)
        if resume_text:
            st.success("Resume text extracted.")
            with st.spinner("Analyzing with Gemini..."):
                result = get_resume_score(resume_text, job_description)
            st.markdown("---")
            st.subheader("✅ Resume Match Analysis:")
            st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)
    else:
        st.warning("Please upload a resume and enter a job description.")

st.markdown('</div>', unsafe_allow_html=True)



from dotenv import load_dotenv
import base64
import streamlit as st
import os
import google.generativeai as genai
import pandas as pd
import PyPDF2 as pdf

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content, prompt])
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

st.set_page_config(page_title="ATS Resume Expert")
st.header("AI-Powered Resume Screening and Matching System")

input_text = st.text_area("Job Description: ", key="input")
uploaded_files = st.file_uploader("Upload your resumes (PDF)...", type=["pdf"], accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) > 0:
    st.write(f"{len(uploaded_files)} PDFs Uploaded Successfully")

submit = st.button("Evaluate Resumes")

prompt_name = """
Your task is to extract the full name of the candidate from the resume and just return the name. Name of candidate is always given in resume and posibly in the top part of the resume.
"""

prompt_review = """
You are an expert ATS system, and your task is to review the resume of the candidate based on the job description provided.
Provide an overview of the match between the resume and the job description. It should be short and crisp just for the HR to know about the candidate.
"""

prompt_match_percentage = """
As an ATS scanner, your task is to calculate the percentage match between the resume and the provided job description.
Give me the percentage, while calculating percentage keep in mind the skills and the work experience should be taken into consideration in the calculation. That should be according to the job description provided.
Just give the percentage match value nothing else. Give the score by calculating so that no one can question it.
"""

if submit:
    if uploaded_files is not None and len(uploaded_files) > 0:
        results = []
        
        for uploaded_file in uploaded_files:
            pdf_content = input_pdf_text(uploaded_file)
            name_response = get_gemini_response(prompt_name, pdf_content, input_text)
            review_response = get_gemini_response(prompt_review, pdf_content, input_text)
            match_response = get_gemini_response(prompt_match_percentage, pdf_content, input_text)
            match_percentage = round(float(match_response.strip().replace('%', '')), 2)
            results.append({
                'Name': name_response,
                'Resume Review': review_response,
                'Percentage Match': match_percentage
            })
        df = pd.DataFrame(results)
        df = df.sort_values(by='Percentage Match', ascending=False)
        df['Ranking'] = df['Percentage Match'].rank(method='first', ascending=False).astype(int)
        st.subheader("Evaluation Results (Sorted by Ranking)")
        st.table(df[['Name', 'Resume Review', 'Percentage Match', 'Ranking']])
        
    else:
        st.write("Please upload the resumes.")

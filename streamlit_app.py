# streamlit_app.py
import streamlit as st
from checker import run_full_audit
from report import generate_pdf_report
import os, tempfile

st.title("🏪 Digital Health Checker")
st.write("Check how visible your local business is online — free, in 60 seconds.")

business = st.text_input("Business Name", placeholder="e.g. Sharma Cafe")
city     = st.text_input("City", placeholder="e.g. Mumbai")
website  = st.text_input("Website URL (optional)", placeholder="e.g. https://sharmacafe.com")

if st.button("Run Audit 🔍") and business and city:
    with st.spinner("Checking Google, website, and social media..."):
        audit = run_full_audit(business, city, website)

    score = audit["score"]
    st.metric("Digital Health Score", f"{score['total']}/100", f"Grade: {score['grade']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Google", f"{score['google_score']}/40")
    col2.metric("Website", f"{score['website_score']}/40")
    col3.metric("Social", f"{score['social_score']}/20")

    st.subheader("💡 Recommendations")
    for tip in audit["recommendations"]:
        st.write(tip)

    # Generate + offer PDF download
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = generate_pdf_report(audit, tmp)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF Report", f, file_name="audit_report.pdf")
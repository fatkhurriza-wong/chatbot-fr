import streamlit as st
import requests
import PyPDF2
import io
from datetime import date

# n8n webhook URL
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/contract-upload"  # ganti sesuai URL n8n kamu

st.title("📑 Contract Uploader (to n8n Workflow)")

# === Step 1: Upload file ===
uploaded_file = st.file_uploader("Upload Contract (PDF or TXT)", type=["pdf", "txt"])

contract_text = ""
file_name = ""
if uploaded_file is not None:
    file_name = uploaded_file.name
    if uploaded_file.type == "application/pdf":
        # Extract text from PDF
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            contract_text += page.extract_text() or ""
    elif uploaded_file.type == "text/plain":
        contract_text = uploaded_file.read().decode("utf-8")

    st.success(f"Extracted {len(contract_text)} characters from {file_name}")

# === Step 2: Metadata form ===
with st.form("contract_form"):
    contract_id = st.text_input("Contract ID", value=f"CNT-{date.today().strftime('%Y%m%d')}")
    party = st.text_input("Party", value="ACME Corp")
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date(date.today().year, 12, 31))
    email_recipient = st.text_input("Email Recipient", value="legal@example.com")

    submitted = st.form_submit_button("Submit to n8n")

    if submitted:
        if not uploaded_file:
            st.error("Please upload a contract file first.")
        else:
            payload = {
                "contract_id": contract_id,
                "file_name": file_name,
                "party": party,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "email_recipient": email_recipient,
                "contract_text": contract_text,
            }
            try:
                resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
                if resp.status_code == 200:
                    st.success(f"✅ Sent to n8n! Response: {resp.json()}")
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Failed to send: {e}")

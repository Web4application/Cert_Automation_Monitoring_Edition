import streamlit as st
from cert_status import check_cert_status

st.set_page_config(page_title="Cert Monitor", page_icon="🔐")
st.title("🔐 ProjectPilotAI Certificate Monitor")
st.write("Track your device cert expiry and health in real-time.")

status = check_cert_status("certs/DeviceCert.cer")
st.metric("Days Until Expiry", f"{status['days_remaining']} days")
st.text(f"Subject: {status['subject']}")
st.text(f"Issuer: {status['issuer']}")
st.text(f"Expires On: {status['expiry'].strftime('%Y-%m-%d %H:%M:%S')}")

if status["days_remaining"] < 15:
    st.error("🚨 Certificate expiring soon! Time to renew.")
elif status["days_remaining"] < 0:
    st.warning("❌ Certificate is expired!")
else:
    st.success("✅ Certificate is healthy.")

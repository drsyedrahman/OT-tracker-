import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="OT Flow Tracker", layout="wide")
st.title("🛏️ OT Case Entry & Analytics")

if "logged_in" not in st.session_state:
    with st.form("login_form"):
        st.subheader("Doctor Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if user == "doctor1" and pwd == "password":
                st.session_state.logged_in = True
                st.success("Logged in successfully.")
            else:
                st.error("Invalid credentials")
    st.stop()

st.sidebar.header("📋 Enter OT Case")
with st.sidebar.form("ot_form"):
    date = st.date_input("Date")
    patient = st.text_input("Patient Name")
    operation = st.text_input("Operation Name")
    received = st.time_input("Time Received")
    shifted = st.time_input("Time Shifted to OT")
    ana_start = st.time_input("Anaesthesia Start")
    ana_end = st.time_input("Anaesthesia End")
    surg_start = st.time_input("Surgery Start")
    surg_end = st.time_input("Surgery End")
    recov_in = st.time_input("Recovery In")
    recov_out = st.time_input("Recovery Out")
    comment = st.text_area("Issues / Comments", height=100)
    submit_case = st.form_submit_button("Add Case")

    if submit_case:
        get_dt = lambda t: datetime.datetime.combine(date, t)
        data = {
            "Date": date,
            "Patient": patient,
            "Operation": operation,
            "Received": received,
            "Shifted": shifted,
            "Anaesthesia Start": ana_start,
            "Anaesthesia End": ana_end,
            "Surgery Start": surg_start,
            "Surgery End": surg_end,
            "Recovery In": recov_in,
            "Recovery Out": recov_out,
            "Gap: Received ➝ Shifted (min)": (get_dt(shifted) - get_dt(received)).total_seconds() / 60,
            "Gap: Shifted ➝ Anaesthesia Start (min)": (get_dt(ana_start) - get_dt(shifted)).total_seconds() / 60,
            "Gap: Anaesthesia ➝ Incision (min)": (get_dt(surg_start) - get_dt(ana_start)).total_seconds() / 60,
            "Gap: Closure ➝ Recovery In (min)": (get_dt(recov_in) - get_dt(surg_end)).total_seconds() / 60,
            "Anaesthesia Duration (min)": (get_dt(ana_end) - get_dt(ana_start)).total_seconds() / 60,
            "Surgery Duration (min)": (get_dt(surg_end) - get_dt(surg_start)).total_seconds() / 60,
            "Recovery Duration (min)": (get_dt(recov_out) - get_dt(recov_in)).total_seconds() / 60,
            "Comments": comment
        }
        if "cases" not in st.session_state:
            st.session_state.cases = []
        st.session_state.cases.append(data)
        st.success("Case saved successfully.")

if "cases" in st.session_state and st.session_state.cases:
    df = pd.DataFrame(st.session_state.cases)
    st.subheader("📄 OT Case Log")
    st.dataframe(df)

    df['Month'] = pd.to_datetime(df['Date']).dt.to_period("M")
    summary = df.groupby("Month")[[
        "Anaesthesia Duration (min)",
        "Surgery Duration (min)",
        "Recovery Duration (min)"
    ]].mean().reset_index()

    st.subheader("📊 Monthly Average Durations")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(summary['Month'].astype(str), summary['Anaesthesia Duration (min)'], label="Anaesthesia", color="skyblue")
    ax.bar(summary['Month'].astype(str), summary['Surgery Duration (min)'],
           bottom=summary['Anaesthesia Duration (min)'], label="Surgery", color="lightgreen")
    ax.bar(summary['Month'].astype(str), summary['Recovery Duration (min)'],
           bottom=summary['Anaesthesia Duration (min)'] + summary['Surgery Duration (min)'],
           label="Recovery", color="orange")
    ax.set_ylabel("Minutes")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("No OT cases entered yet.")

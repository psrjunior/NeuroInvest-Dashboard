
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import uuid
from datetime import datetime, timedelta
from zipfile import ZipFile
from PIL import Image
import matplotlib.pyplot as plt

# App version
APP_VERSION = "1.1.0"

# Page config
st.set_page_config(
    page_title="NeuroBase",
    page_icon="🧠",
    layout="wide"
)

# Custom vibrant CSS
st.markdown("""
<style>
    body { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    .main-header { font-size: 3rem; color: #ffffff; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.8rem; color: #ffffff; margin-bottom: 0.5rem; }
    .card { background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .skill-tag { background-color: #6a11cb; color: #ffffff; padding: 6px 12px; border-radius: 12px; margin: 4px; display: inline-block; }
    .metric-card { background-color: #ff9a9e; border-radius: 10px; padding: 15px; text-align: center; color: #ffffff; }
    .calendar-day-today { background: #43cea2; color: #ffffff; border-radius: 50%; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Simulation data
def generate_demo_data():
    patients = []
    for i in range(5):
        patients.append({
            'id': str(uuid.uuid4()),
            'name': f"Patient {i+1}",
            'dob': (datetime.now() - timedelta(days=365*(10+i))).strftime('%Y-%m-%d'),
            'diagnosis': 'TEA' if i%2==0 else 'TDAH'
        })
    sessions = []
    for i in range(15):
        sessions.append({
            'id': str(uuid.uuid4()),
            'patient_id': patients[i%5]['id'],
            'date': (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d'),
            'therapist': 'Demo Therapist',
            'skills': 'Equilíbrio estático, Coordenação motora fina',
            'notes': f"Session notes {i+1}"
        })
    return pd.DataFrame(patients), pd.DataFrame(sessions)

patients_df, sessions_df = generate_demo_data()

# Sidebar
st.sidebar.title("NeuroBase")
st.sidebar.markdown(f"Version {APP_VERSION}")
menu = st.sidebar.radio("Menu", ["Dashboard", "Patients", "Sessions"])

# Dashboard
if menu == "Dashboard":
    st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Patients", len(patients_df))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        today = datetime.now().strftime('%Y-%m-%d')
        st.metric("Sessions Today", len(sessions_df[sessions_df['date']==today]))
        st.markdown("</div>", unsafe_allow_html=True)

# Patients page
elif menu == "Patients":
    st.markdown("<h1 class='main-header'>Patients</h1>", unsafe_allow_html=True)
    for _, p in patients_df.iterrows():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(p['name'])
        age = (datetime.now() - datetime.strptime(p['dob'], '%Y-%m-%d')).days//365
        st.write(f"Age: {age}")
        st.write(f"Diagnosis: {p['diagnosis']}")
        st.markdown("</div>", unsafe_allow_html=True)

# Sessions page
elif menu == "Sessions":
    st.markdown("<h1 class='main-header'>Sessions</h1>", unsafe_allow_html=True)
    patient_options = ["All"] + patients_df['id'].tolist()
    selected = st.selectbox("Filter by patient", options=patient_options, format_func=lambda x: "All Patients" if x=="All" else patients_df[patients_df['id']==x]['name'].iloc[0])
    df = sessions_df if selected=="All" else sessions_df[sessions_df['patient_id']==selected]
    for _, s in df.sort_values('date', ascending=False).iterrows():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"**Date:** {s['date']}")
        st.write(f"**Therapist:** {s['therapist']}")
        tags = s['skills'].split(',')
        for t in tags:
            st.markdown(f"<span class='skill-tag'>{t.strip()}</span>", unsafe_allow_html=True)
        st.write(s['notes'])
        st.markdown("</div>", unsafe_allow_html=True)

import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine
import mysql.connector

st.markdown("""
    <div style='text-align:center; background:linear-gradient(to right, #ffffff, #fdf5e6);
                padding:20px; border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
        <h1 style='color:#B22222; font-size:46px; font-family:Georgia;'>🏛 Harvard Artifact Explorer</h1>
        <p style='color:#333333; font-size:20px; font-family:Trebuchet MS;'>
            Discover the beauty of history with <b style='color:#DAA520;'>golden insights</b> into Harvard Art Museum artifacts.
        </p>
    </div>
""", unsafe_allow_html=True)

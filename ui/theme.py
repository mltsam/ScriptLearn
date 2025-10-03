# ui/theme.py
import os, streamlit as st

def inject_css(path: str) -> None:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("CSS file not found! Ensure 'assets/styles.css' exists.")

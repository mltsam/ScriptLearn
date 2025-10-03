# ui/downloads.py
import json
import streamlit as st
from datetime import datetime

def render_downloads(data):
    st.markdown("## 📥 Download Results")
    c1, c2 = st.columns(2)
    with c1:
        full = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            "📄 Download Full Results (JSON)",
            data=full.encode("utf-8"),
            file_name=f"subtitle_alignment_{ts()}.json",
            mime="application/json",
        )
    with c2:
        acc = [d for d in data if d.get("accepted")]
        acc_json = json.dumps(acc, ensure_ascii=False, indent=2)
        st.download_button(
            "✅ Download Accepted Only (JSON)",
            data=acc_json.encode("utf-8"),
            file_name=f"accepted_alignments_{ts()}.json",
            mime="application/json",
        )

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

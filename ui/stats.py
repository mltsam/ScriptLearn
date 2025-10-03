# ui/stats.py
import streamlit as st

def _num(data, key, default=0.0):
    return sum(d.get(key, 0.0) for d in data)

def render_statistics(data):
    total = len(data)
    accepted = sum(1 for d in data if d.get("accepted"))
    rejected = total - accepted
    avg_conf = (_num(data, "confidence") / total) if total else 0.0

    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(box(total, "Total Pairs", "var(--accent-blue)"), unsafe_allow_html=True)
    c2.markdown(box(accepted, "Accepted", "var(--accent-green)"), unsafe_allow_html=True)
    c3.markdown(box(rejected, "Rejected", "var(--accent-orange)"), unsafe_allow_html=True)
    c4.markdown(box(f"{avg_conf:.2f}", "Avg Confidence", "var(--accent-purple)"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def box(value, label, color):
    return f"""
    <div class="stat-card">
      <div class="stat-number" style="color:{color};">{value}</div>
      <div class="stat-label">{label}</div>
    </div>
    """

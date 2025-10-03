# ui/pairs.py
import streamlit as st

def _fmt(t) -> str:
    """MM:SS or —:— for None/invalid."""
    if t is None:
        return "—:—"
    try:
        t = float(t)
    except (TypeError, ValueError):
        return "—:—"
    if t < 0:
        t = 0.0
    m, s = divmod(int(t), 60)
    return f"{m:02d}:{s:02d}"

def _conf_class(c: float) -> str:
    return "confidence-high" if c >= 0.8 else ("confidence-medium" if c >= 0.6 else "confidence-low")

def _pair_html(p, i: int):
    fa, en = p.get("fa_text", "N/A"), p.get("en_text", "N/A")
    c, acc = p.get("confidence", 0.0), p.get("accepted", False)
    fs, es = p.get("fa_start"), p.get("en_start")  # may be None
    pcls = "accepted" if acc else "rejected"
    scls = "status-accepted" if acc else "status-rejected"
    icon, txt = ("✓", "ACCEPTED") if acc else ("✗", "REJECTED")
    cc = _conf_class(c)
    return f"""
    <div class="dialogue-pair {pcls}" style="--d:{i};">
      <div class="subtitle-persian">{fa}</div>
      <div class="subtitle-english">{en}</div>
      <div class="subtitle-meta">
        <div class="time-info">
          <span class="time-badge">FA: {_fmt(fs)}</span>
          <span class="time-badge">EN: {_fmt(es)}</span>
        </div>
        <div>
          <span class="confidence-badge {cc}">{c:.2f}</span>
          <span class="status-indicator {scls}">{icon} {txt}</span>
        </div>
      </div>
    </div>"""

def render_dialogue_results(data):
    st.markdown("## 💬 Subtitle Alignment Results")
    opt = st.selectbox("Show:", ["All pairs", "Accepted only", "Rejected only"], 0)

    if opt == "Accepted only":
        data = [d for d in data if d.get("accepted")]
        filter_attr = ' data-filter="accepted"'
    elif opt == "Rejected only":
        data = [d for d in data if not d.get("accepted")]
        filter_attr = ' data-filter="rejected"'
    else:
        filter_attr = ""

    st.markdown(f'<div class="dialogue-container"{filter_attr}>', unsafe_allow_html=True)

    lim = min(50, len(data))
    if len(data) > lim:
        st.info(f"Showing first {lim} / {len(data)} pairs")

    for i, p in enumerate(data[:lim]):
        st.markdown(_pair_html(p, i), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

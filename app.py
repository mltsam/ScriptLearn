# app.py
import os, json, tempfile, traceback
from datetime import datetime
import streamlit as st
from align.processor import SubtitleProcessor
from align.offset import iterative_find_and_apply_offset
from ui.theme import inject_css
from ui.stats import render_statistics
from ui.downloads import render_downloads
from exporters.ebook import render_ebook_export

st.set_page_config("Subtitle Aligner", layout="wide", initial_sidebar_state="collapsed")
inject_css(os.path.join("assets", "styles.css"))

# Initialize session state
if 'alignment_data' not in st.session_state:
    st.session_state.alignment_data = None
if 'fa_subs' not in st.session_state:
    st.session_state.fa_subs = None
if 'en_path' not in st.session_state:
    st.session_state.en_path = None
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'final_offset' not in st.session_state:
    st.session_state.final_offset = 0.0

# Enhanced hero section with animated elements
st.markdown("""
    <div class="hero-container">
        <h1 class="animated-title">🎬 Subtitle Aligner</h1>
        <p class="subtitle-text pulse-text">Aligned, clean, bilingual dialogues → eBooks</p>
        <div class="hero-decoration">
            <span class="deco-dot"></span>
            <span class="deco-dot"></span>
            <span class="deco-dot"></span>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        t_tol = st.number_input("⏱️ Time tolerance (s)", 0.1, 10.0, 2.0, 0.1,
                                help="Maximum time difference for alignment")
        conf_thr = st.slider("🎯 Confidence threshold", 0.0, 1.0, 0.65, 0.01,
                             help="Minimum confidence for accepting pairs")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        init_off = st.number_input("🔧 Initial EN time offset (s)", value=2.0, step=0.1,
                                   help="Starting offset for English subtitles")
        max_iters = st.slider("🔄 Max offset iterations", 1, 6, 3,
                              help="Iterations for finding optimal offset")
        mode = st.selectbox("📊 Offset compute mode", ['accepted', 'top_combined', 'all'], 0,
                            help="Method for calculating offset")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div class="legend-box">
            <div class="legend-item">
                <span class="legend-dot accepted"></span>
                <span>Accepted pairs</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot rejected"></span>
                <span>Rejected pairs</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Enhanced file upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="upload-card upload-left">', unsafe_allow_html=True)
    fa_up = st.file_uploader("📁 Upload Persian SRT", ["srt"], key="fa_upload")
    if fa_up:
        st.markdown('<div class="file-status success">✓ File loaded</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-card upload-right">', unsafe_allow_html=True)
    en_up = st.file_uploader("📁 Upload English SRT", ["srt"], key="en_upload")
    if en_up:
        st.markdown('<div class="file-status success">✓ File loaded</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# Function to render animated subtitle pairs
def render_animated_subtitles(data, max_display=50):
    st.markdown("""
        <div class="section-divider">
            <span class="divider-text">🎬 Subtitle Alignments</span>
        </div>
    """, unsafe_allow_html=True)

    # Handle both dict and list formats
    if isinstance(data, dict):
        pairs_to_show = data.get('pairs', [])[:max_display]
        total_pairs = len(data.get('pairs', []))
    else:
        pairs_to_show = data[:max_display]
        total_pairs = len(data)

    for idx, pair in enumerate(pairs_to_show):
        # Handle different data formats
        if isinstance(pair, dict):
            status = pair.get('status', 'unknown')
            confidence = pair.get('confidence', 0)
            fa_text = pair.get('fa_text', pair.get('persian', 'N/A'))
            en_text = pair.get('en_text', pair.get('english', 'N/A'))
            fa_time = pair.get('fa_time', pair.get('fa_start', 'N/A'))
            en_time = pair.get('en_time', pair.get('en_start', 'N/A'))
        else:
            # If pair is a tuple or list
            status = 'unknown'
            confidence = 0
            fa_text = str(pair[0]) if len(pair) > 0 else 'N/A'
            en_text = str(pair[1]) if len(pair) > 1 else 'N/A'
            fa_time = 'N/A'
            en_time = 'N/A'

        status_class = 'accepted' if status == 'accepted' else 'rejected'
        conf_class = 'high' if confidence > 0.7 else 'low'

        st.markdown(f"""
            <div class="subtitle-pair-container">
                <div class="subtitle-pair {status_class}">
                    <div class="subtitle-header">
                        <span class="subtitle-time">FA: {fa_time} → EN: {en_time}</span>
                        <span class="subtitle-confidence {conf_class}">
                            {confidence:.2f}
                        </span>
                    </div>
                    <div class="subtitle-text-container">
                        <div class="subtitle-fa">
                            <div class="subtitle-label">🇮🇷 Persian</div>
                            <div class="subtitle-content">{fa_text}</div>
                        </div>
                        <div class="subtitle-en">
                            <div class="subtitle-label">🇬🇧 English</div>
                            <div class="subtitle-content">{en_text}</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if total_pairs > max_display:
        st.info(f"📊 Showing first {max_display} pairs out of {total_pairs} total pairs")


# Enhanced action button
if fa_up and en_up:
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("🚀 Start Alignment", use_container_width=True):
        try:
            # Progress indicator
            st.markdown("""
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <p class="progress-text">Processing your files...</p>
                </div>
            """, unsafe_allow_html=True)

            tmp = tempfile.gettempdir()
            fa_path = os.path.join(tmp, f"fa_{datetime.now().timestamp()}.srt")
            en_path = os.path.join(tmp, f"en_{datetime.now().timestamp()}.srt")
            with open(fa_path, "wb") as f:
                f.write(fa_up.getbuffer())
            with open(en_path, "wb") as f:
                f.write(en_up.getbuffer())

            proc = SubtitleProcessor(time_tolerance=t_tol, confidence_threshold=conf_thr)

            with st.spinner("🔄 Detecting global offset..."):
                verbose = os.path.join(tmp, "alignment_verbose.json")
                final_off = iterative_find_and_apply_offset(proc, fa_path, en_path, verbose, init_off, max_iters, mode)

            fa_subs = proc.parse_srt_file(fa_path)
            en_subs = proc.parse_srt_file(en_path, time_offset=final_off)
            data = proc.align_subtitles_verbose(fa_subs, en_subs, save_path=os.path.join(tmp, "final_alignment.json"))

            # Store in session state
            st.session_state.alignment_data = data
            st.session_state.fa_subs = fa_subs
            st.session_state.en_path = en_path
            st.session_state.processor = proc
            st.session_state.final_offset = final_off

            # Animated success message
            st.markdown(f"""
                <div class="success-banner">
                    <div class="success-icon">✓</div>
                    <div class="success-content">
                        <h3>Alignment Complete!</h3>
                        <p>Final offset applied: <strong>{final_off:.3f}s</strong></p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            render_statistics(data)
            render_animated_subtitles(data)

        except Exception:
            st.markdown("""
                <div class="error-banner">
                    <div class="error-icon">⚠</div>
                    <div class="error-content">
                        <h3>Processing Error</h3>
                        <p>Something went wrong during alignment</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

# Show manual tuning and export options if alignment data exists
if st.session_state.alignment_data is not None:
    # Enhanced manual tuning section
    st.markdown("""
        <div class="section-divider">
            <span class="divider-text">🔧 Fine-Tuning</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tuning-card">', unsafe_allow_html=True)
    man_off = st.number_input("Adjust English offset manually (s):",
                              float(st.session_state.final_offset),
                              step=0.01, format="%.3f",
                              help="Fine-tune the offset if needed",
                              key="manual_offset")

    if st.button("🔄 Re-align with manual offset", use_container_width=True, key="realign_btn"):
        try:
            with st.spinner("Re-processing..."):
                en_manual = st.session_state.processor.parse_srt_file(
                    st.session_state.en_path,
                    time_offset=man_off
                )
                data = st.session_state.processor.align_subtitles_verbose(
                    st.session_state.fa_subs,
                    en_manual
                )
                st.session_state.alignment_data = data
                st.session_state.final_offset = man_off

            st.markdown(f"""
                <div class="success-banner mini">
                    <div class="success-icon">✓</div>
                    <p>Re-alignment complete @ <strong>{man_off:.3f}s</strong></p>
                </div>
            """, unsafe_allow_html=True)

            render_statistics(data)
            render_animated_subtitles(data)
        except Exception:
            st.error("❌ Error during re-alignment")
            st.code(traceback.format_exc())

    st.markdown('</div>', unsafe_allow_html=True)

    # Export section
    st.markdown("""
        <div class="section-divider">
            <span class="divider-text">📥 Export & Download</span>
        </div>
    """, unsafe_allow_html=True)

    render_downloads(st.session_state.alignment_data)
    render_ebook_export(st.session_state.alignment_data)

elif not (fa_up and en_up):
    st.markdown("""
        <div class="info-banner">
            <div class="info-icon">👆</div>
            <div class="info-content">
                <h3>Ready to Start</h3>
                <p>Upload both Persian and English subtitle files to begin alignment</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
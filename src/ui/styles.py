import streamlit as st

# ---------------------------------------------------------------------------
# Màu bounding box theo loại xe
# ---------------------------------------------------------------------------
CLASS_COLORS = {
    "xe buyt": (255, 165,   0),   # cam
    "xe hoi":  (  0, 200, 100),   # xanh lá
    "xe may":  ( 30, 144, 255),   # xanh dương
    "xe tai":  (220,  50,  50),   # đỏ
}
DEFAULT_COLOR = (128, 0, 255)  # tím cho class không xác định

def get_class_color(label: str):
    return CLASS_COLORS.get(label.lower(), DEFAULT_COLOR)

def apply_custom_css():
    st.markdown("""
    <style>
    /* ===== Global ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0d1b2a 100%);
        color: #e2e8f0;
    }

    /* ===== Header gradient banner ===== */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d2137 40%, #162032 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 8px 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* ===== Metric cards ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 20px 18px;
        text-align: center;
        transition: border-color 0.3s;
    }
    .metric-card:hover { border-color: rgba(56,189,248,0.3); }
    .metric-icon { font-size: 1.6rem; margin-bottom: 6px; }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #38bdf8;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }

    /* ===== Video frame container ===== */
    .video-container {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 12px;
    }

    /* ===== Status badge ===== */
    .status-running {
        display: inline-block;
        background: rgba(52,211,153,0.15);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.3);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .status-stopped {
        display: inline-block;
        background: rgba(248,113,113,0.15);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.3);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .status-idle {
        display: inline-block;
        background: rgba(148,163,184,0.1);
        color: #94a3b8;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stSlider > div { color: #e2e8f0; }

    /* ===== Buttons ===== */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 12px 0;
        border: none;
        transition: all 0.25s ease;
    }
    div[data-testid="stButton"]:first-of-type > button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
    }
    div[data-testid="stButton"]:first-of-type > button:hover {
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(14,165,233,0.35);
    }

    /* ===== Dataframe ===== */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ===== Divider ===== */
    hr { border-color: rgba(255,255,255,0.07) !important; }

    /* ===== Violation Cards ===== */
    .violation-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px;
        margin-top: 15px;
        max-height: 400px;
        overflow-y: auto;
    }
    .violation-card {
        background: rgba(248, 113, 113, 0.08);
        border: 1px solid rgba(248, 113, 113, 0.2);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s;
    }
    .violation-card:hover {
        border-color: rgba(248, 113, 113, 0.4);
        background: rgba(248, 113, 113, 0.12);
    }
    .violation-title {
        color: #f87171;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }
    .violation-details {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 2px;
    }
    .violation-speed {
        color: #ef4444;
        font-weight: 800;
        font-size: 1.25rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }

    /* ===== Hide Streamlit branding ===== */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

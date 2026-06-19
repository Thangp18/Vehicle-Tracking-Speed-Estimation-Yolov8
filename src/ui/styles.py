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

# ---------------------------------------------------------------------------
# Accent colors cho metric cards
# ---------------------------------------------------------------------------
METRIC_COLORS = {
    "total":      "#22d3ee",  # cyan
    "avg_speed":  "#34d399",  # emerald
    "max_speed":  "#fbbf24",  # amber
    "fps":        "#a78bfa",  # violet
    "violations": "#fb7185",  # rose
}

def get_class_color(label: str):
    return CLASS_COLORS.get(label.lower(), DEFAULT_COLOR)

def apply_custom_css():
    st.markdown("""
    <style>
    /* ===== Google Font ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ===== Global ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 40%, #0f172a 70%, #0a1628 100%);
        background-attachment: fixed;
        color: #e2e8f0;
    }

    /* ===== Animated Gradient Mesh Overlay ===== */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(ellipse 600px 400px at 15% 20%, rgba(34,211,238,0.04) 0%, transparent 70%),
            radial-gradient(ellipse 500px 500px at 85% 70%, rgba(139,92,246,0.04) 0%, transparent 70%),
            radial-gradient(ellipse 400px 300px at 50% 90%, rgba(251,113,133,0.03) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: meshShift 20s ease-in-out infinite alternate;
    }
    @keyframes meshShift {
        0%   { opacity: 0.6; }
        50%  { opacity: 1; }
        100% { opacity: 0.7; }
    }

    /* ===== Hero Banner ===== */
    .hero-banner {
        background: linear-gradient(135deg, #0f2337 0%, #162544 40%, #1a1f3a 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 4px 30px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -60%;
        right: -15%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(56,189,248,0.07) 0%, transparent 60%);
        animation: heroPulse 8s ease-in-out infinite alternate;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139,92,246,0.05) 0%, transparent 60%);
        animation: heroPulse 10s ease-in-out infinite alternate-reverse;
    }
    @keyframes heroPulse {
        0%   { transform: scale(1); opacity: 0.5; }
        100% { transform: scale(1.15); opacity: 1; }
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 40%, #34d399 80%, #38bdf8 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 10px 0;
        position: relative;
        z-index: 1;
        animation: gradientText 6s linear infinite;
    }
    @keyframes gradientText {
        0%   { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.92rem;
        margin: 0;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }
    .hero-badges {
        display: flex;
        gap: 8px;
        margin-top: 14px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 500;
        color: #94a3b8;
        backdrop-filter: blur(8px);
    }

    /* ===== Metric Cards — Horizontal Grid ===== */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    @media (max-width: 900px) {
        .metric-row {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    @media (max-width: 600px) {
        .metric-row {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .metric-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
        opacity: 0.8;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    /* Per-metric accent colors */
    .metric-card.mc-cyan::before    { background: linear-gradient(90deg, #22d3ee, #06b6d4); }
    .metric-card.mc-cyan:hover      { border-color: rgba(34,211,238,0.3); box-shadow: 0 8px 32px rgba(34,211,238,0.1); }
    .metric-card.mc-cyan .metric-value { color: #22d3ee; }

    .metric-card.mc-emerald::before { background: linear-gradient(90deg, #34d399, #10b981); }
    .metric-card.mc-emerald:hover   { border-color: rgba(52,211,153,0.3); box-shadow: 0 8px 32px rgba(52,211,153,0.1); }
    .metric-card.mc-emerald .metric-value { color: #34d399; }

    .metric-card.mc-amber::before   { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
    .metric-card.mc-amber:hover     { border-color: rgba(251,191,36,0.3); box-shadow: 0 8px 32px rgba(251,191,36,0.1); }
    .metric-card.mc-amber .metric-value { color: #fbbf24; }

    .metric-card.mc-violet::before  { background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
    .metric-card.mc-violet:hover    { border-color: rgba(167,139,250,0.3); box-shadow: 0 8px 32px rgba(167,139,250,0.1); }
    .metric-card.mc-violet .metric-value { color: #a78bfa; }

    .metric-card.mc-rose::before    { background: linear-gradient(90deg, #fb7185, #f43f5e); }
    .metric-card.mc-rose:hover      { border-color: rgba(251,113,133,0.3); box-shadow: 0 8px 32px rgba(251,113,133,0.1); }
    .metric-card.mc-rose .metric-value { color: #fb7185; }

    .metric-icon { font-size: 1.5rem; margin-bottom: 6px; }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    .metric-unit {
        font-size: 0.85rem;
        font-weight: 400;
        color: #64748b;
    }
    .metric-label {
        font-size: 0.68rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 6px;
        font-weight: 500;
    }

    /* ===== Video Container ===== */
    .video-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    /* ===== Status Badges ===== */
    .status-running {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        border-radius: 24px;
        padding: 6px 18px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .status-running .pulse-dot {
        width: 8px; height: 8px;
        background: #34d399;
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(52,211,153,0.5);
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.4); opacity: 0.5; }
    }

    .status-stopped {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(34,211,238,0.1);
        color: #22d3ee;
        border: 1px solid rgba(34,211,238,0.25);
        border-radius: 24px;
        padding: 6px 18px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .status-idle {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(148,163,184,0.08);
        color: #94a3b8;
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 24px;
        padding: 6px 18px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1322 0%, #0f172a 50%, #0a1020 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stSlider > div { color: #e2e8f0; }

    .sidebar-brand {
        text-align: center;
        padding: 16px 0 8px;
    }
    .sidebar-brand-icon {
        font-size: 2.8rem;
        margin-bottom: 4px;
        filter: drop-shadow(0 0 12px rgba(56,189,248,0.3));
    }
    .sidebar-brand-title {
        font-weight: 800;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sidebar-brand-sub {
        font-size: 0.7rem;
        color: #475569;
        margin-top: 2px;
    }
    .sidebar-brand-ver {
        display: inline-block;
        background: rgba(56,189,248,0.12);
        color: #38bdf8;
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 12px;
        padding: 1px 8px;
        font-size: 0.6rem;
        font-weight: 600;
        margin-top: 6px;
    }

    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 6px 0 4px;
        margin-top: 4px;
    }

    /* ===== Buttons ===== */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 12px 0;
        border: none;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        letter-spacing: 0.02em;
    }

    /* Start button */
    .start-btn button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(14,165,233,0.25);
    }
    .start-btn button:hover {
        background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(14,165,233,0.35) !important;
    }

    /* Stop button */
    .stop-btn button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(239,68,68,0.2);
    }
    .stop-btn button:hover {
        background: linear-gradient(135deg, #f87171, #ef4444) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(239,68,68,0.3) !important;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #64748b;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background: rgba(255,255,255,0.04);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56,189,248,0.1) !important;
        color: #38bdf8 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #38bdf8 !important;
        border-radius: 2px;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ===== Dataframes ===== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
        margin: 16px 0 !important;
    }

    /* ===== Violation Cards ===== */
    .violation-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 12px;
        margin-top: 12px;
        max-height: 420px;
        overflow-y: auto;
    }
    /* Custom scrollbar */
    .violation-container::-webkit-scrollbar {
        width: 5px;
    }
    .violation-container::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
        border-radius: 5px;
    }
    .violation-container::-webkit-scrollbar-thumb {
        background: rgba(248,113,113,0.3);
        border-radius: 5px;
    }
    .violation-container::-webkit-scrollbar-thumb:hover {
        background: rgba(248,113,113,0.5);
    }

    .violation-card {
        background: rgba(248, 113, 113, 0.06);
        border: 1px solid rgba(248, 113, 113, 0.15);
        border-left: 3px solid;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-12px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    /* Severity colors via inline border-left-color */
    .violation-card:hover {
        background: rgba(248, 113, 113, 0.1);
        border-color: rgba(248, 113, 113, 0.3);
        transform: translateX(4px);
    }
    .violation-title {
        color: #f87171;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
    }
    .violation-details {
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 3px;
    }
    .violation-speed {
        color: #ef4444;
        font-weight: 800;
        font-size: 1.3rem;
        text-shadow: 0 0 16px rgba(239, 68, 68, 0.25);
        white-space: nowrap;
    }

    /* ===== Section Headers ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
    .section-header-icon {
        font-size: 1.3rem;
    }
    .section-header-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .section-header-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
    }

    /* ===== Idle Screen ===== */
    .idle-screen {
        height: 380px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #334155;
        border: 2px dashed rgba(56,189,248,0.15);
        border-radius: 16px;
        gap: 14px;
        background: rgba(255,255,255,0.01);
        position: relative;
        overflow: hidden;
        animation: borderPulse 4s ease-in-out infinite;
    }
    @keyframes borderPulse {
        0%, 100% { border-color: rgba(56,189,248,0.1); }
        50%      { border-color: rgba(56,189,248,0.25); }
    }
    .idle-icon {
        font-size: 3.5rem;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50%      { transform: translateY(-8px); }
    }
    .idle-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #64748b;
    }
    .idle-sub {
        font-size: 0.82rem;
        color: #475569;
    }
    .idle-steps {
        display: flex;
        gap: 24px;
        margin-top: 8px;
    }
    .idle-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        font-size: 0.72rem;
        color: #475569;
    }
    .idle-step-num {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.2);
        color: #38bdf8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.7rem;
    }

    /* ===== Download Cards ===== */
    .download-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }
    .download-card:hover {
        border-color: rgba(56,189,248,0.2);
        background: rgba(255,255,255,0.05);
    }
    .download-card-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin-bottom: 6px;
    }
    .download-card-desc {
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 12px;
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* ===== Hide Streamlit branding ===== */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """, unsafe_allow_html=True)

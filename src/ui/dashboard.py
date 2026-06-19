import streamlit as st
import pandas as pd
import os

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


# ---------------------------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------------------------
def render_header():
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🚗 Vehicle Speed Estimation System</p>
        <p class="hero-subtitle">
            Nhận diện & theo dõi phương tiện theo thời gian thực với <strong>YOLOv8</strong>
            và ước tính tốc độ qua thuật toán <strong>Homography</strong>.
            Thiết lập tham số tại sidebar rồi nhấn <em>Bắt đầu</em>.
        </p>
        <div class="hero-badges">
            <span class="hero-badge">🧠 YOLOv8</span>
            <span class="hero-badge">📐 Homography</span>
            <span class="hero-badge">🎯 4 Classes</span>
            <span class="hero-badge">📊 EMA Filter</span>
            <span class="hero-badge">⚡ Real-time</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Status Badge
# ---------------------------------------------------------------------------
def render_status(placeholder, status):
    if status == "running":
        placeholder.markdown(
            '<span class="status-running"><span class="pulse-dot"></span> Đang xử lý…</span>',
            unsafe_allow_html=True
        )
    elif status == "stopped":
        placeholder.markdown(
            '<span class="status-stopped">✔ Hoàn tất xử lý — Xem kết quả bên dưới</span>',
            unsafe_allow_html=True
        )
    else:
        placeholder.markdown(
            '<span class="status-idle">○ Chờ bắt đầu</span>',
            unsafe_allow_html=True
        )


# ---------------------------------------------------------------------------
# Metric Cards — 5 cards hàng ngang
# ---------------------------------------------------------------------------
def render_metrics_row(placeholder, stats):
    violation_count = stats.get("violations", 0)
    placeholder.markdown(f"""
    <div class="metric-row">
        <div class="metric-card mc-cyan">
            <div class="metric-icon">🚘</div>
            <div class="metric-value">{stats['total_vehicles']}</div>
            <div class="metric-label">Tổng xe phát hiện</div>
        </div>
        <div class="metric-card mc-emerald">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{stats['avg_speed']:.1f} <span class="metric-unit">km/h</span></div>
            <div class="metric-label">Tốc độ trung bình</div>
        </div>
        <div class="metric-card mc-amber">
            <div class="metric-icon">🏎️</div>
            <div class="metric-value">{stats['max_speed']:.1f} <span class="metric-unit">km/h</span></div>
            <div class="metric-label">Tốc độ cao nhất</div>
        </div>
        <div class="metric-card mc-violet">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{stats['fps']:.1f}</div>
            <div class="metric-label">FPS xử lý</div>
        </div>
        <div class="metric-card mc-rose">
            <div class="metric-icon">🚨</div>
            <div class="metric-value">{violation_count}</div>
            <div class="metric-label">Vi phạm phát hiện</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Legacy render_metrics wrapper (for sidebar column layout, kept for backwards compat)
def render_metrics(placeholder, stats):
    render_metrics_row(placeholder, stats)


# ---------------------------------------------------------------------------
# Violation Cards — Real-time
# ---------------------------------------------------------------------------
def _get_severity_color(speed, limit=25.0):
    """Trả về màu severity dựa trên mức vượt tốc"""
    ratio = speed / max(limit, 1) if limit > 0 else 1
    if ratio > 2.0:
        return "#ef4444"   # đỏ đậm — vượt gấp đôi
    elif ratio > 1.5:
        return "#f97316"   # cam — vượt 50%+
    elif ratio > 1.2:
        return "#f59e0b"   # amber — vượt 20%+
    else:
        return "#fbbf24"   # vàng — vượt nhẹ


def _build_violation_html(v_list, speed_limit=25.0, max_items=10):
    """Tạo HTML cho violation cards"""
    if not v_list:
        return """
        <div style="color: #475569; font-style: italic; text-align: center; padding: 24px; font-size: 0.85rem;">
            <div style="font-size: 2rem; margin-bottom: 8px; opacity: 0.5;">✅</div>
            Chưa phát hiện vi phạm nào.
        </div>
        """
    
    v_html = '<div class="violation-container">'
    for v in v_list[:max_items]:
        severity = _get_severity_color(v['Tốc độ vi phạm (km/h)'], speed_limit)
        v_html += f"""
        <div class="violation-card" style="border-left-color: {severity};">
            <div>
                <span class="violation-title">⚠️ XE VƯỢT TỐC ĐỘ (ID: {v['ID xe']})</span>
                <div class="violation-details">Loại: {v['Loại xe']} &nbsp;│&nbsp; Thời điểm: {v['Thời điểm']}</div>
            </div>
            <div class="violation-speed">{v['Tốc độ vi phạm (km/h)']:.1f} <span style="font-size:0.7rem;">km/h</span></div>
        </div>
        """
    v_html += '</div>'
    return v_html


def render_violations_realtime(title_placeholder, placeholder, violation_tracker, speed_limit=25.0):
    title_placeholder.markdown("""
    <div class="section-header">
        <span class="section-header-icon">🚨</span>
        <span class="section-header-text">Vi phạm quá tốc độ</span>
        <span class="section-header-line"></span>
    </div>
    """, unsafe_allow_html=True)
    
    v_list = list(violation_tracker.values())
    v_list.reverse()
    placeholder.markdown(_build_violation_html(v_list, speed_limit, max_items=5), unsafe_allow_html=True)


def render_violations_history(title_placeholder, placeholder, violation_log, speed_limit=25.0):
    title_placeholder.markdown("""
    <div class="section-header">
        <span class="section-header-icon">🚨</span>
        <span class="section-header-text">Vi phạm quá tốc độ</span>
        <span class="section-header-line"></span>
    </div>
    """, unsafe_allow_html=True)
    
    v_list = list(violation_log)
    v_list.reverse()
    placeholder.markdown(_build_violation_html(v_list, speed_limit, max_items=10), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Idle Screen
# ---------------------------------------------------------------------------
def render_idle_screen(stframe):
    stframe.markdown("""
    <div class="idle-screen">
        <div class="idle-icon">📹</div>
        <div class="idle-title">Chọn nguồn video và nhấn Bắt đầu</div>
        <div class="idle-sub">Video và kết quả sẽ hiển thị thời gian thực tại đây</div>
        <div class="idle-steps">
            <div class="idle-step">
                <div class="idle-step-num">1</div>
                <span>Chọn nguồn</span>
            </div>
            <div class="idle-step">
                <div class="idle-step-num">2</div>
                <span>Cấu hình</span>
            </div>
            <div class="idle-step">
                <div class="idle-step-num">3</div>
                <span>Bắt đầu</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Plotly Chart Helpers
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.06)",
        font=dict(color="#94a3b8", size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
)

PLOTLY_COLORS = ["#22d3ee", "#34d399", "#fbbf24", "#a78bfa", "#fb7185", "#f97316", "#38bdf8"]


def _render_plotly_class_chart(df_chart):
    """Donut chart — phân loại xe"""
    class_counts = df_chart["label"].value_counts().reset_index()
    class_counts.columns = ["Loại xe", "Số lượng"]
    
    fig = go.Figure(go.Pie(
        labels=class_counts["Loại xe"],
        values=class_counts["Số lượng"],
        hole=0.55,
        marker=dict(colors=PLOTLY_COLORS[:len(class_counts)]),
        textinfo="label+percent",
        textfont=dict(size=12, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>Số lượng: %{value}<br>Tỉ lệ: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Phân loại phương tiện", font=dict(size=14, color="#e2e8f0")),
        showlegend=True,
        height=340,
    )
    return fig


def _render_plotly_speed_bar(df_chart, speed_limit):
    """Bar chart — tốc độ tối đa theo ID"""
    df_sorted = df_chart.sort_values("max_speed", ascending=True).tail(25)
    
    colors = ["#fb7185" if s > speed_limit else "#22d3ee" for s in df_sorted["max_speed"]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["max_speed"],
        y=[f"ID {i}" for i in df_sorted["id"]],
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>ID %{y}</b><br>Tốc độ: %{x:.1f} km/h<extra></extra>",
    ))
    fig.add_vline(
        x=speed_limit, line_dash="dash", line_color="#fbbf24",
        annotation_text=f"Giới hạn: {speed_limit} km/h",
        annotation_font=dict(color="#fbbf24", size=11),
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Tốc độ tối đa theo phương tiện", font=dict(size=14, color="#e2e8f0")),
        height=max(340, len(df_sorted) * 28),
        xaxis_title="Tốc độ (km/h)",
    )
    return fig


def _render_plotly_histogram(df_chart):
    """Histogram — phân bố tốc độ"""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df_chart["max_speed"],
        nbinsx=15,
        marker=dict(
            color="rgba(34,211,238,0.5)",
            line=dict(color="#22d3ee", width=1),
        ),
        hovertemplate="Khoảng: %{x:.0f} km/h<br>Số xe: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Phân bố tốc độ phương tiện", font=dict(size=14, color="#e2e8f0")),
        xaxis_title="Tốc độ (km/h)",
        yaxis_title="Số lượng xe",
        height=340,
        bargap=0.08,
    )
    return fig


# ---------------------------------------------------------------------------
# Fallback charts (no Plotly)
# ---------------------------------------------------------------------------
def _render_fallback_charts(df_chart):
    """Render basic Streamlit charts when Plotly is not available"""
    class_counts = df_chart["label"].value_counts().reset_index()
    class_counts.columns = ["Loại xe", "Số lượng xe"]
    st.subheader("Số lượng phương tiện theo phân loại")
    st.bar_chart(class_counts.set_index("Loại xe"))
    
    st.subheader("Tốc độ tối đa của từng phương tiện (km/h)")
    st.bar_chart(df_chart.set_index("id")["max_speed"])


# ---------------------------------------------------------------------------
# Tabbed Results Section
# ---------------------------------------------------------------------------
def render_results_tabs(speed_log, violation_log, output_vid_path, speed_limit=25.0):
    """Hiển thị kết quả trong tabs: Lịch sử | Phân tích | Tải xuống"""
    if not speed_log:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #475569;">
            <div style="font-size: 2.5rem; margin-bottom: 12px; opacity: 0.4;">📊</div>
            <div style="font-size: 0.95rem; font-weight: 600;">Chưa có dữ liệu</div>
            <div style="font-size: 0.82rem; margin-top: 4px;">Dữ liệu thống kê sẽ hiển thị sau khi xử lý video.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    tab_history, tab_analysis, tab_download = st.tabs([
        "📋 Lịch sử phương tiện",
        "📊 Phân tích & Biểu đồ",
        "📥 Tải xuống báo cáo"
    ])

    df = pd.DataFrame(speed_log)

    # ---- Tab 1: Lịch sử ----
    with tab_history:
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon">📋</span>
            <span class="section-header-text">Lịch sử Tốc độ Phương tiện</span>
            <span class="section-header-line"></span>
        </div>
        """, unsafe_allow_html=True)
        
        df_display = df.sort_values("max_speed", ascending=False).reset_index(drop=True)
        df_display.index += 1
        df_display.columns = ["ID xe", "Loại xe", "Tốc độ tối đa (km/h)"]
        st.dataframe(
            df_display.style.format({"Tốc độ tối đa (km/h)": "{:.1f}"}),
            use_container_width=True
        )

        if violation_log:
            st.markdown("""
            <div class="section-header" style="margin-top: 24px;">
                <span class="section-header-icon">🚨</span>
                <span class="section-header-text">Lịch sử Vi phạm Chi tiết</span>
                <span class="section-header-line"></span>
            </div>
            """, unsafe_allow_html=True)
            
            df_violations = pd.DataFrame(violation_log)
            df_violations = df_violations.sort_values("Tốc độ vi phạm (km/h)", ascending=False).reset_index(drop=True)
            df_violations.index += 1
            st.dataframe(
                df_violations.style.format({"Tốc độ vi phạm (km/h)": "{:.1f}"}),
                use_container_width=True
            )

    # ---- Tab 2: Phân tích ----
    with tab_analysis:
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon">📊</span>
            <span class="section-header-text">Phân tích Thống kê</span>
            <span class="section-header-line"></span>
        </div>
        """, unsafe_allow_html=True)
        
        if not df.empty:
            if HAS_PLOTLY:
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.plotly_chart(_render_plotly_class_chart(df), use_container_width=True)
                with col_chart2:
                    st.plotly_chart(_render_plotly_histogram(df), use_container_width=True)
                
                st.plotly_chart(_render_plotly_speed_bar(df, speed_limit), use_container_width=True)
            else:
                _render_fallback_charts(df)

    # ---- Tab 3: Tải xuống ----
    with tab_download:
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon">📥</span>
            <span class="section-header-text">Tải xuống Báo cáo</span>
            <span class="section-header-line"></span>
        </div>
        """, unsafe_allow_html=True)

        # Speed report CSV
        st.markdown("""
        <div class="download-card">
            <div class="download-card-title">📄 Báo cáo Tốc độ (CSV)</div>
            <div class="download-card-desc">Bảng tốc độ tối đa của tất cả phương tiện được phát hiện trong video.</div>
        </div>
        """, unsafe_allow_html=True)
        df_export = df.copy()
        df_export.columns = ["ID xe", "Loại xe", "Tốc độ tối đa (km/h)"]
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Tải Báo cáo Tốc độ",
            data=csv_data,
            file_name="bao_cao_toc_do.csv",
            mime="text/csv",
            key="download_csv_history",
            use_container_width=True
        )

        # Violation report CSV
        if violation_log:
            st.markdown("""
            <div class="download-card" style="margin-top: 8px;">
                <div class="download-card-title">🚨 Danh sách Vi phạm (CSV)</div>
                <div class="download-card-desc">Chi tiết các phương tiện vượt quá giới hạn tốc độ cho phép.</div>
            </div>
            """, unsafe_allow_html=True)
            df_v_export = pd.DataFrame(violation_log)
            csv_violations = df_v_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Tải Danh sách Vi phạm",
                data=csv_violations,
                file_name="danh_sach_vi_pham.csv",
                mime="text/csv",
                key="download_csv_violations",
                use_container_width=True
            )

        # Output video
        if output_vid_path and os.path.exists(output_vid_path):
            st.markdown("""
            <div class="download-card" style="margin-top: 8px;">
                <div class="download-card-title">🎬 Video kết quả (MP4)</div>
                <div class="download-card-desc">Video đã qua xử lý với bounding box, tốc độ và cảnh báo vi phạm.</div>
            </div>
            """, unsafe_allow_html=True)
            with open(output_vid_path, "rb") as f:
                st.download_button(
                    label="⬇️ Tải Video kết quả",
                    data=f,
                    file_name="video_ket_qua.mp4",
                    mime="video/mp4",
                    key="download_processed_video",
                    use_container_width=True
                )


# ---------------------------------------------------------------------------
# Legacy support — render_history_and_charts
# ---------------------------------------------------------------------------
def render_history_and_charts(col_history, col_chart, speed_log, violation_log, output_vid_path):
    """Legacy wrapper — redirect to tabbed view"""
    # This is no longer used in the new layout but kept for compatibility
    pass

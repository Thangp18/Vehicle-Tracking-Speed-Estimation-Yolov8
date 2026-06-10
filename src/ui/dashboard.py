import streamlit as st
import pandas as pd
import os

def render_header():
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🚗 Vehicle Speed Estimation System</p>
        <p class="hero-subtitle">
            Nhận diện & theo dõi phương tiện theo thời gian thực với <strong>YOLOv8</strong>
            và ước tính tốc độ qua thuật toán <strong>Homography</strong>.
            Thiết lập tham số tại sidebar rồi nhấn <em>Bắt đầu</em>.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_status(placeholder, status):
    if status == "running":
        placeholder.markdown(
            '<span class="status-running">● Đang xử lý…</span>',
            unsafe_allow_html=True
        )
    elif status == "stopped":
        placeholder.markdown(
            '<span class="status-stopped">✔ Hoàn tất xử lý</span>',
            unsafe_allow_html=True
        )
    else:
        placeholder.markdown(
            '<span class="status-idle">○ Chờ bắt đầu</span>',
            unsafe_allow_html=True
        )

def render_metrics(placeholder, stats):
    placeholder.markdown(f"""
    <div class="metric-card" style="margin-bottom:12px;">
        <div class="metric-icon">🚘</div>
        <div class="metric-value">{stats['total_vehicles']}</div>
        <div class="metric-label">Tổng xe phát hiện</div>
    </div>
    <div class="metric-card" style="margin-bottom:12px;">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{stats['avg_speed']:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ trung bình</div>
    </div>
    <div class="metric-card" style="margin-bottom:12px;">
        <div class="metric-icon">🏎️</div>
        <div class="metric-value">{stats['max_speed']:.1f} <span style='font-size:1rem;color:#94a3b8'>km/h</span></div>
        <div class="metric-label">Tốc độ cao nhất</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-value">{stats['fps']:.1f}</div>
        <div class="metric-label">FPS xử lý</div>
    </div>
    """, unsafe_allow_html=True)

def render_violations_realtime(title_placeholder, placeholder, violation_tracker):
    if violation_tracker:
        title_placeholder.markdown("### 🚨 Vi phạm quá tốc độ")
        v_list = list(violation_tracker.values())
        v_list.reverse()
        v_html = '<div class="violation-container">'
        for v in v_list[:5]:
            v_html += f"""
            <div class="violation-card">
                <div>
                    <span class="violation-title">⚠️ XE VƯỢT TỐC ĐỘ (ID: {v['ID xe']})</span>
                    <div class="violation-details">Loại: {v['Loại xe']} | Thời điểm: {v['Thời điểm']}</div>
                </div>
                <div class="violation-speed">{v['Tốc độ vi phạm (km/h)']:.1f} <span style="font-size:0.75rem;">km/h</span></div>
            </div>
            """
        v_html += '</div>'
        placeholder.markdown(v_html, unsafe_allow_html=True)
    else:
        title_placeholder.markdown("### 🚨 Vi phạm quá tốc độ")
        placeholder.markdown(
            '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Chưa phát hiện vi phạm nào.</div>',
            unsafe_allow_html=True
        )

def render_violations_history(title_placeholder, placeholder, violation_log):
    if violation_log:
        title_placeholder.markdown("### 🚨 Vi phạm quá tốc độ")
        v_list = list(violation_log)
        v_list.reverse()
        v_html = '<div class="violation-container">'
        for v in v_list[:10]:
            v_html += f"""
            <div class="violation-card">
                <div>
                    <span class="violation-title">⚠️ XE VƯỢT TỐC ĐỘ (ID: {v['ID xe']})</span>
                    <div class="violation-details">Loại: {v['Loại xe']} | Thời điểm: {v['Thời điểm']}</div>
                </div>
                <div class="violation-speed">{v['Tốc độ vi phạm (km/h)']:.1f} <span style="font-size:0.75rem;">km/h</span></div>
            </div>
            """
        v_html += '</div>'
        placeholder.markdown(v_html, unsafe_allow_html=True)
    else:
        title_placeholder.markdown("### 🚨 Vi phạm quá tốc độ")
        placeholder.markdown(
            '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Chưa có dữ liệu vi phạm.</div>',
            unsafe_allow_html=True
        )

def render_idle_screen(stframe):
    stframe.markdown("""
    <div style="
        height: 360px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #334155;
        border: 2px dashed #1e293b;
        border-radius: 12px;
        gap: 12px;
    ">
        <div style="font-size: 3rem">📹</div>
        <div style="font-size: 1rem; font-weight: 600">Chọn nguồn video và nhấn Bắt đầu</div>
        <div style="font-size: 0.8rem; color: #475569">Video và kết quả sẽ hiển thị thời gian thực tại đây</div>
    </div>
    """, unsafe_allow_html=True)

def render_history_and_charts(col_history, col_chart, speed_log, violation_log, output_vid_path):
    if speed_log:
        with col_history:
            st.markdown("### 📋 Lịch sử Tốc độ Phương tiện")
            df = pd.DataFrame(speed_log)
            df = df.sort_values("max_speed", ascending=False).reset_index(drop=True)
            df.index += 1
            df.columns = ["ID xe", "Loại xe", "Tốc độ tối đa (km/h)"]
            st.dataframe(
                df.style.format({"Tốc độ tối đa (km/h)": "{:.1f}"}),
                use_container_width=True
            )
            
            # Xuất file CSV báo cáo tốc độ
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải Báo cáo Tốc độ (CSV)",
                data=csv_data,
                file_name="bao_cao_toc_do.csv",
                mime="text/csv",
                key="download_csv_history"
            )
            
            # Tải xuống video kết quả
            if output_vid_path and os.path.exists(output_vid_path):
                with open(output_vid_path, "rb") as f:
                    st.download_button(
                        label="📥 Tải Video kết quả (.mp4)",
                        data=f,
                        file_name="video_ket_qua.mp4",
                        mime="video/mp4",
                        key="download_processed_video"
                    )
            
            # Bảng báo cáo vi phạm
            if violation_log:
                st.markdown("### 🚨 Lịch sử Vi phạm chi tiết")
                df_violations = pd.DataFrame(violation_log)
                df_violations = df_violations.sort_values("Tốc độ vi phạm (km/h)", ascending=False).reset_index(drop=True)
                df_violations.index += 1
                st.dataframe(
                    df_violations.style.format({"Tốc độ vi phạm (km/h)": "{:.1f}"}),
                    use_container_width=True
                )
                
                csv_violations = df_violations.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Tải Báo cáo Vi phạm (CSV)",
                    data=csv_violations,
                    file_name="danh_sach_vi_pham.csv",
                    mime="text/csv",
                    key="download_csv_violations"
                )

        with col_chart:
            st.markdown("### 📊 Thống kê Phân tích")
            df_chart = pd.DataFrame(speed_log)
            if not df_chart.empty:
                # Đếm số lượng xe theo phân loại
                class_counts = df_chart["label"].value_counts().reset_index()
                class_counts.columns = ["Loại xe", "Số lượng xe"]
                st.subheader("Số lượng phương tiện theo phân loại")
                st.bar_chart(class_counts.set_index("Loại xe"))
                
                # Biểu đồ phân bố tốc độ của từng xe
                st.subheader("Tốc độ tối đa của từng phương tiện (km/h)")
                st.bar_chart(df_chart.set_index("id")["max_speed"])

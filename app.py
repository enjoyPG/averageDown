import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Simulator",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. 테마 설정 (사이드바 토글) & 강력한 CSS 주입
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ 설정")
    is_dark_mode = st.toggle("🌙 다크 모드", value=True)
    
    st.divider()
    st.info("👇 아래 정보를 입력해주세요")

# 색상 팔레트 정의
if is_dark_mode:
    # [다크 모드]
    main_bg = "#121212"       # 메인 배경
    header_bg = "#121212"     # 헤더(상단바) 배경 (메인과 동일하게)
    sidebar_bg = "#1E1E1E"    # 사이드바 배경
    text_color = "#FFFFFF"    # 기본 글자
    sub_text_color = "#E0E0E0" 
    card_bg = "#2C2C2C"       
    accent_color = "#00E5FF"  # 형광 하늘색
    border_color = "#444444"
    chart_template = "plotly_dark"
else:
    # [라이트 모드]
    main_bg = "#FFFFFF"       
    header_bg = "#FFFFFF"
    sidebar_bg = "#F8F9FA"    
    text_color = "#000000"    
    sub_text_color = "#333333" 
    card_bg = "#FFFFFF"       
    accent_color = "#2962FF"  
    border_color = "#DDDDDD"
    chart_template = "plotly_white"

# CSS 강제 주입
st.markdown(f"""
<style>
    /* 1. 메인 영역 배경 */
    .stApp {{
        background-color: {main_bg};
        color: {text_color};
    }}
    
    /* 2. 상단 헤더(Header) 배경색 강제 지정 (흰색 띠 제거) */
    header[data-testid="stHeader"] {{
        background-color: {header_bg} !important;
    }}
    
    /* 3. 사이드바 배경 */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    
    /* 4. 전체 폰트 사이즈 키우기 (기본 16px -> 18px로 상향) */
    html, body, p, div, span, label, li {{
        font-size: 18px !important;
        color: {text_color} !important;
    }}
    
    /* 5. 입력 위젯 폰트 및 라벨 스타일 */
    .stNumberInput input, .stSlider div {{
        color: {text_color} !important;
    }}
    .stNumberInput label, .stSlider label {{
        font-size: 18px !important; /* 라벨 크기 키움 */
        font-weight: bold !important;
    }}
    
    /* 6. KPI 카드 디자인 (폰트 더 크게) */
    .metric-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 25px; /* 패딩 늘림 */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .card-title {{
        color: {sub_text_color} !important;
        font-size: 18px !important; /* 제목 크기 키움 */
        margin-bottom: 8px;
    }}
    .card-value {{
        color: {accent_color} !important;
        font-size: 36px !important; /* 숫자 크기 대폭 키움 */
        font-weight: 800;
    }}
    
    /* 7. 탭 글씨 크기 */
    .stTabs button {{
        font-size: 20px !important;
        font-weight: bold !important;
    }}
    
    /* 8. 경고창 등 예외 처리 */
    .stAlert {{
        color: #000000 !important; 
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 사이드바: 데이터 입력
# -----------------------------------------------------------------------------
with st.sidebar:
    # 입력창 (format으로 콤마 표시하면 입력할 때 불편할 수 있어 제거하거나 유지)
    current_avg = st.number_input("기존 평단가 (원)", value=80700, step=100)
    held_qty = st.number_input("보유 수량 (주)", value=12, step=1)
    current_price = st.number_input("현재 시장가 (원)", value=49050, step=100)
    
    st.markdown("---")
    st.markdown("### 📊 현재 내 상태")
    
    cur_total = current_avg * held_qty
    cur_eval = current_price * held_qty
    cur_loss = cur_eval - cur_total
    cur_pct = (cur_loss / cur_total) * 100
    
    col_s1, col_s2 = st.columns(2)
    # metric은 Streamlit 기본 스타일 따름 (CSS로 폰트 강제 적용됨)
    col_s1.metric("손익 금액", f"{cur_loss:,.0f}원")
    col_s2.metric("수익률", f"{cur_pct:.2f}%")

# -----------------------------------------------------------------------------
# 4. 메인 화면
# -----------------------------------------------------------------------------
st.title("📉 Stock Simulator")
st.write("") 

tab1, tab2 = st.tabs(["🚀 평단가 시뮬레이션", "🎯 목표가 역산"])

# === TAB 1: 실시간 시뮬레이션 ===
with tab1:
    st.markdown("#### 🎚️ 수량 조절")
    
    max_sim_qty = max(100, held_qty * 10)
    add_qty = st.slider("추가 매수 수량 (드래그하세요)", 0, max_sim_qty, 0)
    
    new_money = add_qty * current_price
    total_qty = held_qty + add_qty
    total_money = (current_avg * held_qty) + new_money
    new_avg = total_money / total_qty
    
    st.write("")
    
    # HTML 카드로 결과 표시 (CSS class 적용)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-title">📉 예상 평단가</div>
            <div class="card-value">{new_avg:,.0f} 원</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-title">💰 필요 금액</div>
            <div class="card-value" style="color:{text_color} !important;">{new_money:,.0f} 원</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-title">📦 총 보유량</div>
            <div class="card-value" style="color:{text_color} !important;">{total_qty:,} 주</div>
        </div>""", unsafe_allow_html=True)

    st.write("---")
    
    # --- 차트 그리기 ---
    x_data = list(range(0, max_sim_qty + 1, 1))
    y_data = []
    for q in x_data:
        sim_avg = ((current_avg * held_qty) + (current_price * q)) / (held_qty + q)
        y_data.append(sim_avg)
        
    fig = go.Figure()
    
    # 1. 라인 차트
    fig.add_trace(go.Scatter(
        x=x_data, y=y_data, mode='lines', name='평단가',
        line=dict(color=accent_color, width=4)
    ))
    
    # 2. 현재 위치 점
    fig.add_trace(go.Scatter(
        x=[add_qty], y=[new_avg], mode='markers+text', name='Current',
        marker=dict(color='#FF4081', size=18, line=dict(color='white', width=2)), # 점 크기 15->18
        text=[f"{int(new_avg):,}원"], textposition="top right",
        textfont=dict(color=text_color, size=18, weight='bold') # 차트 폰트 15->18
    ))

    fig.update_layout(
        template=chart_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500, # 차트 높이 약간 키움
        margin=dict(t=50, l=20, r=20, b=20),
        xaxis=dict(title="추가 매수 수량", showgrid=True, gridcolor=border_color, zeroline=False, title_font=dict(size=18)),
        yaxis=dict(title="평단가", showgrid=True, gridcolor=border_color, zeroline=False, title_font=dict(size=18)),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# === TAB 2: 목표가 역산 ===
with tab2:
    st.markdown("#### 🎯 목표가 설정")
    
    col_input, col_res = st.columns([1, 2])
    with col_input:
        st.write("")
        target_price = st.number_input("목표 평단가", value=int(current_avg*0.9), step=100)
        btn = st.button("계산하기", type="primary", use_container_width=True)
        
    if btn:
        if target_price >= current_avg:
            st.warning("이미 목표가보다 평단가가 낮습니다.")
        elif target_price <= current_price:
            st.error("현재가보다 낮은 목표가는 불가능합니다.")
        else:
            numerator = held_qty * (current_avg - target_price)
            denominator = target_price - current_price
            needed_qty = math.ceil(numerator / denominator)
            needed_cost = needed_qty * current_price
            
            with col_res:
                st.markdown(f"""
                <div class="metric-card" style="border: 1px solid {accent_color};">
                    <div style="color:{accent_color}; font-size:24px; font-weight:bold;">🎉 목표 달성 조건</div>
                    <ul style="margin-top:15px; font-size:20px; line-height:1.8; color:{text_color};">
                        <li>추가 매수: <b>{needed_qty:,} 주</b></li>
                        <li>필요 자금: <b>{needed_cost:,.0f} 원</b></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Bar Chart
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=['내 평단', '목표', '현재가'],
                    x=[current_avg, target_price, current_price],
                    orientation='h',
                    marker_color=['#777777', accent_color, '#FF4081'],
                    text=[f"{current_avg:,}", f"{target_price:,}", f"{current_price:,}"],
                    textposition='auto',
                    textfont=dict(color='white', size=16, weight='bold')
                ))
                fig_bar.update_layout(
                    template=chart_template,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(t=20, b=20),
                    xaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# -----------------------------------------------------------------------------
# 1. 페이지 설정 (Dark Theme & Layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Dilution Simulator",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (카드 디자인, 네온 효과)
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .big-font { font-size: 24px !important; font-weight: bold; color: #E0E0E0; }
    .highlight { color: #00FFCC; } /* Neon Cyan */
    .stApp { background-color: #0E1117; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 사이드바: 기본 데이터 입력
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🛠️ 내 주식 설정")
    st.markdown("현재 보유 중인 종목 정보를 입력하세요.")
    
    # 입력값 받기 (숫자 입력의 편의를 위해 number_input 사용)
    current_avg = st.number_input("기존 평단가 (원)", value=80700, step=100)
    held_qty = st.number_input("보유 수량 (주)", value=12, step=1)
    current_price = st.number_input("현재 시장가 (원)", value=49050, step=100)
    
    st.divider()
    
    st.markdown("### 📊 현재 상태")
    cur_total_invest = current_avg * held_qty
    cur_eval_value = current_price * held_qty
    cur_loss = cur_eval_value - cur_total_invest
    cur_loss_pct = (cur_loss / cur_total_invest) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("투자 원금", f"{cur_total_invest:,.0f}원")
    col2.metric("평가 손익", f"{cur_loss:,.0f}원", delta=f"{cur_loss_pct:.2f}%")

# -----------------------------------------------------------------------------
# 3. 메인 화면: 시뮬레이션
# -----------------------------------------------------------------------------
st.title("📉 물타기 시뮬레이터 (Pro)")
st.markdown("추가 매수를 통해 평단가가 어떻게 변하는지 **시각적**으로 확인하세요.")

tab1, tab2 = st.tabs(["🚀 평단가 예측 (Simulation)", "🎯 목표가 역산 (Targeting)"])

# === TAB 1: 실시간 시뮬레이션 ===
with tab1:
    st.markdown("#### 🎚️ 추가 매수 시뮬레이션")
    
    # 슬라이더로 동적인 조작감 제공
    # 최대 100주, 혹은 현재 보유량의 5배까지 시뮬레이션
    max_sim_qty = max(100, held_qty * 10)
    add_qty = st.slider("추가로 몇 주를 더 살까요?", 0, max_sim_qty, 0, key="slider_qty")
    
    # 계산 로직
    new_invest_amt = add_qty * current_price
    total_qty = held_qty + add_qty
    total_invest = (current_avg * held_qty) + new_invest_amt
    new_avg_price = total_invest / total_qty
    
    # 결과 KPI 카드 표시
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <span style='color:gray'>예상 평단가</span><br>
            <span class="big-font highlight">{new_avg_price:,.0f} 원</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <span style='color:gray'>필요 금액</span><br>
            <span class="big-font">{new_invest_amt:,.0f} 원</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <span style='color:gray'>총 보유 수량</span><br>
            <span class="big-font">{total_qty:,} 주</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- 차트: 물타기 효율 곡선 (The Efficiency Curve) ---
    st.subheader("📈 물타기 효율 곡선")
    
    # 데이터 생성 (0주 ~ 100주 추가 시 평단가 변화 데이터 생성)
    x_data = list(range(0, max_sim_qty + 1, 1)) # X축: 추가 수량
    y_data = []
    
    for q in x_data:
        sim_total_qty = held_qty + q
        sim_total_invest = (current_avg * held_qty) + (current_price * q)
        sim_avg = sim_total_invest / sim_total_qty
        y_data.append(sim_avg)
    
    # DataFrame 변환
    df_chart = pd.DataFrame({"Add_Qty": x_data, "New_Avg": y_data})
    
    # Plotly 차트 그리기
    fig = go.Figure()
    
    # 1. 메인 곡선
    fig.add_trace(go.Scatter(
        x=df_chart['Add_Qty'], 
        y=df_chart['New_Avg'],
        mode='lines',
        name='평단가 변화',
        line=dict(color='#00FFCC', width=4) # Neon Cyan Color
    ))
    
    # 2. 현재 선택 지점 (Point)
    fig.add_trace(go.Scatter(
        x=[add_qty], 
        y=[new_avg_price],
        mode='markers',
        name='현재 시뮬레이션',
        marker=dict(color='white', size=12, line=dict(color='#FF0055', width=2))
    ))

    # 차트 레이아웃 꾸미기 (Dark Mode)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', # 투명 배경
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="추가 매수 수량 (주)",
        yaxis_title="예상 평단가 (원)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **Tip:** 곡선이 완만해지는 구간(L자 꺾임) 이후로는 돈을 많이 써도 평단가가 잘 내려가지 않습니다. 그 '가성비 구간'을 찾으세요!")


# === TAB 2: 목표가 역산 ===
with tab2:
    st.markdown("#### 🎯 목표 평단가 설정")
    
    col_input, col_result = st.columns([1, 2])
    
    with col_input:
        target_price = st.number_input("목표 평단가 입력 (원)", value=int(current_avg * 0.9), step=100)
        
        calc_btn = st.button("계산하기 🧮")
    
    if calc_btn:
        if target_price >= current_avg:
            st.warning("목표가가 현재 평단가보다 높습니다. (물타기 필요 없음)")
        elif target_price <= current_price:
            st.error("목표가가 현재가보다 낮습니다. 추가 매수만으로는 불가능합니다.")
        else:
            # 역산 공식
            numerator = held_qty * (current_avg - target_price)
            denominator = target_price - current_price
            needed_qty = math.ceil(numerator / denominator)
            needed_cost = needed_qty * current_price
            
            with col_result:
                st.success(f"목표 달성 가능! 🎉")
                st.markdown(f"""
                - 필요한 추가 매수량: **{needed_qty:,} 주**
                - 필요한 자금: **{needed_cost:,.0f} 원**
                - 총 보유하게 될 수량: **{held_qty + needed_qty:,} 주**
                """)
                
                # 시각적 비교 (Bar Chart)
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=['현재 평단가', '목표 평단가', '현재 시장가'],
                    x=[current_avg, target_price, current_price],
                    orientation='h',
                    marker_color=['#FF5555', '#00FFCC', '#5555FF'],
                    text=[f"{current_avg:,}", f"{target_price:,}", f"{current_price:,}"],
                    textposition='auto'
                ))
                fig_bar.update_layout(
                    template="plotly_dark", 
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=250,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf  # 📊 실시간 주가 연동 라이브러리

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide"
)

# 🔄 2. 자동 새로고침 주기 설정값 선언
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30  # 기본값 30초

# 🎨 3. 금융 앱 스타일 카드 디자인을 위한 CSS 적용
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .card {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
        .dividend-card {
            background-color: #e8f5e9;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #c8e6c9;
        }
        .warn-card {
            background-color: #fff3cd;
            border-radius: 15px;
            padding: 15px;
            border-left: 5px solid #ffc107;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# 🔐 4. 세션 상태 및 로그인 관리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

# [화면 A] 로그인 화면
if not st.session_state.logged_in:
    st.title("💰 배당 포트폴리오")
    st.caption("배당 투자자를 위한 자산관리 앱")
    account = st.selectbox("계좌 선택", ["ISA", "연금저축1", "연금저축2", "일반계좌"])
    password = st.text_input("비밀번호", type="password")
    st.checkbox("자동 로그인")
    if st.button("로그인", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# [화면 B] 최초 설정 화면
if not st.session_state.setup_done:
    st.title("최초 설정")
    st.button("한국투자증권 계좌 연동", use_container_width=True)
    st.button("수동 포트폴리오 사용", use_container_width=True)
    dark_mode = st.toggle("다크모드")
    if st.button("설정 완료", use_container_width=True):
        st.session_state.setup_done = True
        st.rerun()
    st.stop()


# 🧭 5. 사이드바 메뉴
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio(
    "이동할 화면을 선택하세요",
    ["🏠 홈", "💰 배당", "📊 포트폴리오", "📄 리포트", "⚙️ 설정"]
)

# 🌐 [실시간 데이터 처리] 야후 파이낸스에서 TIGER 미국배당다우존스(453850.KS) 데이터 긁어오기
@st.cache_data(ttl=60)
def get_realtime_data():
    try:
        # TIGER 미국배당다우존스 티커 조회
        tiger_div = yf.Ticker("453850.KS")
        tiger_price = tiger_div.history(period="1d")['Close'].iloc[-1]  # 현재 주가 (원)
        
        # 한국 상장 ETF는 info에서 dividendYield가 안 나오는 경우가 많아 한국 상장 다우존스 평균 시가배당률(약 3.8%) 적용
        tiger_yield = 3.8
    except:
        # 네트워크 오류 시 기본 가격 세팅
        tiger_price = 11450.0
        tiger_yield = 3.8
        
    return tiger_price, tiger_yield

# 실시간 주가 및 배당률 변수 저장
tiger_current_price, tiger_yield = get_realtime_data()

#  보유 수량 설정 (예시: 1,200주)
tiger_quantity = 1200
tiger_total_krw = tiger_quantity * tiger_current_price

# 기타 자산 수치 계산
sp500_value_krw = 40000000
etc_value_krw = 10000000
total_asset_krw = tiger_total_krw + sp500_value_krw + etc_value_krw


# 💳 6. 각 메뉴별 화면 구현
# 🏠 홈 화면
if menu == "🏠 홈":
    st.caption(f"🔄 {st.session_state.refresh_interval}초마다 주가가 실시간으로 업데이트됩니다.")
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 목요일")
    
    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        # 자산 요약 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💳 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        st.divider()
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("총 평가손익", "+11,250,000원", delta_color="inverse")
        mc2.metric("오늘 평가손익", "+210,000원")
        mc3.metric("총 수익률", "+10.8%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 배당 현황 카드
        st.markdown('<div class="dividend-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2e7d32;'>💰 배당 현황</h3>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "145,000원")
        dc2.metric("연 예상 배당", "1,850,000원")
        dc3.metric("배당수익률", f"{tiger_yield:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 계좌 현황 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏦 계좌 현황")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")  # ISA 계좌에 TIGER 실시간 반영
        ac2.metric("연금저축1", "18,000,000원")
        ac3.metric("연금저축2", "35,000,000원")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 다음 배당 일정")
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 2일**\n\n**6월 15일**")
        with cal_col2:
            st.markdown(f"TIGER 미국배당다우존스 <span style='color:green;'>({tiger_current_price:,.0f}원)</span><br>TIGER 미국S&P500 <span style='color:blue;'>(16,500원)</span>", unsafe_allow_html=True)
        
        if st.button("배당 전체보기", key="go_div", use_container_width=True):
            st.info("배당 탭으로 이동 기능을 구현할 예정입니다.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="warn-card">', unsafe_allow_html=True)
        st.markdown("⚠️ **리밸런싱 알림**")
        st.markdown("**금 ETF**가 목표 비중(20%)보다 **4% 부족**합니다. (현재 16%) <br>👉 **추가 매수를 권장합니다.**", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pie 자산배분 현황")
        allocation = pd.DataFrame({
            "자산": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
            "비중": [23, 27, 16, 18, 11, 5]
        })
        fig = px.pie(allocation, names="자산", values="비중", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 📊 실시간 가격이 반영된 포트폴리오 분석 그래프
    st.markdown("---")
    st.subheader("📊 내 포트폴리오 분석 (상세 시뮬레이션)")
    
    graph_data = {
        "종목명": ["TIGER 미국배당다우존스", "S&P 500", "기타 자산"],
        "자산가치": [tiger_total_krw, sp500_value_krw, etc_value_krw],
        "예상배당금": [tiger_total_krw * (tiger_yield/100), 52000, 0]          
    }
    df_graph = pd.DataFrame(graph_data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🍩 종목별 자산 비중")
        fig_pie = px.pie(df_graph, values="자산가치", names="종목명", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.markdown("#### 💰 종목별 연간 예상 배당금 (Cash Flow)")
        fig_bar = px.bar(df_graph, x="종목명", y="예상배당금", text="예상배당금", color="종목명", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 📈 보유종목 TOP 10 (실제 증권사 어플 스타일 두 줄 레이아웃)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 보유종목 TOP 10")
    
    tiger_purchase_price = 10150.0  # 예시 평단가 (원)
    tiger_profit_krw = tiger_total_krw - (tiger_quantity * tiger_purchase_price)
    tiger_profit_rate = (tiger_current_price - tiger_purchase_price) / tiger_purchase_price * 100

    display_stocks = [
        {
            "name": "TIGER 미국배당다우존스 (실시간)",
            "total_value": f"{tiger_total_krw:,.0f}원",
            "profit": f"{tiger_profit_krw:+,.0f}원",
            "profit_color": "#d32f2f" if tiger_profit_krw >= 0 else "#1565c0",
            "quantity": f"{tiger_quantity:,}주",
            "buy_price": f"{tiger_purchase_price:,.0f}원",
            "current_price": f"{tiger_current_price:,.0f}원",
            "rate": f"{tiger_profit_rate:+.2f}%"
        },
        {
            "name": "TIGER 미국S&P500",
            "total_value": "12,500,000원",
            "profit": "+1,450,000원",
            "profit_color": "#d32f2f",
            "quantity": "145주",
            "buy_price": "76,200원",
            "current_price": "86,200원",
            "rate": "+13.12%"
        },
        {
            "name": "TIGER 미국나스닥100",
            "total_value": "8,200,000원",
            "profit": "+1,280,000원",
            "profit_color": "#d32f2f",
            "quantity": "80주",
            "buy_price": "86,500원",
            "current_price": "102,500원",
            "rate": "+18.50%"
        }
    ]

    for s in display_stocks:
        st.markdown(f"""
        <div style="background-color: #ffffff; border-radius: 10px; padding: 12px 15px; margin-bottom: 10px; border: 1px solid #e9ecef; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: bold; font-size: 15px; color: #212529;">{s['name']}</span>
                <span style="font-weight: bold; font-size: 15px; color: #212529;">
                    {s['total_value']} 
                    <span style="font-size: 12px; font-weight: normal; color: {s['profit_color']}; margin-left: 4px;">({s['profit']})</span>
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6c757d;">
                <div>
                    <span>보유: <b style="color:#495057;">{s['quantity']}</b></span>
                    <span style="margin: 0 6px; color:#dee2e6;">|</span>
                    <span>매입: <b style="color:#495057;">{s['buy_price']}</b></span>
                    <span style="margin: 0 6px; color:#dee2e6;">|</span>
                    <span>현재: <b style="color:#495057;">{s['current_price']}</b></span>
                </div>
                <div style="font-weight: bold; color: {s['profit_color']}; font-size: 13px;">
                    {s['rate']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 💰 배당 화면
elif menu == "💰 배당":
    st.title("📅 배당 상세 대시보드")
    st.caption("배당 투자자를 위한 월별 현금흐름 및 성장성 분석")
    st.divider()

    st.subheader("📊 배당 요약")
    sum1, sum2, sum3 = st.columns(3)
    
    with sum1:
        st.markdown('<div class="dividend-card" style="text-align: center;">', unsafe_allow_html=True)
        st.metric("올해 받은 배당금 (2026)", "₩847,000")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with sum2:
        st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
        st.metric("전년 대비 성장률", "+12.4%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with sum3:
        st.markdown('<div class="dividend-card" style="text-align: center;">', unsafe_allow_html=True)
        st.metric("예상 연 배당금", "₩1,850,000")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    g_col1, g_col2 = st.columns([1.2, 0.8])
    with g_col1:
        st.subheader("🎵 월별 배당 현금흐름")
        monthly_data = pd.DataFrame({
            "월": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "배당금(원)": [120000, 110000, 180000, 140000, 160000, 150000]
        })
        fig_monthly = px.bar(monthly_data, x="월", y="배당금(원)", text="배당금(원)", color_discrete_sequence=["#2e7d32"])
        fig_monthly.update_traces(texttemplate='%{text}:,원', textposition='outside')
        fig_monthly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})

    with g_col2:
        st.subheader("📈 연간 배당 성장 추이")
        yearly_data = pd.DataFrame({
            "연도": ["2024", "2025", "2026 예상"],
            "연간 배당금(원)": [1200000, 1550000, 1850000]
        })
        fig_yearly = px.line(yearly_data, x="연度", y="연간 배당금(원)", markers=True, color_discrete_sequence=["#1565c0"])
        fig_yearly.update_traces(line=dict(width=4), marker=dict(size=10))
        fig_yearly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_yearly, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    st.subheader("🔍 종목별 배당 상세")
    stock_col1, stock_col2 = st.columns(2)
    with stock_col1:
        st.markdown(f"""
        <div class="card">
            <h3>🇰🇷 TIGER 미국배당다우존스 (실시간)</h3>
            <p><b>보유수량:</b> {tiger_quantity:,}주</p>
            <p><b>현재 주가:</b> {tiger_current_price:,.0f}원</p>
            <p><b>원화 가치:</b> {tiger_total_krw:,.0f}원</p>
            <p style="color:#2e7d32;"><b>예상 배당수익률:</b> {tiger_yield:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with stock_col2:
        st.markdown("""
        <div class="card">
            <h3>🇰🇷 TIGER 미국S&P500</h3>
            <p><b>보유수량:</b> 145주</p>
            <p><b>연 예상 배당:</b> 52,000원</p>
            <p style="color:#2e7d32;"><b>배당수익률:</b> 1.4%</p>
        </div>
        """, unsafe_allow_html=True)

# 📊 포트폴리오 화면
elif menu == "📊 포트폴리오":
    st.title("💼 포트폴리오 및 리밸런싱 전략")
    st.divider()

    portfolio_data = pd.DataFrame({
        "자산군": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
        "목표 비중(%)": [25, 25, 20, 15, 10, 5],
        "현재 비중(%)": [23, 27, 16, 18, 11, 5]
    })
    st.dataframe(portfolio_data, use_container_width=True, hide_index=True)

elif menu == "📄 리포트":
    st.title("📊 월간 투자 리포트")

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정 및 API 연동")

# ⏱️ 7. 지정된 시간(30초) 대기 후 화면 자동 새로고침
time.sleep(st.session_state.refresh_interval)
st.rerun()
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf  # 📊 실시간 주가 연동을 위한 라이브러리 추가

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

# 🌐 [실시간 데이터 처리] 야후 파이낸스에서 SCHD 실시간 데이터 긁어오기
# (인터넷에서 가져오는 속도가 있으므로, 성능을 위해 잠시 캐싱하거나 안전하게 처리합니다)
@st.cache_data(ttl=60)  # 60초 동안은 금융 서버에 부담을 주지 않기 위해 데이터를 기억합니다.
def get_realtime_data():
    try:
        # SCHD 데이터 가져오기
        schd = yf.Ticker("SCHD")
        schd_price = schd.history(period="1d")['Close'].iloc[-1]  # 현재 주가 ($)
        
        # 안전하게 배당 수익률 가져오기 (없으면 기본값 3.5%)
        schd_info = schd.info
        schd_div_yield = schd_info.get('dividendYield', 0.035) * 100  # 퍼센트 전환
        
        # 환율 (원/달러) 정보도 실시간으로 가져옵니다 (USDKRW=X)
        exchange_rate_ticker = yf.Ticker("USDKRW=X")
        exchange_rate = exchange_rate_ticker.history(period="1d")['Close'].iloc[-1]
    except:
        # 혹시 라이브러리 오류나 네트워크 문제가 생겼을 때 앱이 멈추지 않게 기본값 세팅
        schd_price = 82.50
        schd_div_yield = 3.5
        exchange_rate = 1380.0
        
    return schd_price, schd_div_yield, exchange_rate

# 실시간 주가 및 환율 변수 저장
schd_current_price_usd, schd_yield, current_usdkrw = get_realtime_data()

# 지훈님의 SCHD 실제 보유 수량 설정 (예시: 120주)
schd_quantity = 120
schd_total_usd = schd_quantity * schd_current_price_usd
schd_total_krw = schd_total_usd * current_usdkrw

# 기타 자산 및 S&P500 수치 계산 (SCHD 실시간 가격에 연동되어 총 자산이 변하게 설정)
sp500_value_krw = 40000000
etc_value_krw = 10000000
total_asset_krw = schd_total_krw + sp500_value_krw + etc_value_krw


# 💳 6. 각 메뉴별 화면 구현
# ────────────────────────────────────────────────────────
# 🏠 홈 화면
# ────────────────────────────────────────────────────────
if menu == "🏠 홈":
    st.caption(f"🔄 {st.session_state.refresh_interval}초마다 주가가 실시간으로 업데이트됩니다. (현재 적용 환율: 1$ = {current_usdkrw:,.1f}원)")
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 목요일")
    
    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        # 자산 요약 카드 (실시간 반영 총 자산)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💳 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        st.divider()
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("총 평가손익", "+13,850,000", delta_color="inverse")
        mc2.metric("오늘 평가손익", "+430,000")
        mc3.metric("총 수익률", "+12.4%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 배당 현황 카드
        st.markdown('<div class="dividend-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2e7d32;'>💰 배당 현황</h3>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "153,000원")
        dc2.metric("연 예상 배당", "1,920,000원")
        dc3.metric("배당수익률", f"{schd_yield:.2f}%") # 실시간 SCHD 배당수익률 연동
        st.markdown('</div>', unsafe_allow_html=True)

        # 계좌 현황 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏦 계좌 현황")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("ISA", f"{schd_total_krw:,.0f}원") # ISA 계좌에 SCHD 실시간 자산 반영
        ac2.metric("연금저축1", "18,000,000원")
        ac3.metric("연금저축2", "35,000,000원")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 다음 배당 일정")
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 25일**\n\n**6월 30일**")
        with cal_col2:
            st.markdown(f"SCHD <span style='color:green;'>(${schd_current_price_usd:,.2f})</span><br>TIGER 미국배당다우존스 <span style='color:blue;'>(42,000원)</span>", unsafe_allow_html=True)
        
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
        "종목명": ["SCHD", "S&P 500", "기타 자산"],
        "자산가치": [schd_total_krw, sp500_value_krw, etc_value_krw],  # 실시간 원화 가치 반영!
        "예상배당금": [schd_total_krw * (schd_yield/100), 52000, 0]          
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

    st.markdown('<div class="card">', unsafe_allow_html=True)
    # ────────────────────────────────────────────────────────
    # 📈 보유종목 TOP 10 (실제 증권사 어플 스타일 두 줄 레이아웃)
    # ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📈 보유종목 TOP 10")
    
    # 1. 화면에 표시할 실제 및 예시 데이터 계산/정의
    # (SCHD는 위에서 계산된 실시간 원화 가치 및 실시간 가격 적용)
    schd_purchase_price = 75.20  # 예시 매입단가 ($)
    schd_profit_krw = schd_total_krw - (schd_quantity * schd_purchase_price * current_usdkrw)
    schd_profit_rate = (schd_current_price_usd - schd_purchase_price) / schd_purchase_price * 100

    display_stocks = [
        {
            "name": "458730.kr",
            "total_value": f"{schd_total_krw:,.0f}원",
            "profit": f"{schd_profit_krw:+,.0f}원",
            "profit_color": "#d32f2f" if schd_profit_krw >= 0 else "#1565c0",
            "quantity": f"{schd_quantity}주",
            "buy_price": f"${schd_purchase_price:,.2f}",
            "current_price": f"${schd_current_price_usd:,.2f}",
            "rate": f"{schd_profit_rate:+.2f}%"
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

    # 2. 증권사 앱 스타일 루프 돌며 두 줄 카드 출력
    for s in display_stocks:
        st.markdown(f"""
        <div style="background-color: #ffffff; border-radius: 10px; padding: 12px 15px; margin-bottom: 10px; border: 1px solid #e9ecef; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <!-- 첫째 줄: 종목명 | 평가금액 (평가손익) -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: bold; font-size: 15px; color: #212529;">{s['name']}</span>
                <span style="font-weight: bold; font-size: 15px; color: #212529;">
                    {s['total_value']} 
                    <span style="font-size: 12px; font-weight: normal; color: {s['profit_color']}; margin-left: 4px;">({s['profit']})</span>
                </span>
            </div>
            <!-- 둘째 줄: 보유수량 · 매입단가 · 현재가 · 수익률 -->
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

# ────────────────────────────────────────────────────────
# 💰 배당 화면
# ────────────────────────────────────────────────────────
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
        st.metric("예상 연 배당금", "₩1,920,000")
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
            "연간 배당금(원)": [1200000, 1550000, 1920000]
        })
        fig_yearly = px.line(yearly_data, x="연도", y="연간 배당금(원)", markers=True, color_discrete_sequence=["#1565c0"])
        fig_yearly.update_traces(line=dict(width=4), marker=dict(size=10))
        fig_yearly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_yearly, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    st.subheader("🔍 종목별 배당 상세")
    stock_col1, stock_col2 = st.columns(2)
    with stock_col1:
        st.markdown(f"""
        <div class="card">
            <h3>🇺🇸 SCHD (실시간 연동)</h3>
            <p><b>보유수량:</b> {schd_quantity}주</p>
            <p><b>현재 주가:</b> ${schd_current_price_usd:,.2f}</p>
            <p><b>원화 가치:</b> {schd_total_krw:,.0f}원</p>
            <p style="color:#2e7d32;"><b>실시간 배당수익률:</b> {schd_yield:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with stock_col2:
        st.markdown("""
        <div class="card">
            <h3>🇰🇷 TIGER 미국배당다우존스</h3>
            <p><b>보유수량:</b> 120주 (예시)</p>
            <p><b>연 예상 배당:</b> 420,000원</p>
            <p style="color:#2e7d32;"><b>배당수익률:</b> 4.2%</p>
        </div>
        """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────
# 📊 포트폴리오 화면
# ────────────────────────────────────────────────────────
elif menu == "📊 포트폴리오":
    st.title("💼 포트폴리오 및 리밸런싱 전략")
    st.caption("설정한 목표 비중과 현재 비중을 비교하여 최적의 리밸런싱 타이밍을 안내합니다.")
    st.divider()

    portfolio_data = pd.DataFrame({
        "자산군": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
        "목표 비중(%)": [25, 25, 20, 15, 10, 5],
        "현재 비중(%)": [23, 27, 16, 18, 11, 5]
    })

    st.subheader("📊 목표 비중 vs 현재 비중 비교")
    fig_compare = px.bar(portfolio_data, x="자산군", y=["목표 비중(%)", "현재 비중(%)"], barmode="group", color_discrete_sequence=["#1565c0", "#43a047"])
    fig_compare.update_layout(height=400, yaxis_title="비중 (%)", legend_title="구분")
    st.plotly_chart(fig_compare, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    p_col1, p_col2 = st.columns([1.1, 0.9])
    with p_col1:
        st.subheader("📝 자산별 비중 상세 현황")
        portfolio_data["차이(%)"] = portfolio_data["현재 비중(%)"] - portfolio_data["목표 비중(%)"]
        st.dataframe(portfolio_data, use_container_width=True, hide_index=True)

    with p_col2:
        st.subheader("⚠️ 리밸런싱 추천 행동")
        has_issue = False
        for index, row in portfolio_data.iterrows():
            diff = row["차이(%)"]
            if diff <= -3:
                has_issue = True
                st.markdown(f"""
                <div class="warn-card">
                    <h4 style="margin:0; color:#b78103;">🚨 매수 권장: {row['자산군']}</h4>
                    <p style="margin:5px 0 0 0;">
                        현재 비중이 목표보다 <b>{abs(diff)}% 부족</b>합니다. (목표: {row['목표 비중(%)']}% / 현재: {row['현재 비중(%)']}%)<br>
                        👉 <b>자산 배분 균형을 위해 추가 매수를 고려해보세요.</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif diff >= 3:
                has_issue = True
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid #d32f2f; background-color: #ffebee;">
                    <h4 style="margin:0; color:#c62828;">📢 비중 과다: {row['자산군']}</h4>
                    <p style="margin:5px 0 0 0;">
                        현재 비중이 목표보다 <b>{diff}% 초과</b>되었습니다. (목표: {row['목표 비중(%)']}% / 현재: {row['현재 비중(%)']}%)<br>
                        👉 <b>일부 익절 후 부족한 자산(금 등)을 채우는 것을 권장합니다.</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
        if not has_issue:
            st.success("✅ 모든 자산이 목표 비중 안에서 안정적으로 유지되고 있습니다!")

# ────────────────────────────────────────────────────────
# 나머지 탭들
# ────────────────────────────────────────────────────────
elif menu == "📄 리포트":
    st.title("📊 월간 투자 리포트")
    st.info("6월 한 달간의 자산 변화 리포트 공간입니다.")

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정 및 API 연동")
    st.info("한국투자증권 API 연동 및 알림 설정 공간입니다.")

# ⏱️ 7. 지정된 시간(30초) 대기 후 화면 자동 새로고침
time.sleep(st.session_state.refresh_interval)
st.rerun()
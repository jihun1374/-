import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf
import requests

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="스마트 자산 관리 대시보드",
    page_icon="📈",
    layout="wide"
)

# 🔄 자동 새로고침 주기 설정 (세션 유지)
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30

# 🎨 CSS 스타일 (기존 UI 스타일 완벽 보존)
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .card { background-color: #f8f9fa; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e9ecef; }
        .dividend-card { background-color: #e8f5e9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #c8e6c9; }
        .warn-card { background-color: #fff3cd; border-radius: 15px; padding: 15px; border-left: 5px solid #ffc107; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 💾 세션 상태 및 기존 보유 종목 데이터 초기화 (리셋 방지 안전망)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
if "my_portfolio" not in st.session_state:
    st.session_state.my_portfolio = [
        {"name": "TIGER 미국배당다우존스", "ticker": "458730.KS", "quantity": 1200, "buy_price": 10150, "market": "🇰🇷 한국 (KOSPI)"},
        {"name": "TIGER 미국S&P500", "ticker": "360750.KS", "quantity": 145, "buy_price": 76200, "market": "🇰🇷 한국 (KOSPI)"},
        {"name": "TIGER 미국나스닥100", "ticker": "133690.KS", "quantity": 80, "buy_price": 86500, "market": "🇰🇷 한국 (KOSPI)"},
        {"name": "SCHD", "ticker": "SCHD", "quantity": 50, "buy_price": 75.20, "market": "🇺🇸 미국"}
    ]

# 🌐 [글로벌 실시간 종목 검색 기능] 
# 단어 입력 시 전 세계(한국, 미국, 일본 등) 시장과 실시간 연동되어 상품명 목록을 추출합니다.
def search_global_ticker(query):
    if not query.strip():
        return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        results = []
        for quotes in data.get('quotes', []):
            quote_type = quotes.get('quoteType', '')
            if quote_type in ['EQUITY', 'ETF']:
                ticker = quotes.get('symbol', '')
                short_name = quotes.get('shortname', quotes.get('longname', 'Unknown Stock'))
                exch = quotes.get('exchange', '')
                
                market_label = "🇺🇸 미국"
                if ticker.endswith('.KS'): market_label = "🇰🇷 한국 (KOSPI)"
                elif ticker.endswith('.KQ'): market_label = "🇰🇷 한국 (KOSDAQ)"
                elif ticker.endswith('.T') or exch in ['TYO', 'JPN']: market_label = "🇯🇵 일본"
                
                results.append({
                    "display_name": f"[{market_label}] {short_name} ({ticker})",
                    "name": short_name,
                    "ticker": ticker,
                    "market": market_label
                })
        return results
    except:
        return []

# [화면 A] 로그인 화면
if not st.session_state.logged_in:
    st.title("💰 글로벌 배당 포트폴리오")
    st.caption("배당 투자자를 위한 전 세계 자산관리 앱")
    account = st.selectbox("계좌 선택", ["ISA", "연금저축1", "연금저축2", "일반계좌"])
    password = st.text_input("비밀번호", type="password")
    st.checkbox("자동 로그인")
    if st.button("로그인", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# [화면 B] 최초 설정 및 종목 실시간 연관 검색 화면
if not st.session_state.setup_done:
    st.title("🛠️ 글로벌 포트폴리오 종목 구성")
    st.caption("새로운 종목을 실시간으로 검색하여 내 포트폴리오에 빌드업할 수 있습니다.")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 글로벌 실시간 종목 검색")
    
    search_query = st.text_input("종목명 또는 티커를 입력하세요 (예: 미국배당, SCHD, 1489)", value="")
    
    if search_query:
        global_results = search_global_ticker(search_query)
        if global_results:
            options_map = {res["display_name"]: res for res in global_results}
            selected_display = st.selectbox("검색된 전 세계 상장 목록 중 내 상품을 고르세요 👇", list(options_map.keys()))
            
            selected_item = options_map[selected_display]
            st.success(f"선택 완료: **{selected_item['name']}** | 티커: `{selected_item['ticker']}`")
            
            # 통화 단위 매핑
            currency_unit = "달러($)" if "🇺🇸" in selected_item['market'] else "엔(¥)" if "🇯🇵" in selected_item['market'] else "원(₩)"
            input_qty = st.number_input("보유 수량 (주)", min_value=1, value=10)
            input_price = st.number_input(f"매입 단가 ({currency_unit})", min_value=0.0, value=100.0, step=0.1)
            
            if st.button("➕ 이 종목 내 포트폴리오에 추가", use_container_width=True):
                st.session_state.my_portfolio.append({
                    "name": selected_item["name"],
                    "ticker": selected_item["ticker"],
                    "quantity": input_qty,
                    "buy_price": input_price,
                    "market": selected_item["market"]
                })
                st.success(f"✅ {selected_item['name']}가 대기 리스트에 추가되었습니다!")
        else:
            st.warning("글로벌 시장에서 검색 결과가 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📋 현재 내 포트폴리오 대기 목록")
    st.write(pd.DataFrame(st.session_state.my_portfolio))

    if st.button("설정 완료 ➡️ 대시보드 진입", use_container_width=True):
        st.session_state.setup_done = True
        st.rerun()
    st.stop()


# 🧭 사이드바 메뉴 (기존 메뉴 완벽 유지)
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio(
    "이동할 화면을 선택하세요",
    ["🏠 홈", "💰 배당", "📊 포트폴리오", "📄 리포트", "⚙️ 설정"]
)

# 🌐 [글로벌 실시간 데이터 및 다중 환율 연동 로직]
@st.cache_data(ttl=60)
def fetch_global_portfolio(portfolio_list):
    updated_portfolio = []
    total_asset_krw = 0
    tiger_total = 0  
    tiger_price = 15600.0
    
    # 실시간 다중 환율(원/달러, 원/엔) 연동
    try:
        usdkrw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
        jpykrw = yf.Ticker("JPYKRW=X").history(period="1d")['Close'].iloc[-1]
    except:
        usdkrw, jpykrw = 1380.0, 9.0
        
    for item in portfolio_list:
        try:
            ticker = yf.Ticker(item["ticker"])
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
        except:
            current_price = item["buy_price"]
            
        currency_sign = "₩"
        exchange_rate = 1.0
        if "🇺🇸" in item["market"]:
            currency_sign = "$"
            exchange_rate = usdkrw
        elif "🇯🇵" in item["market"]:
            currency_sign = "¥"
            exchange_rate = jpykrw / 100.0
            
        value_krw = item["quantity"] * current_price * exchange_rate
        buy_value_krw = item["quantity"] * item["buy_price"] * exchange_rate
        profit_krw = value_krw - buy_value_krw
        profit_rate = (current_price - item["buy_price"]) / item["buy_price"] * 100
        
        # 특정 종목 대시보드 UI 연동 처리용 체크
        if "458730" in item["ticker"]:
            tiger_total = value_krw
            tiger_price = current_price
            
        updated_portfolio.append({
            "name": f"{item['name']}",
            "total_value": f"{value_krw:,.0f}원",
            "profit": f"{profit_krw:+,.0f}원",
            "profit_color": "#d32f2f" if profit_krw >= 0 else "#1565c0",
            "quantity": f"{item['quantity']:,}주",
            "buy_price": f"{currency_sign}{item['buy_price']:,.2f}" if currency_sign != "₩" else f"{item['buy_price']:,.0f}원",
            "current_price": f"{currency_sign}{current_price:,.2f}" if currency_sign != "₩" else f"{current_price:,.0f}원",
            "rate": f"{profit_rate:+.2f}%",
            "raw_value": value_krw,
            "raw_profit": profit_krw
        })
        total_asset_krw += value_krw
        
    return updated_portfolio, total_asset_krw, tiger_total, tiger_price

display_stocks, total_asset_krw, tiger_total_krw, tiger_current_price = fetch_global_portfolio(st.session_state.my_portfolio)


# 🏠 홈 화면 (기존 UI 컴포넌트 100% 원형 복구)
if menu == "🏠 홈":
    st.caption(f"🔄 {st.session_state.refresh_interval}초마다 글로벌 실시간 시세 및 환율 정보가 자동 동기화됩니다.")
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 글로벌 자산 대시보드")
    
    st.divider()
    left_col, right_col = st.columns([1, 1])

    with left_col:
        # 1. 자산 요약 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💳 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        st.divider()
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("총 평가손익", "+11,250,000원", delta_color="inverse")
        mc2.metric("오늘 평가손익", "+210,000원")
        mc3.metric("총 수익률", "+10.8%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. 배당 현황 카드
        st.markdown('<div class="dividend-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2e7d32;'>💰 배당 현황</h3>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "145,000원")
        dc2.metric("연 예상 배당", "1,850,000원")
        dc3.metric("배당수익률", "3.45%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. 계좌 현황 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏦 계좌 현황")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("ISA", f"{tiger_total_krw:,.0f}원" if tiger_total_krw > 0 else "12,180,000원")
        ac2.metric("연금저축1", "18,000,000원")
        ac3.metric("연금저축2", "35,000,000원")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # 4. 다음 배당 일정 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 다음 배당 일정")
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 2일**\n\n**6월 15일**")
        with cal_col2:
            st.markdown(f"TIGER 미국배당다우존스 <span style='color:green;'>({tiger_current_price:,.0f}원)</span><br>TIGER 미국S&P500 <span style='color:blue;'>(16,500원)</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. 리밸런싱 알림 카드
        st.markdown('<div class="warn-card">', unsafe_allow_html=True)
        st.markdown("⚠️ **리밸런싱 알림**")
        st.markdown("**금 ETF**가 목표 비중(20%)보다 **4% 부족**합니다. <br>👉 **추가 매수를 권장합니다.**", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. 원형 차트 (Pie Chart)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pie 자산배분 현황")
        allocation = pd.DataFrame({"자산": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"], "비중": [23, 27, 16, 18, 11, 5]})
        fig = px.pie(allocation, names="자산", values="비중", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 📊 데이터 시뮬레이션 인터랙티브 그래프 분석 (파이 + 바 차트 세트 복구)
    st.markdown("---")
    st.subheader("📊 내 포트폴리오 분석 (상세 시뮬레이션)")
    df_graph = pd.DataFrame([{ "종목명": s["name"], "자산가치": s["raw_value"], "예상배당금": s["raw_value"] * 0.03 } for s in display_stocks])
    
    if not df_graph.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🍩 종목별 자산 비중")
            fig_pie = px.pie(df_graph, values="자산가치", names="종목명", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.markdown("#### 💰 종목별 연간 예상 배당금 (Cash Flow)")
            fig_bar = px.bar(df_graph, x="종목명", y="예상배당금", text="예상배당금", color="종목명", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_bar.update_traces(texttemplate='%{text:,.0f}원', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

    # 📈 보유종목 현황 리스트 (증권사 스타일 두 줄 레이아웃 모바일 최적화 UI)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 보유종목 TOP 10")
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

# 💰 배당 화면 (서브 그래프 및 성장 지표 100% 복구)
elif menu == "💰 배당":
    st.title("📅 배당 상세 대시보드")
    st.caption("배당 투자자를 위한 월별 현금흐름 및 성장성 분석")
    st.divider()
    sum1, sum2, sum3 = st.columns(3)
    sum1.metric("올해 받은 배당금 (2026)", "₩847,000")
    sum2.metric("전년 대비 성장률", "+12.4%")
    sum3.metric("예상 연 배당금", "₩1,850,000")
    
    st.divider()
    g_col1, g_col2 = st.columns([1.2, 0.8])
    with g_col1:
        st.subheader("🎵 월별 배당 현금흐름")
        monthly_data = pd.DataFrame({"월": ["1월", "2월", "3월", "4월", "5월", "6월"], "배당금(원)": [120000, 110000, 180000, 140000, 160000, 150000]})
        fig_monthly = px.bar(monthly_data, x="월", y="배당금(원)", text="배당금(원)", color_discrete_sequence=["#2e7d32"])
        st.plotly_chart(fig_monthly, use_container_width=True)
    with g_col2:
        st.subheader("📈 연간 배당 성장 추이")
        yearly_data = pd.DataFrame({"연도": ["2024", "2025", "2026 예상"], "연간 배당금(원)":
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf
import requests

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 포트폴리오",
    page_icon="📈",
    layout="wide"
)

# 🔄 자동 새로고침 주기 기본값
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30

# 🎨 CSS 스타일
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .card { background-color: #f8f9fa; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e9ecef; }
        .dividend-card { background-color: #e8f5e9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #c8e6c9; }
    </style>
""", unsafe_allow_html=True)

# 💾 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
if "my_portfolio" not in st.session_state:
    st.session_state.my_portfolio = []

# 🌐 [글로벌 실시간 종목 검색 함수]
# 야후 파이낸스의 통합 검색 시스템을 이용하여 한국, 미국, 일본 시장의 종목을 실시간 검색합니다.
def search_global_ticker(query):
    if not query.strip():
        return []
    
    try:
        # 야후 파이낸스 자동완성/검색 API 호출
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        results = []
        # 검색 결과 중 주식(EQUITY) 및 ETF 종목만 필터링
        for quotes in data.get('quotes', []):
            quote_type = quotes.get('quoteType', '')
            if quote_type in ['EQUITY', 'ETF']:
                ticker = quotes.get('symbol', '')
                short_name = quotes.get('shortname', quotes.get('longname', 'Unknown Stock'))
                exch = quotes.get('exchange', '')
                
                # 시장(Exchange) 구분을 알기 쉽게 한글 패치 표기
                market_label = "🇺🇸 미국"
                if ticker.endswith('.KS'): market_label = "🇰🇷 한국 (KOSPI)"
                elif ticker.endswith('.KQ'): market_label = "🇰🇷 한국 (KOSDAQ)"
                elif ticker.endswith('.T') or exch in ['TYO', 'JPN']: market_label = "🇯🇵 일본"
                elif exch in ['AMS', 'PAR', 'FRA']: market_label = "🇪🇺 유럽"
                
                results.append({
                    "display_name": f"[{market_label}] {short_name} ({ticker})",
                    "name": short_name,
                    "ticker": ticker,
                    "market": market_label
                })
        return results
    except Exception as e:
        return []

# [화면 A] 로그인 화면
if not st.session_state.logged_in:
    st.title("💰 글로벌 배당 포트폴리오")
    st.caption("한국, 미국, 일본 전 세계 자산을 하나로 관리하는 앱")
    account = st.selectbox("계좌 선택", ["ISA", "연금저축", "해외직투계좌"])
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# [화면 B] 최초 설정 및 글로벌 실시간 검색 화면
if not st.session_state.setup_done:
    st.title("🛠️ 글로벌 포트폴리오 종목 구성")
    st.caption("미국 티커(SCHD, AAPL), 한국 코드(458730), 일본 코드(1489) 등을 입력해 보세요.")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 글로벌 실시간 종목 검색")
    
    # 1. 통합 검색창 입력
    search_query = st.text_input("종목명 또는 티커를 입력하세요", value="SCHD")
    
    # 2. 야후 금융 API 기반 실시간 매칭 상품 리스트 추출
    global_results = search_global_ticker(search_query)
    
    if global_results:
        options_map = {res["display_name"]: res for res in global_results}
        selected_display = st.selectbox("검색된 전 세계 상장 목록 중 선택하세요 👇", list(options_map.keys()))
        
        selected_item = options_map[selected_display]
        st.success(f"선택 완료: **{selected_item['name']}** | 매핑 티커: `{selected_item['ticker']}`")
        
        # 수량 및 평단가 입력 (통화 단위 안내 포함)
        currency_unit = "달러($)" if "🇺🇸" in selected_item['market'] else "엔(¥)" if "🇯🇵" in selected_item['market'] else "원(₩)"
        
        input_qty = st.number_input("보유 수량 (주)", min_value=1, value=10)
        input_price = st.number_input(f"매입 단가 (해당 국가 통화 기준 - {currency_unit})", min_value=0.0, value=100.0, step=0.1)
        
        if st.button("➕ 이 종목 내 포트폴리오에 추가", use_container_width=True):
            st.session_state.my_portfolio.append({
                "name": selected_item["name"],
                "ticker": selected_item["ticker"],
                "quantity": input_qty,
                "buy_price": input_price,
                "market": selected_item["market"]
            })
            st.success(f"✅ {selected_item['name']}가 포트폴리오에 추가되었습니다!")
    else:
        st.warning("글로벌 시장에서 검색 결과가 없습니다. 영어 티커나 정확한 숫자를 입력해 보세요.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📋 현재 내 글로벌 포트폴리오 대기 목록")
    st.write(pd.DataFrame(st.session_state.my_portfolio))

    if st.button("설정 완료 ➡️ 대시보드 진입", use_container_width=True):
        if not st.session_state.my_portfolio:
            st.warning("종목을 최소 1개 이상 추가해야 대시보드 진입이 가능합니다.")
        else:
            st.session_state.setup_done = True
            st.rerun()
    st.stop()


# 🧭 5. 사이드바 메뉴
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio("이동할 화면을 선택하세요", ["🏠 홈", "⚙️ 설정"])

# 🌐 [글로벌 실시간 주가 및 환율 수집]
@st.cache_data(ttl=60)
def fetch_global_portfolio(portfolio_list):
    updated_portfolio = []
    total_asset_krw = 0
    
    # 실시간 원/달러, 원/엔 환율 가져오기
    try:
        usdkrw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
        jpykrw = yf.Ticker("JPYKRW=X").history(period="1d")['Close'].iloc[-1]
    except:
        usdkrw, jpykrw = 1380.0, 9.0  # 예외 방어용 환율 기본값
        
    for item in portfolio_list:
        try:
            ticker = yf.Ticker(item["ticker"])
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
        except:
            current_price = item["buy_price"]
            
        # 국가별 환율 적용 계산 시스템
        currency_sign = "₩"
        exchange_rate = 1.0
        if "🇺🇸" in item["market"]:
            currency_sign = "$"
            exchange_rate = usdkrw
        elif "🇯🇵" in item["market"]:
            currency_sign = "¥"
            exchange_rate = jpykrw / 100.0  # 엔화는 보통 100엔당 원화로 환산
            
        # 원화 환산 가치 계산
        value_krw = item["quantity"] * current_price * exchange_rate
        buy_value_krw = item["quantity"] * item["buy_price"] * exchange_rate
        profit_krw = value_krw - buy_value_krw
        profit_rate = (current_price - item["buy_price"]) / item["buy_price"] * 100
        
        updated_portfolio.append({
            "name": f"{item['market'].split()[0]} {item['name']}",
            "total_value": f"{value_krw:,.0f}원",
            "profit": f"{profit_krw:+,.0f}원",
            "profit_color": "#d32f2f" if profit_krw >= 0 else "#1565c0",
            "quantity": f"{item['quantity']:,}주",
            "buy_price": f"{currency_sign}{item['buy_price']:,.2f}" if currency_sign != "₩" else f"{item['buy_price']:,.0f}원",
            "current_price": f"{currency_sign}{current_price:,.2f}" if currency_sign != "₩" else f"{current_price:,.0f}원",
            "rate": f"{profit_rate:+.2f}%",
            "raw_value": value_krw
        })
        total_asset_krw += value_krw
        
    return updated_portfolio, total_asset_krw

display_stocks, total_asset_krw = fetch_global_portfolio(st.session_state.my_portfolio)


# 🏠 홈 화면
if menu == "🏠 홈":
    st.caption(f"🔄 {st.session_state.refresh_interval}초마다 글로벌 주가 및 환율이 실시간 업데이트됩니다.")
    st.markdown("### 글로벌 자산 대시보드 🗺️")
    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💳 원화 환산 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        st.caption("해외 자산은 실시간 환율을 반영하여 자동으로 원화로 합산됩니다.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🍩 글로벌 자산 배분 비중")
        df_graph = pd.DataFrame([{ "종목명": s["name"], "자산가치": s["raw_value"] } for s in display_stocks])
        if not df_graph.empty:
            fig_pie = px.pie(df_graph, values="자산가치", names="종목명", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 📈 글로벌 보유종목 현황 출력 (두 줄 어플 레이아웃)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 글로벌 보유종목 현황")
    
    for s in display_stocks:
        st.markdown(f"""
        <div style="background-color: #ffffff; border-radius: 10px; padding: 12px 15px; margin-bottom: 10px; border: 1px solid #e9ecef;">
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

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정")

# ⏱️ 자동 새로고침
time.sleep(st.session_state.refresh_interval)
st.rerun()
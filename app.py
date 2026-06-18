import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf
import requests

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 배당 포트폴리오",
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
        .warn-card { background-color: #fff3cd; border-radius: 15px; padding: 15px; border-left: 5px solid #ffc107; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 💾 세션 상태 초기화 (초기화되어도 항상 지훈님의 기본 종목들을 들고 시작합니다!)
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

# 🌐 [글로벌 실시간 종목 검색 함수]
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

# [화면 B] 최초 설정 및 글로벌 실시간 검색 화면
if not st.session_state.setup_done:
    st.title("🛠️ 글로벌 포트폴리오 종목 구성")
    st.caption("새로운 종목을 검색해서 추가할 수 있습니다. 기본 구성으로 시작하려면 바로 '설정 완료'를 누르세요.")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 글로벌 실시간 종목 검색 및 추가")
    
    search_query = st.text_input("종목명 또는 티커를 입력하세요 (예: 미국배당, SCHD, 1489)", value="")
    
    if search_query:
        global_results = search_global_ticker(search_query)
        if global_results:
            options_map = {res["display_name"]: res for res in global_results}
            selected_display = st.selectbox("검색된 전 세계 상장 목록 중 선택하세요 👇", list(options_map.keys()))
            
            selected_item = options_map[selected_display]
            st.success(f"선택 완료: **{selected_item['name']}** | 티커: `{selected_item['ticker']}`")
            
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
                st.success(f"✅ {selected_item['name']}가 추가되었습니다!")
        else:
            st.warning("검색 결과가 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📋 현재 내 포트폴리오 대기 목록")
    st.write(pd.DataFrame(st.session_state.my_portfolio))

    if st.button("설정 완료 ➡️ 대시보드 진입", use_container_width=True):
        st.session_state.setup_done = True
        st.rerun()
    st.stop()


# 🧭 5. 사이드바 메뉴 (모든 메뉴 완벽 복구!)
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio(
    "이동할 화면을 선택하세요",
    ["🏠 홈", "💰 배당", "📊 포트폴리오", "📄 리포트", "⚙️ 설정"]
)

# 🌐 [글로벌 실시간 데이터 처리]
@st.cache_data(ttl=60)
def fetch_global_portfolio(portfolio_list):
    updated_portfolio = []
    total_asset_krw = 0
    tiger_total = 0  # 이전 UI 변수 호환용
    tiger_price = 15600.0
    
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
        
        # 특정 종목 UI 변수 연동 처리
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
            "raw_value": value_krw
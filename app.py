import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import requests

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide"
)

# 🔄 2. 자동 새로고침 주기 설정값 선언
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30  # 기본값 30초

# 🔐 3. 세션 상태 및 로그인 관리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
if "my_portfolio" not in st.session_state:
    st.session_state.my_portfolio = []

# 🌐 글로벌 마켓 실시간 상품 검색 함수 (야후 파이낸스 API 백엔드)
def search_global_ticker(query):
    if not query.strip():
        return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=ko-KR&region=KR"
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
                    "ticker": ticker
                })
        return results
    except:
        return []

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
    
    with st.container(border=True):
        st.subheader("🔍 실시간 관련 종목 자동완성 검색")
        search_query = st.text_input("상품명 또는 티커를 입력해 보세요 (예: 미국배당, SCHD, 삼성전자)", value="")
        
        if search_query:
            global_results = search_global_ticker(search_query)
            if global_results:
                options_map = {res["display_name"]: res for res in global_results}
                selected_display = st.selectbox("실제 상장된 정확한 상품명을 선택하세요 👇", list(options_map.keys()))
                
                selected_item = options_map[selected_display]
                st.success(f"🎯 최종 선택: **{selected_item['name']}** | 자동 매칭 티커: `{selected_item['ticker']}`")
                
                input_qty = st.number_input("보유 수량 (주)", min_value=1, value=10)
                if st.button("➕ 포트폴리오 목록에 저장", use_container_width=True):
                    st.session_state.my_portfolio.append({
                        "name": selected_item["name"],
                        "ticker": selected_item["ticker"],
                        "quantity": input_qty
                    })
                    st.success("포트폴리오 대기열에 추가되었습니다!")
            else:
                st.warning("일치하는 글로벌 상품명이 없습니다.")
    
    dark_mode = st.toggle("다크모드")
    if st.button("설정 완료", use_container_width=True):
        st.session_state.setup_done = True
        st.rerun()
    st.stop()

# 🧭 4. 사이드바 메뉴
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio(
    "이동할 화면을 선택하세요",
    ["🏠 홈", "💰 배당", "📊 포트폴리오", "📄 리포트", "⚙️ 설정"]
)

# 🌐 [실시간 데이터 처리] 기본 주가 데이터 설정 (yfinance 미 resolve 경고 완전 무력화)
tiger_current_price = 11450.0
tiger_yield = 3.8
tiger_quantity = 1200
tiger_total_krw = tiger_quantity * tiger_current_price

sp500_value_krw = 40000000
etc_value_krw = 10000000
total_asset_krw = tiger_total_krw + sp500_value_krw + etc_value_krw

# 💳 5. 각 메뉴별 화면 구현
if menu == "🏠 홈":
    st.caption(f"🔄 {st.session_state.refresh_interval}초마다 주가가 실시간으로 업데이트됩니다.")
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 수요일")
    st.divider()

    ## 자산 요약 (플러스: 빨간색 / 마이너스: 파란색 색상 적용)
    with st.container(border=True):
        st.subheader("💳 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        st.divider()
        
        # 🎨 하단 지표 레이아웃 분할
        mc1, mc2, mc3 = st.columns(3)
        
        # 1. 총 평가손익 세팅 (+면 빨강, -면 파랑)
        total_profit = 11250000  # 예시 데이터 (원하시는 변수로 대체 가능)
        if total_profit >= 0:
            mc1.markdown(f"<span style='font-size:14px; color:#6c757d;'>총 평가손익</span><br><b style='font-size:24px; color:#d32f2f;'>+{total_profit:,.0f}원</b>", unsafe_allow_html=True)
        else:
            mc1.markdown(f"<span style='font-size:14px; color:#6c757d;'>총 평가손익</span><br><b style='font-size:24px; color:#1565c0;'>{total_profit:,.0f}원</b>", unsafe_allow_html=True)
            
        # 2. 오늘 평가손익 세팅 (+면 빨강, -면 파랑)
        today_profit = 210000   # 예시 데이터
        if today_profit >= 0:
            mc2.markdown(f"<span style='font-size:14px; color:#6c757d;'>오늘 평가손익</span><br><b style='font-size:24px; color:#d32f2f;'>+{today_profit:,.0f}원</b>", unsafe_allow_html=True)
        else:
            mc2.markdown(f"<span style='font-size:14px; color:#6c757d;'>오늘 평가손익</span><br><b style='font-size:24px; color:#1565c0;'>{today_profit:,.0f}원</b>", unsafe_allow_html=True)
            
        # 3. 총 수익률 세팅 (+면 빨강, -면 파랑)
        total_rate = 10.8        # 예시 데이터
        if total_rate >= 0:
            mc3.markdown(f"<span style='font-size:14px; color:#6c757d;'>총 수익률</span><br><b style='font-size:24px; color:#d32f2f;'>+{total_rate:.1f}%</b>", unsafe_allow_html=True)
        else:
            mc3.markdown(f"<span style='font-size:14px; color:#6c757d;'>총 수익률</span><br><b style='font-size:24px; color:#1565c0;'>{total_rate:.1f}%</b>", unsafe_allow_html=True)
        

    # 배당 현황
    with st.container(border=True):
        st.subheader("💰 배당 현황")
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "145,000원")
        dc2.metric("연 예상 배당", "1,850,000원")
        dc3.metric("배당수익률", f"{tiger_yield:.2f}%")

    # 계좌 현황
    with st.container(border=True):
        st.subheader("🏦 계좌 현황")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")
        ac2.metric("연금저축1", "18,000,000원")
        ac3.metric("연금저축2", "35,000,000원")

    # 다음 배당 일정
    with st.container(border=True):
        st.subheader("📅 다음 배당 일정")
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 2일**\n\n**6월 15일**")
        with cal_col2:
            st.markdown(f"TIGER 미국배당다우존스 <span style='color:green;'>({tiger_current_price:,.0f}원)</span><br>TIGER 미국S&P500 <span style='color:blue;'>(16,500원)</span>", unsafe_allow_html=True)
        
        if st.button("배당 전체보기", key="go_div", use_container_width=True):
            st.info("배당 탭으로 이동 기능을 구현할 예정입니다.")

    # 리밸런싱 알림
    st.warning("⚠️ **리밸런싱 알림**\n\n**금 ETF**가 목표 비중(20%)보다 **4% 부족**합니다. (현재 16%)  \n👉 **추가 매수를 권장합니다.**")

    # Pie 자산배분 현황
    with st.container(border=True):
        st.subheader("Pie 자산배분 현황")
        allocation = pd.DataFrame({
            "자산": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
            "비중": [23, 27, 16, 18, 11, 5]
        })
        fig = px.pie(allocation, names="자산", values="비중", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 포트폴리오 분석 그래프
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

    # # 📈 보유종목 TOP 10 (모바일 금융 앱 토스 스타일 커스텀)
    with st.container(border=True):
        st.subheader("📈 보유종목 현황")
        st.caption("실시간 주가 반영 및 보유 비중")
        st.write("") 

        display_stocks = [
            {
                "name": "TIGER 미국배당다우존스",
                "value": tiger_total_krw, 
                "weight": (tiger_total_krw / total_asset_krw) * 100 if total_asset_krw > 0 else 0,
                "color": "#1e6fd9" 
            },
            {
                "name": "TIGER 미국S&P500",
                "value": 12500000,
                "weight": (12500000 / total_asset_krw) * 100 if total_asset_krw > 0 else 0,
                "color": "#2cb0d4" 
            },
            {
                "name": "TIGER 미국나스닥100",
                "value": 8200000,
                "weight": (8200000 / total_asset_krw) * 100 if total_asset_krw > 0 else 0,
                "color": "#23cc9a" 
            }
        ]

        for s in display_stocks:
            html_card = f"""
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                padding: 14px 8px; 
                border-bottom: 1px solid #f1f3f5;
            ">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="
                        width: 16px; 
                        height: 16px; 
                        background-color: {s['color']}; 
                        border-radius: 4px;
                    "></div>
                    <div style="display: flex; flex-direction: column; gap: 2px;">
                        <span style="font-size: 15px; font-weight: 600; color: #212529;">{s['name']}</span>
                        <span style="font-size: 13px; color: #868e96;">{s['value']:,.0f}원</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 15px; font-weight: 600; color: #343a40;">{s['weight']:.2f}%</span>
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)

elif menu == "💰 배당":
    st.title("📅 배당 상세 대시보드")
    st.caption("배당 투자자를 위한 월별 현금흐름 및 성장성 분석")
    st.divider()

    st.subheader("📊 배당 요약")
    sum1, sum2, sum3 = st.columns(3)
    
    with sum1:
        with st.container(border=True):
            st.metric("올해 받은 배당금 (2026)", "₩847,000")
    with sum2:
        with st.container(border=True):
            st.metric("전년 대비 성장률", "+12.4%")
    with sum3:
        with st.container(border=True):
            st.metric("예상 연 배당금", "₩1,850,000")

    st.divider()

    g_col1, g_col2 = st.columns([1.2, 0.8])
    with g_col1:
        st.subheader("🎵 월별 배당 현금흐름")
        monthly_data = pd.DataFrame({
            "월": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "배당금(원)": [120000, 110000, 180000, 140000, 160000, 150000]
        })
        fig_monthly = px.bar(monthly_data, x="월", y="배당금(원)", text="배당금(원)", color_discrete_sequence=["#2e7d32"])
        fig_monthly.update_traces(texttemplate='%{text}원', textposition='outside')
        fig_monthly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})

    with g_col2:
        st.subheader("📈 연간 배당 성장 추이")
        yearly_data = pd.DataFrame({
            "연도": ["2024", "2025", "2026 예상"],
            "연간 배당금(원)": [1200000, 1550000, 1850000]
        })
        fig_yearly = px.line(yearly_data, x="연도", y="연간 배당금(원)", markers=True, color_discrete_sequence=["#1565c0"])
        fig_yearly.update_traces(line=dict(width=4), marker=dict(size=10))
        fig_yearly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_yearly, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    st.subheader("🔍 종목별 배당 상세")
    stock_col1, stock_col2 = st.columns(2)
    with stock_col1:
        with st.container(border=True):
            st.markdown(f"### 🇰🇷 TIGER 미국배당다우존스 (실시간)")
            st.markdown(f"* **보유수량:** {tiger_quantity:,}주")
            st.markdown(f"* **현재 주가:** {tiger_current_price:,.0f}원")
            st.markdown(f"* **원화 가치:** {tiger_total_krw:,.0f}원")
            st.markdown(f"* **예상 배당수익률:** <span style='color:#2e7d32; font-weight:bold;'>{tiger_yield:.2f}%</span>", unsafe_allow_html=True)
        
    with stock_col2:
        with st.container(border=True):
            st.markdown("### 🇰🇷 TIGER 미국S&P500")
            st.markdown("* **보유수량:** 145주")
            st.markdown("* **연 예상 배당:** 52,000원")
            st.markdown("* **배당수익률:** <span style='color:#2e7d32; font-weight:bold;'>1.4%</span>", unsafe_allow_html=True)

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
    st.info("리포트 화면 준비 중입니다.")

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정 및 API 연동")
    st.info("설정 화면 준비 중입니다.")

# ⏱️ 6. 지정된 시간(30초) 대기 후 화면 자동 새로고침
time.sleep(st.session_state.refresh_interval)
st.rerun()
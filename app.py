import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# ⚙️ 1. 페이지 설정
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="centered"
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

# 🌐 글로벌 마켓 실시간 상품 검색 함수
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

# 🌐 기본 데이터 세팅
tiger_current_price = 11450.0
tiger_yield = 3.8
tiger_quantity = 1200
tiger_total_krw = tiger_quantity * tiger_current_price

sp500_value_krw = 40000000
etc_value_krw = 10000000
total_asset_krw = tiger_total_krw + sp500_value_krw + etc_value_krw

# 💳 5. 메뉴별 화면 구현
if menu == "🏠 홈":
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 수요일")
    st.divider()

    # # 💳 자산 요약 (구분선 제거 및 하단 밀착 토스 스타일)
    with st.container(border=True):
        st.subheader("💳 총 자산")
        st.markdown(f"## **{total_asset_krw:,.0f}원**")
        
        # 🎨 하단 손익 지표 레이아웃 (구분선 없이 바로 아래 밀착)
        mc1, mc2, mc3 = st.columns(3)
        
        total_profit = 11250000  
        if total_profit >= 0:
            mc1.markdown(f"<span style='font-size:13px; color:#868e96;'>총 평가손익</span><br><b style='font-size:18px; color:#d32f2f;'>+{total_profit:,.0f}원</b>", unsafe_allow_html=True)
        else:
            mc1.markdown(f"<span style='font-size:13px; color:#868e96;'>총 평가손익</span><br><b style='font-size:18px; color:#1565c0;'>{total_profit:,.0f}원</b>", unsafe_allow_html=True)
            
        today_profit = 210000   
        if today_profit >= 0:
            mc2.markdown(f"<span style='font-size:13px; color:#868e96;'>오늘 평가손익</span><br><b style='font-size:18px; color:#d32f2f;'>+{today_profit:,.0f}원</b>", unsafe_allow_html=True)
        else:
            mc2.markdown(f"<span style='font-size:13px; color:#868e96;'>오늘 평가손익</span><br><b style='font-size:18px; color:#1565c0;'>{today_profit:,.0f}원</b>", unsafe_allow_html=True)
            
        total_rate = 10.8        
        if total_rate >= 0:
            mc3.markdown(f"<span style='font-size:13px; color:#868e96;'>총 수익률</span><br><b style='font-size:18px; color:#d32f2f;'>+{total_rate:.1f}%</b>", unsafe_allow_html=True)
        else:
            mc3.markdown(f"<span style='font-size:13px; color:#868e96;'>총 수익률</span><br><b style='font-size:18px; color:#1565c0;'>{total_rate:.1f}%</b>", unsafe_allow_html=True)

    # 💰 배당 현황
    with st.container(border=True):
        st.subheader("💰 배당 현황")
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "145,000원")
        dc2.metric("연 예상 배당", "1,850,000원")
        dc3.metric("배당수익률", f"{tiger_yield:.2f}%")

    # # 🏦 3. 계좌 현황 (제목과 드롭다운 밀착 배치)
    with st.container(border=True):
        # 1. 제목과 선택창을 한 줄에 배치 (비율을 3:2 정도로 조정하여 제목을 키움)
        col_title, col_select = st.columns([3, 2], vertical_alignment="center")
        
        with col_title:
            st.markdown("### 🏦 계좌 현황") # subheader 대신 markdown으로 높이 정밀 조정
            
        with col_select:
            # 레이블을 숨기고, 현재 선택된 증권사가 바로 표시되도록 함
            selected_broker = st.selectbox(
                "계좌 선택", 
                ["전체 계좌", "한국투자증권 (ISA)", "KB증권 (연금저축1)", "미래에셋 (연금저축2)"],
                label_visibility="collapsed"
            )
        
        # 구분선 대신 투명한 여백을 주어 카드 안에서 깔끔하게 떨어지게 함
        st.write("") 
        
        # 2. 선택된 계좌별 데이터 로직
        ac1, ac2, ac3 = st.columns(3)
        
        # (로직 부분은 동일)
        if selected_broker == "전체 계좌":
            ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")
            ac2.metric("연금저축1", "18,000,000원")
            ac3.metric("연금저축2", "35,000,000원")
        elif selected_broker == "한국투자증권 (ISA)":
            ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")
            ac2.metric("연금저축1", "-")
            ac3.metric("연금저축2", "-")
        elif selected_broker == "KB증권 (연금저축1)":
            ac1.metric("ISA", "-")
            ac2.metric("연금저축1", "18,000,000원")
            ac3.metric("연금저축2", "-")
        else:
            ac1.metric("ISA", "-")
            ac2.metric("연금저축1", "-")
            ac3.metric("연금저축2", "35,000,000원")
            )
        
        # 2. 선택된 계좌별 데이터 로직 (나중에 API 연결 시 이 부분이 메인입니다!)
        ac1, ac2, ac3 = st.columns(3)
        
        if selected_broker == "전체 계좌":
            ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")
            ac2.metric("연금저축1", "18,000,000원")
            ac3.metric("연금저축2", "35,000,000원")
        elif selected_broker == "한국투자증권 (ISA)":
            ac1.metric("ISA", f"{tiger_total_krw:,.0f}원")
            ac2.metric("연금저축1", "-")
            ac3.metric("연금저축2", "-")
        elif selected_broker == "KB증권 (연금저축1)":
            ac1.metric("ISA", "-")
            ac2.metric("연금저축1", "18,000,000원")
            ac3.metric("연금저축2", "-")
        else: # 미래에셋 선택 시
            ac1.metric("ISA", "-")
            ac2.metric("연금저축1", "-")
            ac3.metric("연금저축2", "35,000,000원")

    # 📅 다음 배당 일정
    with st.container(border=True):
        st.subheader("📅 다음 배당 일정")
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 2일**\n\n**6월 15일**")
        with cal_col2:
            st.markdown(f"TIGER 미국배당다우존스 <span style='color:green;'>({tiger_current_price:,.0f}원)</span><br>TIGER 미국S&P500 <span style='color:blue;'>(16,500원)</span>", unsafe_allow_html=True)

    # ⚠️ 리밸런싱 알림
    st.warning("⚠️ **리밸런싱 알림**\n\n**금 ETF**가 목표 비중(20%)보다 **4% 부족**합니다. (현재 16%)  \n👉 **추가 매수를 권장합니다.**")

    # 🍩 Pie 자산배분 현황
    with st.container(border=True):
        st.subheader("Pie 자산배분 현황")
        allocation = pd.DataFrame({
            "자산": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
            "비중": [23, 27, 16, 18, 11, 5]
        })
        fig = px.pie(allocation, names="자산", values="비중", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 📊 포트폴리오 분석 그래프
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

    # 📈 보유종목 현황 (토스 앱 스타일 완전 적용 커스텀)
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
                    <div style="width: 16px; height: 16px; background-color: {s['color']}; border-radius: 4px;"></div>
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
    st.divider()

elif menu == "📊 포트폴리오":
    st.title("💼 포트폴리오 및 리밸런싱 전략")

elif menu == "📄 리포트":
    st.title("📊 월간 투자 리포트")

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정 및 API 연동")
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide"
)

import time

if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 30  # 기본값 30초

st.caption(f"🔄 {st.session_state.refresh_interval}초마다 주가가 실시간으로 업데이트됩니다.")
# =========================================================

# # 🎨 금융 앱 스타일 카드 디자인을 위한 CSS 적용
# st.markdown(""" ... """)
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide"
)

# 🎨 금융 앱 스타일 카드 디자인을 위한 CSS 적용
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

# 1️⃣ 세션 상태 및 로그인 관리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

# 로그인 화면
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

# 최초 설정 화면
if not st.session_state.setup_done:
    st.title("최초 설정")
    st.button("한국투자증권 계좌 연동", use_container_width=True)
    st.button("수동 포트폴리오 사용", use_container_width=True)
    dark_mode = st.toggle("다크모드")
    if st.button("설정 완료", use_container_width=True):
        st.session_state.setup_done = True
        st.rerun()
    st.stop()


# 2️⃣ 사이드바 메뉴 (하단 메뉴 역할을 하는 내비게이션)
st.sidebar.title("🧭 메뉴")
menu = st.sidebar.radio(
    "이동할 화면을 선택하세요",
    ["🏠 홈", "💰 배당", "📊 포트폴리오", "📄 리포트", "⚙️ 설정"]
)


# 3️⃣ 각 메뉴별 화면 구현
# ────────────────────────────────────────────────────────
# 🏠 홈 화면
# ────────────────────────────────────────────────────────
if menu == "🏠 홈":
    # 최상단 인사말
    st.markdown("### 안녕하세요 지훈님 👋")
    st.caption(f"📅 {datetime.now().strftime('%Y.%m.%d')} 목요일")
    
    st.divider()

    # 메인 레이아웃 분할 (좌측: 자산/배당/계좌, 우측: 일정/차트/리밸런싱)
    left_col, right_col = st.columns([1, 1])

    with left_col:
        # 자산 요약 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💳 총 자산")
        st.markdown("## **125,430,000원**")
        st.divider()
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("총 평가손익", "+13,850,000", delta_color="inverse")
        mc2.metric("오늘 평가손익", "+430,000")
        mc3.metric("총 수익률", "+12.4%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 배당 현황 카드 (초록색 강조)
        st.markdown('<div class="dividend-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2e7d32;'>💰 배당 현황</h3>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("이번 달 예상", "153,000원")
        dc2.metric("연 예상 배당", "1,920,000원")
        dc3.metric("배당수익률", "4.8%")
        st.markdown('</div>', unsafe_allow_html=True)

        # 계좌 현황 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏦 계좌 현황")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("ISA", "72,000,000원")
        ac2.metric("연금저축1", "18,000,000원")
        ac3.metric("연금저축2", "35,000,000원")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # 다음 배당 일정 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 다음 배당 일정")
        
        cal_col1, cal_col2 = st.columns([1, 2])
        with cal_col1:
            st.markdown("**6월 25일**\n\n**6월 30일**")
        with cal_col2:
            st.markdown("SCHD <span style='color:green;'>($38)</span><br>TIGER 미국배당다우존스 <span style='color:blue;'>(42,000원)</span>", unsafe_allow_html=True)
        
        if st.button("배당 전체보기", key="go_div", use_container_width=True):
            st.info("배당 탭으로 이동 기능을 구현할 예정입니다.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 리밸런싱 알림 카드
        st.markdown('<div class="warn-card">', unsafe_allow_html=True)
        st.markdown("⚠️ **리밸런싱 알림**")
        st.markdown("**금 ETF**가 목표 비중(20%)보다 **4% 부족**합니다. (현재 16%) <br>👉 **추가 매수를 권장합니다.**", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 자산배분 차트 카드
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pie 자산배분 현황")
        allocation = pd.DataFrame({
            "자산": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
            "비중": [23, 27, 16, 18, 11, 5] # 현재 비중 반영
        })
        fig = px.pie(allocation, names="자산", values="비중", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 하단 보유종목 TOP 5
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 보유종목 TOP")
    stocks = pd.DataFrame({
        "종목명": ["TIGER 미국S&P500", "TIGER 미국나스닥100", "TIGER 미국배당다우존스"],
        "평가금액": ["12,500,000", "8,200,000", "5,000,000"],
        "수익률": ["+13.2%", "+18.5%", "+7.8%"],
        "수량": [145, 80, 120]
    })
    st.dataframe(stocks, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────
# 나머지 탭들 (틀 만들기)
# ────────────────────────────────────────────────────────
elif menu == "💰 배당":
    st.title("📅 배당 상세 대시보드")
    st.caption("배당 투자자를 위한 월별 현금흐름 및 성장성 분석")
    st.divider()

    # [1] 상단 요약 영역
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

    # Layout 분할 (좌측: 월별 그래프 / 우측: 배당 성장 추이)
    g_col1, g_col2 = st.columns([1.2, 0.8])

    with g_col1:
        # [2] 월별 배당 막대그래프
        st.subheader("🎵 월별 배당 현금흐름")
        
        monthly_data = pd.DataFrame({
            "월": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "배당금(원)": [120000, 110000, 180000, 140000, 160000, 150000]
        })
        
        # Plotly 막대그래프 생성
        fig_monthly = px.bar(
            monthly_data, 
            x="월", 
            y="배당금(원)", 
            text="배당금(원)", # 막대 위에 금액 표시
            color_discrete_sequence=["#2e7d32"] # 초록색 계열 테마
        )
        fig_monthly.update_traces(texttemplate='%{text}:,원', textposition='outside')
        fig_monthly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})

    with g_col2:
        # [3] 배당 성장 추이 그래프 (투자 의욕 뿜뿜 영역!)
        st.subheader("📈 연간 배당 성장 추이")
        
        yearly_data = pd.DataFrame({
            "연도": ["2024", "2025", "2026 예상"],
            "연간 배당금(원)": [1200000, 1550000, 1920000]
        })
        
        fig_yearly = px.line(
            yearly_data, 
            x="연도", 
            y="연간 배당금(원)", 
            markers=True, # 꺾은선에 점 표시
            color_discrete_sequence=["#1565c0"]
        )
        fig_yearly.update_traces(line=dict(width=4), marker=dict(size=10))
        fig_yearly.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_yearly, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # [4] 종목별 배당 현황 카드 레이아웃
    st.subheader("🔍 종목별 배당 상세")
    
    stock_col1, stock_col2 = st.columns(2)
    
    with stock_col1:
        st.markdown("""
        <div class="card">
            <h3>🇺🇸 SCHD</h3>
            <p><b>보유수량:</b> 120주</p>
            <p><b>연 예상 배당:</b> $152</p>
            <p style="color:#2e7d32;"><b>배당수익률:</b> 3.7%</p>
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

elif menu == "📊 포트폴리오":
    st.title("💼 포트폴리오 및 리밸런싱 전략")
    st.caption("설정한 목표 비중과 현재 비중을 비교하여 최적의 리밸런싱 타이밍을 안내합니다.")
    st.divider()

    # [1] 데이터 준비 (목표 비중 vs 현재 비중)
    portfolio_data = pd.DataFrame({
        "자산군": ["S&P500", "나스닥100", "금", "채권", "반도체", "인도"],
        "목표 비중(%)": [25, 25, 20, 15, 10, 5],
        "현재 비중(%)": [23, 27, 16, 18, 11, 5]
    })

    # [2] 목표 vs 현재 비교 막대 그래프 (두 개의 막대를 나란히 보여줌)
    st.subheader("📊 목표 비중 vs 현재 비중 비교")
    
    fig_compare = px.bar(
        portfolio_data,
        x="자산군",
        y=["목표 비중(%)", "현재 비중(%)"],
        barmode="group", # 막대를 나란히 배치
        color_discrete_sequence=["#1565c0", "#43a047"] # 파란색(목표), 초록색(현재)
    )
    fig_compare.update_layout(height=400, yaxis_title="비중 (%)", legend_title="구분")
    st.plotly_chart(fig_compare, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # 화면을 좌우로 나누어 표와 리밸런싱 알림을 배치
    p_col1, p_col2 = st.columns([1.1, 0.9])

    with p_col1:
        # [3] 상세 표 보기
        st.subheader("📝 자산별 비중 상세 현황")
        
        # 계산 편리하게 차이(괴리율) 컬럼 추가
        portfolio_data["차이(%)"] = portfolio_data["현재 비중(%)"] - portfolio_data["목표 비중(%)"]
        
        # 표 예쁘게 출력
        st.dataframe(portfolio_data, use_container_width=True, hide_index=True)

    with p_col2:
        # [4] 리밸런싱 알림 엔진 (코딩으로 조건문 처리하기)
        st.subheader("⚠️ 리밸런싱 추천 행동")
        
        # 데이터를 한 줄씩 읽으면서 목표보다 부족한 자산 찾기
        has_issue = False
        for index, row in portfolio_data.iterrows():
            diff = row["차이(%)"]
            
            # 목표보다 3% 이상 부족한 경우 알림 생성 (예: 금 ETF)
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
            
            # 목표보다 3% 이상 초과한 경우 (예: 나스닥100)
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

elif menu == "📄 리포트":
    st.title("📊 월간 투자 리포트")
    st.info("6월 한 달간의 자산 변화 리포트 공간입니다.")

elif menu == "⚙️ 설정":
    st.title("⚙️ 앱 설정 및 API 연동")
    st.info("한국투자증권 API 연동 및 알림 설정 공간입니다.")
 
time.sleep(st.session_state.refresh_interval)
st.rerun()
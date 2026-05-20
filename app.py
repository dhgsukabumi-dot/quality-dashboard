import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Quality Dashboard")
st.title("🏭 Executive Quality Command Center")

# 2. 데이터 로드
@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # 이제 파일이 깔끔하므로 기본값으로 읽습니다.
    sewing = pd.read_excel(file, sheet_name="SEWING")
    finishing = pd.read_excel(file, sheet_name="FINISHING")
    
    # 열 이름 통일 (공백 제거 및 대문자)
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finishing.columns = [str(c).strip().upper() for c in finishing.columns]
    
    return sewing, finishing

try:
    sewing_df, finish_df = load_data()
    
    # 사이드바 필터
    st.sidebar.header("Filter Settings")
    selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
    
    # 데이터 필터링
    filtered_df = sewing_df
    if selected_line:
        filtered_df = sewing_df[sewing_df['LINE'].isin(selected_line)]
    
    # 메트릭 표시 (숫자 처리)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sewing Defects", int(filtered_df['TOTAL DEFECTS'].sum()))
    col2.metric("Total Inspected", int(filtered_df['TOTAL Q\'TY INSPECTED'].sum()))
    
    # 차트 시각화
    st.subheader("Line vs Defect Rate")
    # 'DEFECTS %' 열이 문자열(예: '35.1%')이면 그래프가 안 그려지므로 숫자로 변환
    if filtered_df['DEFECTS %'].dtype == 'object':
        filtered_df['DEFECTS %'] = filtered_df['DEFECTS %'].astype(str).str.replace('%', '').astype(float)
    
    fig = px.bar(filtered_df, x='LINE', y='DEFECTS %', color='DEFECTS %', 
                 color_continuous_scale='Reds', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"데이터 로드 중 오류 발생: {e}")
    st.write("엑셀 헤더가 올바른지 다시 한번 확인해주세요.")

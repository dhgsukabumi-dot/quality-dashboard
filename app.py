import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="Quality Command Center", layout="wide")

st.title("🏭 Executive Quality Command Center")

# 데이터 로드 (시트별로 불러오기)
@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx" # 파일명
    sewing = pd.read_excel(file, sheet_name="Raw Data - Sewing")
    finishing = pd.read_excel(file, sheet_name="Raw Data - Finishing")
    return sewing, finishing

sewing_df, finish_df = load_data()

# 사이드바 필터 (날짜 및 라인 선택)
st.sidebar.header("Filter Settings")
selected_date = st.sidebar.date_input("Select Date")
selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())

# 데이터 필터링 로직
mask = (sewing_df['Date'].dt.date == selected_date)
if selected_line:
    mask &= sewing_df['LINE'].isin(selected_line)
filtered_sewing = sewing_df[mask]

# 1. 핵심 지표 (Metric Cards)
col1, col2, col3 = st.columns(3)
col1.metric("Total Sewing Defects", filtered_sewing['Total Defects'].sum())
col2.metric("Avg Defect Rate", f"{filtered_sewing['Defects %'].mean():.2%}")
col3.metric("Total Inspected", filtered_sewing['Total Q\'ty Inspected'].sum())

# 2. 그래프 시각화 (Plotly)
st.subheader("Worst Performing Lines (Defect Rate)")
fig = px.bar(filtered_sewing, x='LINE', y='Defects %', color='Defects %', 
             color_continuous_scale='Reds', template='plotly_dark')
st.plotly_chart(fig, use_container_width=True)

# 3. 불량 유형 파레토 차트 (Top 10)
st.subheader("Top 10 Defect Types")
defect_columns = ['Broken Stitch', 'Skip stitch', 'Puckering', 'Dirty Stain/ Oil/ chalk mark'] # 추가 필요
data_melted = filtered_sewing[defect_columns].sum().reset_index()
data_melted.columns = ['Type', 'Count']
fig2 = px.pie(data_melted, values='Count', names='Type', hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

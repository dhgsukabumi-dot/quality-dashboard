import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # header=0을 지우고 기본값으로 읽어봅니다.
    sewing = pd.read_excel(file, sheet_name="SEWING")
    # 열 이름을 모두 문자로 변환하고 공백 제거
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    return sewing

try:
    sewing_df = load_data()
    
    # 1. 무엇이 문제인지 화면에 전부 출력
    st.write("### 현재 로드된 열 이름 목록 (이 목록에 LINE이 있나요?)")
    st.write(sewing_df.columns.tolist()) 
    
    # 2. 강제로 LINE 열을 찾아서 사용하되, 없으면 다음으로 넘어감
    if 'LINE' in sewing_df.columns:
        selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
    else:
        st.error("리스트에 'LINE'이 없네요! 위 목록에서 정확한 이름을 알려주세요.")

except Exception as e:
    st.error(f"오류: {e}")

# 2. 여기서 확인!
st.write("사용 가능한 열 이름 목록:")
st.write(sewing_df.columns.tolist())

# 3. 에러 방지를 위해 LINE이 있는지 체크
if 'LINE' in sewing_df.columns:
    selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
else:
    st.error("데이터 프레임에 'LINE'이라는 열이 없습니다. 위 목록을 확인해 보세요.")

# 이제 여기서 LINE이라는 열이 있는지 확인
if 'LINE' in sewing_df.columns:
    selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
else:
    st.error("데이터에 'LINE'이라는 열이 없습니다! 위에 출력된 열 이름 목록을 확인해주세요.")

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

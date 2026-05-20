import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # header=1: 엑셀의 두 번째 줄을 헤더로 읽어옵니다.
    sewing = pd.read_excel(file, sheet_name="SEWING", header=1)
    
    # 열 이름 정리
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    return sewing

try:
    sewing_df = load_data()
    
    # 이제 헤더가 제대로 잡혔는지 확인 (DATE, BUYER, STYLE, LINE이 보여야 합니다)
    st.write("### 수정된 컬럼 목록:")
    st.write(sewing_df.columns.tolist())
    
    if 'LINE' in sewing_df.columns and 'DEFECTS %' in sewing_df.columns:
        st.sidebar.header("Filter Settings")
        selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
        
        filtered_df = sewing_df
        if selected_line:
            filtered_df = sewing_df[sewing_df['LINE'].isin(selected_line)]
            
        st.subheader("Line vs Defect Rate")
        # 여기서 퍼센트 기호(%)를 제거하고 숫자로 변환하는 과정이 필요할 수 있습니다.
        fig = px.bar(filtered_df, x='LINE', y='DEFECTS %', color='DEFECTS %')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("컬럼이 제대로 로드되지 않았습니다. 위 목록을 확인해주세요.")

except Exception as e:
    st.error(f"오류 발생: {e}")

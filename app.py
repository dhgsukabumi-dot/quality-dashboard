import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # header=2: 세 번째 줄을 헤더로 읽습니다.
    sewing = pd.read_excel(file, sheet_name="SEWING", header=2)
    
    # 열 이름 정리 (공백 제거 및 대문자)
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    
    # 퍼센트 기호 제거 및 숫자로 변환 (그래프를 그리기 위해 필수!)
    if 'DEFECTS %' in sewing.columns:
        sewing['DEFECTS %'] = sewing['DEFECTS %'].astype(str).str.replace('%', '')
        sewing['DEFECTS %'] = pd.to_numeric(sewing['DEFECTS %'], errors='coerce')
        
    return sewing

try:
    sewing_df = load_data()
    
    st.write("### 현재 로드된 컬럼 목록:")
    st.write(sewing_df.columns.tolist())
    
    # 이제 'LINE'과 'DEFECTS %'가 있는지 확인
    if 'LINE' in sewing_df.columns and 'DEFECTS %' in sewing_df.columns:
        st.sidebar.header("Filter Settings")
        selected_line = st.sidebar.multiselect("Select Line", sewing_df['LINE'].unique())
        
        filtered_df = sewing_df
        if selected_line:
            filtered_df = sewing_df[sewing_df['LINE'].isin(selected_line)]
            
        st.subheader("Line vs Defect Rate")
        fig = px.bar(filtered_df, x='LINE', y='DEFECTS %', color='DEFECTS %', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("컬럼을 찾을 수 없습니다. 위 목록을 보고 정확한 헤더 위치를 확인해야 합니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")

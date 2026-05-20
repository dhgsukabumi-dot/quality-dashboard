import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # 시트를 읽어옵니다.
    sewing = pd.read_excel(file, sheet_name="SEWING")
    # 열 이름을 깔끔하게 정리 (대문자 + 공백 제거)
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    return sewing

try:
    sewing_df = load_data()
    
    # 1. 실제 컬럼 목록을 확인 (에러 시 원인 파악용)
    cols = sewing_df.columns.tolist()
    
    # 2. 'LINE' 또는 '라인' 등이 있는지 확인
    line_col = 'LINE' if 'LINE' in cols else (cols[3] if len(cols) > 3 else None)
    
    st.write("### 데이터 구조 확인 (이 리스트를 보고 열 이름을 수정해야 합니다)")
    st.write("컬럼 목록:", cols)
    
    if line_col:
        st.sidebar.header("Filter Settings")
        selected_line = st.sidebar.multiselect("Select Line", sewing_df[line_col].unique())
        
        # 필터 적용
        filtered_df = sewing_df
        if selected_line:
            filtered_df = sewing_df[sewing_df[line_col].isin(selected_line)]
            
        # 메트릭 표시 (총 불량 수 열이 TOTAL DEFECTS 인지 확인)
        # 엑셀 헤더명을 다시 확인하여 매칭해야 합니다.
        st.write("데이터 미리보기:", filtered_df.head())
        
        st.subheader("Line vs Defect Rate")
        if 'DEFECTS %' in filtered_df.columns:
            fig = px.bar(filtered_df, x=line_col, y='DEFECTS %', color='DEFECTS %')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("그래프를 그릴 'DEFECTS %' 열을 찾을 수 없습니다.")
            
    else:
        st.error("데이터에서 라인 정보를 찾을 수 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")

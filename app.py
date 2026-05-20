import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # 시트별로 로드
    sewing = pd.read_excel(file, sheet_name="SEWING")
    finish = pd.read_excel(file, sheet_name="FINISHING")
    
    # 열 이름 정리
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    return sewing, finish

try:
    sewing_df, finish_df = load_data()
    
    # 컬럼명이 정확히 일치하는지 확인 (이미지에서 보신 'SEWING DEFECTS %' 사용)
    st.write("### 품질 현황 대시보드")
    
    # 1. 라인별 불량률 바 차트
    if 'SEWING DEFECTS %' in sewing_df.columns:
        # % 기호가 있다면 제거
        sewing_df['SEWING DEFECTS %'] = sewing_df['SEWING DEFECTS %'].astype(str).str.replace('%', '').astype(float)
        
        st.subheader("🧵 Sewing Defect Rate by Line")
        fig = px.bar(sewing_df, x='LINE', y='SEWING DEFECTS %', color='SEWING DEFECTS %', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"SEWING 시트에 'SEWING DEFECTS %' 컬럼을 찾을 수 없습니다. 현재 컬럼: {sewing_df.columns.tolist()}")

    # 2. Finishing 불량률 (두 종류)
    st.subheader("👔 Finishing Defect Rate")
    finish_cols = ['FINISHING BEFORE IRON DEFECTS %', 'FINISHING AFTER IRON DEFECTS %']
    
    # finish_df에서 해당 컬럼들이 있는지 확인 후 처리
    for col in finish_cols:
        if col in finish_df.columns:
            finish_df[col] = finish_df[col].astype(str).str.replace('%', '').astype(float)
    
    fig2 = px.bar(finish_df, x='LINE', y=finish_cols, barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"오류 발생: {e}")

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DHG2 Quality Dashboard")
st.title("🏭 Executive Quality Command Center")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # 시트 읽기
    sewing = pd.read_excel(file, sheet_name="SEWING")
    finish = pd.read_excel(file, sheet_name="FINISHING")
    
    # 열 이름 통일 (공백 제거 및 대문자)
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    
    return sewing, finish

try:
    sewing_df, finish_df = load_data()
    
    # 데이터 정리: % 기호 제거 및 숫자로 변환
    # Sewing 시트: 'SEWING DEFECTS %'
    # Finishing 시트: 'FINISHING BEFORE IRON DEFECTS %' & 'FINISHING AFTER IRON DEFECTS %'
    
    for col in sewing_df.columns:
        if 'DEFECTS %' in col:
            sewing_df[col] = sewing_df[col].astype(str).str.replace('%', '').astype(float)
            
    for col in finish_df.columns:
        if 'DEFECTS %' in col:
            finish_df[col] = finish_df[col].astype(str).str.replace('%', '').astype(float)

    # 1. 시각화 1: Sewing 불량률
    st.subheader("🧵 Sewing Defect Rate by Line")
    fig1 = px.bar(sewing_df, x='LINE', y='SEWING DEFECTS %', color='SEWING DEFECTS %', 
                 color_continuous_scale='Reds', template='plotly_dark')
    st.plotly_chart(fig1, use_container_width=True)

    # 2. 시각화 2: Finishing 불량률 (두 종류 모두 표시)
    st.subheader("👔 Finishing Defect Rate (Before & After Iron)")
    finish_melted = finish_df.melt(id_vars='LINE', 
                                   value_vars=['FINISHING BEFORE IRON DEFECTS %', 'FINISHING AFTER IRON DEFECTS %'],
                                   var_name='Type', value_name='Rate')
    fig2 = px.bar(finish_melted, x='LINE', y='Rate', color='Type', barmode='group', template='plotly_dark')
    st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("컬럼명을 확인 중입니다. 엑셀의 헤더 이름이 코드와 일치하는지 확인해주세요.")

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    sewing = pd.read_excel(file, sheet_name="SEWING", header=0)
    finish = pd.read_excel(file, sheet_name="FINISHING", header=0)
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    return sewing, finish

sewing_df, finish_df = load_data()

# 불량 항목 리스트 (이미지상에서 확인된 항목들)
defect_cols = ['UNTRIMED', 'BROKEN STITCH', 'SKIP STITCH', 'PUCKERING', 'PLEATED', 'RUN OF STITCH'] 

# 1. 봉제 라인별 불량률 (%)
st.subheader("🧵 봉제(Sewing) 라인별 평균 불량률")
s_line = sewing_df.groupby('LINE')['SEWING DEFECTS %'].mean().reset_index()
# 0.XX를 27.2 형식으로 복구
s_line['SEWING DEFECTS %'] = s_line['SEWING DEFECTS %'] * 100 
fig1 = px.bar(s_line, x='LINE', y='SEWING DEFECTS %', text_auto='.1f%')
st.plotly_chart(fig1, use_container_width=True)

# 2. 완성 라인별 불량률 (%)
st.subheader("👔 완성(Finishing) 라인별 평균 불량률")
f_line = finish_df.groupby('LINE')['FINISHING AFTER IRON DEFECTS %'].mean().reset_index()
f_line['FINISHING AFTER IRON DEFECTS %'] = f_line['FINISHING AFTER IRON DEFECTS %'] * 100
fig2 = px.bar(f_line, x='LINE', y='FINISHING AFTER IRON DEFECTS %', text_auto='.1f%')
st.plotly_chart(fig2, use_container_width=True)

# 3. 파레토 차트 (봉제 & 완성 항목별 비중)
st.subheader("📈 불량 항목별 비중(%) 분석")
# 봉제 불량 합계
s_pareto = sewing_df[defect_cols].sum().reset_index()
s_pareto.columns = ['Item', 'Count']
s_pareto['%'] = (s_pareto['Count'] / s_pareto['Count'].sum()) * 100

fig3 = px.pie(s_pareto, values='%', names='Item', title="봉제 불량 항목별 구성비")
st.plotly_chart(fig3, use_container_width=True)

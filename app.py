import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DHG2 Quality Dashboard")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    # 데이터가 1행부터 바로 시작한다고 가정 (이미지 기준)
    sewing = pd.read_excel(file, sheet_name="SEWING", header=0)
    finish = pd.read_excel(file, sheet_name="FINISHING", header=0)
    
    # 1. 컬럼명 정리
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    
    # 2. 퍼센트 텍스트 -> 숫자(0.351 등)로 변환
    def to_float(x):
        try:
            return float(str(x).replace('%', '')) / 100
        except:
            return 0.0

    sewing['SEWING DEFECTS %'] = sewing['SEWING DEFECTS %'].apply(to_float)
    finish['FINISHING BEFORE IRON DEFECTS %'] = finish['FINISHING BEFORE IRON DEFECTS %'].apply(to_float)
    finish['FINISHING AFTER IRON DEFECTS %'] = finish['FINISHING AFTER IRON DEFECTS %'].apply(to_float)
    
    return sewing, finish

sewing_df, finish_df = load_data()

# 1. 라인별 불량률 바 차트
st.subheader("🧵 Sewing Defect Rate by Line")
fig1 = px.bar(sewing_df, x='LINE', y='SEWING DEFECTS %', text_auto='.1%', color='SEWING DEFECTS %', color_continuous_scale='Reds')
fig1.update_layout(yaxis_tickformat='.1%')
st.plotly_chart(fig1, use_container_width=True)

# 2. Finishing (Before vs After) 바 차트
st.subheader("👔 Finishing Defect Rate (Before vs After Iron)")
finish_melted = finish_df.melt(id_vars=['LINE'], 
                               value_vars=['FINISHING BEFORE IRON DEFECTS %', 'FINISHING AFTER IRON DEFECTS %'],
                               var_name='Type', value_name='Rate')
fig2 = px.bar(finish_melted, x='LINE', y='Rate', color='Type', barmode='group', text_auto='.1%')
fig2.update_layout(yaxis_tickformat='.1%')
st.plotly_chart(fig2, use_container_width=True)

# 3. 파레토 차트 (불량 항목 순위 - sewing_df 기준)
st.subheader("📈 Top Defect Types (Pareto)")
# 불량 항목 열들만 선택
ignore_cols = ['DATE', 'BUYER', 'STYLE', 'LINE', 'TOTAL DEFECTS', 'Q\'TY ACCEPTED', 'TOTAL Q\'TY INSPECTED', 'SEWING DEFECTS %', 'REMARKS']
defect_cols = [c for c in sewing_df.columns if c not in ignore_cols]
pareto_data = sewing_df[defect_cols].sum().sort_values(ascending=False).head(10).reset_index()
pareto_data.columns = ['Defect Type', 'Count']
fig3 = px.bar(pareto_data, x='Defect Type', y='Count', color='Count', text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

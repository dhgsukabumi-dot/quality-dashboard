import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="DHG2 Quality Dashboard")
st.title("🏭 Executive Quality Command Center")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    sewing = pd.read_excel(file, sheet_name="SEWING")
    finish = pd.read_excel(file, sheet_name="FINISHING")
    
    for df in [sewing, finish]:
        df.columns = [str(c).strip().upper() for c in df.columns]
        if 'DEFECTS %' in df.columns:
            df['DEFECTS %'] = df['DEFECTS %'].astype(str).str.replace('%', '').astype(float)
    return sewing, finish

sewing_df, finish_df = load_data()

# 1. 라인별 평균 계산 (Sewing & Finishing 비교)
s_avg = sewing_df.groupby('LINE')['DEFECTS %'].mean().reset_index().rename(columns={'DEFECTS %': 'SEWING'})
f_avg = finish_df.groupby('LINE')['DEFECTS %'].mean().reset_index().rename(columns={'DEFECTS %': 'FINISHING'})
combined = pd.merge(s_avg, f_avg, on='LINE')
combined['GAP'] = combined['FINISHING'] - combined['SEWING']

# 2. 대시보드 레이아웃
st.subheader("📊 Sewing vs Finishing Gap Analysis")
fig_gap = px.bar(combined.melt(id_vars='LINE', value_vars=['SEWING', 'FINISHING']), 
                 x='LINE', y='value', color='variable', barmode='group', template='plotly_dark')
st.plotly_chart(fig_gap, use_container_width=True)

# 3. 40% 이상 라인 경고 (Action Plan)
st.subheader("🚨 Critical Alert (Defect Rate > 40%)")
critical_lines = combined[(combined['SEWING'] > 40) | (combined['FINISHING'] > 40)]
if not critical_lines.empty:
    st.error(f"다음 라인이 40%를 초과했습니다: {critical_lines['LINE'].tolist()}")
else:
    st.success("모든 라인이 정상 범위(40% 미만) 내에 있습니다.")

# 4. 파레토 차트 (전체 불량 유형 합산)
st.subheader("📈 Top Defect Types (Pareto Analysis)")
# 데이터가 많으므로 주요 불량 항목만 선택 (사용자 데이터 컬럼명에 맞춰 수정)
defect_cols = [c for c in sewing_df.columns if c not in ['DATE', 'BUYER', 'STYLE', 'LINE', 'TOTAL DEFECTS', 'Q\'TY ACCEPTED', 'TOTAL Q\'TY INSPECTED', 'DEFECTS %', 'REMARKS']]
pareto_data = sewing_df[defect_cols].sum().sort_values(ascending=False).head(10).reset_index()
pareto_data.columns = ['Defect Type', 'Count']

fig_pareto = px.bar(pareto_data, x='Defect Type', y='Count', template='plotly_dark', color='Count', color_continuous_scale='Blues')
st.plotly_chart(fig_pareto, use_container_width=True)

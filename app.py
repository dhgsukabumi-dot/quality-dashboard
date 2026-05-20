import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DHG2 Quality Dashboard")
st.title("🏭 Executive Quality Command Center")

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    sewing = pd.read_excel(file, sheet_name="SEWING")
    finish = pd.read_excel(file, sheet_name="FINISHING")
    
    # 헤더 정리 및 대문자 변환
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    
    # % 제거 및 숫자 변환
    for df in [sewing, finish]:
        if 'DEFECTS %' in df.columns:
            df['DEFECTS %'] = df['DEFECTS %'].astype(str).str.replace('%', '').astype(float)
    return sewing, finish

sewing_df, finish_df = load_data()

# 1. 종합 지표 및 Gap 분석
st.subheader("📊 Sewing vs Finishing Gap Analysis")
s_avg = sewing_df.groupby('LINE')['DEFECTS %'].mean().reindex(range(1, 29), fill_value=0).reset_index()
f_avg = finish_df.groupby('LINE')['DEFECTS %'].mean().reindex(range(1, 29), fill_value=0).reset_index()
combined = pd.merge(s_avg, f_avg, on='LINE', suffixes=('_S', '_F'))

fig_gap = px.bar(combined.melt(id_vars='LINE', value_vars=['DEFECTS %_S', 'DEFECTS %_F']), 
                 x='LINE', y='value', color='variable', barmode='group', template='plotly_dark')
st.plotly_chart(fig_gap, use_container_width=True)

# 2. 40% 이상 라인 경고
critical_lines = combined[(combined['DEFECTS %_S'] > 40) | (combined['DEFECTS %_F'] > 40)]
if not critical_lines.empty:
    st.error(f"🚨 Critical Alert (Defect > 40%): Line {critical_lines['LINE'].tolist()}")

# 3. 파레토 차트 (불량 항목 순위)
st.subheader("📈 Top 10 Defect Types (Pareto Analysis)")
exclude = ['DATE', 'BUYER', 'STYLE', 'LINE', 'TOTAL DEFECTS', 'Q\'TY ACCEPTED', 'TOTAL Q\'TY INSPECTED', 'DEFECTS %', 'REMARKS']
defect_cols = [c for c in sewing_df.columns if c not in exclude]
pareto_data = sewing_df[defect_cols].sum().sort_values(ascending=False).head(10).reset_index()
pareto_data.columns = ['Defect Type', 'Count']
fig_pareto = px.bar(pareto_data, x='Defect Type', y='Count', color='Count', template='plotly_dark')
st.plotly_chart(fig_pareto, use_container_width=True)

# 4. 스타일별 불량률 추이
st.subheader("📅 Style-wise Defect Trend")
styles = sewing_df['STYLE'].unique()
selected_style = st.multiselect("Select Style to view trend", styles, default=styles[:3] if len(styles)>3 else styles)
trend_df = sewing_df[sewing_df['STYLE'].isin(selected_style)]
fig_trend = px.line(trend_df, x='DATE', y='DEFECTS %', color='STYLE', markers=True, template='plotly_dark')
st.plotly_chart(fig_trend, use_container_width=True)

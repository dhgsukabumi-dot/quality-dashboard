import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    file = "QC DEFECT REPORT.xlsx"
    sewing = pd.read_excel(file, sheet_name="SEWING")
    # 공백만 제거하고 대문자로 변경한 뒤, 컬럼 리스트를 반환
    return sewing.columns.str.strip().str.upper().tolist()

try:
    cols = load_data()
    st.write("### 엑셀에서 확인된 컬럼 이름들:")
    st.write(cols)
except Exception as e:
    st.error(e)

try:
    sewing_df, finish_df = load_data()

    # --- 1. Gap 분석 (Line 1~28 전체 표시) ---
    st.subheader("📊 Sewing vs Finishing Gap Analysis")
    s_avg = sewing_df.groupby('LINE')['DEFECTS %'].mean().reindex(range(1, 29), fill_value=0).reset_index()
    f_avg = finish_df.groupby('LINE')['DEFECTS %'].mean().reindex(range(1, 29), fill_value=0).reset_index()
    combined = pd.merge(s_avg, f_avg, on='LINE', suffixes=('_S', '_F'))
    
    fig_gap = px.bar(combined.melt(id_vars='LINE', value_vars=['DEFECTS %_S', 'DEFECTS %_F']), 
                     x='LINE', y='value', color='variable', barmode='group')
    st.plotly_chart(fig_gap, use_container_width=True)

    # --- 2. 파레토 차트 (불량 항목 순위) ---
    st.subheader("📈 Top 10 Defect Types (Pareto Analysis)")
    # 실제 데이터의 컬럼을 보고 불량항목을 자동으로 추출 (DATE, BUYER 등 제외)
    common_cols = ['DATE', 'BUYER', 'STYLE', 'LINE', 'TOTAL DEFECTS', 'Q\'TY ACCEPTED', 'TOTAL Q\'TY INSPECTED', 'DEFECTS %', 'REMARKS']
    defect_cols = [c for c in sewing_df.columns if c not in common_cols]
    
    pareto_data = sewing_df[defect_cols].sum().sort_values(ascending=False).head(10).reset_index()
    pareto_data.columns = ['Defect Type', 'Count']
    fig_pareto = px.bar(pareto_data, x='Defect Type', y='Count', color='Count')
    st.plotly_chart(fig_pareto, use_container_width=True)

    # --- 3. 스타일 추이 ---
    st.subheader("📅 Style-wise Defect Trend")
    styles = sewing_df['STYLE'].unique()
    selected_style = st.multiselect("Select Style", styles, default=styles[:1])
    trend_df = sewing_df[sewing_df['STYLE'].isin(selected_style)]
    fig_trend = px.line(trend_df, x='DATE', y='DEFECTS %', color='STYLE', markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

except Exception as e:
    st.error(f"오류: {e}")
    st.write("엑셀 파일을 다시 확인해주세요.")

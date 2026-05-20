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
    
    # 열 이름 정리
    sewing.columns = [str(c).strip().upper() for c in sewing.columns]
    finish.columns = [str(c).strip().upper() for c in finish.columns]
    
    # % 제거 및 숫자 변환
    def clean_pct(df, col_name):
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(str).str.replace('%', '').astype(float)
        return df

    sewing = clean_pct(sewing, 'SEWING DEFECTS %')
    finish = clean_pct(finish, 'FINISHING BEFORE IRON DEFECTS %')
    finish = clean_pct(finish, 'FINISHING AFTER IRON DEFECTS %')
    
    # 라인 번호를 문자로 변환하여 순서대로 정렬
    sewing['LINE'] = sewing['LINE'].astype(str)
    finish['LINE'] = finish['LINE'].astype(str)
    
    return sewing, finish

sewing_df, finish_df = load_data()

# 1. Sewing 그래프 (상세 표기 포함)
st.subheader("🧵 Sewing Defect Rate by Line")
fig1 = px.bar(sewing_df, x='LINE', y='SEWING DEFECTS %', text='SEWING DEFECTS %',
             color='SEWING DEFECTS %', color_continuous_scale='Reds', template='plotly_dark')
fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig1.update_xaxes(type='category') # 1~28 전체 라인 강제 노출
st.plotly_chart(fig1, use_container_width=True)

# 2. Finishing 그래프 (상세 표기 포함)
st.subheader("👔 Finishing Defect Rate (Before vs After Iron)")
finish_melted = finish_df.melt(id_vars='LINE', 
                               value_vars=['FINISHING BEFORE IRON DEFECTS %', 'FINISHING AFTER IRON DEFECTS %'],
                               var_name='Type', value_name='Rate')
fig2 = px.bar(finish_melted, x='LINE', y='Rate', color='Type', barmode='group', 
             text='Rate', template='plotly_dark')
fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig2.update_xaxes(type='category')
st.plotly_chart(fig2, use_container_width=True)

# 3. 불량 항목 순위 파레토 차트 (전체 합계 기준)
st.subheader("📈 Top Defect Types Analysis (Total Count)")

# 엑셀의 불량 항목 열들을 자동으로 추출 (앞서 배운 것처럼 특정 항목 제외)
# (DATE, BUYER, STYLE, LINE, TOTAL DEFECTS, Q'TY ACCEPTED, TOTAL Q'TY INSPECTED, DEFECTS %, REMARKS 제외)
common_cols = ['DATE', 'BUYER', 'STYLE', 'LINE', 'TOTAL DEFECTS', 'Q\'TY ACCEPTED', 'TOTAL Q\'TY INSPECTED', 'SEWING DEFECTS %', 'REMARKS']
defect_item_cols = [c for c in sewing_df.columns if c not in common_cols]

# 불량 항목별 합계 계산
defect_sums = sewing_df[defect_item_cols].sum().sort_values(ascending=False).head(10).reset_index()
defect_sums.columns = ['Defect Item', 'Count']

# 파레토 차트 그리기
fig3 = px.bar(defect_sums, x='Defect Item', y='Count', text='Count',
             color='Count', color_continuous_scale='Blues', template='plotly_dark')
fig3.update_traces(texttemplate='%{text}', textposition='outside')
st.plotly_chart(fig3, use_container_width=True)

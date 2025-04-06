# 파일명: app.py
import streamlit as st
import pandas as pd

st.title("엑셀 자동 변환 도구")

uploaded_file = st.file_uploader("파일을 업로드하세요", type=["csv", "xlsx", "xls", "tsv"])

if uploaded_file:
    try:
        # 파일 형식에 따라 읽기
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".tsv"):
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            df = pd.read_excel(uploaded_file)

        st.success("파일을 성공적으로 읽었습니다.")
        st.dataframe(df)

        # xlsx 변환 버튼
        if st.button("📥 .xlsx로 변환 및 다운로드"):
            output_file = "converted_file.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button("변환된 파일 다운로드", f, file_name="converted_file.xlsx")

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")

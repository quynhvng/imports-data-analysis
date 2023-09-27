import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from utils import extract_product_data
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():

    st.set_page_config(
        page_title="Báo cáo thống kê nhập khẩu máy móc xây dựng",
        layout="wide"
    )

    if ("submitted" in st.session_state):
        df = st.session_state.df
    else:
        df = pd.read_csv("sample.csv", index_col=0)
        df["Ngày đăng ký"] = pd.to_datetime(df["Ngày đăng ký"])
        df["Ngày hợp đồng"] = pd.to_datetime(df["Ngày hợp đồng"])
    
    df.dropna(inplace=True, subset=["Mặt hàng", "Nhãn hiệu", "Model"])
    df["Nhãn hiệu - Model"] = df["Nhãn hiệu"] + " - " + df["Model"]

    "# BÁO CÁO THỐNG KÊ NHẬP KHẨU MÁY MÓC XÂY DỰNG"

    with st.sidebar:
        op2 = st.selectbox(
            "Thống kê cho một đơn vị nhập khẩu",
            np.append(["Không xem theo đơn vị nhập khẩu"], pd.unique(df["Tên doanh nghiệp XNK"]))
        )
        st.divider()
        with st.form("my-form", clear_on_submit=False):
            uploaded_files = st.file_uploader("Tải lên các file danh sách tờ khai nhập khẩu (.xlsx)", accept_multiple_files=True)
            submitted = st.form_submit_button("Tách dữ liệu")
            if (submitted):
                st.session_state.submitted = True  
                if (uploaded_files != []):
                    st.session_state.df = extract_product_data(uploaded_files)    
        if ("submitted" in st.session_state):
            st.download_button(
                label="Tải xuống file kết quả tách dữ liệu (.csv)",
                data=st.session_state.df.to_csv(),
                file_name="output.csv",
                mime="text/csv",
            )

    if (op2!="Không xem theo đơn vị nhập khẩu"):
        df = df[df["Tên doanh nghiệp XNK"]==op2]

    col1, col2 = st.columns(2)

    with col1:
        st.write("TỪ {} ĐẾN {}".format(
            df["Ngày đăng ký"].min().strftime("%d/%m/%Y"),
            df["Ngày đăng ký"].max().strftime("%d/%m/%Y"))
        )
        "ĐƠN VỊ TÍNH: USD"
    with col2:
        df["Giá trị hàng nhập"] = np.round(df["Đơn giá khai báo(USD)"]*df["Lượng"],0)
        st.metric(
            "TỔNG GIÁ TRỊ HÀNG NHẬP KHẨU", 
            "{:,.0f} USD".format(df["Giá trị hàng nhập"].sum())
        )

    st.subheader("THỐNG KÊ SỐ LƯỢNG HÀNG NHẬP")

    tab1, tab2 = st.tabs(["Tổng quan", "Chi tiết"])

    with tab1:
        op1 = st.selectbox(
            "Thống kê số lượng hàng nhập theo",
            ("Mặt hàng", "Nhãn hiệu", "Nhãn hiệu - Model")
        )
        sum1 = df.groupby(op1)["Lượng"].sum().sort_values(ascending=False).reset_index()
        col3, col4 = st.columns(2)
        with col3:
            st.dataframe(
                sum1,
                use_container_width=True,
                hide_index=True
            )
        with col4:
            st.altair_chart(
                alt.Chart(sum1.head(15)).mark_bar().encode(
                    alt.X("Lượng"),
                    alt.Y(op1).sort("-x")
                ).properties(
                    title="Top 15 theo số lượng nhập khẩu"
                ),
                use_container_width=True
            )
    with tab2:
        sum2 = df.groupby(["Mặt hàng", "Nhãn hiệu", "Model"])[["Lượng", "Giá trị hàng nhập"]]
        sum2 = sum2.sum().sort_values(by="Giá trị hàng nhập", ascending=False).reset_index()
        sum2.loc["Tổng"] = sum2.sum()
        sum2.loc[sum2.index[-1], "Mặt hàng":"Model"] = ""
        st.dataframe(
            sum2,
            use_container_width=True,
        )

    st.subheader("THỐNG KÊ XUẤT XỨ HÀNG NHẬP")

    tab3, tab4 = st.tabs(["Theo đơn vị xuất khẩu", "Theo nước xuất xứ"])
    
    with tab3:
        sum3 = df.groupby("Đơn vị đối tác")["Giá trị hàng nhập"].sum().sort_values(ascending=False).reset_index()
        col5, col6 = st.columns(2)
        with col5:
            st.dataframe(
                sum3,
                use_container_width=True,
                hide_index=True
            )
        with col6:
            st.altair_chart(
                alt.Chart(sum3.head(15)).mark_bar().encode(
                    alt.X("Giá trị hàng nhập"),
                    alt.Y("Đơn vị đối tác").sort("-x"),
                    tooltip=[alt.Tooltip("Giá trị hàng nhập", format=",.0f"), "Đơn vị đối tác"]
                ).properties(
                    title="Top 15 theo giá trị nhập khẩu"
                ),
                use_container_width=True
            )    
    with tab4:
        sum4 = df.groupby("Tên nuớc xuất xứ")["Giá trị hàng nhập"].sum().sort_values(ascending=False).reset_index()
        col7, col8 = st.columns(2)
        with col7:
            st.altair_chart(
                alt.Chart(sum4).mark_bar().encode(
                    alt.X("Giá trị hàng nhập"),
                    alt.Y("Tên nuớc xuất xứ").sort("-x"),
                    tooltip=[alt.Tooltip("Giá trị hàng nhập", format=",.0f"), "Tên nuớc xuất xứ"]
                ),
                use_container_width=True
            )
        with col8:
            sum4 = sum4.rename(columns={"Giá trị hàng nhập": "Value"})
            st.altair_chart(
                alt.Chart(sum4).transform_joinaggregate(
                    TotalVal='sum(Value)',
                ).transform_calculate(
                    PercentOfTotal="datum.Value / datum.TotalVal"
                ).mark_arc().encode(
                    alt.Theta("PercentOfTotal:Q"),
                    alt.Color("Tên nuớc xuất xứ"),
                    tooltip=[alt.Tooltip("PercentOfTotal:Q", format=".0%"), "Tên nuớc xuất xứ"]
                )
            )

    
    st.subheader("DỮ LIỆU GỐC")
    "Thêm chức năng sửa dữ liệu?"
    st.dataframe(df)
   

if __name__ == "__main__":
    run()

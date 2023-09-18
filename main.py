import streamlit as st
from streamlit.logger import get_logger
from utils import extract_product_data

LOGGER = get_logger(__name__)

output = None

def run():
    global output

    st.set_page_config(
        page_title="Imports Data Analysis",
    )

    st.write("# Phân tích dữ liệu hàng nhập khẩu")

    st.markdown(
        """
        Tách dữ liệu mặt hàng, nhãn hiệu và model từ danh sách tờ khai nhập khẩu.\n
        Tách dữ liệu bằng cách tìm lọc ký tự. Một số tờ khai sẽ không thể tách được các dữ liệu trên do mô tả hàng hóa không theo quy luật chung.\n
        Vì vậy sau khi tách tự động cần kiểm tra và tách dữ liệu thủ công nếu cần.
    """
    )

    with st.form("my-form", clear_on_submit=True):
        
        uploaded_files = st.file_uploader("Tải lên các file danh sách tờ khai nhập khẩu (.xlsx)", accept_multiple_files=True)
        submitted = st.form_submit_button("Tách dữ liệu")

        if ((uploaded_files != []) & submitted):
            output = extract_product_data(uploaded_files)
        
    if (output):
        st.download_button(
            label="Tải xuống file kết quả (.csv)",
            data=output,
            file_name='output.csv',
            mime='text/csv',
        )
   

if __name__ == "__main__":
    run()

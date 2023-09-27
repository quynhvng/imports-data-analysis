import pandas as pd
import re
import streamlit as st

@st.cache
def extract_product_data(raw_files):

    df = pd.DataFrame()

    if (raw_files == None):
        return df

    for raw_file in raw_files:
        df = pd.concat([df, pd.read_excel(raw_file)], ignore_index=True)

    df["Ngày đăng ký"] = pd.to_datetime(df["Ngày đăng ký"])
    df["Ngày hợp đồng"] = pd.to_datetime(df["Ngày hợp đồng"])

    product_desc = df["Tên hàng"].str.upper()

    brand_names = ['FOTON', 'BOMAG', 'CAT', 'CATERPILLAR', 'CHENGLIWEI', 'SITRAK',
                'HOWO', 'CNHTC', 'WANGPAI', 'DONGFENG', 'DOOSAN', 'DYNAPAC',
                'EP', 'JIE FANG', 'FORD', 'MARSHELL', 'HAMM', 'GL', 'HINO',
                'HITACHI', 'HYUNDAI', 'IHI', 'ISUZU', 'KATO', 'KOBELCO',
                'KOMATSU', 'KUBOTA', 'LEHMAN', 'MIKASA', 'MINGYU', 'MITSUBISHI',
                'NORMET', 'SAKAI', 'SANY', 'SCANIA', 'SHACMAN', 'BAODING',
                'SDLG', 'SUMITOMO', 'TCM', 'TOYOTA', 'VOLVO', 'WEICHAI',
                'XIANDAIZHONGGONG', 'XCMG', 'YANMAR', 'ZOOMLION']

    item = []
    brand = []
    model = []
    output = df

    for i in product_desc:
        find = []
        known = False
        item_i, brand_i, model_i = ("", "", "")
        # extract item and brand according to known brand names
        find = [x for x in brand_names if(re.search(r'\W'+x+r'\W', i))]
        if find != []:
            known = True
            if len(find)>1:
                first_match = find[0]
                for x in find:
                    if i.find(x) < i.find(first_match): first_match = x
                brand_i = first_match
            else: brand_i = find[0]
            item_i = i[0:i.find(brand_i)]

        # extract item by regex
        if item_i == "":
            find = re.findall(r'.+?(?=NHÃN)', i)
            if find == []:
                find = re.findall(r'.+?(?=HIỆU)', i)
            if find != []:
                item_i = find[0]

        item_i = re.sub(r'(NHÃN|HIỆU|MODEL|,).+', "", item_i).strip(":., ")

        # extract brand by regex
        if brand_i == "":
            find = re.findall(r'(?<=HIỆU).+?(?=[\.,])', i)
            if find != []:
                brand_i = re.sub(r'(MODEL|\().+', "", find[0]).strip(":., ")

        # extract model by regex
        find = re.findall(r'(?<=MODEL[;:\s])[\w\d\s\/\(\)\-]+?(?=[,\.\s])', i)
        if find == []:
            find = re.findall(r'(?<=MODEL\s[;:\s])[\w\d\s\/\(\)\-]+?(?=[,\.\s])', i)
        if find == []:
            find = re.findall(r'(?<=MÃ KIỂU LOẠI[;:\s])[\w\d\s\/\(\)\-]+?(?=[,\.\s])', i)
        if find != []:
            model_i = find[0].strip()
        if (model_i == "")&(known):
            find = re.findall(r'(?<='+brand_i+r'\s).+?(?=[\s.,])', i)
            if find != []: model_i = find[0].strip()

        item.append(item_i)
        brand.append(brand_i)
        model.append(model_i)

    output["Mặt hàng"] = item
    output["Nhãn hiệu"] = brand
    output["Model"] = model

    return output
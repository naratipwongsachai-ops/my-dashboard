#ส่วนที่ใส่ไลบลารี่
import streamlit as st
import pandas as pd
import plotly.express as px

# สร้างตารางข้อมูลเริ่มต้นเป็นค่าว่างใน Session
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(
        columns=['ชื่อสินค้า', 'หมวดหมู่', 'ราคาทุน', 'ราคาขาย', 'จำนวนที่ขายได้', 'วันที่ขาย']
    )

#ส่วน สีพื้นหลังเว็บไซต์ ฉวยๆ
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #0f172a,
            #1e3a5f,
            #312e81
        );
    }
    </style>
    """,
    unsafe_allow_html=True
)

#ส่วน ทำข้อความแสดงหัวข้อเว็บตรงกลาง
st.markdown(
    """
    <div style="width: 100%; text-align: center;">
        <h1 style="font-size: 42px; margin-bottom: 8px;">
            MiniProject-DB
        </h1>
        <p style="font-size: 24px; margin-top: 0;">
            My Dashboard 
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

#ส่วน ช่องอัปโหลดไฟล์
st.markdown(
    """
    <h3 style="color: white; font-size: 24px;">
        Upload File
    </h3>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "เปิดไฟล์ใส่ตรงนี้เลยยย",
    type=["json"],
    key="upload_file"
)

# 1. สร้างฟอร์มสำหรับกรอกข้อมูลสินค้าใหม่
st.markdown("<h3 style='color: white; margin-top: 20px;'>➕ เพิ่มรายการยอดขาย</h3>", unsafe_allow_html=True)

with st.form("input_form", clear_on_submit=True):
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        prod_name = st.text_input("ชื่อสินค้า")
        prod_cat = st.selectbox("หมวดหมู่", ["ของกิน", "ของตกแต่ง", "ของขวัญ", "เครื่องประดับ", "อื่นๆ"])
        cost_price = st.number_input("ราคาทุน (บาท)", min_value=0.0, step=1.0)
        
    with col_input2:
        sell_price = st.number_input("ราคาขาย (บาท)", min_value=0.0, step=1.0)
        quantity = st.number_input("จำนวนที่ขายได้", min_value=1, step=1)
        sale_date = st.date_input("วันที่ขาย")
        
    submit_button = st.form_submit_button("➕ เพิ่มข้อมูลลงแดชบอร์ด")

# 2. เมื่อกดปุ่ม ให้เอาข้อมูลที่กรอกไปใส่ในตารางรวม
if submit_button:
    if prod_name == "":
        st.warning("⚠️ กรุณากรอกชื่อสินค้าก่อนกดเพิ่มข้อมูล")
    else:
        new_row = {
            'ชื่อสินค้า': prod_name,
            'หมวดหมู่': prod_cat,
            'ราคาทุน': cost_price,
            'ราคาขาย': sell_price,
            'จำนวนที่ขายได้': quantity,
            'วันที่ขาย': pd.to_datetime(sale_date)
        }
        st.session_state.sales_data = pd.concat([st.session_state.sales_data, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"เพิ่มข้อมูล '{prod_name}' เรียบร้อยแล้ว!")

# รวมข้อมูลจากไฟล์ JSON (ถ้ามี) เข้ากับข้อมูลที่กดกรอกในฟอร์มเว็บ
if uploaded_file is not None:
    file_df = pd.read_json(uploaded_file)
    file_df['วันที่ขาย'] = pd.to_datetime(file_df['วันที่ขาย'])
    df = pd.concat([st.session_state.sales_data, file_df], ignore_index=True)
else:
    df = st.session_state.sales_data

# แสดงผลการคำนวณและกราฟ (เมื่อมีข้อมูลอย่างน้อย 1 รายการในระบบ)
if not df.empty:
    # คำนวณคอลัมน์ ยอดขาย และ กำไร
    df['ยอดขาย'] = pd.to_numeric(df['ราคาขาย']) * pd.to_numeric(df['จำนวนที่ขายได้'])
    df['กำไร'] = (pd.to_numeric(df['ราคาขาย']) - pd.to_numeric(df['ราคาทุน'])) * pd.to_numeric(df['จำนวนที่ขายได้'])
    
    # 1. แสดงผล ยอดขายรวมและกำไรสุทธิ
    total_sales = df['ยอดขาย'].sum()
    total_profit = df['กำไร'].sum()
    
    st.markdown("<hr style='border: 1px solid #475569;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💰 ยอดขายรวมทั้งหมด", value=f"฿{total_sales:,.2f}")
    with col2:
        st.metric(label="📈 กำไรสุทธิทั้งหมด", value=f"฿{total_profit:,.2f}")
        
    # 2. ทำกราฟเส้นแสดงยอดขายแยกตามรายเดือน (เพิ่มการแยกสีตามหมวดหมู่ 🌈)
    df['วันที่ขาย'] = pd.to_datetime(df['วันที่ขาย'])
    df['เดือน-ปี'] = df['วันที่ขาย'].dt.to_period('M').astype(str)
    
    # [ปรับปรุง] เปลี่ยนกลุ่มประมวลผลให้รวมหมวดหมู่เข้าไปด้วย
    df_monthly = df.groupby(['เดือน-ปี', 'หมวดหมู่'])['ยอดขาย'].sum().reset_index().sort_values('เดือน-ปี')
    
    fig_line = px.line(
        df_monthly, 
        x='เดือน-ปี', 
        y='ยอดขาย', 
        color='หมวดหมู่', # 🔥 สั่งให้แยกสีเส้นตามหมวดหมู่สินค้า
        title='📉 ยอดขายแยกตามรายเดือนและหมวดหมู่',
        markers=True,
        template='plotly_dark'
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # 3. หา สินค้าขายดี 5 อันดับแรก (Top 5) (เพิ่มการโชว์หมวดหมู่ 🌈)
    # [ปรับปรุง] รวมหมวดหมู่เข้ามาในกลุ่มเพื่อนำไปพล็อตสี
    df_top5 = df.groupby(['ชื่อสินค้า', 'หมวดหมู่'])['จำนวนที่ขายได้'].sum().reset_index()
    df_top5 = df_top5.sort_values(by='จำนวนที่ขายได้', ascending=False).head(5)
    
    fig_bar = px.bar(
        df_top5,
        x='จำนวนที่ขายได้',
        y='ชื่อสินค้า',
        color='หมวดหมู่', # 🔥 สั่งให้แท่งกราฟเปลี่ยนสีตามหมวดหมู่ของสินค้านั้น
        title='🏆 สินค้าขายดี 5 อันดับแรก (Top 5)',
        orientation='h',
        template='plotly_dark'
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

    # 4. ส่วนปุ่ม Save ข้อมูลออกมาเป็นไฟล์จริง (สไตล์เขียวมุมบนขวาตามที่คุณออกแบบ)
    json_string = df.to_json(orient='records', force_ascii=False, date_format='iso')
    st.markdown(
        """
        <style>
        div.stDownloadButton {
            position: fixed;
            top: 55px;
            right: 30px;
            z-index: 999999;
        }
        div.stDownloadButton > button {
            background-color: #22C55E !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25) !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #16A34A !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.download_button(label="Save", data=json_string, file_name="my_sales_data.json", mime="application/json")
#โค้ดรัน streamlit run Dashboard.py

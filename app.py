import base64
import io
from pathlib import Path

import pandas as pd
import streamlit as st
from openpyxl import load_workbook
from PIL import Image

BASE = Path(__file__).parent
EXCEL_FILE = BASE / "diecast-list.xlsx"
CURRENCY = "₹"

st.set_page_config(page_title="Diecast Cars For Sale", page_icon="🏎️", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_FILE)
    df["Name"] = df["Name"].str.strip()
    df["Brand"] = (
        df["Brand"].str.strip().str.lower()
        .replace({"mathcbox": "matchbox", "hotwheels": "hot wheels"})
        .str.title()
    )
    df["Category"] = df["Category"].str.strip().str.title()

    # Pull the pictures that are embedded in the Excel sheet, matched by row
    ws = load_workbook(EXCEL_FILE).active
    images = {}
    for im in ws._images:
        row_index = im.anchor._from.row - 1  # Excel row 2 -> DataFrame index 0
        img = Image.open(io.BytesIO(im._data())).convert("RGB")
        img.thumbnail((400, 400))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        images[row_index] = base64.b64encode(buf.getvalue()).decode()
    df["ImageBytes"] = [images.get(i) for i in df.index]
    return df


df = load_data()

st.title("🏎️ Diecast Cars For Sale")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
brands = sorted(df["Brand"].unique())
categories = sorted(df["Category"].unique())

sel_brands = st.sidebar.multiselect("Brand", brands, default=brands)
sel_cats = st.sidebar.multiselect("Category", categories, default=categories)

filtered = df[df["Brand"].isin(sel_brands) & df["Category"].isin(sel_cats)]

# ---------- Top metrics ----------
c1, c2 = st.columns(2)
c1.metric("Total cars", len(filtered))
c2.metric("Total price", f"{CURRENCY}{filtered['Price'].sum():,.0f}")

st.divider()

# ---------- Car grid ----------
if filtered.empty:
    st.info("No cars match these filters.")
else:
    COLS = 4
    for i in range(0, len(filtered), COLS):
        cols = st.columns(COLS)
        for col, (_, car) in zip(cols, filtered.iloc[i:i + COLS].iterrows()):
            with col.container(border=True):
                if car["ImageBytes"] is not None:
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{car["ImageBytes"]}" '
                        'style="width:100%;border-radius:8px;">',
                        unsafe_allow_html=True,
                    )
                st.markdown(f"**{car['Name']}**")
                st.markdown(f"### {CURRENCY}{car['Price']:,.0f}")
                st.caption(f"{car['Brand']}  ·  {car['Category']}")

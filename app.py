from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
CURRENCY = "₹"

st.set_page_config(page_title="Diecast Cars For Sale", page_icon="🏎️", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(BASE / "diecast-list.xlsx")
    df["Name"] = df["Name"].str.strip()
    # clean up brand / category text (also fixes typos like "mathcbox")
    df["Brand"] = (
        df["Brand"].str.strip().str.lower()
        .replace({"mathcbox": "matchbox", "hotwheels": "hot wheels"})
        .str.title()
    )
    df["Category"] = df["Category"].str.strip().str.title()
    # images were extracted from the Excel file as images/car_<row index>.jpg
    df["ImagePath"] = [BASE / "images" / f"car_{i}.jpg" for i in df.index]
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
    rows = [filtered.iloc[i:i + COLS] for i in range(0, len(filtered), COLS)]
    for chunk in rows:
        cols = st.columns(COLS)
        for col, (_, car) in zip(cols, chunk.iterrows()):
            with col.container(border=True):
                if car["ImagePath"].exists():
                    st.image(str(car["ImagePath"]), width="stretch")
                st.markdown(f"**{car['Name']}**")
                st.markdown(f"### {CURRENCY}{car['Price']:,.0f}")
                st.caption(f"{car['Brand']}  ·  {car['Category']}")

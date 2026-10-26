import re

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="HawkerGo Dashboard", page_icon="🍜", layout="wide")

DATA_FILE = "hawker_centres_final.csv"


def short_name(name: str) -> str:
    """Use the text in the last brackets as a short display name."""
    matches = re.findall(r"\(([^)]+)\)", str(name))
    return matches[-1].strip() if matches else str(name).strip()


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["total_stalls"] = df["no_of_market_stalls"].fillna(0) + df["no_of_food_stalls"].fillna(0)
    df["stall_type"] = df.apply(
        lambda r: "Wet-market heavy"
        if r["no_of_market_stalls"] >= r["no_of_food_stalls"]
        else "Food-court style",
        axis=1,
    )
    df["short_name"] = df["name"].apply(short_name)
    return df


df = load_data()

st.title("🍜 HawkerGo Dashboard")

# ------------------------- Top 10 largest hawker centres -------------------------
st.subheader("Top 10 largest hawker centres by total stalls")

top10 = df.nlargest(10, "total_stalls").sort_values("total_stalls", ascending=True)

fig_top = px.bar(
    top10,
    y="short_name",
    x=["no_of_food_stalls", "no_of_market_stalls"],
    orientation="h",
    barmode="stack",
    color_discrete_map={
        "no_of_food_stalls": "#4c72b0",
        "no_of_market_stalls": "#dd8452",
    },
    hover_name="name",
    labels={"short_name": "Hawker centre", "value": "Number of stalls"},
)
names = {"no_of_food_stalls": "Food stalls", "no_of_market_stalls": "Market stalls"}
fig_top.for_each_trace(lambda t: t.update(name=names[t.name]))
fig_top.update_layout(legend_title_text="", height=450)
st.plotly_chart(fig_top, use_container_width=True)

with st.expander("Show top 10 table"):
    st.dataframe(
        top10.sort_values("total_stalls", ascending=False)[
            ["name", "no_of_market_stalls", "no_of_food_stalls", "total_stalls", "address_myenv"]
        ],
        use_container_width=True,
        hide_index=True,
    )

# ----------------------- Distribution: market vs food stalls -----------------------
st.subheader("Distribution of market stalls vs food stalls")

fig_dist = px.scatter(
    df,
    x="no_of_food_stalls",
    y="no_of_market_stalls",
    color="stall_type",
    color_discrete_map={"Wet-market heavy": "#1f77b4", "Food-court style": "#d62728"},
    hover_name="short_name",
    labels={
        "no_of_food_stalls": "Food stalls",
        "no_of_market_stalls": "Market stalls",
        "stall_type": "",
    },
)
fig_dist.update_traces(marker=dict(size=10, opacity=0.8))
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown(
    """
This chart shows how hawker centres split their space between raw grocery trading and cooked food.

- **Blue dots** are wet-market heavy centres, with at least as many market stalls as food stalls.
- **Red dots** are food-court style centres, which focus more on cooked food stalls.
"""
)

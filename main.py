import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

st.set_page_config(
    page_title="Fogyás Challenge",
    layout="wide"
)

#Adatok betöltése
@st.cache_data
def load_data():
    df = pd.read_excel("challenge 2026 12_1.xlsx", skiprows=3)
    df = df.iloc[:, 1:]
    cols = list(df.columns)
    cols[0] = "Név"
    df.columns = cols
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
    df = df.dropna(subset=[df.columns[0]])
    df = df.dropna(axis=1, how="all")
    #df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("Név")
    return df

def color_yes_no(val):
    if val == "Igen":
        return "background-color: lightgreen"
    elif val == "Nem":
        return "background-color: lightcoral"
    return ""

@st.cache_data
def load_tips():
    df_tips = pd.read_excel("challenge 2026 tippek.xlsx")
    cols = list(df_tips.columns)
    cols[0] = "Név"
    df_tips.columns = cols
    return df_tips

@st.cache_data
def load_goals():
    df_goals = pd.read_csv("challenge 2026_celertek.xlsx")
    return df_goals

@st.cache_data
def create_table(df):
    df_preprocessed = df.copy()
    cols = df_preprocessed.filter(regex=r'^\d').columns
    for i, col in enumerate(cols):
        if i == 0:
            continue
        new_col_name = cols[0] +"->" + cols[i]
        df_preprocessed[new_col_name] = df_preprocessed[cols[i]] - df_preprocessed[cols[0]]
        new_col_name = new_col_name + "%"
        df_preprocessed[new_col_name] = (df_preprocessed[cols[i]] - df_preprocessed[cols[0]]) / df_preprocessed[cols[0]] *100
    df_preprocessed["teljes fogyás"] = df_preprocessed[cols[-1]] - df_preprocessed[cols[0]]
    return df_preprocessed

def calc_kpis(df_in):
    df = df_in.copy()
    df["diff"] = df[df.columns[-1]]-df[df.columns[0]]
    df["diff"] = df["diff"] * (-1)
    max_name = df["diff"].idxmax()
    max_value = df["diff"].max()
    min_name = df["diff"].idxmin()
    min_value = df["diff"].min()

    return max_name, max_value, min_name, min_value

def calc_kpis2(df_in):
    df_in = df_in * (-1)
    max_name = df_in.iloc[:, -2].idxmax()
    max_value = df_in.iloc[:, -2].max()
    min_name = df_in.iloc[:, -2].idxmin()
    min_value = df_in.iloc[:, -2].min()
    return max_name, max_value, min_name, min_value

def calc_kpis3(df_in):
    df_in = df_in
    max_name = df_in.iloc[:, -1].idxmax()
    max_value = df_in.iloc[:, -1].max()
    min_name = df_in.iloc[:, -1].idxmin()
    min_value = df_in.iloc[:, -1].min()
    return max_name, max_value, min_name, min_value

#Plotly lineplot
def create_line_plot(df):
    weeks = list(df.columns)

    fig = go.Figure()
    for i, person in enumerate(df.index):
        weights = df.loc[person].values
        hovertemplate = (
            "Név: %{customdata}<br>"
            "Hét: %{x}<br>"
            "Súly: %{y} kg<extra></extra>"
        )
        fig.add_trace(go.Scatter(
            x=weeks,
            y=weights,
            mode="lines+markers",
            name=person,
            line=dict(width=2),
            customdata=[person]*len(weeks),
            hovertemplate=hovertemplate
        ))

    fig.update_layout(
        title="Súly alakulása",
        height=400,
        width=800,
        legend=dict(
            itemclick="toggle",
            itemdoubleclick="toggleothers"
        )
    )
    return fig

#Plotly oszlopdiagram
def create_barplot(df_preprocessed):
    df_plot = df_preprocessed.copy()
    df_plot["teljes fogyás"] = df_plot["teljes fogyás"] * -1
    # rendezés
    df_plot = df_plot.sort_values("teljes fogyás", ascending=False)

    colors = [
        "#2ecc71" if v > 0 else "#e74c3c"
        for v in df_plot["teljes fogyás"]
    ]

    fig = go.Figure()
    fig.add_bar(
        x=df_plot.index,
        y=df_plot["teljes fogyás"],
        marker_color=colors
    )
    fig.update_layout(
        title = "Az utolsó mérésig elért fogyás:"
    )
    return fig

##################################################
#1. Adatok betöltése
df = load_data()
##################################################
#2. Datatable előállítása
df_preprocessed=create_table(df)

#################################################
#3. célérték join
df_tippek=load_tips()
df_full = pd.merge(df_tippek, df, on="Név")
cols = list(df.columns)
last_col=cols[-1]
col_progress = ['Név', 'Kezdő súly', "kitűzött cél", "diff", last_col]
df_progress = df_full[col_progress]
df_progress["last_diff"] = df_progress['Kezdő súly'] - df_progress[last_col]
df_progress["Előrehaladás"] = df_progress["last_diff"] / df_progress["diff"] * 100
df_progress = df_progress.sort_values("Előrehaladás", ascending=True)
df_progress=df_progress.set_index("Név")

#4. Első sorban cím
st.title("A Nagy Fogyás 2026 Tavasz - Mediso")
st.divider()
st.write("A legutolsó hét bajnokai!:")
#5. KPI számítása és megjelenítése
col1, col2, col3, col4 = st.columns(4)
max_name, max_value, min_name, min_value = calc_kpis(df)
with col1:
    metric_max = st.metric("🏆 A legtöbb fogyás kg-ban", max_name, f"{max_value:.1f} kg")

with col2:
    metric_min = st.metric("🏆 Legkevesebb fogyás kg-ban", min_name, f"{min_value:.1f} kg")
    
max_name, max_value, min_name, min_value= calc_kpis3(df_progress)
with col3:
    metric_max = st.metric("🏆 Aki legközelebb van a célhoz", max_name, f"{max_value:.1f} %")

with col4:
    metric_min = st.metric("🏆 Aki a legtávolabb van a céltól", min_name, f"{min_value:.1f} %")    
st.divider()
#6. A verseny aktuális állása
st.write("A verseny aktuális állása:")

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(
        df_progress,
        x="Előrehaladás",
        y=df_progress.index,
        orientation="h",
        range_x=[df_progress["Előrehaladás"].min(),df_progress["Előrehaladás"].max()],
        title="Fogyási cél teljesítése (%)",
        text="Előrehaladás"
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>" + "Előrehaladás: %{x:.1f}%<extra></extra>"
    )
    fig.add_vline(
        x=100,
        line_color="red",
        line_width=2,
        line_dash="dash"
    )

    st.plotly_chart(fig, width='stretch')
    st.write("(Tipp: kattints magadon duplán, hogy látványosabb legyen a saját haladásod!⬇️)")
    #8. Plotly vonaldiagram %-os fogyásra
    df_percent = df_preprocessed.filter(regex=r'%$')
    fig_percent = px.line(df_percent.T, markers=True)
    fig_percent.update_layout(
            title="A testsúly változása százalékban:",
            height=400,
            width=800,
            xaxis_title="Hét",
            yaxis_title="Változás mértéke(%)",
            legend=dict(
                itemclick="toggle",
                itemdoubleclick="toggleothers"
            )
        )
    st.plotly_chart(fig_percent, width='stretch')
    
with col2:
    #7. Oszlopdiagram az aktuális kg értékekkel
    fig = create_barplot(df_preprocessed)
    st.plotly_chart(fig, width='stretch')

    st.write("")
    
    #9. Plotly vonaldiagram kg-okra
    fig = create_line_plot(df)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
#10. Táblázat
st.write("A részletes mérési adatok:")
row_height = 35
header_height = 38
height = header_height + row_height * len(df_preprocessed)
st.dataframe(df_preprocessed, height=height)

st.divider()
#11. Tippek df megjelenítése
st.write("A versenyre leadott tippek:")
num_cols = df_tippek.select_dtypes(include="number").columns
styled_df = df_tippek.style.map(color_yes_no).format({col: "{:.1f}" for col in num_cols})
height = header_height + row_height * len(df_tippek)
st.dataframe(styled_df, height=height)








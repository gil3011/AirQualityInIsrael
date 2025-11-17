import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import scipy.stats as stats
st.set_page_config(layout="wide")
@st.cache_data
def load_data():
    season_data = pd.read_csv("Data/season_data.csv")
    scaler = MinMaxScaler()
    pollutants1 = season_data[["PM25","O3","PM10","NOx","SO2","TEMP"]]
    pollutants1= scaler.fit_transform(pollutants1)
    scaled_df = pd.DataFrame(pollutants1, columns=["PM25","O3","PM10","NOx","SO2","TEMP"])

    scaled_df["תאריך ושעה"] = season_data["תאריך ושעה"].values
    scaled_df = scaled_df[["תאריך ושעה", "PM25","O3","PM10","NOx","SO2","TEMP"]]

    return season_data,scaled_df

season_data,scaled_df = load_data()

st.markdown("""
    <style>
    body, .reportview-container, .main {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

columns = season_data.drop(["תאריך ושעה", 'month', 'year'], axis=1).columns.tolist()
st.header("השוואת מזהמים")
st.subheader("מטריצת מתאם בין מזהמים",divider=True)

corr = scaled_df.drop(["תאריך ושעה"], axis=1).corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(corr, mask=mask, annot=True, vmin=-0.9, vmax=0.9, cmap="crest", ax=ax)
ax.set_xlabel("מזהם"[::-1])
ax.set_ylabel("מזהם"[::-1])
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
st.pyplot(fig)

st.subheader("השוואה בין זוגות מזהמים",divider=True)

col1, col2 = st.columns(2)
with col1:
    pollutant_1 = st.selectbox("בחר עמודה ראשונה", columns)

# Filter out col1 from the options for col2
col2_options = [col for col in columns if col != pollutant_1]
with col2:
    pollutant_2 = st.selectbox("בחר עמודה שנייה", col2_options)

filtered_df = season_data[[pollutant_1, pollutant_2, 'year']]

col1, col2  = st.columns(2)

with col1:
    with st.spinner("Generating plot..."):
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.kdeplot(scaled_df[[pollutant_1,pollutant_2]], fill=True, alpha=0.4)
        ax.set_title(f"Kde Plot: {pollutant_1} vs {pollutant_2}")
        st.pyplot(fig)
with col2:  
    with st.spinner("Generating plot..."):
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(scaled_df[[pollutant_1,pollutant_2]])
        ax.set_title(f"Box Plot: {pollutant_1} vs {pollutant_2}")
        st.pyplot(fig)
with st.spinner("Generating plot..."):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=filtered_df, x=pollutant_1, y=pollutant_2, alpha=0.8, hue='year', palette='crest')
    ax.set_title(f"Scatter Plot: {pollutant_1} vs {pollutant_2}")
    ax.grid(True)

    st.pyplot(fig)
st.write("השוואה סטטיסטית בין זוגות מזהמים")
stat, p_value = stats.mannwhitneyu(filtered_df[pollutant_1], filtered_df[pollutant_2], alternative='two-sided')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="U Statistic", value=f"{stat:.2f}")
with col2:
    st.metric(label="p-value", value=f"{p_value:.4f}")
with col3:
    st.metric(label="Significant", value="✅" if p_value < 0.05 else "❌")
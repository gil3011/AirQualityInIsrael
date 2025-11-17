import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import itertools

st.set_page_config(layout="wide")
@st.cache_data
def load_data():
    pollutants = ['O3','NOx','PM10','PM25','SO2','TEMP']
    pollutants_df = {}
    for p in pollutants:
        df = pd.read_csv(f"Data/{p}_raw_data.csv")
        df["תאריך ושעה"] = pd.to_datetime(df["תאריך ושעה"])   
        df["year"] = df["תאריך ושעה"].dt.year
        df["month"] = df["תאריך ושעה"].dt.month
        pollutants_df[p] = df
    season_data = pd.read_csv("Data/season_data.csv")
    return pollutants_df , season_data

st.markdown("""
    <style>
    body, .reportview-container, .main {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)
pollutants_df,season_data = load_data()
pollutants = list(pollutants_df.keys())
selected_polutant = st.selectbox("Choose a pollutant", pollutants)

st.subheader("התפלגות ערכים לפי עונה", divider=True)
season_df = season_data[[selected_polutant, "Season"]].copy()
season_df['Season'] = season_df['Season'].apply(lambda x: x[::-1])  # reverse Hebrew text

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Boxplot לפי עונה")
    plt.figure(figsize=(6, 5))
    sns.boxplot(data=season_df, x="Season", y=selected_polutant, hue="Season", palette="Set2")
    plt.ylabel(selected_polutant)
    st.pyplot(plt.gcf())

with col2:
    st.subheader("KDE לפי עונה")
    plt.figure(figsize=(6, 5))
    sns.kdeplot(data=season_df, x=selected_polutant, hue="Season",alpha=0.5, fill=True, common_norm=False, palette="Set2")
    plt.xlabel(selected_polutant)
    plt.ylabel("Density")
    st.pyplot(plt.gcf())

st.subheader("השוואה סטטיסטית בין עונות",divider=True)
season_df['Season'] = season_df['Season'].apply(lambda x: x[::-1])
# Get unique seasons
seasons = season_df['Season'].unique()
results = []
for s1, s2 in itertools.combinations(seasons, 2):
    group1 = season_df[season_df['Season'] == s1][selected_polutant]
    group2 = season_df[season_df['Season'] == s2][selected_polutant]
    stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    
    results.append({
        'Season 1': s1,
        'Season 2': s2,
        'U Statistic': round(stat, 2),
        'p-value': round(p_value, 4),
        'Significant': '✅' if p_value < 0.05 else '❌'
    })

results_df = pd.DataFrame(results)

st.dataframe(results_df, use_container_width=True)


st.subheader("התפלגות ערכים לפי שעה ויום בשבוע",divider=True)
season_data['תאריך ושעה'] = pd.to_datetime(season_data['תאריך ושעה'])
season_data['hour'] = season_data['תאריך ושעה'].dt.hour
season_data['day_of_week'] = season_data['תאריך ושעה'].dt.dayofweek

fig, ax = plt.subplots(figsize=(7, 7))
day_names_hebrew = {
    0: "שני",     # Monday
    1: "שלישי",   # Tuesday
    2: "רביעי",   # Wednesday
    3: "חמישי",   # Thursday
    4: "שישי",    # Friday
    5: "שבת",     # Saturday
    6: "ראשון"    # Sunday
}
pivot_data = season_data[[selected_polutant, 'hour', 'day_of_week']].pivot_table(values=selected_polutant, 
                             index='hour', 
                             columns='day_of_week', 
                             aggfunc='mean')
day_order = [6, 0, 1, 2, 3, 4, 5]
pivot_data = pivot_data[day_order]

sns.heatmap(pivot_data, cmap='YlOrRd', ax=ax)
ax.set_xlabel("יום בשבוע"[::-1])
ax.set_ylabel("שעה"[::-1])
ax.set_xticklabels([day_names_hebrew[i][::-1] for i in pivot_data.columns])
st.pyplot(fig)

st.subheader(f"התפלגות ערכים לפי תחנה עבור {selected_polutant}",divider=True)
station_options = pollutants_df[selected_polutant].drop(["תאריך ושעה","month","year"], axis=1).columns.sort_values()
selected_stations = st.multiselect("Choose station(s)", station_options, default=[station_options[0]])
min_date = pollutants_df[selected_polutant]["תאריך ושעה"].min()
max_date = pollutants_df[selected_polutant]["תאריך ושעה"].max()
col1,col2 = st.columns(2)
with col1:
    start_date= st.date_input(
        "בחר תאריך התחלה",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
with col2:
    end_date = st.date_input(
        "בחר תאריך סיום",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

mask = (pollutants_df[selected_polutant]["תאריך ושעה"] >= pd.to_datetime(start_date)) & \
       (pollutants_df[selected_polutant]["תאריך ושעה"] <= pd.to_datetime(end_date))
filtered_df_raw = pollutants_df[selected_polutant][mask]
filtered_df = filtered_df_raw.groupby(["year", "month"])[selected_stations].mean().reset_index()
filtered_df["date"] = pd.to_datetime(filtered_df[["year", "month"]].assign(day=1))

if not selected_stations:
    st.subheader("לא נבחרו תחנות")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ערכים ממוצעים חודשיים")
        with st.spinner("Generating plot..."):
            filtered_df = filtered_df_raw.groupby(["year", "month"])[selected_stations].mean().reset_index()
            filtered_df["date"] = pd.to_datetime(filtered_df[["year", "month"]].assign(day=1))
            fig, ax = plt.subplots(figsize=(7, 5))  
            for station in selected_stations:
                sns.lineplot(x=filtered_df["date"], y=filtered_df[station], label=station[::-1], ax=ax)
            ax.set_xlabel("תאריך"[::-1])
            ax.set_ylabel("ערך ממוצע חודשי"[::-1])
            ax.legend(title="תחנה"[::-1])
            st.pyplot(fig)
        st.subheader("התפלגות ערכים")
        with st.spinner("Generating plot..."):
            dist_data = filtered_df_raw[station].dropna()
            fig2, ax2 = plt.subplots(figsize=(7, 5))  
            for station in selected_stations:
                dist_data = pollutants_df[selected_polutant][station].dropna()
                sns.kdeplot(dist_data, label=station[::-1], ax=ax2, fill=True, alpha=0.4)
            ax2.set_xlabel("ערך נמדד"[::-1])
            ax2.set_ylabel("תדירות"[::-1])
            ax2.legend(title="תחנה"[::-1])
            st.pyplot(fig2)


    with col2:
        st.subheader("ערכים מקסימליים חודשיים")
        with st.spinner("Generating plot..."):
            filtered_df_max = filtered_df_raw.groupby(["year", "month"])[selected_stations].max().reset_index()
            filtered_df_max["date"] = pd.to_datetime(filtered_df_max[["year", "month"]].assign(day=1))
            fig4, ax4 = plt.subplots(figsize=(7, 5))  
            for station in selected_stations:
                sns.lineplot(x=filtered_df_max["date"], y=filtered_df_max[station], label=station[::-1], ax=ax4)
            ax4.set_xlabel("תאריך"[::-1])
            ax4.set_ylabel("ערך מקסימלי חודשי"[::-1])
            ax4.legend(title="תחנה"[::-1])
            st.pyplot(fig4)

        with st.spinner("Generating box plot..."):
            st.subheader("Box Plot")
            box_data = pd.melt(
                filtered_df_raw[["תאריך ושעה"] + selected_stations],
                id_vars=["תאריך ושעה"],
                value_vars=selected_stations,
                var_name="תחנה",
                value_name="ערך"
            )
            fig3, ax3 = plt.subplots(figsize=(7, 5))
            box_data = pd.melt(
                pollutants_df[selected_polutant][["תאריך ושעה"] + selected_stations],
                id_vars=["תאריך ושעה"],
                value_vars=selected_stations,
                var_name="תחנה",
                value_name="ערך"
            )
            box_data["תחנה"] = box_data["תחנה"].apply(lambda x: x[::-1])

            sns.boxplot(x="תחנה", y="ערך", data=box_data, ax=ax3,hue="תחנה", palette="tab10")
            ax3.set_xlabel("תחנה"[::-1])
            ax3.set_ylabel("ערך נמדד"[::-1])
            st.pyplot(fig3)



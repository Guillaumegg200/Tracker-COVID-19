import streamlit as st
from utils import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(layout="wide")


st.markdown("<h1 style='text-align: center;'>Covid-19: maps and graphs of the epidemic in France</h1>", unsafe_allow_html=True)

st.markdown("<h6 style='text-align: center;'>By Sami Jallouli, Martin Lefèvre, Samuel Pariente, Guillaume Grasset-Gothon</h6>", unsafe_allow_html=True)



st.header('State of the epidemic in France')

df = pd.read_csv('./preprocessed_data/epidemic_state.csv')
df['date'] = pd.to_datetime(df['date'])

st.write(f'As of May 31, 2023, the total number of infections detected since the start of the epidemic has reached {"{:,}".format(np.sum(df["P"]))} cases')

# Global figures
col = st.columns((1.5, 1.5, 1.5), gap="medium")
today = df["date"].max()
st.markdown(
    """
<style>
.big-font {
    font-size:45px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


with col[0]:
    with st.container():
        st.subheader("Total number of Covid cases last week")
        df_week = df[df["date"] > today - timedelta(days=7)]
        st.markdown(f"""<p class="big-font">{np.sum(df_week['P'])}</p>""", unsafe_allow_html=True)

with col[1]:
    with st.container():
        st.subheader("Percentage of cases among last week's tests")
        percentage_positive = np.sum(df_week["P"])/np.sum(df_week['T']) * 100
        st.markdown(f"""<p class="big-font" ">{percentage_positive:.2f} %</p>""", unsafe_allow_html=True)

with col[2]:
    with st.container():
        st.subheader("Evolution of Covid cases")
        df_previous_week = df[(df["date"] > today - timedelta(days=14)) & (df["date"] < today - timedelta(days=7))]
        evolution = (np.sum(df_week["P"]) - np.sum(df_previous_week["P"]))/np.sum(df_week["P"]) * 100
        if evolution > 0:
            st.markdown(
                f"""<p class="big-font" style="color: #228B22;">{evolution:.2f} %</p>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<p class="big-font" style="color: #ff0000;">{evolution:.2f} %</p>""",
                unsafe_allow_html=True,
            )


end_date = max(df['date'])
# Add 9 months to the start date
start_date =  pd.to_datetime(end_date) - pd.DateOffset(months=9)


min_value = datetime(2020, 5, 13)
max_value = datetime(2023, 6, 23) - timedelta(days=30*9)
start_value = datetime(2023, 6, 23) - timedelta(days=30*9)

st.subheader("Epidemic evolution")
st.write('Number of Covid-19 cases reported at the time of testing in hospitals and Ehpad.')

# Create a slider for date selection
selected_date = st.slider(
"Move the sliding window:",
min_value=min_value,
max_value=max_value,
value=start_value,
format="YYYY-MM-DD"
)
end_object = datetime.strptime(str(selected_date), '%Y-%m-%d %H:%M:%S')

start_date = str(pd.Timestamp(end_object.date()) )

end_date =  str(pd.to_datetime(start_date)+ pd.DateOffset(months=9))

col1, col2  = st.columns(2)
with col1:
    st.plotly_chart(plot_positive_cases_with_zoom(df,  start_date, end_date),height=30, width=300)
    st.write('Move or resize the period you wish to inspect ')

with col2:
    st.plotly_chart(plot_positive_cases(df, start_date, end_date))


st.subheader("National dynamics of the epidemic")
st.write('These graphs show the average weekly incidence rate (per 100,000 inhabitants, i.e. ), the number of tests and their positivity rate on May 31, 2023.')
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Incidence rate")
    st.markdown(
                f"""<h4 style="color: #c8738b;">{df.iloc[-1]['Ti']:.2f} ‰ on {today.strftime("%A, %B %d, %Y")}</h4>""",
                unsafe_allow_html=True,
            )
    st.plotly_chart(plot_incidence_rate(df), use_container_width=True)

with col2:
    st.subheader("People tested")
    st.markdown(
                f"""<h4 style="color: #c8738b;">{df.iloc[-1]['T']:.0f} on {today.strftime("%A, %B %d, %Y")}</h4>""",
                unsafe_allow_html=True,
            )
    st.plotly_chart(plot_cases_trend(df), use_container_width=True)

with col3:
    st.subheader("Positive Rate")
    st.markdown(
                f"""<h4 style="color: #c8738b;">{df.iloc[-1]['Tp']:.1f} % on {today.strftime("%A, %B %d, %Y")}</h4>""",
                unsafe_allow_html=True,
            )
    st.plotly_chart(plot_positive_rate(df), use_container_width=True)




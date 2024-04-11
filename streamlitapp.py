import streamlit as st
from utils import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


st.set_page_config(layout="wide")




def Overview_page():
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

    st.subheader("Epidemic evolution in terms of number of cases")
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
                    f"""<h4 style="color: #c8738b;">{df.iloc[-1]['Ti']:.0f} ‰ on {today.strftime("%A, %B %d, %Y")}</h4>""",
                    unsafe_allow_html=True,
                )
        st.plotly_chart(plot_incidence_rate(df), use_container_width=True)

    with col2:
        st.subheader("People tested")
        st.markdown(
                    f"""<h4 style="color: #c8738b;">{df.iloc[-1]['T']//1000}k on {today.strftime("%A, %B %d, %Y")}</h4>""",
                    unsafe_allow_html=True,
                )
        st.plotly_chart(plot_tested(df), use_container_width=True)

    with col3:
        st.subheader("Positive Rate")
        st.markdown(
                    f"""<h4 style="color: #c8738b;">{df.iloc[-1]['Tp']:.1f} % on {today.strftime("%A, %B %d, %Y")}</h4>""",
                    unsafe_allow_html=True,
                )
        st.plotly_chart(plot_positive_rate(df), use_container_width=True)

def Departement_page():
    # By department
    departements = ['France'] + list(unique_departments())
    # create a select box for the user to select a department
    st.subheader("Epidemic evolution by department")
    st.write("This part of the dashboard shows the evolution of the epidemic in France and its departments. The map shows the incidence rate in each department, while the graph shows the evolution of the number of cases in the selected department.")

    col_dep, col_wave  = st.columns(2)
    with col_dep:
        selected_departement = st.selectbox('Select a department:', departements)

    with col_wave:
        wave = st.selectbox("Wave", [1, 2, 3])



    #try : 
    map = map_cov(wave=wave, dep_to_highlight=selected_departement)
    #except ValueError:
    #    map = map_cov(wave=1, dep_to_highlight=None)


    # Usage remains the same
    line = plot_timeserie_with_animation(dep=selected_departement)

    # make the title of the dashboard 
    st.plotly_chart(map, use_container_width=True)
    st.plotly_chart(line, use_container_width=True)


#Add different pages
PAGES = {
    "Overview": Overview_page,
    "Covid by Departement": Departement_page,
}

demo_name = st.sidebar.selectbox("Choose a page", PAGES.keys())
PAGES[demo_name]()
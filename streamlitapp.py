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

def DepartmentPage():
    """
    This function creates a page on the Streamlit app that focuses on the
    epidemic's evolution by department in France. It provides interactive
    elements for users to select a department and a wave of the epidemic, 
    and displays corresponding visual data.
    """
    # Begin by defining the departments dropdown, including a default 'France' option
    departments = ['France'] + list(unique_departments())
    
    # Display a section header and an introductory message
    st.subheader("Epidemic Evolution by Department")
    st.write("""
    This section of the dashboard allows users to explore the COVID-19 epidemic's 
    progression in France through an interactive map and a detailed chart. The map 
    illustrates the incidence rate across various departments, and the chart shows 
    the trend in case numbers over time for a selected department, along with the 
    percentage of COVID-related visits compared to all visits.
    """)
    
    # Create two columns for department selection and wave selection
    col_dep, col_wave = st.columns(2)
    
    with col_dep:
        # Department selection dropdown
        selected_department = st.selectbox('Select a Department:', departments)
    
    with col_wave:
        # Epidemic wave selection dropdown
        wave = st.selectbox("Select an Epidemic Wave:", [1, 2, 3], index=2)
    
    # MAP VISUALIZATION
    st.write("""
    #### Map Visualization
    Below is a map depicting the spread of COVID-19 across France. You can select 
    a specific department to focus on and an epidemic wave to see how the situation 
    evolved during that period.
    """)
    # Attempt to generate a map highlighting the selected department and wave
    map_display = map_cov(dep_to_highlight=selected_department, wave=wave)
    st.plotly_chart(map_display, use_container_width=True)

    # CHART VISUALIZATION
    st.write("""
    #### Chart Visualization
    The chart below offers a closer look at the epidemic's evolution within the 
    selected department. It not only displays the moving average of daily COVID-19 
    cases but also visualizes the proportion of COVID-related visits out of all 
    healthcare visits. This metric serves as an indicator of the pandemic's impact 
    on the healthcare system over time for a given department.
    """)
    # Generate and display the chart
    line_chart = plot_timeserie_with_animation(dep=selected_department)
    st.plotly_chart(line_chart, use_container_width=True)



def AgeGroupsPage():
    """
    This function creates a page on the Streamlit app that focuses on the
    COVID-19 hospitalizations in France by age group. It provides interactive
    elements for users to select a date range, and displays corresponding visual data.
    """
    
    st.title('Repartition of COVID-19 per age group in France')
    st.write('This section displays the evolution of COVID-19 hospitalizations in France by age group.')

    # Load the data
    path = "./raw_data/sursaud-covid19-departement_2020.csv"
    df = pd.read_csv(path, sep=";")

    columns = st.columns((4, 1), gap="large")

    with columns[0]:
        st.subheader('Evolution of COVID hospitalizations by age group over time')
        st.write("You can select a date range to zoom in the chart below. An overview of the share of each age group over this period will be displayed on the right.")
        # Add a transparent box to chart_evol to select a date range
        date_range = st.select_slider('Select a date range:', df['date_de_passage'].unique(), (df['date_de_passage'].min(), df['date_de_passage'].max()))
        date_start, date_end = date_range[0], date_range[1]

        # Plot the evolution of hospitalizations by age group
        chart_evol, df_chart = plot_age_group_px(df, date_end=date_end, date_start=date_start)
        st.plotly_chart(chart_evol)

    with columns[1]:
        st.subheader('Share of each Age Group in hospitalizations')
        st.write("Zoom in the selected period")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        # Plot the share of each age group in hospitalizations over time
        chart_prop = plot_age_group_share(df_chart, date_start, date_end)
        st.plotly_chart(chart_prop)



def SaturationPage():
    """This function creates a page on the Streamlit app that focuses on the
    saturation of hospitals by department in France. It provides interactive
    elements for users to select a department, 
    and displays corresponding visual data.
    """
    # Data loading
    df = pd.read_csv('./preprocessed_data/covid19-saturation-dep.csv')

    # Begin by defining the departments dropdown, including a default 'France' option
    departments = ["France"] + df["Libellé"].unique().tolist()
    
    # Display a section header and an introductory message
    st.subheader("Health System Saturation by Department")
    st.write("""
    This section of the dashboard allows users to explore the saturation of the health system 
    in France through a detailed chart.
    """)
    
    # Create a column for department selection
    col_dep, _ = st.columns(2)
    
    with col_dep:
        selected_department = st.selectbox('Select a Department:', departments)

    # CHART VISUALIZATION
    st.write("""
    #### Chart Visualization
    The chart below offers a closer look at the health system saturation rate within the 
    selected department. It displays the moving average of three main indicators
    over time, providing insights into the healthcare system's capacity to handle the 
    COVID-19 pandemic.
    """)

    # Generate and display the chart
    line_chart = plot_saturation(df, selected_department)
    st.plotly_chart(line_chart, use_container_width=True)


#Add different pages
PAGES = {
    "Overview": Overview_page,
    "Covid by Departement": DepartmentPage,
    "Age groups repartition": AgeGroupsPage,
    "Health System Saturation": SaturationPage
}

demo_name = st.sidebar.selectbox("Choose a page", PAGES.keys())
PAGES[demo_name]()
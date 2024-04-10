import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def plot_age_group_px(df, date_start, date_end):
    # Create a working dataframe
    df_evol_ages = df.groupby(['date_de_passage', 'sursaud_cl_age_corona']).agg({
        "nbre_hospit_corona": 'sum',
        "nbre_hospit_corona_h": 'sum',
        "nbre_hospit_corona_f": 'sum'
    }).reset_index()

    # Map the age group codes to their corresponding labels
    age_group_labels = {
        "0": '7. All ages',
        "A": '5. Less than 15 years old',
        "B": '4. 15-44 years old',
        "C": '3. 45-64 years old',
        "D": '2. 65-74 years old',
        "E": '1. 75 years old and more',
    }
    df_evol_ages['sursaud_cl_age_corona'] = df_evol_ages["sursaud_cl_age_corona"].apply(lambda x: age_group_labels[x])

    # Calculate rolling average and normalize counts
    df_evol_ages['nbre_hospit_corona_weekly_avg'] = df_evol_ages.groupby('sursaud_cl_age_corona')['nbre_hospit_corona'].transform(lambda x: x.rolling(7).mean())
    df_evol_ages['nbre_hospit_corona_normalized'] = df_evol_ages.groupby('date_de_passage')['nbre_hospit_corona_weekly_avg'].transform(lambda x: 2 * 100 * (x / x.sum()))

    # Filter out the 'All ages' category
    df_chart = df_evol_ages[df_evol_ages["sursaud_cl_age_corona"] != "7. All ages"]

    # Set desired order for age groups
    desired_order = ['1. 75 years old and more', '2. 65-74 years old', '3. 45-64 years old', '4. 15-44 years old', '5. Less than 15 years old']

    # Create the line chart for hospitalizations over time
    chart_evol = px.area(df_chart, x='date_de_passage', y='nbre_hospit_corona_weekly_avg',
                          color='sursaud_cl_age_corona', category_orders={"sursaud_cl_age_corona": desired_order},
                          labels={'date_de_passage': 'Date', 'nbre_hospit_corona_weekly_avg': 'Count'},
                          width=500, height=300)
    # Add a transparent box cover the graph from date_start to date_end. Fill it in lightgrey with opacity 0.5
    chart_evol.add_vrect(x0=date_start, x1=date_end, fillcolor='rgba(100,100,100,0.1)', line_width=0, )

    # Update the layout to display legend above the chart
    chart_evol.update_layout(legend=dict(
        orientation="h",  # Set legend orientation to horizontal
        yanchor="top",  # Anchor legend to the top
        y=10,  # Adjust the distance of the legend from the top
        xanchor="center",  # Anchor legend to the center horizontally
        x=0.5  # Position legend at the center horizontally
    ))

    return chart_evol, df_chart

def plot_age_group_share(df_chart, date_start, date_end):

    # Create the line chart for normalized hospitalizations over time
    # Filter the data to only include the relevant dates
    desired_order = ['1. 75 years old and more', '2. 65-74 years old', '3. 45-64 years old', '4. 15-44 years old', '5. Less than 15 years old']
    df_chart = df_chart[(df_chart["date_de_passage"] >= date_start) & (df_chart["date_de_passage"] < date_end)]
    chart_prop = px.area(df_chart, x='date_de_passage', y='nbre_hospit_corona_normalized',
                          color='sursaud_cl_age_corona', category_orders={"sursaud_cl_age_corona": desired_order},
                          labels={'date_de_passage': 'Date', 'nbre_hospit_corona_normalized': ''},
                            width=100, height=300
                          )
    
    chart_prop.layout.update(showlegend=False)

    return chart_prop

st.title('COVID-19 Hospitalizations in France')
st.subheader('This app displays the evolution of COVID-19 hospitalizations in France by age group.')

# Load the data
path = "./sursaud-covid19-departement_2020.csv"
df = pd.read_csv(path, sep=";")

columns = st.columns((4, 1), gap="large")

with columns[0]:
    st.subheader('Evolution of COVID hospitalizations by age group over time')
    # Add a transparent box to chart_evol to select a date range
    date_range = st.select_slider('Select a date range:', df['date_de_passage'].unique(), (df['date_de_passage'].min(), df['date_de_passage'].max()))
    date_start, date_end = date_range[0], date_range[1]

    # Plot the evolution of hospitalizations by age group
    chart_evol, df_chart = plot_age_group_px(df, date_end=date_end, date_start=date_start)
    st.plotly_chart(chart_evol)

with columns[1]:
    st.subheader('Share of each Age Group in hospitalizations')
    st.write("Zoom in the selected period")
    # Plot the share of each age group in hospitalizations over time
    chart_prop = plot_age_group_share(df_chart, date_start, date_end)
    st.plotly_chart(chart_prop)

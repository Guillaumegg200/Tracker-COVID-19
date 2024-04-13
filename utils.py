import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd

def load_data(filename):
    data = pd.read_csv(filename, sep=';')
    for name in ['Ti','Td','Tp']:
        data[name] = data[name].str.replace(',', '.')
        data[name] = data[name].astype(float)
    df = data.copy()
    df = df.fillna(0)
    df['date'] = pd.to_datetime(data['jour'])
    df.drop(['dep','jour','cl_age90'], axis=1, inplace=True)
    df = df.groupby('date').agg({'P':'sum', 'T':'sum','Ti':'mean', 'Tp':'mean','Td':'mean', 'pop':'sum'}).reset_index()
    df['P7'] = df['P'].rolling(window=7).mean()
    df['T7'] = df['T'].rolling(window=7).mean()

    return df

def plot_positive_cases(df, start_date, end_date):
    df_filtered = df[(df['date'] > start_date) & (df['date'] < end_date)]
    fig = px.bar(df_filtered, x='date', y='P')
    fig.data[0].marker.color = '#eed5dc'
    line_trace = go.Scatter(x=df_filtered['date'], y=df_filtered['P7'], mode='lines', line=dict(color='#c8738b'), showlegend=False, hoverinfo = 'none')
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.1),
                      plot_bgcolor='white',
                      yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                      hovermode="x unified")
    # Update hovertemplate for each trace
    fig.update_traces(
    hovertemplate='%{x}<br> <b>%{y:.2s}</b> <extra></extra>'  # Customize tooltip content
    )
    fig.add_trace(line_trace)

    fig.update_yaxes(title_text='')
    fig.update_xaxes(title_text='')
    return fig

def plot_positive_cases_with_zoom(df, start_date, end_date):
    fig = px.bar(df, x='date', y='P')
    fig.data[0].marker.color = '#eed5dc'
    line_trace = go.Scatter(x=df['date'], y=df['P7'], mode='lines', name='Moving average over the last 7 days', line=dict(color='#c8738b'), hoverinfo = 'none')
    fig.update_traces(
    hovertemplate='%{x}<br> <b>%{y:.2s}</b> <extra></extra>'  # Customize tooltip content
    )

    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.1),
                      yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                      plot_bgcolor='white',
                      hovermode="x unified")
    fig.update_yaxes(title_text='')
    fig.update_xaxes(title_text='')
    fig.add_trace(line_trace)
    fig.add_vrect(x0=str(start_date), x1=str(end_date),
                  annotation_text="Zoom Area", annotation_position="top left",
                  fillcolor="grey", opacity=0.1, line_width=1,
                  annotation_font=dict(size=15, color='grey'))
    fig.add_vline(x=str(start_date), line_width=1, line_dash="dash", line_color="grey")
    fig.add_vline(x=str(end_date), line_width=1, line_dash="dash", line_color="grey")
    return fig

def plot_tested(df):
    fig = px.line(df, x='date', y='T7')
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.1),
                      xaxis=dict(title_text=''),
                      plot_bgcolor='white',
                      yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey', title_text=''),
                      hovermode="x unified")
    fig.data[0].fill = 'tozeroy'
    fig.data[0].fillcolor = '#eed5dc'
    fig.update_traces(marker=dict(size=10), line=dict(color='#c8738b'))
    fig.update_traces(
    marker=dict(size=10),
    line=dict(color='#c8738b'),
    hovertemplate=' <b>%{y:.2s}</b><extra></extra>'
    )
    return fig

def plot_positive_rate(df):
    df['Tp7'] = df['P7']/df['T7']
    df['Tp7'] = df['Tp7'].round(2)
    fig = px.line(df, x='date', y='Tp7')
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.1),
                      xaxis=dict(title_text=''),
                      plot_bgcolor='white',
                      yaxis=dict(
                          showgrid=True,
                          gridwidth=1,
                          gridcolor='lightgrey',
                          title_text='',
                          tickformat=".0%",
                      ),
                      hovermode="x unified")
    fig.data[0].fill = 'tozeroy'
    fig.data[0].fillcolor = '#eed5dc'
    fig.update_traces(marker=dict(size=10), line=dict(color='#c8738b'))
    fig.update_traces(
    marker=dict(size=10),
    line=dict(color='#c8738b'),
    hovertemplate='<b>%{y} </b><extra></extra>'
    )
    return fig

def plot_incidence_rate(df):
    df['Ti7'] = df['P7']/df['pop']*100000
    fig = px.line(df, x='date', y='Ti7')
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.1),
                      xaxis=dict(title_text=''),
                      plot_bgcolor='white',
                      yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey', title_text=''),
                      hovermode="x unified")
    fig.data[0].fill = 'tozeroy'
    fig.data[0].fillcolor = '#eed5dc'
    fig.update_traces(marker=dict(size=10), line=dict(color='#c8738b'))
    fig.update_traces(
    marker=dict(size=10),
    line=dict(color='#c8738b'),
    hovertemplate='<b>%{y:.0f}‰ </b><extra></extra>'
    )
    return fig

def prop_covid(date, dep_df):
    # Filter the DataFrame for the given date and date-1
    date_df = dep_df[dep_df['date_de_passage'] == date]

    previous_date_df = dep_df[dep_df['date_de_passage'] == date - pd.DateOffset(days=1)]

    value_at_date = date_df['prop_covid'].values[0] if not date_df.empty else 0
    try : 
        value_at_date_before = previous_date_df['prop_covid'].values[0] if not previous_date_df.empty else 0
    except:
        value_at_date_before = 0
    return value_at_date, value_at_date_before

def unique_departments():
    weekly_df = pd.read_csv("raw_data/sursaud-covid19-departement.csv", sep = ";")
    weekly_df["dep"] = weekly_df["dep"].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)
    return weekly_df['dep'].unique()

def plot_timeserie_with_animation(dep):
    dep = int(dep) if isinstance(dep, str) and dep.isdigit() else dep
    dep = None if dep == "France" else dep
    weekly_df = pd.read_csv("raw_data/sursaud-covid19-departement.csv", sep = ";")
    weekly_df["date_de_passage"] = pd.to_datetime(weekly_df["date_de_passage"])
    weekly_df["dep"] = weekly_df["dep"].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else x)

    if dep is not None:
        # Filter data based on department and dates
        weekly_df = weekly_df[weekly_df['dep'] == dep]
        dep_df = weekly_df[['date_de_passage', 'nbre_pass_corona',"nbre_pass_tot"]].groupby('date_de_passage').sum().reset_index()
        dep_df['prop_covid'] = dep_df['nbre_pass_corona'] / dep_df['nbre_pass_tot']
        #make a moving average on nbre_pass_corona
        dep_df['nbre_pass_corona'] = dep_df['nbre_pass_corona'].rolling(window=7).mean()

    else:
        #group by date and sum the values
        dep_df = weekly_df[['date_de_passage', 'nbre_pass_corona',"nbre_pass_tot"]].groupby('date_de_passage').sum().reset_index()
        dep_df['prop_covid'] = dep_df['nbre_pass_corona'] / dep_df['nbre_pass_tot']
        #make a moving average on nbre_pass_corona
        dep_df['nbre_pass_corona'] = dep_df['nbre_pass_corona'].rolling(window=7).mean()

    wave1_end_date = '2020-09-14'

    wave2_end_date = '2020-11-02'
        
    wave3_end_date = '2021-02-01'
    
    max_val = dep_df['nbre_pass_corona'].max()
    dates = sorted(dep_df['date_de_passage'].unique())
    
    # Create a subplot with 2 rows and 1 column
    fig = make_subplots(rows=2, cols=3, 
                        specs=[[{"type": "scatter", "colspan": 3}, None, None],
                               [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                        vertical_spacing=0.2, column_widths=[0.3, 0.4, 0.3])
    

    fig.add_trace(go.Scatter(x=dep_df['date_de_passage'], y=dep_df['nbre_pass_corona'],
                                mode='lines+markers', name=f"Cases for department {dep}", line=dict(color='#c8738b')),
                    row=1, col=1)
    

    wave1_end_date = pd.to_datetime('2020-09-14').timestamp() * 1000
    wave2_end_date = pd.to_datetime('2020-11-02').timestamp() * 1000
    wave3_end_date = pd.to_datetime('2021-02-01').timestamp() * 1000

    fig.update_layout(xaxis_type='date')

    # Now use these datetime objects in your add_vline calls
    fig.add_vline(x=wave1_end_date, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_vline(x=wave1_end_date, line_dash="dash", line_color="green", row=1, col=1, 
                annotation_text="End of wave 1", annotation_position="top left")
    fig.add_vline(x=wave2_end_date, line_dash="dash", line_color="green", row=1, col=1, 
                annotation_text="End of wave 2", annotation_position="top left")
    fig.add_vline(x=wave3_end_date, line_dash="dash", line_color="green", row=1, col=1, 
                annotation_text="End of wave 3", annotation_position="top left")
    
    
    #add waves legend 
   
    gauge={
            'axis': {'range': [None, 0.3], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#c8738b"},
            'steps': [
                {'range': [0, 0.06], 'color': 'lightgray'},
                {'range': [0.06, 0.12], 'color': 'gray'},
                {'range': [0.12, 0.18], 'color': 'darkgray'},
                {'range': [0.18, 0.24], 'color': 'gray'},
                {'range': [0.24, 3], 'color': 'lightgray'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.25
            }
        }

    # Add a placeholder trace for the proportion over max value, to be updated in frames
    fig.add_trace(go.Indicator(mode="number+gauge", value=dep_df['prop_covid'][0], delta={'reference': 1, 'relative': True},
                               title={"text": "<span style='font-size:0.8em'>Proportion of covid cases out of all healthcare visits</span>"},gauge=gauge),
                  row=2, col=2)
    

    # Add frames for each date with the red dashed line and update the indicator
    frames = []
    for date in dates:
        prop_at_date, prop_at_date_before = prop_covid(date, dep_df)

        # Update the indicators for each frame
        frame_data = [
            go.Scatter(
                x=dep_df['date_de_passage'],
                y=dep_df['nbre_pass_corona'],
                mode='lines+markers'
            ),
            go.Indicator(
                mode="number+gauge+delta",
                value=prop_at_date ,
                delta={'reference': prop_at_date_before, 'relative': True}
            ),
            ]

        # Add shapes to indicate the current date with a vertical line
        frame_layout = go.Layout(shapes=[dict(
            type="line",
            x0=date,
            y0=0,
            x1=date,
            y1=max_val,
            line=dict(color="Red", width=2, dash="dash")
        )])
    
        frames.append(go.Frame(
            data=frame_data,
            layout=frame_layout,
            name=str(date)
        ))

    fig.frames = frames

    
    # Set up the slider and play button
    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]
            }]
        }],
        sliders=[{
            "steps": [{"method": "animate", "args": [[str(date)], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}], "label": str(date)} for date in dates]
        }]
    )
    if dep is None:
        fig.update_layout(title="Covid cases for all departments",
                        xaxis_title="Date", yaxis_title="Covid cases", height=800)
    else:
        fig.update_layout(title=f"Covid cases for department {dep}",
                        xaxis_title="Date", yaxis_title="Covid cases", height=800)

    return fig


def map_cov(dep_to_highlight=None, wave = 1):
    dep_to_highlight = None if dep_to_highlight == "France" else dep_to_highlight

    if wave == 1 :
        weekly_df = pd.read_csv("preprocessed_data/weekly_covid_cases_by_department_wave_1.csv")
    
    if wave == 2 :
        weekly_df = pd.read_csv("preprocessed_data/weekly_covid_cases_by_department_wave_2.csv")
    
    if wave == 3 :
        weekly_df = pd.read_csv("preprocessed_data/weekly_covid_cases_by_department_wave_3.csv")

    weekly_df["date_de_passage"] = pd.to_datetime(weekly_df["date_de_passage"])
    max_cumulative_value = weekly_df['cumulative_nbre_pass_corona'].max()
    
    dep_names = pd.read_csv("raw_data/departements-region.csv")
    dep_names["num_dep"] = dep_names["num_dep"].apply(lambda x: str(int(x)) if isinstance(x, str) and x.isdigit() else x)
    dep_names = dep_names[["num_dep","dep_name"]]
    weekly_df = pd.merge(weekly_df, dep_names, how='left', left_on='dep', right_on='num_dep')

    geo_df = gpd.read_file('raw_data/departements.geojson')
    # Convert 'code' column to int except for '2A' and '2B'
    geo_df["code"] = geo_df["code"].apply(lambda x: int(x) if x.isdigit() else x)
    
    if dep_to_highlight == None:
       
        fig = px.choropleth_mapbox(weekly_df, geojson=geo_df, locations='dep',
                                featureidkey="properties.code",
                                color='cumulative_nbre_pass_corona',
                                hover_name='dep_name',
                                center={"lat": 46.2276, "lon": 2.2137},
                                mapbox_style="carto-positron", zoom=3.5,
                                animation_frame='date_de_passage',
                                color_continuous_scale='PuRd',
                                range_color=[0, max_cumulative_value])
        fig.update_layout(title_text=f'Covid cases in France by department during the {wave} wave')

    if dep_to_highlight is not None:
        dep_to_highlight = int(dep_to_highlight)
        #long lat of the center of highlighted department
        center_lat = geo_df[geo_df['code'] == dep_to_highlight].geometry.centroid.y.values[0]
        center_lon = geo_df[geo_df['code'] == dep_to_highlight].geometry.centroid.x.values[0] 
        
        weekly_df =  weekly_df[weekly_df['dep'] == str(dep_to_highlight)]
        fig = px.choropleth_mapbox(weekly_df, geojson=geo_df, locations='dep',
                                featureidkey="properties.code",
                                hover_name='dep_name',
                                color='cumulative_nbre_pass_corona',
                                center={"lat": center_lat, "lon": center_lon},
                                mapbox_style="carto-positron", zoom=7,
                                animation_frame='date_de_passage',
                                color_continuous_scale='PuRd',
                                range_color=[0, max_cumulative_value])
        # add department name to the map
        dep_name = geo_df[geo_df['code'] == dep_to_highlight].nom.values[0]
        fig.update_layout(title_text=f'Covid cases in {dep_name} during the {wave} wave')
    
    return fig


def get_date_first_peak(data: pd.DataFrame, column: str):
    # Filter data to keep only the period of interest
    data = data[(data["date"]<"2020-10-01") & (data["date"]>"2020-03-01")]
    max_value = data[column].max()
    if pd.isna(max_value):
        return None, None
    return data[data[column] == max_value]["date"].values[0], max_value


def plot_saturation(data: pd.DataFrame, department: str):
    # Filter data to keep only department of interest
    if department == "France":
        department = "France entière"
    data = data[data["Libellé"] == department]
    data = data[(data["date"]>"2020-03-01")]

    # Create the plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["date"], y=data["Share of SOS med calls for Covid"], mode='lines', name='Share of SOS medecin calls for Covid'))
    fig.add_trace(go.Scatter(x=data["date"], y=data["Share of hospital emergency visits for Covid"], mode='lines', name='Share of all emergency visits for Covid'))
    fig.add_trace(go.Scatter(x=data["date"], y=data["Share of all critical care beds occupied by Covid patients"], mode='lines', name='Share of all critical care beds occupied by Covid patients'))
    fig.add_shape(type="line", x0=data["date"].min(), y0=100, x1=data["date"].max(), y1=100, line=dict(color="red", width=1, dash="dash"))
    fig.add_annotation(x=data["date"].max(), y=100, text="Saturation", showarrow=False, yshift=10, xshift=30)
    
    # Plot dash lines to indicate the date of the first peak for each indicator
    max_dates = [get_date_first_peak(data, column) for column in ["Share of SOS med calls for Covid","Share of hospital emergency visits for Covid", "Share of all critical care beds occupied by Covid patients"]]
    max_dates = [date for date in max_dates if date[0] is not None]
    for index, (x0, max_value) in enumerate(max_dates):
        fig.add_shape(type="line", x0=x0, y0=0, x1=x0, y1=max_value, line=dict(color="black", width=1, dash="dash"))
        fig.add_annotation(x=x0, y=max_value, text=f"({index+1})", showarrow=False, yshift=10)
    
    # Update layout
    fig.update_layout(title='Saturation of health system during Covid-19 in France',
                        xaxis_title='Date',
                        yaxis_title='Percentage',
                        showlegend=True,
                        plot_bgcolor='white',  
                        paper_bgcolor='white', 
                        font=dict(color='black'),
                        xaxis=dict(showgrid=False), 
                        yaxis=dict(showgrid=False)
                    )
    return fig

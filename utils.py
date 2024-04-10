import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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


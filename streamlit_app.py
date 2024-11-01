import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(page_title="📊 SEO Analysis Dashboard", layout="wide")
st.title("📊 SEO Performance Analysis Dashboard")

# Carregar dados
@st.cache_data
def load_data():
    gsc_df = pd.read_excel('data/Cópia de SEO_exercise_anonymized_GSC_data.xlsx')
    metadata_df = pd.read_excel('data/SEO_exercise_anonymized_metadata.xlsx')
    gsc_df = pd.merge(gsc_df, metadata_df[['page', 'Cluster']], on='page', how='left')
    gsc_df['date'] = pd.to_datetime(gsc_df['date'])
    metadata_df['Date_Published'] = pd.to_datetime(metadata_df['Date_Published'])
    return gsc_df, metadata_df

gsc_df, metadata_df = load_data()

# Key Metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Clicks", f"{gsc_df['clicks'].sum():,.0f}")
col2.metric("Total Impressions", f"{gsc_df['impressions'].sum():,.0f}")
col3.metric("Average CTR", f"{(gsc_df['clicks'].sum() / gsc_df['impressions'].sum() * 100):.2f}%")
col4.metric("Average Position", f"{gsc_df['position'].mean():.2f}")

# 1. Monthly Traffic Trends
st.header("1. Monthly Traffic Trends")
monthly_metrics = gsc_df.groupby(gsc_df['date'].dt.to_period('M')).agg({
    'clicks': 'sum',
    'impressions': 'sum',
    'position': 'mean'
}).reset_index()
monthly_metrics['date'] = monthly_metrics['date'].astype(str)

fig1 = make_subplots(rows=3, cols=1, vertical_spacing=0.1, subplot_titles=('Clicks', 'Impressions', 'Average Position'))

# Clicks
fig1.add_trace(go.Scatter(
    x=monthly_metrics['date'], 
    y=monthly_metrics['clicks'],
    name='Clicks', 
    mode='lines+markers+text',
    text=[f"{x/1e6:.1f}M" if x >= 1e6 else f"{x:,.0f}" for x in monthly_metrics['clicks']],
    textposition='top center'
), row=1, col=1)

# Impressions
fig1.add_trace(go.Bar(
    x=monthly_metrics['date'], 
    y=monthly_metrics['impressions'],
    name='Impressions',
    text=[f"{x/1e6:.1f}M" if x >= 1e6 else f"{x:,.0f}" for x in monthly_metrics['impressions']],
    textposition='outside'
), row=2, col=1)

# Position
fig1.add_trace(go.Scatter(
    x=monthly_metrics['date'], 
    y=monthly_metrics['position'],
    name='Position', 
    mode='lines+markers+text',
    text=[f"{x:.1f}" for x in monthly_metrics['position']],
    textposition='top center'
), row=3, col=1)

fig1.update_layout(
    height=1200,
    showlegend=True,
    title_text="Monthly Traffic Trends",
    title_x=0.5
)

# Update y-axes labels
fig1.update_yaxes(title_text="Clicks", row=1, col=1)
fig1.update_yaxes(title_text="Impressions", row=2, col=1)
fig1.update_yaxes(title_text="Position", row=3, col=1)

st.plotly_chart(fig1, use_container_width=True)

# 2. Content Category Analysis
st.header("2. Content Category Analysis")

content_metrics = gsc_df.groupby('Cluster').agg({
    'clicks': 'sum',
    'impressions': 'sum'
}).reset_index()

content_metrics = content_metrics.sort_values('impressions', ascending=True)

fig2 = make_subplots(rows=2, cols=1, 
                     subplot_titles=('Content Category: Clicks', 'Content Category: Impressions'),
                     vertical_spacing=0.1)

# Clicks subplot
fig2.add_trace(
    go.Bar(
        x=content_metrics['clicks'],
        y=content_metrics['Cluster'],
        orientation='h',
        name='Clicks',
        text=[f"{x/1e6:.1f}M" if x >= 1e6 else f"{x:,.0f}" for x in content_metrics['clicks']],
        textposition='auto',
        hovertemplate='Clicks: %{x:.2f}<extra></extra>'
    ),
    row=1, col=1
)

# Impressions subplot
fig2.add_trace(
    go.Bar(
        x=content_metrics['impressions'],
        y=content_metrics['Cluster'],
        orientation='h',
        name='Impressions',
        text=[f"{x/1e6:.1f}M" if x >= 1e6 else f"{x:,.0f}" for x in content_metrics['impressions']],
        textposition='auto',
        hovertemplate='Impressions: %{x:.2f}<extra></extra>'
    ),
    row=2, col=1
)

fig2.update_layout(
    height=1000,
    showlegend=True,
    title_text="Content Category Analysis",
    title_x=0.5
)

fig2.update_xaxes(title_text="Clicks", row=1, col=1)
fig2.update_xaxes(title_text="Impressions", row=2, col=1)

st.plotly_chart(fig2, use_container_width=True)

# Publication Frequency Analysis
st.header("Publication Frequency Analysis")
publication_freq = metadata_df.groupby(metadata_df['Date_Published'].dt.to_period('M')).size().reset_index(name='count')
publication_freq['Date_Published'] = publication_freq['Date_Published'].astype(str)

fig3 = px.bar(publication_freq, 
              x='Date_Published', 
              y='count',
              text='count')

fig3.update_traces(textposition='outside')
fig3.update_layout(
    title_text="Publication Frequency Over Time",
    xaxis_title="Month",
    yaxis_title="Number of Publications",
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

# Weekly Pattern
st.header("Weekly Pattern")
gsc_df['weekday'] = gsc_df['date'].dt.day_name()
weekday_performance = gsc_df.groupby('weekday').agg({
    'clicks': 'mean',
    'impressions': 'mean',
    'position': 'mean'
}).reset_index()

weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_performance['weekday'] = pd.Categorical(weekday_performance['weekday'], 
                                              categories=weekday_order, 
                                              ordered=True)
weekday_performance = weekday_performance.sort_values('weekday')

fig4 = make_subplots(rows=1, cols=2, subplot_titles=('Average Daily Clicks', 'Average Position'))

fig4.add_trace(
    go.Bar(
        x=weekday_performance['weekday'],
        y=weekday_performance['clicks'],
        name='Clicks',
        text=[f"{x:.0f}" for x in weekday_performance['clicks']],
        textposition='outside'
    ),
    row=1, col=1
)

fig4.add_trace(
    go.Bar(
        x=weekday_performance['weekday'],
        y=weekday_performance['position'],
        name='Position',
        text=[f"{x:.2f}" for x in weekday_performance['position']],
        textposition='outside'
    ),
    row=1, col=2
)

fig4.update_layout(
    height=500,
    title_text="Average Daily Clicks and Position by Day of the Week",
    showlegend=True,
    title_x=0.5
)

st.plotly_chart(fig4, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(page_title="SEO Analysis Dashboard", layout="wide")
st.title("SEO Performance Analysis Dashboard")

# Carregar dados
@st.cache_data
def load_data():
    gsc_df = pd.read_excel('data/Cópia de SEO_exercise_anonymized_GSC_data.xlsx')
    metadata_df = pd.read_excel('data/SEO_exercise_anonymized_metadata.xlsx')
    gsc_df['date'] = pd.to_datetime(gsc_df['date'])
    metadata_df['Date_Published'] = pd.to_datetime(metadata_df['Date_Published'])
    return gsc_df, metadata_df

gsc_df, metadata_df = load_data()

# 1. Tendências Mensais
st.header("1. Monthly Traffic Trends")
monthly_metrics = gsc_df.groupby(gsc_df['date'].dt.to_period('M')).agg({
    'clicks': 'sum',
    'impressions': 'sum',
    'position': 'mean'
}).reset_index()
monthly_metrics['date'] = monthly_metrics['date'].astype(str)

fig1 = make_subplots(rows=2, cols=1, vertical_spacing=0.25)

# Gráficos
fig1.add_trace(go.Scatter(x=monthly_metrics['date'], y=monthly_metrics['clicks'],
                          name='Clicks', mode='lines+markers'), row=1, col=1)
fig1.add_trace(go.Scatter(x=monthly_metrics['date'], y=monthly_metrics['impressions'],
                          name='Impressions', mode='lines+markers'), row=1, col=1)
fig1.add_trace(go.Scatter(x=monthly_metrics['date'], y=monthly_metrics['position'],
                          name='Position', mode='lines+markers'), row=2, col=1)

fig1.update_yaxes(autorange="reversed", row=2, col=1)
fig1.update_layout(
    height=700,
    title_text="Monthly Clicks and Impressions Trends",
    title_font_size=24,
    title_y=0.98,  # Altura do título
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40)  # Aumente o espaço superior
)

st.plotly_chart(fig1, use_container_width=True)

# 2. Análise por Categoria
st.header("2. Content Category Analysis")
content_performance = pd.merge(gsc_df, metadata_df[['page', 'Cluster']], 
                             left_on='page', right_on='page', how='left')
cluster_metrics = content_performance.groupby('Cluster').agg({
    'clicks': 'sum',
    'impressions': 'sum',
    'position': 'mean'
}).reset_index()
cluster_metrics['CTR'] = (cluster_metrics['clicks'] / cluster_metrics['impressions']) * 100

fig2 = make_subplots(rows=2, cols=1, vertical_spacing=0.25)

fig2.add_trace(go.Bar(x=cluster_metrics['Cluster'], y=cluster_metrics['clicks'], name='Clicks'), row=1, col=1)
fig2.add_trace(go.Bar(x=cluster_metrics['Cluster'], y=cluster_metrics['impressions'], name='Impressions'), row=1, col=1)
fig2.add_trace(go.Scatter(x=cluster_metrics['Cluster'], y=cluster_metrics['CTR'], name='CTR (%)', mode='lines+markers'), row=2, col=1)
fig2.add_trace(go.Scatter(x=cluster_metrics['Cluster'], y=cluster_metrics['position'], name='Position', mode='lines+markers'), row=2, col=1)

fig2.update_layout(
    height=700,
    title_text="Traffic Metrics by Content Category",
    title_font_size=24,
    title_y=0.98,  # Altura do título
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40)  # Aumente o espaço superior
)

st.plotly_chart(fig2, use_container_width=True)

# 3. Matriz de Correlação
st.header("3. Correlation Analysis")
correlation_matrix = gsc_df[['clicks', 'impressions', 'position']].corr()
fig3 = px.imshow(correlation_matrix, 
                 labels=dict(color="Correlation"),
                 x=correlation_matrix.columns,
                 y=correlation_matrix.columns,
                 color_continuous_scale='RdBu_r')

fig3.update_layout(
    title_text="Correlation Matrix of Clicks, Impressions, and Position",
    title_font_size=24,
    title_y=0.98,  # Altura do título
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40)  # Aumente o espaço superior
)

st.plotly_chart(fig3, use_container_width=True)

# 4. Análise de Sazonalidade
st.header("4. Weekly Patterns")
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

fig4 = make_subplots(rows=1, cols=2, vertical_spacing=0.25)

fig4.add_trace(go.Bar(x=weekday_performance['weekday'], y=weekday_performance['clicks'], name='Clicks'), row=1, col=1)
fig4.add_trace(go.Bar(x=weekday_performance['weekday'], y=weekday_performance['position'], name='Position'), row=1, col=2)

fig4.update_yaxes(range=[0, weekday_performance['clicks'].max() * 1.1], row=1, col=1)
fig4.update_yaxes(range=[0, weekday_performance['position'].max() * 1.1], row=1, col=2)

fig4.update_layout(
    height=400,
    title_text="Average Daily Clicks and Position by Day of the Week",
    title_font_size=24,
    title_y=0.98,  # Altura do título
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40)  # Aumente o espaço superior
)

st.plotly_chart(fig4, use_container_width=True)

# Métricas principais
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Clicks", f"{gsc_df['clicks'].sum():,.0f}")
col2.metric("Total Impressions", f"{gsc_df['impressions'].sum():,.0f}")
col3.metric("Average CTR", f"{(gsc_df['clicks'].sum() / gsc_df['impressions'].sum() * 100):.2f}%")
col4.metric("Average Position", f"{gsc_df['position'].mean():.2f}")

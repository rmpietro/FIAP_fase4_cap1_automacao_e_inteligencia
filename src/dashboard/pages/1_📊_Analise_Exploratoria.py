import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

# Adicionar diretório pai ao PYTHONPATH
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dados.data_analysis import SensorDataAnalyzer

# Função para carregar os dados
@st.cache_data
def load_data():
    farm_tech_analyzer = SensorDataAnalyzer()
    return farm_tech_analyzer.load_data()

# Carregar dados
df = load_data()

st.title("📊 Análise Exploratória dos Dados")

# Análise Univariada
st.header("Análise Univariada")
col1, col2 = st.columns(2)

with col1:
    # Box plots para variáveis numéricas
    fig_box = px.box(df, y=['temp', 'hum', 'pH'],
                     title="Distribuição das Variáveis Numéricas")
    st.plotly_chart(fig_box)

with col2:
    # Histogramas
    fig_hist = px.histogram(df, x='temp', title="Distribuição da Temperatura")
    st.plotly_chart(fig_hist)

# Análise Bivariada
st.header("Análise Bivariada")
col3, col4 = st.columns(2)

with col3:
    # Scatter plot
    fig_scatter = px.scatter(df, x='temp', y='hum',
                             color='estado_irrigacao',
                             title="Temperatura vs Umidade")
    st.plotly_chart(fig_scatter)

with col4:
    # Violin plot
    fig_violin = px.violin(df, y='pH', x='estado_irrigacao',
                           title="Distribuição do pH por Estado de Irrigação")
    st.plotly_chart(fig_violin)

# Análise de Correlação
st.header("Análise de Correlação")
numeric_cols = df[['temp', 'hum', 'pH']].corr()
fig_corr = px.imshow(numeric_cols,
                     title="Mapa de Correlação",
                     color_continuous_scale='RdBu')
st.plotly_chart(fig_corr)

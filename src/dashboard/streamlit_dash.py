
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import json
import sys
import os

# Adicionar o diretório pai ao PATH para importar data_analysis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_analysis import SensorDataAnalyzer

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Monitoramento Agrícola",
    page_icon="🌱",
    layout="wide"
)

# Função para carregar os dados
@st.cache_data
def load_data():
    analyzer = SensorDataAnalyzer('../dados/dados_app.json')
    return analyzer.load_data()

# Carregar dados
df = load_data()

# Sidebar para navegação
page = st.sidebar.selectbox(
    "Escolha uma página",
    ["Análise Exploratória", "Modelo Preditivo"]
)

# Página de Análise Exploratória
if page == "Análise Exploratória":
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

# Página do Modelo Preditivo
elif page == "Modelo Preditivo":
    st.title("🤖 Modelo Preditivo")
    
    # Treinar modelo
    analyzer = SensorDataAnalyzer('../dados/dados_app.json')
    results = analyzer.train_model()
    
    # Métricas do modelo
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Acurácia do Modelo", f"{results['accuracy']:.2%}")
    
    # Feature Importance
    st.header("Importância das Features")
    fig_importance = px.bar(results['feature_importance'],
                          x='feature', y='importance',
                          title="Importância das Features")
    st.plotly_chart(fig_importance)
    
    # Previsões para as próximas 24 horas
    st.header("Previsões para as Próximas 24 Horas")
    predictions = analyzer.predict_next_24h()
    
    # Converter previsões para DataFrame
    pred_df = pd.DataFrame(predictions)
    pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
    
    # Gráfico de probabilidade das previsões
    fig_pred = px.line(pred_df, x='timestamp', y='probabilidade',
                      title="Probabilidade das Previsões",
                      labels={'probabilidade': 'Probabilidade',
                             'timestamp': 'Horário'})
    st.plotly_chart(fig_pred)
    
    # Tabela com as previsões
    st.dataframe(pred_df)

# Adicionar footer
st.markdown("---")
st.markdown("Dashboard desenvolvido para monitoramento agrícola - FIAP")

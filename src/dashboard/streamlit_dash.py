import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import json
from data_analysis import SensorDataAnalyzer

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Análise de Sensores",
    page_icon="🌱",
    layout="wide"
)

# Função para carregar dados
@st.cache_data
def load_data():
    with open('./dados/dados_app.json') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data['leituras'])
    df['estado_irrigacao'] = df['irrigacao'].apply(lambda x: x['estado'])
    df['motivo_irrigacao'] = df['irrigacao'].apply(lambda x: x['motivo'])
    df = df.drop('irrigacao', axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

# Carregando os dados
df = load_data()

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a página:", ["Análise Exploratória", "Modelo Preditivo"])

if page == "Análise Exploratória":
    st.title("📊 Análise Exploratória dos Dados")
    
    # Análise Univariada
    st.header("Análise Univariada")
    
    # Seletor de variável
    col1, col2 = st.columns(2)
    with col1:
        numeric_cols = ['temp', 'hum', 'pH']
        selected_var = st.selectbox("Selecione a variável numérica:", numeric_cols)
        
        # Box Plot
        fig_box = px.box(df, y=selected_var, title=f'Box Plot - {selected_var}')
        st.plotly_chart(fig_box)
        
        # Estatísticas descritivas
        st.write("Estatísticas Descritivas:")
        st.write(df[selected_var].describe())
    
    with col2:
        # Histograma
        fig_hist = px.histogram(df, x=selected_var, 
                              title=f'Histograma - {selected_var}',
                              marginal="rug")
        st.plotly_chart(fig_hist)
    
    # Análise Bivariada
    st.header("Análise Bivariada")
    
    col3, col4 = st.columns(2)
    with col3:
        x_var = st.selectbox("Selecione variável X:", numeric_cols)
        y_var = st.selectbox("Selecione variável Y:", 
                            [col for col in numeric_cols if col != x_var])
        
        # Scatter plot
        fig_scatter = px.scatter(df, x=x_var, y=y_var, 
                               title=f'Scatter Plot - {x_var} vs {y_var}',
                               trendline="ols")
        st.plotly_chart(fig_scatter)
    
    with col4:
        # Violin plot
        fig_violin = px.violin(df, y=y_var, x='estado_irrigacao',
                             title=f'Violin Plot - {y_var} por Estado de Irrigação',
                             box=True)
        st.plotly_chart(fig_violin)
    
    # Análise de Correlação
    st.header("Análise de Correlação")
    
    # Matriz de correlação
    corr_matrix = df[numeric_cols].corr()
    fig_heatmap = px.imshow(corr_matrix,
                           title="Mapa de Calor - Correlações",
                           labels=dict(color="Correlação"))
    st.plotly_chart(fig_heatmap)
    
    # Análise Multivariada
    st.header("Análise Multivariada")
    
    # Scatter matrix
    fig_scatter_matrix = px.scatter_matrix(df[numeric_cols + ['estado_irrigacao']],
                                         dimensions=numeric_cols,
                                         color='estado_irrigacao',
                                         title="Matriz de Dispersão")
    st.plotly_chart(fig_scatter_matrix)

else:  # Página do Modelo Preditivo
    st.title("🤖 Modelo Preditivo")
    
    # Inicializando o analisador
    analyzer = SensorDataAnalyzer('./dados/dados_app.json')
    
    # Treinando o modelo
    with st.spinner('Treinando o modelo...'):
        results = analyzer.train_model()
    
    # Métricas principais
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Acurácia do Modelo", f"{results['accuracy']:.2%}")
    
    # Importância das features
    st.header("Importância das Features")
    fig_importance = px.bar(results['feature_importance'],
                          x='feature', y='importance',
                          title="Importância das Features")
    st.plotly_chart(fig_importance)
    
    # Matriz de Confusão
    st.header("Matriz de Confusão")
    conf_matrix = results['confusion_matrix']
    fig_conf_matrix = px.imshow(conf_matrix,
                               labels=dict(x="Previsto", y="Real"),
                               title="Matriz de Confusão")
    st.plotly_chart(fig_conf_matrix)
    
    # Previsões para as próximas 24 horas
    st.header("Previsões para as Próximas 24 Horas")
    
    predictions = analyzer.predict_next_24h()
    pred_df = pd.DataFrame(predictions)
    pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
    
    fig_predictions = px.line(pred_df,
                            x='timestamp',
                            y='probabilidade',
                            title="Probabilidade de Irrigação nas Próximas 24 Horas")
    st.plotly_chart(fig_predictions)
    
    # Tabela de previsões
    st.dataframe(pred_df)

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Adicionar diretório pai ao PYTHONPATH
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dados.data_analysis import SensorDataAnalyzer

st.title("🤖 Modelo Preditivo")

# Treinar modelo
analyzer = SensorDataAnalyzer(str(Path(__file__).parent.parent.parent / 'dados' / 'dados_app.json'))
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

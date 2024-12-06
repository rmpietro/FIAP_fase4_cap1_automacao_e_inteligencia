import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório pai ao PYTHONPATH
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Monitoramento Agrícola",
    page_icon="🌱",
    layout="wide"
)

# Página inicial
st.title("🌱 Dashboard de Monitoramento Agrícola")

st.markdown("""
Este dashboard fornece análises e previsões para o sistema de monitoramento agrícola.

### Navegação:
- **📊 Análise Exploratória**: Visualize análises detalhadas dos dados dos sensores
- **🤖 Modelo Preditivo**: Explore previsões e métricas do modelo

Use o menu lateral para navegar entre as páginas.
""")

# Footer
st.markdown("---")
st.markdown("Dashboard desenvolvido para monitoramento agrícola - FIAP")

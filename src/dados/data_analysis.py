import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from datetime import datetime, timedelta

class SensorDataAnalyzer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_importance = None
        self.accuracy = None

    # Carrega os dados do JSON e os transforma/normaliza para serem utilizados no modelo
    def load_data(self):
        # Carregando e preparando os dados do arquivo JSON
        with open(self.json_file_path) as f:
            data = json.load(f)
        
        # Converter dados para DataFrame
        df = pd.DataFrame(data['leituras'])
        
        # Extrair estado de irrigação e motivo de irrigação
        # No JSON estão como um único objeto, mas vamos separar em duas colunas no dataframe
        df['estado_irrigacao'] = df['irrigacao'].apply(lambda x: x['estado'])
        df['motivo_irrigacao'] = df['irrigacao'].apply(lambda x: x['motivo'])
        df = df.drop('irrigacao', axis=1)
        
        # Converter timestamp para datetime e extrair dia da semana e hora como características
        # A escolha por essas características foi feita com base no que pensamos, no grupo de alunos, ser a melhor opção para essa análise
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hora'] = df['timestamp'].dt.hour
        df['dia_semana'] = df['timestamp'].dt.dayofweek
        
        # Variáveis categóricas - Aplicando Label Encoding pra transformar em valores numéricos, já que trata-se de um Boolean
        df['P'] = self.label_encoder.fit_transform(df['P'])
        df['K'] = self.label_encoder.fit_transform(df['K'])
        df['target'] = self.label_encoder.fit_transform(df['estado_irrigacao'])
        
        return df
    
    def train_model(self):
        """Treina o modelo Random Forest"""
        df = self.load_data()
        
        # Preparar features e target
        features = ['temp', 'hum', 'P', 'K', 'pH', 'hora', 'dia_semana']
        X = df[features]
        y = df['target']
        
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treinar modelo
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Calcular importância das features e accuracy
        self.feature_importance = pd.DataFrame({
            'feature': features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Avaliar modelo
        y_pred = self.model.predict(X_test)
        self.accuracy = np.mean(y_pred == y_test)
        
        return {
            'accuracy': self.accuracy,
            'feature_importance': self.feature_importance,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
    
    def predict_next_24h(self):
        """Faz previsões para as próximas 24 horas"""
        if self.model is None:
            self.train_model()
            
        # Pegar últimos dados conhecidos
        df = self.load_data()
        last_reading = df.iloc[-1]
        
        # Preparar dados para próximas 24 horas
        next_24h = []
        start_time = pd.to_datetime(last_reading['timestamp'])
        
        for i in range(24):
            next_time = start_time + timedelta(hours=i+1)
            prediction_data = {
                'temp': last_reading['temp'],  # Usando último valor conhecido
                'hum': last_reading['hum'],
                'P': last_reading['P'],
                'K': last_reading['K'],
                'pH': last_reading['pH'],
                'hora': next_time.hour,
                'dia_semana': next_time.dayofweek
            }
            next_24h.append(prediction_data)
        
        # Fazer previsões
        X_pred = pd.DataFrame(next_24h)
        predictions = self.model.predict(X_pred)
        probabilities = self.model.predict_proba(X_pred)
        
        # Preparar resultados
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            time = start_time + timedelta(hours=i+1)
            results.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'previsao': self.label_encoder.inverse_transform([pred])[0],
                'probabilidade': float(max(prob))
            })
            
        return results
    
    def save_model(self, filepath='models/sensor_model.joblib'):
        """Salva o modelo treinado"""
        if self.model is not None:
            joblib.dump(self.model, filepath)
            print(f"Modelo salvo em {filepath}")
        else:
            print("Modelo ainda não foi treinado")
    
    def load_saved_model(self, filepath='models/sensor_model.joblib'):
        """Carrega um modelo salvo"""
        self.model = joblib.load(filepath)
        print(f"Modelo carregado de {filepath}")

def main():
    # Inicializar analisador
    analyzer = SensorDataAnalyzer('src/dados/dados_app.json')
    
    # Treinar modelo e mostrar resultados
    results = analyzer.train_model()
    
    print("\nResultados do Treinamento:")
    print(f"Acurácia: {results['accuracy']:.2f}")
    
    print("\nImportância das Features:")
    print(results['feature_importance'])
    
    print("\nRelatório de Classificação:")
    print(results['classification_report'])
    
    # Fazer previsões para próximas 24 horas
    predictions = analyzer.predict_next_24h()
    
    print("\nPrevisões para próximas 24 horas:")
    for pred in predictions:
        print(f"Horário: {pred['timestamp']}")
        print(f"Previsão: {pred['previsao']}")
        print(f"Probabilidade: {pred['probabilidade']:.2f}")
        print("---")
    
    # Salvar modelo
    analyzer.save_model()

if __name__ == "__main__":
    main()

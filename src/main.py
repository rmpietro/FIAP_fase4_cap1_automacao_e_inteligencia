import oracledb
import json
import requests
import pandas as pd
import subprocess
from dados.data_analysis import main as data_analysis_main
from src.dados.db_crud import create_tipo_cultura, create_area_cultivo, create_sensor, create_leitura

# Conexão ao Oracle com entrada de credenciais
def connect_to_db():
    try:
        with open("config/config.json") as config_file:
            config = json.load(config_file)
        return oracledb.connect(
            user=config['user'],
            password=config['password'],
            dsn=config['dsn']
        )
    except FileNotFoundError:

        print("------Programa de Monitoramento de Culturas------\n")

        username = input("Digite o usuário do banco de dados: ")
        password = input("Digite a senha do banco de dados: ")
        dsn = "oracle.fiap.com.br:1521/ORCL"
        criar_config_json(username, password, dsn)
        return oracledb.connect(user=username, password=password, dsn=dsn)

def criar_config_json(user, password, dsn, filename="config/config.json"):
    config_data = {
        "user": user,
        "password": password,
        "dsn": dsn
    }

    with open(filename, "w") as config_file:
        json.dump(config_data, config_file, indent=2)

    print(f"Arquivo '{filename}' criado com sucesso no diretório src/config.")

# Função para ler o DDL e criar as tabelas no Banco de Dados
def create_tables(connection):
    try:
        # Verifica se as tabelas já existem
        with connection.cursor() as cursor:
            cursor.execute("""SELECT COUNT(*) FROM user_Tables WHERE table_name IN ('AREA_CULTIVO', 'LEITURAS', 'SENSOR', 'TIPO_CULTURA')""")
            if cursor.fetchone()[0] != 0:
                print("\n---> Estrutura de Banco de Dados encontrada e já criada. <---\n\n")
                return

        # Se as tabelas não existem, cria-as usando o script DDL
        ddl_file_path = 'config/script_ddl.sql'
        with open(ddl_file_path, 'r') as ddl_file:
            ddl_commands = ddl_file.read()

        ddl_blocks = ddl_commands.split(';\n')

        with connection.cursor() as cursor:
            for block in ddl_blocks:
                block = block.strip()
                if block:
                    if block.upper().startswith("BEGIN"):
                        block += ";\n/"
                    cursor.execute(block)
                    print(f"Comando executado com sucesso:\n{block}\n")

        connection.commit()
        print("\n--> Todas as tabelas foram criadas com sucesso. <--\n\n")
    except oracledb.Error as e:
        print(f"\nOcorreu um erro ao executar o DDL: {e}\n\n")

# Função para inserir dados a partir do JSON
def insert_data_from_json(connection, json_file_path):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT COUNT(*) FROM LEITURAS
        """)
        if cursor.fetchone()[0] != 0:
            print("\n--> Tabelas aparentemente já estão populadas com pelo menos uma linha. Dados não serão importados. <-- \n\n")
            return

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Inserindo dados na tabela tipo_cultura
    for cultura in data["tipo_cultura"]:
        create_tipo_cultura(connection, cultura["id_cultura"], cultura["nome"], cultura["data_plantio"])

    # Inserindo dados na tabela area_cultivo
    for area in data["area_cultivo"]:
        create_area_cultivo(connection, area["id_area"], area["id_cultura"], area["area_extensao"], area["end_localizacao"])

    # Inserindo dados na tabela sensor
    for sensor in data["sensor"]:
        create_sensor(connection, sensor["id_sensor"], sensor["id_area"], sensor["descricao"], sensor["tipo"], sensor["modelo"])

    # Inserindo dados na tabela leituras
    for leitura in data["leituras"]:
        create_leitura(
            connection,
            leitura["timestamp"],
            leitura["temp"],
            leitura["hum"],  # Corrigido de "humid" para "hum"
            leitura["P"],
            leitura["K"],
            leitura["pH"],
            leitura["irrigacao"]["estado"],
            leitura["irrigacao"]["motivo"],
            1  # Assumindo id_sensor 1 para todas as leituras, ajuste conforme necessário
        )

    print("\n--> Dados inseridos com sucesso a partir do JSON. >-- \n\n")

def get_chuva_previsao():
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': -22.1256,
        'lon': -51.3889,
        'appid': "48380355e6896ab9c1318bc85deca9c3",
        'units': 'metric',
        'cnt': 5  # Limitar a previsão para 5 dias
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extrair dados de chuva e data
    previsao_chuva = []
    for item in data['list']:
        data_hora = item['dt_txt']
        chuva = item.get('rain', {}).get('3h', 0)  # Usa 0 mm se não houver previsão de chuva
        previsao_chuva.append({"Data e Hora": data_hora, "Previsão de Chuva (mm)": chuva})

    # Exibir tabela formatada
    df_chuva = pd.DataFrame(previsao_chuva)
    print("\n\n-------Previsão de Chuva para Presidente Prudente na data de amanhã a cada 3h-------")
    print(df_chuva)
    print("-----------------------------------------------------------------------------\n\n")

# Função principal para uso do script
def main_menu():
    connection = connect_to_db()
    print("\n\nBem-vindo ao Programa de Monitoramento de Culturas - FarmTech!")
    print("-----------------------------------------------------------------------------\n\n")
    while True:
        print("Escolha uma opção:")
        print("-----")
        print("1. Criar tabelas no banco de dados")
        print("2. Inserir dados do JSON no banco de dados")
        print("3. Iniciar o dashboard criado com a biblioteca Dash")
        print("4. Iniciar o dashboard criado com a biblioteca Streamlit")
        print("5. Obter previsão de chuva para a cidade de Presidente Prudente (3/3h)")
        print("6. Obter dados de modelo preditivo para as leituras de sensores feitas")
        print("7. Sair")
        print("-----")
        
        choice = input("Digite o número da opção desejada:")

        if choice == "1":
            create_tables(connection)
        elif choice == "2":
            json_file_path = 'dados/dados_app.json'
            insert_data_from_json(connection, json_file_path)
        elif choice == "3":
            from dashboard.dashboard_dash import app as dashboard_app
            dashboard_app.run_server(debug=False)
        elif choice == "4":
            print("Iniciando o dashboard Streamlit...")
            try:
                subprocess.run(["streamlit", "run", "dashboard/Dashboard_Inicial.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erro ao iniciar o Streamlit: {e}")
            except FileNotFoundError:
                print("Erro: Streamlit não encontrado. Certifique-se de que o Streamlit está instalado.")
        elif choice == "5":
            get_chuva_previsao()
        elif choice == "6":
            print("\nExecutando análise preditiva dos dados...")
            data_analysis_main()
        elif choice == "7":
            print("Encerrando o programa...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

    # Fecha a conexão
    connection.close()

if __name__ == "__main__":
    main_menu()



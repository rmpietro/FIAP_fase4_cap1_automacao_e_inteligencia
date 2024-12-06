# READ - Ler dados de uma tabela
def read_table(connection, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

# Funções para a tabela 'TIPO_CULTURA'
def create_tipo_cultura(connection, id_cultura, nome, data_plantio):
    with connection.cursor() as cursor:
        query = """
            INSERT INTO tipo_cultura (id_cultura, nome, data_plantio)
            VALUES (:id_cultura, :nome, TO_DATE(:data_plantio, 'YYYY-MM-DD'))
        """
        cursor.execute(query, [id_cultura, nome, data_plantio])
        connection.commit()
        print("Tipo de cultura criado com sucesso.")

def update_tipo_cultura(connection, id_cultura, **kwargs):
    with connection.cursor() as cursor:
        query = "UPDATE tipo_cultura SET "
        query += ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
        query += " WHERE id_cultura = :id_cultura"
        kwargs['id_cultura'] = id_cultura
        cursor.execute(query, kwargs)
        connection.commit()
        print("Tipo de cultura atualizado com sucesso.")

def delete_tipo_cultura(connection, id_cultura):
    with connection.cursor() as cursor:
        query = "DELETE FROM tipo_cultura WHERE id_cultura = :id_cultura"
        cursor.execute(query, [id_cultura])
        connection.commit()
        print("Tipo de cultura deletado com sucesso.")

# Funções para a tabela 'AREA_CULTIVO'
def create_area_cultivo(connection, id_area, id_cultura, area_extensao, end_localizacao):
    with connection.cursor() as cursor:
        query = """
            INSERT INTO area_cultivo (id_area, id_cultura, area_extensao, end_localizacao)
            VALUES (:id_area, :id_cultura, :area_extensao, :end_localizacao)
        """
        cursor.execute(query, [id_area, id_cultura, area_extensao, end_localizacao])
        connection.commit()
        print("Área de cultivo criada com sucesso.")

def update_area_cultivo(connection, id_area, **kwargs):
    with connection.cursor() as cursor:
        query = "UPDATE area_cultivo SET "
        query += ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
        query += " WHERE id_area = :id_area"
        kwargs['id_area'] = id_area
        cursor.execute(query, kwargs)
        connection.commit()
        print("Área de cultivo atualizada com sucesso.")

def delete_area_cultivo(connection, id_area):
    with connection.cursor() as cursor:
        query = "DELETE FROM area_cultivo WHERE id_area = :id_area"
        cursor.execute(query, [id_area])
        connection.commit()
        print("Área de cultivo deletada com sucesso.")

# Funções para a tabela 'SENSOR'
def create_sensor(connection, id_sensor, id_area, descricao, tipo, modelo):
    with connection.cursor() as cursor:
        query = """
            INSERT INTO sensor (id_sensor, id_area, descricao, tipo, modelo)
            VALUES (:id_sensor, :id_area, :descricao, :tipo, :modelo)
        """
        cursor.execute(query, [id_sensor, id_area, descricao, tipo, modelo])
        connection.commit()
        print("Sensor criado com sucesso.")

def update_sensor(connection, id_sensor, **kwargs):
    with connection.cursor() as cursor:
        query = "UPDATE sensor SET "
        query += ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
        query += " WHERE id_sensor = :id_sensor"
        kwargs['id_sensor'] = id_sensor
        cursor.execute(query, kwargs)
        connection.commit()
        print("Sensor atualizado com sucesso.")

def delete_sensor(connection, id_sensor):
    with connection.cursor() as cursor:
        query = "DELETE FROM sensor WHERE id_sensor = :id_sensor"
        cursor.execute(query, [id_sensor])
        connection.commit()
        print("Sensor deletado com sucesso.")

# Funções para a tabela 'LEITURAS'
def create_leitura(connection, timestamp, temp, humid, p, k, ph, estado_irrigacao, motivo_irrigacao, id_sensor):
    with connection.cursor() as cursor:
        query = """
            INSERT INTO leituras (timestamp, temp, humid, P, K, pH, estado_irrigacao, motivo_irrigacao, id_sensor)
            VALUES (TO_TIMESTAMP(:timestamp, 'YYYY-MM-DD"T"HH24:MI:SS'), :temp, :humid, :p, :k, :ph, :estado_irrigacao, :motivo_irrigacao, :id_sensor)
        """
        cursor.execute(query, [timestamp, temp, humid, p, k, ph, estado_irrigacao, motivo_irrigacao, id_sensor])
        connection.commit()
        print("Leitura criada com sucesso.")

def update_leitura(connection, id_leitura, **kwargs):
    with connection.cursor() as cursor:
        query = "UPDATE leituras SET "
        query += ", ".join([f"{key} = :{key}" for key in kwargs.keys()])
        query += " WHERE id_leitura = :id_leitura"
        kwargs['id_leitura'] = id_leitura
        cursor.execute(query, kwargs)
        connection.commit()
        print("Leitura atualizada com sucesso.")

def delete_leitura(connection, id_leitura):
    with connection.cursor() as cursor:
        query = "DELETE FROM leituras WHERE id_leitura = :id_leitura"
        cursor.execute(query, [id_leitura])
        connection.commit()
        print("Leitura deletada com sucesso.")
import psycopg2
from sqlalchemy import create_engine
connection = psycopg2.connect(database_url="postgresql://postgres:lyV0fDeA4LX8EyD9yULa@containers-us-west-203.railway.app:6039/railway")
connection.open()

# Ejecuta una consulta
cursor = connection.cursor()
result = cursor.execute('SELECT * FROM cliente')
rows = result.fetchall()
result.close()

# Cierra la conexión
connection.close()
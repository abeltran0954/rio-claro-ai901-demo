import pandas as pd
import sqlite3

# Conectar a la base de datos maestra
conn = sqlite3.connect('rioclaro_master.db')

# Extraer la tabla completa de productos
df_productos = pd.read_sql_query("SELECT * FROM productos", conn)

# Guardar en un archivo CSV
nombre_archivo = "productos_unificados_maestro.csv"
df_productos.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')

print(f"✅ Archivo '{nombre_archivo}' generado con éxito. Contiene {len(df_productos)} registros.")

conn.close()
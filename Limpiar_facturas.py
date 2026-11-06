import sqlite3

conn = sqlite3.connect('rioclaro_master.db')
cursor = conn.cursor()

# 1. Borrar todos los registros de pruebas anteriores en ambas tablas
cursor.execute('DELETE FROM facturas')
cursor.execute('DELETE FROM recepciones_bodega')

# 2. Reiniciar los contadores de IDs para que vuelvan a ser la #1
try:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='facturas'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='recepciones_bodega'")
except sqlite3.OperationalError:
    pass # Ignoramos si la secuencia no existe aún

conn.commit()
conn.close()

print("✅ Tablas de 'facturas' y 'recepciones_bodega' vaciadas exitosamente. Listas para el flujo de pruebas desde cero.")
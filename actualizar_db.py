import sqlite3

conn = sqlite3.connect('rioclaro_master.db')
cursor = conn.cursor()

print("Iniciando actualización de la base de datos...")

# 1. Agregar columnas a facturas (manejando excepciones si ya existen)
try:
    cursor.execute("ALTER TABLE facturas ADD COLUMN sucursal TEXT")
    print("✅ Columna 'sucursal' agregada a facturas.")
except Exception as e:
    print(f"Aviso sobre 'sucursal': {e}")

try:
    cursor.execute("ALTER TABLE facturas ADD COLUMN orden_compra TEXT")
    print("✅ Columna 'orden_compra' agregada a facturas.")
except Exception as e:
    print(f"Aviso sobre 'orden_compra': {e}")

# 2. Crear tabla de acuses de recibo para el SoD (Inventario vs Pagos)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS recepciones_bodega (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio_factura TEXT, proveedor TEXT, sucursal TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ Tabla 'recepciones_bodega' creada/verificada con éxito.")

conn.commit()
conn.close()
print("Base de datos lista para el nuevo flujo.")
import sqlite3
import pandas as pd
import sys
import os

def cargar_ventas_desde_csv(csv_path='facturas_ventas.csv', db_path='rioclaro_master.db'):
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_path}")
        sys.exit(1)

    try:
        # 1. Leer el CSV
        print(f"Leyendo archivo: {csv_path}...")
        df_ventas = pd.read_csv(csv_path)

        # 2. Validar columnas esperadas
        columnas_esperadas = ['cliente', 'fecha', 'total', 'subtotal', 'iva', 'folio', 'sucursal']
        columnas_faltantes = [col for col in columnas_esperadas if col not in df_ventas.columns]

        if columnas_faltantes:
            print(f"Error: El archivo CSV no tiene las columnas requeridas: {columnas_faltantes}")
            print(f"Columnas detectadas: {list(df_ventas.columns)}")
            sys.exit(1)

        # 3. Normalizar la columna sucursal para quitar acentos y estandarizar
        print("Normalizando nombres de sucursales (removiendo acentos)...")
        if 'sucursal' in df_ventas.columns:
            df_ventas['sucursal'] = (
                df_ventas['sucursal']
                .astype(str)
                .str.strip()
                .str.title()
                .str.replace('Á', 'A')
                .str.replace('É', 'E')
                .str.replace('Í', 'I')
                .str.replace('Ó', 'O')
                .str.replace('Ú', 'U')
                .str.replace('á', 'a')
                .str.replace('é', 'e')
                .str.replace('í', 'i')
                .str.replace('ó', 'o')
                .str.replace('ú', 'u')
            )

        # 4. Conectar a la base de datos unificada rioclaro_master.db
        print(f"Conectando a la base de datos: {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 5. Asegurar que la tabla existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                fecha TEXT,
                total REAL,
                subtotal REAL,
                iva REAL,
                folio TEXT,
                sucursal TEXT
            )
        ''')

        # 6. Insertar los datos
        print(f"Insertando {len(df_ventas)} registros normalizados en la tabla 'facturas_ventas'...")
        df_ventas.to_sql('facturas_ventas', conn, if_exists='append', index=False)

        conn.commit()
        print("✅ ¡Carga masiva completada con éxito!")

        # 7. Mostrar un resumen de lo cargado
        cursor.execute("SELECT sucursal, count(*) as cantidad, sum(total) as total_ventas FROM facturas_ventas GROUP BY sucursal")
        resumen = cursor.fetchall()
        print("\nResumen de ventas cargadas por sucursal:")
        for fila in resumen:
            print(f" - {fila[0]}: {fila[1]} facturas (Total: ${fila[2]:,.2f})")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    archivo_csv = sys.argv[1] if len(sys.argv) > 1 else 'facturas_ventas.csv'
    cargar_ventas_desde_csv(archivo_csv, db_path='rioclaro_master.db')
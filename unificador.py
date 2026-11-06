import pandas as pd
import sqlite3
import os
import json
import glob
from openai import AzureOpenAI
from dotenv import load_dotenv

# 1. Cargar configuración de Foundry
load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# 2. Conectar a la Base de Datos Maestra
conn = sqlite3.connect('rioclaro_master.db')

def obtener_columna_estricta(columnas, palabras_primarias, palabras_secundarias, default_index):
    """Busca coincidencias priorizando descripciones reales sobre códigos."""
    for col in columnas:
        if any(kw in str(col).lower() for kw in palabras_primarias):
            return col

    for col in columnas:
        if any(kw in str(col).lower() for kw in palabras_secundarias):
            return col

    return columnas[default_index] if len(columnas) > default_index else columnas[-1]

def generar_reporte_unificacion(df_total):
    """Genera un archivo Markdown con el reporte ejecutivo y la tabla de homologación."""
    total_registros = len(df_total)
    nombres_originales = df_total['Nombre_Original'].nunique()
    nombres_estandar = df_total['Nombre_Estandar'].nunique()
    reduccion_dispersion = round((1 - (nombres_estandar / nombres_originales)) * 100, 2) if nombres_originales > 0 else 0

    # Resumen de mapeo único agrupado
    mapeo_df = df_total[['Nombre_Original', 'Nombre_Estandar', 'Sucursal']].drop_duplicates()
    mapeo_df = mapeo_df.sort_values(by=['Nombre_Estandar', 'Sucursal'])

    lineas_tabla = [
        "| Nombre Original en Sucursal | Sucursal Origen | Nombre Estándar Consolidado (IA) |",
        "| :--- | :--- | :--- |"
    ]
    for _, row in mapeo_df.iterrows():
        lineas_tabla.append(f"| {row['Nombre_Original']} | {row['Sucursal']} | **{row['Nombre_Estandar']}** |")
    tabla_markdown = "\n".join(lineas_tabla)

    contenido_reporte = f"""# 📊 Reporte Ejecutivo: Homologación de Catálogo Maestro
**Distribuidora Río Claro (Sinaloa)**
**Módulo:** Unificación Inteligente de Datos con Azure OpenAI (`gpt-4.1-mini`)

---

## 1. Resumen de Métricas Clave
* **Total de registros procesados:** {total_registros} productos en 5 sucursales.
* **Variantes de nombres detectadas:** {nombres_originales} descripciones heterogéneas.
* **Catálogo maestro resultante:** {nombres_estandar} productos únicos estandarizados.
* **Reducción de dispersión / duplicidad:** `{reduccion_dispersion}%` de optimización.

---

## 2. Tabla Detallada de Homologación de Productos
A continuación se presenta la trazabilidad del mapeo semántico aplicado para corregir inconsistencias entre sucursales (ej. Cloro 1L, CLORO LITRO, Blanqueador):

{tabla_markdown}

---
*Reporte autogenerado por el motor de limpieza de datos de Río Claro IA.*
"""

    with open("reporte_unificacion_productos.md", "w", encoding="utf-8") as f:
        f.write(contenido_reporte)

    print("📄 Archivo 'reporte_unificacion_productos.md' generado con éxito para presentación y documentación.")

def unificar_catalogos():
    print("Iniciando consolidación de catálogos de productos...")

    archivos_prod = glob.glob("catalogo_suc_*_v3.csv")
    if not archivos_prod:
        print("No se encontraron archivos catalogo_suc_*.csv")
        return

    df_list = []
    kw_nombre_pri = ['descripci', 'nombre', 'producto']
    kw_nombre_sec = ['art', 'item']
    kw_precio = ['precio', 'costo', 'valor', 'price', 'monto']
    kw_stock = ['stock', 'exist', 'cant', 'inv', 'piezas', 'unid', 'disp', 'qty']

    for archivo in archivos_prod:
        sucursal = archivo.split('_')[2].capitalize()
        if sucursal.lower() == "los":
             sucursal = "Los Mochis"

        df = pd.read_csv(archivo)
        df['Sucursal'] = sucursal

        col_nombre = obtener_columna_estricta(df.columns, kw_nombre_pri, kw_nombre_sec, 0)
        col_precio = obtener_columna_estricta(df.columns, kw_precio, [], 1)
        col_stock = obtener_columna_estricta(df.columns, kw_stock, [], 2)

        print(f"[{sucursal}] Mapeando columnas -> Nombre: '{col_nombre}', Precio: '{col_precio}', Stock: '{col_stock}'")

        df = df.rename(columns={col_nombre: 'Nombre_Original', col_precio: 'Precio', col_stock: 'Stock'})
        df_list.append(df[['Nombre_Original', 'Precio', 'Stock', 'Sucursal']])

    df_total = pd.concat(df_list, ignore_index=True)

    nombres_unicos = df_total['Nombre_Original'].unique().tolist()
    print(f"\nSe encontraron {len(nombres_unicos)} nombres distintos de productos. Pidiendo a la IA que estandarice...")

    prompt = f"""
    Eres un experto en limpieza de datos maestros. Aquí tienes una lista de descripciones de productos que vienen de distintas sucursales.
    Agrupa los que son el mismo producto (ej. 'Cloro 1L', 'CLORO LITRO', 'Blanqueador 1000ml') y asígnales un 'Nombre_Estandar' único y profesional.
    Si encuentras códigos alfanuméricos puros en lugar de descripciones, ignóralos y devuelve su mismo valor.
    Devuelve ÚNICAMENTE un objeto JSON donde la clave sea el 'Nombre_Original' y el valor sea el 'Nombre_Estandar'.

    Lista de productos: {json.dumps(nombres_unicos)}
    """

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        respuesta_texto = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        diccionario_estandar = json.loads(respuesta_texto)

        df_total['Nombre_Estandar'] = df_total['Nombre_Original'].map(diccionario_estandar).fillna(df_total['Nombre_Original'])

        # Guardar en SQLite
        df_total.to_sql('productos', conn, if_exists='replace', index=False)
        print("✅ Catálogo de productos unificado y guardado en SQLite con éxito.")

        # Generar Reporte Markdown
        generar_reporte_unificacion(df_total)

    except Exception as e:
        print(f"❌ Error al conectar con Azure OpenAI: {e}")

def consolidar_clientes():
    print("Iniciando consolidación de base de clientes...")
    archivos_clientes = glob.glob("clientes_suc_*_v5.csv")

    df_list = []
    for archivo in archivos_clientes:
        sucursal = archivo.split('_')[2].capitalize()
        if sucursal.lower() == "los":
             sucursal = "Los Mochis"

        df = pd.read_csv(archivo)
        df['Sucursal'] = sucursal
        df_list.append(df)

    if df_list:
        df_clientes = pd.concat(df_list, ignore_index=True)
        df_clientes.to_sql('clientes', conn, if_exists='replace', index=False)
        print("✅ Base de clientes unificada y guardada en SQLite con éxito.\n")

if __name__ == "__main__":
    unificar_catalogos()
    consolidar_clientes()
    conn.close()
    print("🚀 Proceso finalizado. Catálogos y reportes listos.")
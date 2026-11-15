import os
from db_config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
import numpy as np
import pandas as pd
import pymysql


def cargar_tablas_a_mysql():
    print("=== INICIANDO CARGA DIRECTA A MYSQL SERVER (PYMYSQL PURO) ===\n")

    # 1. Conectar directamente al servidor MySQL
    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=int(DB_PORT),
        database=DB_NAME,
    )
    cursor = conexion.cursor()

    ruta_proc = os.path.join("data", "processed")
    df_customers = pd.read_csv(os.path.join(ruta_proc, "dim_customers.csv"))
    df_products = pd.read_csv(os.path.join(ruta_proc, "dim_products.csv"))
    df_orders = pd.read_csv(
        os.path.join(ruta_proc, "fact_orders_financials.csv")
    )

    # 2. CREAR E INYECTAR TABLA: dim_customers
    cursor.execute("DROP TABLE IF EXISTS dim_customers;")
    cursor.execute("""
        CREATE TABLE dim_customers (
            customer_id VARCHAR(20) PRIMARY KEY,
            region VARCHAR(50),
            acquisition_channel VARCHAR(50)
        );
    """)
    sql_cust = "INSERT INTO dim_customers (customer_id, region, acquisition_channel) VALUES (%s, %s, %s)"
    cursor.executemany(sql_cust, df_customers.values.tolist())
    print(f"✔ Tabla 'dim_customers' cargada ({len(df_customers)} filas).")

    # 3. CREAR E INYECTAR TABLA: dim_products
    cursor.execute("DROP TABLE IF EXISTS dim_products;")
    cursor.execute("""
        CREATE TABLE dim_products (
            product_id VARCHAR(20) PRIMARY KEY,
            product_name VARCHAR(100),
            category VARCHAR(50),
            unit_cost_usd DECIMAL(10,2),
            list_price_usd DECIMAL(10,2)
        );
    """)
    sql_prod = "INSERT INTO dim_products VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql_prod, df_products.values.tolist())
    print(f"✔ Tabla 'dim_products' cargada ({len(df_products)} filas).")

    # 4. CREAR E INYECTAR TABLA: fact_orders
    cursor.execute("DROP TABLE IF EXISTS fact_orders;")
    cursor.execute("""
        CREATE TABLE fact_orders (
            order_id VARCHAR(20) PRIMARY KEY,
            order_date DATE,
            customer_id VARCHAR(20),
            product_id VARCHAR(20),
            quantity INT,
            discount_pct DECIMAL(5,2),
            shipping_cost_usd DECIMAL(10,2),
            order_status VARCHAR(20),
            product_name VARCHAR(100),
            category VARCHAR(50),
            unit_cost_usd DECIMAL(10,2),
            list_price_usd DECIMAL(10,2),
            region VARCHAR(50),
            acquisition_channel VARCHAR(50),
            gross_revenue_usd DECIMAL(12,2),
            discount_amount_usd DECIMAL(12,2),
            net_revenue_usd DECIMAL(12,2),
            cogs_usd DECIMAL(12,2),
            net_profit_usd DECIMAL(12,2)
        );
    """)
    columnas_coma = ", ".join(df_orders.columns)
    placeholders = ", ".join(["%s"] * len(df_orders.columns))
    sql_ord = f"INSERT INTO fact_orders ({columnas_coma}) VALUES ({placeholders})"
    cursor.executemany(sql_ord, df_orders.values.tolist())
    print(f"✔ Tabla 'fact_orders' cargada ({len(df_orders)} filas).")

    # Confirmar cambios y cerrar conexión
    conexion.commit()
    cursor.close()
    conexion.close()
    print(
        "\n✅ ¡Inyección completada! Ya podés consultar las tablas en MySQL Workbench."
    )


if __name__ == "__main__":
    cargar_tablas_a_mysql()
import os
import numpy as np
import pandas as pd


def ejecutar_pipeline_financiero():
    print("=== INICIANDO PIPELINE ETL FINANCIERO (MERCATRONICS LATAM) ===\n")

    # 1. CARGA DE LAS 3 TABLAS CRUDAS (EXTRACCIÓN)
    ruta_raw = os.path.join("data", "raw")
    df_orders = pd.read_csv(os.path.join(ruta_raw, "raw_orders.csv"))
    df_products = pd.read_csv(os.path.join(ruta_raw, "raw_products.csv"))
    df_customers = pd.read_csv(os.path.join(ruta_raw, "raw_customers.csv"))

    print(
        f"1. Tablas cargadas -> Órdenes: {len(df_orders)} | Productos: {len(df_products)} | Clientes: {len(df_customers)}"
    )

    # 2. LIMPIEZA DE NULOS Y FORMATO DE FECHAS (TRANSFORMACIÓN I)
    # Convertir order_date de texto a fecha real
    df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

    # Rellenar envíos nulos (promociones de envío gratis) con $0.0
    nulos_envio = df_orders["shipping_cost_usd"].isnull().sum()
    df_orders["shipping_cost_usd"] = df_orders["shipping_cost_usd"].fillna(0.0)

    # Rellenar canal de adquisición nulo en clientes con 'Direct / Unknown'
    nulos_canal = df_customers["acquisition_channel"].isnull().sum()
    df_customers["acquisition_channel"] = df_customers[
        "acquisition_channel"
    ].fillna("Direct / Unknown")

    print(
        f"2. Nulos auditados y corregidos -> Envíos gratis ($0): {nulos_envio} | Canales sin atribuir: {nulos_canal}"
    )

    # 3. CRUCE RELACIONAL DE LAS 3 TABLAS (LEFT JOINS)
    # Primero unimos Órdenes con Productos usando product_id
    df_master = pd.merge(df_orders, df_products, on="product_id", how="left")
    # Luego unimos el resultado con Clientes usando customer_id
    df_master = pd.merge(df_master, df_customers, on="customer_id", how="left")

    # 4. INGENIERÍA DE VARIABLES FINANCIERAS (UNIT ECONOMICS)
    # Cálculos base teóricos de la orden
    df_master["gross_revenue_usd"] = (
        df_master["quantity"] * df_master["list_price_usd"]
    )
    df_master["discount_amount_usd"] = np.round(
        df_master["gross_revenue_usd"] * df_master["discount_pct"], 2
    )

    # Aplicamos la regla de auditoría según order_status (Completed vs Returned/Canceled)
    # Si la orden NO está 'Completed', el ingreso neto y el costo de mercadería (COGS) son $0
    es_completada = df_master["order_status"] == "Completed"
    es_cancelada = df_master["order_status"] == "Canceled"

    df_master["net_revenue_usd"] = np.where(
        es_completada,
        df_master["gross_revenue_usd"] - df_master["discount_amount_usd"],
        0.0,
    )

    df_master["cogs_usd"] = np.where(
        es_completada, df_master["quantity"] * df_master["unit_cost_usd"], 0.0
    )

    # Si fue 'Canceled' antes de salir, no se pagó flete ($0). Si fue 'Completed' o 'Returned', el flete sí se pagó.
    df_master["shipping_cost_usd"] = np.where(
        es_cancelada, 0.0, df_master["shipping_cost_usd"]
    )

    # Ganancia Neta (Net Profit) = Ingreso Neto - Costo de Producto (COGS) - Costo de Envío
    df_master["net_profit_usd"] = np.round(
        df_master["net_revenue_usd"]
        - df_master["cogs_usd"]
        - df_master["shipping_cost_usd"],
        2,
    )

    # 5. EXPORTACIÓN DE DATOS PROCESADOS (CARGA)
    ruta_proc = os.path.join("data", "processed")
    os.makedirs(ruta_proc, exist_ok=True)

    # Guardamos las tablas limpias para MySQL, Power BI y Excel
    df_customers.to_csv(
        os.path.join(ruta_proc, "dim_customers.csv"), index=False
    )
    df_products.to_csv(os.path.join(ruta_proc, "dim_products.csv"), index=False)
    df_master.to_csv(
        os.path.join(ruta_proc, "fact_orders_financials.csv"), index=False
    )

    # Resumen Ejecutivo en Consola
    print("\n=== RESUMEN DEL ESTADO DE RESULTADOS (P&L) ===")
    print(
        f"Facturación Bruta (Gross Revenue): ${df_master['gross_revenue_usd'].sum():,.2f} USD"
    )
    print(
        f"Ingresos Netos (Net Revenue):      ${df_master['net_revenue_usd'].sum():,.2f} USD"
    )
    print(
        f"Costo de Mercadería (COGS):        ${df_master['cogs_usd'].sum():,.2f} USD"
    )
    print(
        f"Costo Logístico (Shipping):        ${df_master['shipping_cost_usd'].sum():,.2f} USD"
    )
    print(
        f"Ganancia Neta Real (Net Profit):   ${df_master['net_profit_usd'].sum():,.2f} USD"
    )
    print(
        "\n✅ Archivos limpios guardados exitosamente en data/processed/ listos para MySQL."
    )


if __name__ == "__main__":
    ejecutar_pipeline_financiero()
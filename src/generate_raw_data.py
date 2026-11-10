import os
import numpy as np
import pandas as pd


def generar_datos_erp():
    print("=== EXTRAYENDO DATOS CRUDOS DEL ERP (MERCATRONICS LATAM) ===")
    np.random.seed(101)
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)

    # 1. TABLA DE PRODUCTOS (Catálogo con Costos Unitarios y Precios de Lista en USD)
    productos = pd.DataFrame({
        "product_id": [
            "P-101",
            "P-102",
            "P-103",
            "P-104",
            "P-105",
            "P-106",
            "P-107",
            "P-108",
        ],
        "product_name": [
            "Monitor Gamer 27 4K",
            "Teclado Mecanico RGB",
            "Mouse Inalambrico Pro",
            "Notebook Workstation 16GB",
            "Auriculares Noise Cancelling",
            "Silla Ergonomica Corporativa",
            "Disco SSD NVMe 1TB",
            "Webcam Full HD Streaming",
        ],
        "category": [
            "Monitores",
            "Perifericos",
            "Perifericos",
            "Computadoras",
            "Audio",
            "Mobiliario",
            "Almacenamiento",
            "Perifericos",
        ],
        "unit_cost_usd": [
            210.0,
            45.0,
            25.0,
            680.0,
            85.0,
            140.0,
            52.0,
            30.0,
        ],  # Lo que nos cuesta fabricarlo/comprarlo
        "list_price_usd": [
            350.0,
            85.0,
            50.0,
            1050.0,
            160.0,
            260.0,
            95.0,
            65.0,
        ],  # Precio de venta al público
    })
    productos.to_csv(os.path.join("data", "raw", "raw_products.csv"), index=False)

    # 2. TABLA DE CLIENTES (2,000 clientes registrados)
    n_clientes = 2000
    clientes = pd.DataFrame({
        "customer_id": [f"CUST-{i:04d}" for i in range(1, n_clientes + 1)],
        "region": np.random.choice(
            ["Norte", "Centro", "Sur", "Patagonia"],
            size=n_clientes,
            p=[0.25, 0.45, 0.20, 0.10],
        ),
        "acquisition_channel": np.random.choice(
            ["Organic Search", "Paid Ads", "Referral", "Social Media", None],
            size=n_clientes,
            p=[0.30, 0.35, 0.15, 0.15, 0.05],
        ),
    })
    clientes.to_csv(os.path.join("data", "raw", "raw_customers.csv"), index=False)

    # 3. TABLA DE ÓRDENES TRANSACCIONALES (10,000 ventas entre 2024 y 2025)
    n_ordenes = 10000
    fechas = pd.date_range(start="2024-01-01", end="2025-12-31", freq="D")

    ordenes = pd.DataFrame({
        "order_id": [f"ORD-{i:05d}" for i in range(1, n_ordenes + 1)],
        "order_date": np.random.choice(fechas, size=n_ordenes),
        "customer_id": np.random.choice(clientes["customer_id"], size=n_ordenes),
        "product_id": np.random.choice(
            productos["product_id"],
            size=n_ordenes,
            p=[0.12, 0.18, 0.20, 0.08, 0.12, 0.07, 0.13, 0.10],
        ),
        "quantity": np.random.choice(
            [1, 2, 3, 4, 5], size=n_ordenes, p=[0.60, 0.22, 0.10, 0.05, 0.03]
        ),
        "discount_pct": np.random.choice(
            [0.0, 0.05, 0.10, 0.15, 0.25, 0.35],
            size=n_ordenes,
            p=[0.40, 0.20, 0.15, 0.10, 0.10, 0.05],
        ),
        "shipping_cost_usd": np.round(np.random.uniform(5.0, 35.0, size=n_ordenes), 2),
        "order_status": np.random.choice(
            ["Completed", "Returned", "Canceled"],
            size=n_ordenes,
            p=[0.86, 0.09, 0.05],
        ),
    })

    # Introducir imperfecciones del mundo real (envíos gratis como NaN y filas duplicadas de sistema)
    mask_nulos = np.random.rand(n_ordenes) < 0.08
    ordenes.loc[mask_nulos, "shipping_cost_usd"] = np.nan
    ordenes.to_csv(os.path.join("data", "raw", "raw_orders.csv"), index=False)

    print(
        f"✅ Extracción completada: {len(productos)} productos, {len(clientes)} clientes y {len(ordenes)} órdenes guardadas en data/raw/."
    )


if __name__ == "__main__":
    generar_datos_erp()
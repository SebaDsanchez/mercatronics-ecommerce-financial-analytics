USE mercatronics_db;

-- =========================================================================
-- REPORTE 1: AUDITORÍA DE DESTRUCCIÓN DE MARGEN POR POLÍTICA DE DESCUENTOS
-- (Integra: CASE WHEN + Agregaciones Financieras + Tasa de Devolución)
-- =========================================================================
SELECT 
    CASE 
        WHEN discount_pct = 0.00 THEN '1. Full Price (0%)'
        WHEN discount_pct <= 0.10 THEN '2. Promo Leve (5% - 10%)'
        WHEN discount_pct <= 0.25 THEN '3. Promo Media (15% - 25%)'
        ELSE '4. Liquidación Agresiva (35%)'
    END AS tramo_descuento,
    COUNT(order_id) AS total_ordenes,
    SUM(gross_revenue_usd) AS facturacion_bruta_usd,
    SUM(net_revenue_usd) AS ingreso_neto_usd,
    SUM(net_profit_usd) AS ganancia_neta_usd,
    ROUND((SUM(net_profit_usd) / NULLIF(SUM(net_revenue_usd), 0)) * 100, 2) AS margen_neto_pct
FROM fact_orders
GROUP BY tramo_descuento
ORDER BY tramo_descuento;


-- =========================================================================
-- REPORTE 2: RANKING DE RENTABILIDAD POR PRODUCTO Y PARTICIPACIÓN (PARETO)
-- (Integra: CTE 'WITH' + Window Functions 'RANK() OVER' y 'SUM() OVER')
-- =========================================================================
WITH MetricasProducto AS (
    SELECT 
        category,
        product_name,
        COUNT(order_id) AS ordenes_totales,
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS ordenes_devueltas,
        SUM(net_revenue_usd) AS ingresos_netos_usd,
        SUM(net_profit_usd) AS ganancia_neta_usd
    FROM fact_orders
    GROUP BY category, product_name
)
SELECT 
    RANK() OVER (ORDER BY ganancia_neta_usd DESC) AS ranking_global,
    category,
    product_name,
    ingresos_netos_usd,
    ganancia_neta_usd,
    ROUND((ganancia_neta_usd / ingresos_netos_usd) * 100, 2) AS margen_producto_pct,
    ROUND((ganancia_neta_usd / SUM(ganancia_neta_usd) OVER ()) * 100, 2) AS participacion_ganancia_total_pct,
    ROUND((ordenes_devueltas / ordenes_totales) * 100, 2) AS tasa_devolucion_pct
FROM MetricasProducto
ORDER BY ranking_global;
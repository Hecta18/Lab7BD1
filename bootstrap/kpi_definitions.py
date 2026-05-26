"""Definiciones de KPIs: SQL nativo, visualización y documentación para el informe."""

TAB_DESEMPENO = "Desempeño y Crecimiento"
TAB_EXPANSION = "Expansión y Oportunidades"

KPIS = [
    {
        "tab": TAB_DESEMPENO,
        "name": "Ventas totales (GMV) por mes",
        "display": "line",
        "business": "Ingresos brutos mensuales generados por pedidos completados (GMV).",
        "importance": "Permite evaluar la tendencia global del negocio y la velocidad de crecimiento para decisiones directivas.",
        "viz_why": "Gráfico de línea: muestra evolución temporal y facilita detectar estacionalidad o desaceleración.",
        "sql": """
SELECT
  DATE_TRUNC('month', p.fecha)::date AS mes,
  ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))::numeric, 2) AS ventas_totales
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY 1
ORDER BY 1;
""".strip(),
    },
    {
        "tab": TAB_DESEMPENO,
        "name": "Ventas por canal y mes",
        "display": "line",
        "business": "Desglose mensual de ventas entre canal tienda física y canal online.",
        "importance": "Orienta la estrategia omnicanal y la asignación de inversión entre canales.",
        "viz_why": "Líneas por canal: comparación directa de trayectorias en el tiempo.",
        "sql": """
SELECT
  DATE_TRUNC('month', p.fecha)::date AS mes,
  p.canal,
  ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))::numeric, 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY 1, 2
ORDER BY 1, 2;
""".strip(),
    },
    {
        "tab": TAB_DESEMPENO,
        "name": "Ticket promedio (AOV) mensual",
        "display": "line",
        "business": "Valor promedio por pedido completado en cada mes.",
        "importance": "Indica si el crecimiento proviene de más transacciones o de mayor gasto por cliente.",
        "viz_why": "Línea temporal: resalta cambios en el comportamiento de compra.",
        "sql": """
SELECT
  DATE_TRUNC('month', p.fecha)::date AS mes,
  ROUND(
    SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))
    / NULLIF(COUNT(DISTINCT p.id_pedido), 0)::numeric,
    2
  ) AS ticket_promedio
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY 1
ORDER BY 1;
""".strip(),
    },
    {
        "tab": TAB_DESEMPENO,
        "name": "Pedidos completados por mes",
        "display": "line",
        "business": "Volumen de pedidos con estado completado por mes.",
        "importance": "Mide la actividad comercial y la demanda operativa del negocio.",
        "viz_why": "Línea: visualiza tendencia de volumen transaccional.",
        "sql": """
SELECT
  DATE_TRUNC('month', fecha)::date AS mes,
  COUNT(*) AS pedidos_completados
FROM pedido
WHERE estado = 'completado'
GROUP BY 1
ORDER BY 1;
""".strip(),
    },
    {
        "tab": TAB_DESEMPENO,
        "name": "Margen bruto estimado por mes",
        "display": "bar",
        "business": "Diferencia entre ingresos de venta y costo de productos vendidos, por mes.",
        "importance": "Evalúa rentabilidad antes de gastos operativos; clave para expansiones rentables.",
        "viz_why": "Barras: comparación clara de magnitud mes a mes.",
        "sql": """
SELECT
  DATE_TRUNC('month', p.fecha)::date AS mes,
  ROUND(SUM(
    dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)
    - dp.cantidad * pr.precio_costo
  )::numeric, 2) AS margen_bruto
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = dp.id_producto
WHERE p.estado = 'completado'
GROUP BY 1
ORDER BY 1;
""".strip(),
    },
    {
        "tab": TAB_DESEMPENO,
        "name": "Top 10 tiendas por ventas",
        "display": "row",
        "business": "Ranking de tiendas con mayor facturación acumulada en pedidos completados.",
        "importance": "Identifica unidades motoras del negocio y referentes para replicar buenas prácticas.",
        "viz_why": "Barras horizontales: lectura eficiente de rankings.",
        "sql": """
SELECT
  t.nombre AS tienda,
  ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))::numeric, 2) AS ventas
FROM tienda t
JOIN pedido p ON p.id_tienda = t.id_tienda
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY t.id_tienda, t.nombre
ORDER BY ventas DESC
LIMIT 10;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Ventas por región",
        "display": "bar",
        "business": "Facturación total agregada por región geográfica de las tiendas.",
        "importance": "Prioriza regiones con mayor potencial o necesidad de inversión en expansión.",
        "viz_why": "Barras verticales: comparación directa entre regiones.",
        "sql": """
SELECT
  t.region,
  ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))::numeric, 2) AS ventas
FROM tienda t
JOIN pedido p ON p.id_tienda = t.id_tienda
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY t.region
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Crecimiento MoM de ventas por región",
        "display": "table",
        "business": "Variación porcentual mes a mes de ventas en cada región.",
        "importance": "Detecta mercados en aceleración o desaceleración para decisiones de apertura.",
        "viz_why": "Tabla: precisión numérica para múltiples dimensiones (región y mes).",
        "sql": """
WITH ventas_mes AS (
  SELECT
    t.region,
    DATE_TRUNC('month', p.fecha)::date AS mes,
    SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)) AS ventas
  FROM tienda t
  JOIN pedido p ON p.id_tienda = t.id_tienda
  JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
  WHERE p.estado = 'completado'
  GROUP BY 1, 2
),
con_lag AS (
  SELECT
    region,
    mes,
    ventas,
    LAG(ventas) OVER (PARTITION BY region ORDER BY mes) AS ventas_mes_anterior
  FROM ventas_mes
)
SELECT
  region,
  mes,
  ROUND(ventas::numeric, 2) AS ventas_mes,
  ROUND(
    CASE
      WHEN ventas_mes_anterior IS NULL OR ventas_mes_anterior = 0 THEN NULL
      ELSE ((ventas - ventas_mes_anterior) / ventas_mes_anterior) * 100
    END::numeric,
    2
  ) AS crecimiento_pct_mom
FROM con_lag
WHERE ventas_mes_anterior IS NOT NULL
ORDER BY mes DESC, region;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Participación de ventas por segmento de cliente",
        "display": "pie",
        "business": "Distribución de ventas entre segmentos VIP, regular y nuevo.",
        "importance": "Define foco comercial y políticas de retención por valor del cliente.",
        "viz_why": "Pastel: muestra proporciones de participación de forma intuitiva.",
        "sql": """
SELECT
  c.segmento,
  ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0))::numeric, 2) AS ventas
FROM cliente c
JOIN pedido p ON p.id_cliente = c.id_cliente
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY c.segmento
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Desempeño de tiendas de reciente apertura",
        "display": "table",
        "business": "Ventas y pedidos de tiendas abiertas desde 2023, indicador de maduración.",
        "importance": "Evalúa el retorno de nuevas aperturas y calibra el plan de expansión.",
        "viz_why": "Tabla: combina métricas cualitativas (nombre, región, fecha) y cuantitativas.",
        "sql": """
SELECT
  t.nombre AS tienda,
  t.region,
  t.fecha_apertura,
  COUNT(DISTINCT p.id_pedido) FILTER (WHERE p.estado = 'completado') AS pedidos_completados,
  ROUND(COALESCE(SUM(
    CASE WHEN p.estado = 'completado'
      THEN dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)
    END
  ), 0)::numeric, 2) AS ventas_totales
FROM tienda t
LEFT JOIN pedido p ON p.id_tienda = t.id_tienda
LEFT JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE t.fecha_apertura >= DATE '2023-01-01'
GROUP BY t.id_tienda, t.nombre, t.region, t.fecha_apertura
ORDER BY t.fecha_apertura DESC;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Tasa de devoluciones mensual",
        "display": "line",
        "business": "Porcentaje del monto devuelto respecto a las ventas del mes.",
        "importance": "La fricción postventa impacta la rentabilidad y la reputación en nuevos mercados.",
        "viz_why": "Línea: monitorea deterioro o mejora de calidad operativa en el tiempo.",
        "sql": """
WITH ventas AS (
  SELECT
    DATE_TRUNC('month', p.fecha)::date AS mes,
    SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)) AS monto_ventas
  FROM pedido p
  JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
  WHERE p.estado = 'completado'
  GROUP BY 1
),
dev AS (
  SELECT
    DATE_TRUNC('month', fecha)::date AS mes,
    SUM(monto_reembolso) AS monto_devoluciones
  FROM devolucion
  GROUP BY 1
)
SELECT
  v.mes,
  ROUND(
    CASE WHEN v.monto_ventas > 0
      THEN (COALESCE(d.monto_devoluciones, 0) / v.monto_ventas) * 100
    END::numeric,
    4
  ) AS tasa_devolucion_pct
FROM ventas v
LEFT JOIN dev d ON d.mes = v.mes
ORDER BY v.mes;
""".strip(),
    },
    {
        "tab": TAB_EXPANSION,
        "name": "Efectividad de campañas de marketing",
        "display": "bar",
        "business": "Tasa de respuesta de clientes contactados por tipo y canal de campaña.",
        "importance": "Optimiza presupuesto de marketing para impulsar crecimiento con mejor ROI.",
        "viz_why": "Barras: comparación entre tipos/canales de campaña.",
        "sql": """
SELECT
  c.tipo,
  c.canal AS canal_campana,
  COUNT(*) AS clientes_contactados,
  SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) AS respuestas,
  ROUND(
    100.0 * SUM(CASE WHEN cc.respondio THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
    2
  ) AS tasa_respuesta_pct
FROM campana c
JOIN campana_cliente cc ON cc.id_campana = c.id_campana
GROUP BY c.tipo, c.canal
ORDER BY tasa_respuesta_pct DESC;
""".strip(),
    },
]

DASHBOARD_NAME = "RetailMax | Estrategia y Expansión Comercial"
GRADER_EMAIL = "calificar@uvg.edu.gt"
GRADER_PASSWORD = "secret123+"

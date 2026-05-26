# Lab 7 — Visualización de Datos (RetailMax)

Solución de visualización empresarial con **Metabase** y **PostgreSQL** para el área **Estrategia y Expansión Comercial**.

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución
- Puerto `3000` libre

## Ejecución (calificación)

Desde la raíz del repositorio:

```bash
docker compose up
```

Espere a que Metabase termine de iniciar (1–3 minutos) y abra:

- **URL:** http://localhost:3000
- **Usuario:** `calificar@uvg.edu.gt`
- **Contraseña:** `secret123+`

El dashboard **RetailMax | Estrategia y Expansión Comercial** aparece con **2 tabs** y **12 indicadores** (consultas SQL nativas).

## Estructura del repositorio

| Archivo / carpeta | Descripción |
|-------------------|-------------|
| `docker-compose.yml` | PostgreSQL + Metabase |
| `DDL.sql` / `DATA.sql` | Esquema y datos RetailMax (carga automática en Postgres) |
| `metabase-data/` | Estado persistido de Metabase (dashboard preconstruido) |
| `informe.pdf` | Documentación de los 12 KPIs |
| `bootstrap/` | Scripts para regenerar Metabase (desarrollo) |

## Dashboard

| Tab | Indicadores |
|-----|-------------|
| **Desempeño y Crecimiento** | GMV mensual, ventas por canal, AOV, pedidos completados, margen bruto, top 10 tiendas |
| **Expansión y Oportunidades** | Ventas por región, crecimiento MoM, segmentos de cliente, tiendas nuevas, tasa de devoluciones, efectividad de campañas |

## Regenerar Metabase (opcional)

Si necesita reconstruir `metabase-data/` desde cero:

```bash
docker compose down
# Eliminar solo el volumen de Metabase local (conservar pg-data si desea)
Remove-Item -Recurse -Force metabase-data\*
docker compose up -d
pip install -r bootstrap/requirements.txt
python bootstrap/bootstrap_metabase.py
python bootstrap/generate_informe.py
```

## Verificación rápida

```bash
docker compose ps
docker exec retailmax-postgres psql -U retailmax -d retailmax -c "SELECT COUNT(*) FROM pedido;"
```

Debe devolver miles de pedidos cargados desde `DATA.sql`.

## Área de negocio

**Estrategia y Expansión Comercial** — análisis del desempeño global, oportunidades de crecimiento y decisiones a nivel directivo.

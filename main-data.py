import os
import pandas as pd
from google.cloud import bigquery
from weasyprint import HTML

import generador_html
import correo

# ─── 1. Cliente BigQuery ──────────────────────────────────────────────────────
client = bigquery.Client(project="sustained-edge-465417-m3")

# ─── 2. Query consolidada ─────────────────────────────────────────────────────
query = """
    WITH Seg AS (
        SELECT * FROM `sustained-edge-465417-m3.EFE_2026.Unificado_Seguimiento_APPEND`
    ),
    Carac AS (
        SELECT * EXCEPT (Nombre, Proyecto, Sexo, Fecha_Append)
        FROM `sustained-edge-465417-m3.EFE_2026.Unificado_Caracterizacion_APPEND`
        QUALIFY ROW_NUMBER() OVER(
            PARTITION BY Documento
            ORDER BY (
                (CASE WHEN Tipo_documento IS NOT NULL AND LOWER(Tipo_documento) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Fecha_nacimiento IS NOT NULL AND LOWER(Fecha_nacimiento) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Edad IS NOT NULL AND LOWER(Edad) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Estrato IS NOT NULL AND LOWER(Estrato) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Actividad_principal IS NOT NULL AND LOWER(Actividad_principal) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Numero_hijos_Personas_cargo IS NOT NULL AND LOWER(Numero_hijos_Personas_cargo) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Ingresos IS NOT NULL AND LOWER(Ingresos) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Escolaridad IS NOT NULL AND LOWER(Escolaridad) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Ciudad_residencia IS NOT NULL AND LOWER(Ciudad_residencia) != 'pendiente' THEN 1 ELSE 0 END)
            ) DESC, fecha_append DESC
        ) = 1
    ),
    Sat AS (
        SELECT * EXCEPT (Nombre, Proyecto, Fecha_Append)
        FROM `sustained-edge-465417-m3.EFE_2026.Unificado_Satisfaccion_APPEND`
        QUALIFY ROW_NUMBER() OVER(
            PARTITION BY Documento
            ORDER BY (
                (CASE WHEN Evaluacion_docente IS NOT NULL AND LOWER(CAST(Evaluacion_docente AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Evaluacion_recursos_contenido IS NOT NULL AND LOWER(CAST(Evaluacion_recursos_contenido AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Evaluacion_institucion IS NOT NULL AND LOWER(CAST(Evaluacion_institucion AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Evaluacion_plataforma IS NOT NULL AND LOWER(CAST(Evaluacion_plataforma AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Evaluacion_empleabilidad IS NOT NULL AND LOWER(Evaluacion_empleabilidad) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Evaluacion_psicosocial IS NOT NULL AND LOWER(CAST(Evaluacion_psicosocial AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Autoevaluacion IS NOT NULL AND LOWER(CAST(Autoevaluacion AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN NPS IS NOT NULL AND LOWER(CAST(NPS AS STRING)) != 'pendiente' THEN 1 ELSE 0 END)
            ) DESC, fecha_append DESC
        ) = 1
    ),
    Emp AS (
        SELECT * EXCEPT (Nombre, Proyecto, Fecha_Append, Ciudad, Estado_Academico)
        FROM `sustained-edge-465417-m3.EFE_2026.Unificado_Empleabilidad_APPEND`
        QUALIFY ROW_NUMBER() OVER(
            PARTITION BY Documento
            ORDER BY (
                (CASE WHEN Total_remisiones_postulaciones IS NOT NULL AND LOWER(Total_remisiones_postulaciones) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Empresa IS NOT NULL AND LOWER(Empresa) != 'pendiente' THEN 1 ELSE 0 END) +
                (CASE WHEN Estado_contratacion IS NOT NULL AND LOWER(Estado_contratacion) != 'pendiente' THEN 1 ELSE 0 END)
            ) DESC, fecha_append DESC
        ) = 1
    )
    SELECT
        Seg.Proyecto,
        COUNT(DISTINCT Seg.Documento) AS Total_Inscritos,
        ROUND(
            AVG(
                (
                    COALESCE(SAFE_CAST(Sat.Evaluacion_docente AS FLOAT64), 0) +
                    COALESCE(SAFE_CAST(Sat.Evaluacion_plataforma AS FLOAT64), 0) +
                    COALESCE(SAFE_CAST(Sat.Evaluacion_recursos_contenido AS FLOAT64), 0) +
                    COALESCE(SAFE_CAST(Sat.Evaluacion_institucion AS FLOAT64), 0) +
                    COALESCE(SAFE_CAST(Sat.Evaluacion_psicosocial AS FLOAT64), 0) +
                    COALESCE(SAFE_CAST(Sat.Autoevaluacion AS FLOAT64), 0)
                ) /
                NULLIF((
                    (CASE WHEN Sat.Evaluacion_docente IS NOT NULL AND LOWER(CAST(Sat.Evaluacion_docente AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                    (CASE WHEN Sat.Evaluacion_plataforma IS NOT NULL AND LOWER(CAST(Sat.Evaluacion_plataforma AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                    (CASE WHEN Sat.Evaluacion_recursos_contenido IS NOT NULL AND LOWER(CAST(Sat.Evaluacion_recursos_contenido AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                    (CASE WHEN Sat.Evaluacion_institucion IS NOT NULL AND LOWER(CAST(Sat.Evaluacion_institucion AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                    (CASE WHEN Sat.Evaluacion_psicosocial IS NOT NULL AND LOWER(CAST(Sat.Evaluacion_psicosocial AS STRING)) != 'pendiente' THEN 1 ELSE 0 END) +
                    (CASE WHEN Sat.Autoevaluacion IS NOT NULL AND LOWER(CAST(Sat.Autoevaluacion AS STRING)) != 'pendiente' THEN 1 ELSE 0 END)
                ), 0)
            ), 2
        ) AS Sat_General,
        ROUND((
            COUNTIF(SAFE_CAST(Sat.NPS AS FLOAT64) >= 9) -
            COUNTIF(SAFE_CAST(Sat.NPS AS FLOAT64) <= 6)
        ) / NULLIF(COUNTIF(Sat.NPS IS NOT NULL), 0), 4) AS Resultado_NPS,
        ROUND(
            (COUNT(DISTINCT CASE WHEN LOWER(Seg.Estado_academico) NOT LIKE '%retiro%' THEN Seg.Documento END) /
            NULLIF(COUNT(DISTINCT Seg.Documento), 0)) * 100, 2
        ) AS Porcentaje_Retencion,
        ROUND(
            COUNTIF(Seg.Resultado_Academico = 'Aprobado') /
            NULLIF(COUNTIF(
                Seg.Resultado_Academico IS NOT NULL AND
                Seg.Resultado_Academico NOT LIKE '%Pendiente%' AND
                LOWER(Seg.Estado_academico) NOT LIKE '%retiro%'
            ), 0), 4
        ) AS Resultado_Aprobacion
    FROM Seg
    LEFT JOIN Carac ON Seg.Documento = Carac.Documento
    LEFT JOIN Sat   ON Seg.Documento = Sat.Documento
    LEFT JOIN Emp   ON Seg.Documento = Emp.Documento
    WHERE Seg.Fecha_Append = '2026-06'
    GROUP BY Seg.Proyecto
    ORDER BY Total_Inscritos DESC
"""

print("Executing BigQuery query...")
df = client.query(query, job_config=bigquery.QueryJobConfig(use_legacy_sql=False)).to_dataframe()

# ─── 3. Metas contractuales ───────────────────────────────────────────────────
METAS_PROYECTOS = {
    "suba": {"Meta_Inscritos": 690, "Meta_Sat": 4.5, "Meta_NPS": 0.70, "Meta_Retencion": 93.0, "Meta_Aprobacion": 0.80},
    "ecolombia": {"Meta_Inscritos": 360, "Meta_Sat": 4.5, "Meta_NPS": 0.65, "Meta_Retencion": 97.0, "Meta_Aprobacion": 0.80},
    "colsubsidio": {"Meta_Inscritos": 3000, "Meta_Sat": 4.5, "Meta_NPS": 0.75, "Meta_Retencion": 90.0, "Meta_Aprobacion": 0.80},
    "jóvenes": {"Meta_Inscritos": 250, "Meta_Sat": 4.2, "Meta_NPS": 0.60, "Meta_Retencion": 92.0, "Meta_Aprobacion": 0.75}
}

# ─── 4. Motor unificado de semáforos e indicadores ───────────────────────────
def calcular_semaforo_y_insights(row):
    proyecto_lower = str(row['Proyecto']).lower()
    
    meta_clave = None
    for clave in METAS_PROYECTOS:
        if clave in proyecto_lower:
            meta_clave = clave
            break

    if not meta_clave:
        colores_gris = {"inscritos": "gray", "sat": "gray", "nps": "gray", "retencion": "gray", "aprobacion": "gray"}
        return 'Gris', f"Proyecto '{row['Proyecto']}' sin metas en el diccionario.", colores_gris

    metas = METAS_PROYECTOS[meta_clave]

    # Reales
    real_inscritos  = row['Total_Inscritos'] or 0
    real_sat        = float(row['Sat_General'] or 0)
    real_nps        = float(row['Resultado_NPS'] or 0)
    real_retencion  = float(row['Porcentaje_Retencion'] or 0)
    real_aprobacion = float(row['Resultado_Aprobacion'] or 0)

    pct_inscritos = real_inscritos / metas['Meta_Inscritos']
    brecha_sat = real_sat - metas['Meta_Sat']
    brecha_nps = real_nps - metas['Meta_NPS']
    brecha_ret = real_retencion - metas['Meta_Retencion']
    brecha_apr = real_aprobacion - metas['Meta_Aprobacion']

    alertas, positivos = [], []

    # Lógica de alertas e insights
    if pct_inscritos >= 0.95: positivos.append(f"Inscritos al {pct_inscritos:.1%} ({real_inscritos}/{metas['Meta_Inscritos']}) ✓")
    elif pct_inscritos >= 0.80: alertas.append(f"Inscritos al {pct_inscritos:.1%} ({real_inscritos}/{metas['Meta_Inscritos']}): brecha moderada")
    else: alertas.append(f"⚠ Captación crítica: {pct_inscritos:.1%} ({real_inscritos}/{metas['Meta_Inscritos']})")

    if brecha_sat >= 0: positivos.append(f"Satisfacción {real_sat:.2f} (Meta {metas['Meta_Sat']}) ✓")
    elif brecha_sat >= -0.3: alertas.append(f"Satisfacción {real_sat:.2f} vs {metas['Meta_Sat']} ({brecha_sat:+.2f})")
    else: alertas.append(f"⚠ Satisfacción crítica: {real_sat:.2f} vs {metas['Meta_Sat']} ({brecha_sat:+.2f})")

    if brecha_nps >= 0: positivos.append(f"NPS {real_nps:.1%} (Meta {metas['Meta_NPS']:.0%}) ✓")
    elif brecha_nps >= -0.10: alertas.append(f"NPS {real_nps:.1%} vs {metas['Meta_NPS']:.0%} ({brecha_nps:+.1%})")
    else: alertas.append(f"⚠ NPS crítico: {real_nps:.1%} vs {metas['Meta_NPS']:.0%} ({brecha_nps:+.1%})")

    if brecha_ret >= 0: positivos.append(f"Retención {real_retencion:.1f}% (Meta {metas['Meta_Retencion']:.0f}%) ✓")
    elif brecha_ret >= -3: alertas.append(f"Retención {real_retencion:.1f}% vs {metas['Meta_Retencion']:.0f}% ({brecha_ret:+.1f}pp)")
    else: alertas.append(f"⚠ Retención crítica: {real_retencion:.1f}% vs {metas['Meta_Retencion']:.0f}% ({brecha_ret:+.1f}pp)")

    if brecha_apr >= 0: positivos.append(f"Aprobación {real_aprobacion:.1%} (Meta {metas['Meta_Aprobacion']:.0%}) ✓")
    elif brecha_apr >= -0.10: alertas.append(f"Aprobación {real_aprobacion:.1%} vs {metas['Meta_Aprobacion']:.0%} ({brecha_apr:+.1%})")
    else: alertas.append(f"⚠ Aprobación crítica: {real_aprobacion:.1%} vs {metas['Meta_Aprobacion']:.0%} ({brecha_apr:+.1%})")

    # Semáforo compuesto
    criticos = sum([pct_inscritos < 0.80, brecha_sat < -0.3, brecha_nps < -0.10, brecha_ret < -3, brecha_apr < -0.10])
    moderados = sum([0.80 <= pct_inscritos < 0.95, -0.3 <= brecha_sat < 0, -0.10 <= brecha_nps < 0, -3 <= brecha_ret < 0, -0.10 <= brecha_apr < 0])

    color = 'Red' if criticos >= 1 else ('Yellow' if moderados >= 1 else 'Green')

    # DETERMINACIÓN EXACTA DE COLORES POR KPI INDIVIDUAL
    colores_kpis = {
        "inscritos": "green" if pct_inscritos >= 0.95 else ("yellow" if pct_inscritos >= 0.80 else "red"),
        "sat": "green" if brecha_sat >= 0 else ("yellow" if brecha_sat >= -0.3 else "red"),
        "nps": "green" if brecha_nps >= 0 else ("yellow" if brecha_nps >= -0.10 else "red"),
        "retencion": "green" if brecha_ret >= 0 else ("yellow" if brecha_ret >= -3 else "red"),
        "aprobacion": "green" if brecha_apr >= 0 else ("yellow" if brecha_apr >= -0.10 else "red")
    }

    partes_insight = []
    if alertas: partes_insight.append(" | ".join(alertas))
    if positivos: partes_insight.append("Fortalezas: " + "; ".join(positivos))
    insight = " // ".join(partes_insight) if partes_insight else "Sin datos sufientes."

    return color, insight, colores_kpis

# ─── 5. Procesamiento ────────────────────────────────────────────────────────
print("\nProcessing risk matrices...")
semaforos, insights, kpis_colores = [], [], []

for _, row in df.iterrows():
    color, insight, col_ind = calcular_semaforo_y_insights(row)
    semaforos.append(color)
    insights.append(insight)
    kpis_colores.append(col_ind)

df['Semaforo'] = semaforos
df['Insight_Accionable'] = insights
df['Colores_KPIs'] = kpis_colores

# ─── 6. Generación ────────────────────────────────────────────────────────────
print("Rendering report...")
html_documento = generador_html.generar_reporte_html(df)

with open("reporte_final.html", "w", encoding="utf-8") as f:
    f.write(html_documento)

HTML("reporte_final.html", base_url=".").write_pdf("reporte_predictivo.pdf")
correo.enviar_correo_con_adjunto(html_documento, "reporte_predictivo.pdf")
print("\n✅ Proceso completado exitosamente.")

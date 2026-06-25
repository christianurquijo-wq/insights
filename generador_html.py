# generador_html.py
from jinja2 import Template
from datetime import datetime

def generar_reporte_html(df):
    proyectos_dict = df.to_dict(orient='records')
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    URL_LOGO_KUEPA = "https://storage.googleapis.com/ket-bucket/bucket/U099Y5NS0Q4/Suba/f102a14a77f09b501d2646a12087e6cc.png"
    
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            /* ─── 1. CONTROL DE MÁRGENES IMPRESIÓN (PDF WEASYPRINT) ─── */
            @page {
                size: A4;
                margin: 15mm 12mm 15mm 12mm; /* Proporción áurea balanceada */
                background-color: #ffffff;
                @bottom-right {
                    content: "Página " counter(page) " de " counter(pages);
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8pt;
                    color: #71717a;
                }
                @bottom-left {
                    content: "Kuepa Edutech • Reporte Predictivo Automatizado";
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8pt;
                    color: #71717a;
                }
            }

            /* ─── 2. ESTILOS BASE (CERO PADDING/MARGIN PARA EVITAR DOBLE COLCHÓN) ─── */
            body { 
                font-family: 'Helvetica Neue', Arial, sans-serif; 
                margin: 0; 
                padding: 0; /* FIX: Eliminado el padding que engrosaba los márgenes */
                background-color: #ffffff; 
                color: #292929; 
            }
            
            /* Contenedor adaptativo: da aire en el correo pero WeasyPrint lo ignora en el PDF */
            .email-wrapper {
                padding: 10px;
            }

            .header-container { border-bottom: 3px solid #FD531E; padding-bottom: 20px; margin-bottom: 35px; }
            .header-container h1 { font-size: 24px; margin: 0 0 8px 0; font-weight: 700; }
            .header-container p { font-size: 13px; color: #666666; margin: 0; }
            h2 { font-size: 15px; margin: 30px 0 15px 0; text-transform: uppercase; border-left: 4px solid #292929; padding-left: 10px; }
            
            table { width: 100%; border-collapse: collapse; margin-bottom: 40px; }
            th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #e4e4e7; font-size: 13px; }
            th { background-color: #FAFAFA; color: #292929; font-weight: 700; font-size: 11px; text-transform: uppercase; border-top: 1px solid #e4e4e7; }
            
            /* Clases de Fondos para los Indicadores Individuales de la Tabla */
            .text-green { background-color: #d1fae5; color: #065f46; font-weight: bold; padding: 3px 6px; border-radius: 4px; display: inline-block; }
            .text-yellow { background-color: #fef3c7; color: #92400e; font-weight: bold; padding: 3px 6px; border-radius: 4px; display: inline-block; }
            .text-red { background-color: #fde8e8; color: #821F0D; font-weight: bold; padding: 3px 6px; border-radius: 4px; display: inline-block; }
            .text-gray { background-color: #f4f4f5; color: #71717a; padding: 3px 6px; border-radius: 4px; display: inline-block; }

            /* Badges del Semáforo General */
            .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; display: inline-block; }
            .bg-green { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
            .bg-yellow { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
            .bg-red { background-color: #fde8e8; color: #821F0D; border: 1px solid #f8b4b4; }
            .bg-gris { background-color: #f4f4f5; color: #71717a; border: 1px solid #e4e4e7; }

            .proyecto-card { border: 1px solid #e4e4e7; border-radius: 6px; padding: 20px; margin-bottom: 20px; page-break-inside: avoid; background-color: #ffffff; }
            .proyecto-title { font-size: 16px; font-weight: 700; color: #292929; }
            .kpi-item { font-size: 11px; margin-bottom: 6px; padding-left: 15px; position: relative; line-height: 1.4; }
            .kpi-item::before { content: "•"; position: absolute; left: 0; color: #FD531E; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="email-wrapper">

            <div class="header-container">
                <table style="width:100%; border:none; margin:0;">
                    <tr style="background:none;">
                        <td style="border:none; padding:0;">
                            <h1>Reporte de Riesgos Predictivos y KPIs</h1>
                            <p>Monitoreo Automatizado de Empleabilidad • Corte: {{ fecha_corte }} (Mayo 2026)</p>
                        </td>
                        <td style="border:none; padding:0; text-align:right;">
                            <img src="{{ url_logo }}" alt="Logo Kuepa" style="height:40px; width:auto;">
                        </td>
                    </tr>
                </table>
            </div>

            <h2>I. Matriz General de Riesgo Contractual</h2>
            <table>
                <thead>
                    <tr>
                        <th>Proyecto Activo</th>
                        <th>Inscritos</th>
                        <th>Satisfacción</th>
                        <th>NPS</th>
                        <th>Retención</th>
                        <th>Aprobación</th>
                        <th>Estatus General</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in proyectos %}
                    <tr>
                        <td><strong>{{ row.Proyecto }}</strong></td>
                        
                        <td><span class="text-{{ row.Colores_KPIs.inscritos }}">{{ row.Total_Inscritos }}</span></td>
                        <td><span class="text-{{ row.Colores_KPIs.sat }}">{{ row.Sat_General if row.Sat_General is not none else "N/A" }}</span></td>
                        <td><span class="text-{{ row.Colores_KPIs.nps }}">{{ "%.1f%%"|format(row.Resultado_NPS * 100) if row.Resultado_NPS is not none else "N/A" }}</span></td>
                        <td><span class="text-{{ row.Colores_KPIs.retencion }}">{{ row.Porcentaje_Retencion }}%</span></td>
                        <td><span class="text-{{ row.Colores_KPIs.aprobacion }}">{{ "%.1f%%"|format(row.Resultado_Aprobacion * 100) if row.Resultado_Aprobacion is not none else "N/A" }}</span></td>
                        
                        <td><span class="badge bg-{{ row.Semaforo|lower }}">{{ row.Semaforo }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <h2>II. Desglose de KPIs e Insights por Proyecto</h2>
            {% for row in proyectos %}
            <div class="proyecto-card">
                <table style="width:100%; border:none; margin-bottom:10px;">
                    <tr style="background:none;">
                        <td style="border:none; padding:0;"><span class="proyecto-title">{{ row.Proyecto }}</span></td>
                        <td style="border:none; padding:0; text-align:right;"><span class="badge bg-{{ row.Semaforo|lower }}">Riesgo: {{ row.Semaforo }}</span></td>
                    </tr>
                </table>
                <div style="border-top:1px solid #f4f4f5; padding-top:10px;">
                    {% set bloques = row.Insight_Accionable.split(' // ') %}
                    {% if bloques[0] is defined and "diccionario" in bloques[0] %}
                        <p style="color:#71717a; font-style:italic; font-size:11px; margin:0;">{{ bloques[0] }}</p>
                    {% else %}
                        {% if bloques[0] is defined and "Fortalezas" not in bloques[0] %}
                            <h4 style="margin:4px 0; font-size:11px; color:#b91c1c; text-transform:uppercase; letter-spacing:0.3px;">Alertas y Desviaciones Críticas:</h4>
                            {% for item in bloques[0].split(' | ') %}
                                <div class="kpi-item" style="color:#b91c1c;">{{ item }}</div>
                            {% endfor %}
                        {% endif %}
                        {% if bloques[1] is defined or (bloques[0] is defined and "Fortalezas" in bloques[0]) %}
                            <h4 style="margin:12px 0 4px 0; font-size:11px; color:#15803d; text-transform:uppercase; letter-spacing:0.3px;">Cumplimiento Contractual Exitoso:</h4>
                            {% set fortaleza_bloque = bloques[1] if bloques[1] is defined else bloques[0] %}
                            {% for item in fortaleza_bloque.replace('Fortalezas: ', '').split('; ') %}
                                <div class="kpi-item" style="color:#15803d;">{{ item }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}

        </div>
    </body>
    </html>
    """
    template = Template(html_template)
    return template.render(proyectos=proyectos_dict, fecha_corte=fecha_actual, url_logo=URL_LOGO_KUEPA)

# correo.py
import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def enviar_correo_con_adjunto(html_body, ruta_pdf):
    """
    Gestiona la autenticación SMTP corporativa, inyecta el reporte HTML
    en el cuerpo del correo y adjunta de forma segura el informe PDF.
    """
    # 1. Configuración de parámetros institucionales
    REMITENTE = "christian.urquijo@kuepa.com"
    PASSWORD = os.environ.get("CORREO_PASS")
    if len(sys.argv) > 1 and "@" in sys.argv[1]:
        DESTINATARIOS = [sys.argv[1]] # Se convierte en el único receptor del reporte
        print(f"📬 Modo Dinámico: Enviando reporte solicitado a {DESTINATARIOS}")
    else:
        # Fallback de respaldo por si ejecutas el script manual desde la terminal
        DESTINATARIOS = ["gerente@kuepa.com", "coordinador_kpis@kuepa.com"]
        print(f"📬 Modo Por Defecto: Enviando a lista fija institucional")
    
    # Validación preventiva de seguridad para Cloud Shell
    if not PASSWORD:
        raise ValueError(
            "❌ Error: La variable de entorno 'CORREO_PASS' no está configurada en la sesión actual de Cloud Shell.\n"
            "Ejecuta antes en tu terminal: export CORREO_PASS='tu_token_de_aplicacion'"
        )

    # 2. Configuración del contenedor del mensaje (Uso de 'mixed' para soportar cuerpo + adjuntos)
    msg = MIMEMultipart('mixed')
    msg['Subject'] = "🚨 Alertas de Riesgo y KPIs - Proyectos Empleabilidad Kuepa"
    msg['From'] = REMITENTE
    msg['To'] = ", ".join(DESTINATARIOS)

    # 3. Adjuntar el HTML renderizado directo para visualización rápida en la bandeja de entrada
    parte_html = MIMEText(html_body, 'html')
    msg.attach(parte_html)

    # 4. Carga y codificación segura del archivo PDF adjunto
    try:
        if os.path.exists(ruta_pdf):
            nombre_archivo = os.path.basename(ruta_pdf)
            with open(ruta_pdf, "rb") as adjunto:
                parte_pdf = MIMEBase("application", "octet-stream")
                parte_pdf.set_payload(adjunto.read())
                
            # Codificar en Base64 para transferencia de correo segura sin corrupción de datos
            encoders.encode_base64(parte_pdf)
            parte_pdf.add_header(
                "Content-Disposition",
                f"attachment; filename={nombre_archivo}",
            )
            msg.attach(parte_pdf)
            print(f"📎 Archivo {nombre_archivo} acoplado con éxito al correo corporativo.")
        else:
            print(f"⚠️ Advertencia: No se encontró el archivo PDF en la ruta: {ruta_pdf}. El correo saldrá sin adjunto.")
    except Exception as e:
        print(f"⚠️ Error al procesar el archivo adjunto: {e}")

    # 5. Autenticación y envío mediante el servidor SMTP seguro de Google Workspace
    try:
        print(f"🔄 Conectando con el servidor SMTP de Google para {REMITENTE}...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Inicializar canal cifrado TLS seguro
        server.login(REMITENTE, PASSWORD)
        server.sendmail(REMITENTE, DESTINATARIOS, msg.as_string())
        server.quit()
        print("🚀 Reporte predictivo enviado con éxito a los stakeholders.")
    except Exception as e:
        print(f"❌ Error al enviar el correo a través del servidor SMTP: {e}")

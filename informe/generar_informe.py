# -*- coding: utf-8 -*-
"""
Genera docs/informe/Informe_Ciudad_Inteligente.pdf con normas APA 7 (trabajo de estudiante).

Uso (desde la carpeta del repositorio):
    python informe/generar_informe.py

Requiere reportlab (pip install reportlab).
- Las capturas tomadas del sitio y del informe publicado están en informe/figuras/.
- Las capturas que debe aportar el equipo se guardan en docs/img/evidencias/ con el nombre
  indicado en cada recuadro. Si el archivo existe, se inserta; si no, queda el recuadro.
- El resumen de ejecuciones del ETL se lee de automatizacion/logs/etl_AAAA-MM.log si existe.
Todas las cifras del texto provienen de las consultas de la carpeta consultas/ (resultados del
13 de noviembre de 2026) y del registro del ETL.
"""
import os, re, glob, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image, KeepTogether, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "informe", "figuras")
EVID = os.path.join(RAIZ, "docs", "img", "evidencias")
SALIDA = os.path.join(RAIZ, "docs", "informe", "Informe_Ciudad_Inteligente.pdf")
SITIO = "https://juan747-art.github.io/canecas-inteligentes/"
REPO = "https://github.com/Juan747-art/canecas-inteligentes"

# ------------------------------------------------------------------ fuentes y estilos
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("TNR", os.path.join(F, "times.ttf")))
pdfmetrics.registerFont(TTFont("TNR-B", os.path.join(F, "timesbd.ttf")))
pdfmetrics.registerFont(TTFont("TNR-I", os.path.join(F, "timesi.ttf")))
pdfmetrics.registerFont(TTFont("TNR-BI", os.path.join(F, "timesbi.ttf")))
pdfmetrics.registerFontFamily("TNR", normal="TNR", bold="TNR-B", italic="TNR-I", boldItalic="TNR-BI")

DOBLE = 24  # interlineado doble para 12 pt
st = {
    "cuerpo": ParagraphStyle("cuerpo", fontName="TNR", fontSize=12, leading=DOBLE, firstLineIndent=0.5 * inch,
                             alignment=TA_LEFT),
    "sin": ParagraphStyle("sin", fontName="TNR", fontSize=12, leading=DOBLE, alignment=TA_LEFT),
    "lista": ParagraphStyle("lista", fontName="TNR", fontSize=12, leading=DOBLE, leftIndent=0.5 * inch,
                            firstLineIndent=-0.25 * inch),
    "h1": ParagraphStyle("h1", fontName="TNR-B", fontSize=12, leading=DOBLE, alignment=TA_CENTER, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="TNR-B", fontSize=12, leading=DOBLE, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="TNR-BI", fontSize=12, leading=DOBLE, keepWithNext=1),
    "titulo": ParagraphStyle("titulo", fontName="TNR-B", fontSize=12, leading=DOBLE, alignment=TA_CENTER),
    "centro": ParagraphStyle("centro", fontName="TNR", fontSize=12, leading=DOBLE, alignment=TA_CENTER),
    "rotulo": ParagraphStyle("rotulo", fontName="TNR-B", fontSize=12, leading=DOBLE, keepWithNext=1,
                             spaceBefore=6),
    "titfig": ParagraphStyle("titfig", fontName="TNR-I", fontSize=12, leading=DOBLE, keepWithNext=1,
                             spaceAfter=4),
    "nota": ParagraphStyle("nota", fontName="TNR", fontSize=12, leading=DOBLE, spaceBefore=4),
    "celda": ParagraphStyle("celda", fontName="TNR", fontSize=10.5, leading=13),
    "celdab": ParagraphStyle("celdab", fontName="TNR-B", fontSize=10.5, leading=13),
    "ref": ParagraphStyle("ref", fontName="TNR", fontSize=12, leading=DOBLE, leftIndent=0.5 * inch,
                          firstLineIndent=-0.5 * inch),
    "hueco": ParagraphStyle("hueco", fontName="TNR", fontSize=11, leading=15, alignment=TA_LEFT),
    "pend": ParagraphStyle("pend", fontName="TNR-B", fontSize=12, leading=DOBLE, alignment=TA_CENTER,
                           textColor=colors.HexColor("#9A3412")),
}
PEND = '<font color="#9A3412">[{}]</font>'
ANCHO = 6.5 * inch


# ------------------------------------------------------------------ plantilla con tabla de contenido
class Doc(BaseDocTemplate):
    def __init__(self, ruta, **kw):
        super().__init__(ruta, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch,
                         bottomMargin=inch, title="Ciudad Inteligente: módulo vertedero",
                         author="Juan Diego Lozano y Deivid Real", subject="Informe del proyecto (APA 7)", **kw)
        marco = Frame(inch, inch, ANCHO, 9 * inch, id="f", leftPadding=0, rightPadding=0, topPadding=0,
                      bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="p", frames=[marco], onPage=self.numero)])
        self.n = 0

    def beforeDocument(self):
        self.n = 0  # mismas claves en cada pasada de multiBuild

    @staticmethod
    def numero(c, d):
        c.saveState()
        c.setFont("TNR", 12)
        c.drawRightString(letter[0] - inch, letter[1] - 0.5 * inch - 12, str(d.page))
        c.restoreState()

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            nivel = 0 if f.style.name == "h1" else 1
            texto = f.getPlainText()
            self.n += 1
            clave = f"s{self.n}"
            self.canv.bookmarkPage(clave)
            self.canv.addOutlineEntry(texto, clave, level=nivel, closed=nivel > 0)
            self.notify("TOCEntry", (nivel, texto, self.page, clave))


# ------------------------------------------------------------------ ayudas
H = []
num_tabla = [0]
num_fig = [0]


def p(t, estilo="cuerpo"):
    H.append(Paragraph(t, st[estilo]))


def h1(t, nueva_pagina=False):
    # APA: las secciones siguen en la misma página; solo las referencias empiezan en página nueva
    H.append(PageBreak() if nueva_pagina else CondPageBreak(3.2 * inch))
    H.append(Paragraph(t, st["h1"]))


def h2(t):
    H.append(CondPageBreak(2.6 * inch))
    H.append(Paragraph(t, st["h2"]))


def h3(t):
    H.append(CondPageBreak(1.1 * inch))
    H.append(Paragraph(t, st["h3"]))


def lista(items, numerada=False):
    for i, t in enumerate(items, 1):
        marca = f"{i}." if numerada else "•"
        H.append(Paragraph(f"{marca}&nbsp;&nbsp;{t}", st["lista"]))


def titulos_previos():
    """Saca de H los títulos (h1, h2, h3) que preceden inmediatamente a una tabla o figura,
    para que viajen con ella y no queden solos al final de una página."""
    previos = []
    while H and isinstance(H[-1], Paragraph) and H[-1].style.name in ("h1", "h2", "h3"):
        previos.insert(0, H.pop())
    return previos


def tabla(titulo, filas, anchos, nota=None, cabecera=True):
    num_tabla[0] += 1
    datos = []
    for i, f in enumerate(filas):
        est = st["celdab"] if (cabecera and i == 0) else st["celda"]
        datos.append([c if not isinstance(c, str) else Paragraph(c, est) for c in f])
    t = Table(datos, colWidths=[a * inch for a in anchos], repeatRows=1 if cabecera else 0, hAlign="LEFT")
    estilo = [("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
              ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
              ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black)]
    if cabecera:
        estilo.append(("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black))
    t.setStyle(TableStyle(estilo))
    bloque = [Paragraph(f"Tabla {num_tabla[0]}", st["rotulo"]), Paragraph(titulo, st["titfig"]), t]
    if nota:
        bloque.append(Paragraph(f"<i>Nota.</i> {nota}", st["nota"]))
    previos = titulos_previos()
    if len(filas) <= 12:
        H.append(KeepTogether(previos + bloque))
    else:
        # tabla larga: se parte entre páginas, pero el título, el rótulo y las primeras filas van juntos
        H.append(CondPageBreak(3.5 * inch))
        H.extend(previos + bloque)
    H.append(Spacer(1, 10))
    return num_tabla[0]


def imagen(ruta, ancho_max=ANCHO, alto_max=4.6 * inch):
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(ruta).getSize()
    k = min(ancho_max / w, alto_max / h)
    img = Image(ruta, width=w * k, height=h * k)
    img.hAlign = "CENTER"
    marco = Table([[img]], colWidths=[w * k + 2])
    marco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return marco


def figura(titulo, nota, archivo=None, pendiente=None):
    """archivo: ruta de una captura tomada (informe/figuras).
    pendiente: (nombre_archivo, qué debe mostrar, cómo tomarla) para las capturas del equipo."""
    num_fig[0] += 1
    cuerpo = None
    if archivo and os.path.exists(archivo):
        cuerpo = imagen(archivo)
    elif pendiente:
        nombre, que, como = pendiente
        ruta = next((r for r in glob.glob(os.path.join(EVID, os.path.splitext(nombre)[0] + ".*"))
                     if not r.endswith(".txt")), None)
        if ruta:
            cuerpo = imagen(ruta)
        else:
            texto = (f"<b>ESPACIO PARA CAPTURA</b><br/><br/>"
                     f"<b>Archivo:</b> docs/img/evidencias/{nombre}<br/>"
                     f"<b>Qué debe mostrar:</b> {que}<br/>"
                     f"<b>Cómo tomarla:</b> {como}")
            cuerpo = Table([[Paragraph(texto, st["hueco"])]], colWidths=[ANCHO], rowHeights=[2.6 * inch])
            cuerpo.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#9A3412"), None, (5, 3)),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14)]))
            PENDIENTES.append((num_fig[0], nombre, que))
    bloque = [Paragraph(f"Figura {num_fig[0]}", st["rotulo"]), Paragraph(titulo, st["titfig"]), cuerpo]
    if nota:
        bloque.append(Paragraph(f"<i>Nota.</i> {nota}", st["nota"]))
    H.append(KeepTogether(titulos_previos() + bloque))
    H.append(Spacer(1, 10))
    return num_fig[0]


PENDIENTES = []


def leer_log_etl():
    """Resume el registro del script de la tarea programada (si existe)."""
    archivos = sorted(glob.glob(os.path.join(RAIZ, "automatizacion", "logs", "etl_*.log")))
    lineas = []
    for a in archivos:
        lineas += [l.strip() for l in open(a, encoding="utf-8-sig") if l.strip()]
    if not lineas:
        return None
    ok = [l for l in lineas if "| OK |" in l]
    err = [l for l in lineas if "| ERROR |" in l]
    return {"n": len(lineas), "ok": len(ok), "err": err, "primera": lineas[0][:16], "ultima": lineas[-1][:16],
            "lineas": lineas}


# ================================================================== PORTADA
H.append(Spacer(1, 2.2 * inch))
p("Ciudad Inteligente: Módulo Vertedero con Canecas Inteligentes, Data Warehouse y Dashboard en Power BI",
  "titulo")
H.append(Spacer(1, DOBLE))
p("Juan Diego Lozano y Deivid Real", "centro")
p("Programa de Big Data, Sede Chía, " + PEND.format("nombre de la institución"), "centro")
p(PEND.format("código y nombre del curso"), "centro")
p(PEND.format("nombre del docente"), "centro")
p("13 de noviembre de 2026", "centro")

# ================================================================== TABLA DE CONTENIDO
H.append(PageBreak())
H.append(Paragraph("Tabla de contenido", st["titulo"]))
toc = TableOfContents(dotsMinLevel=0)
toc.levelStyles = [
    ParagraphStyle("t0", fontName="TNR", fontSize=12, leading=20, leftIndent=0, firstLineIndent=0,
                   rightIndent=0.35 * inch),
    ParagraphStyle("t1", fontName="TNR", fontSize=12, leading=20, leftIndent=0.4 * inch, firstLineIndent=0,
                   rightIndent=0.35 * inch),
]
H.append(toc)

# ================================================================== INTRODUCCIÓN
h1("Ciudad Inteligente: Módulo Vertedero con Canecas Inteligentes", nueva_pagina=True)
p("Este informe documenta el módulo «vertedero» del proyecto Ciudad Inteligente: tres canecas de una maqueta "
  "que abren su tapa al acercar la mano, miden su nivel de llenado con un sensor láser y envían sus datos, por "
  "medio de una ESP32, hasta una base de datos, un data warehouse y un dashboard en Power BI publicado en un "
  "sitio web. Las canecas siguen el código nacional de colores para la separación en la fuente: blanca para "
  "aprovechables (C1), negra para no aprovechables (C2) y verde para orgánicos aprovechables (C3) (Ministerio "
  "de Ambiente y Desarrollo Sostenible, 2019a, 2019b).")
p("En un punto de disposición con canecas convencionales nadie sabe qué tan llena está cada caneca hasta que "
  "alguien la mira; la recolección se programa a una hora fija y no queda registro de a qué horas se usan más, "
  "qué residuo se acumula más rápido o cuántas veces una persona encontró la caneca llena. El Banco Mundial "
  "estima que en 2022 se produjeron 2.560 millones de toneladas de residuos sólidos en el mundo y proyecta "
  "3.860 millones para 2050 si no cambian las tendencias (World Bank, s. f.). Gestionar mejor la recolección "
  "empieza por medir.")
p("<b>Pregunta del proyecto.</b> ¿Qué comportamientos de llenado y de uso de las canecas pueden demostrarse "
  "con los datos del módulo, y cómo orientarían la programación de la recolección?", "sin")
p("El trabajo se organizó con las seis fases de CRISP-DM (Wirth y Hipp, 2000; IBM, s. f.) y el data warehouse "
  "sigue las técnicas de modelado dimensional de Kimball Group (s. f.). El informe presenta la estructura del "
  "sitio, el origen y la preparación de los datos, los indicadores y los procedimientos de análisis, los cinco "
  "conocimientos evidentes, las validaciones, las decisiones, las evidencias de publicación e integración, las "
  "limitaciones y las conclusiones.")
h2("Qué es Real y qué es Simulado")
p("La maqueta, la ESP32, los sensores, el servidor, las bases de datos, el ETL y el dashboard son reales y "
  "funcionan. Los datos que se analizan son, casi en su totalidad, <b>simulados</b>: 1.000.000 de lecturas, "
  "7.495 eventos y 3 alarmas generados para el período del 27 de septiembre al 4 de noviembre de 2026. Las "
  "lecturas reales de la ESP32 son 933 (con 246 eventos), tomadas en pruebas con la maqueta el 6 y el 7 de "
  "noviembre de 2026, y no se usan para sacar conclusiones. El peso de los residuos es siempre simulado, porque "
  "la maqueta no tiene sensor de peso. Por eso los hallazgos describen el escenario simulado y las relaciones "
  "se presentan como asociaciones, no como causas.")

# ================================================================== ESTRUCTURA DEL SITIO
h1("Descripción de la Estructura del Sitio")
p(f"El sitio está publicado en GitHub Pages en <u>{SITIO}</u>. Es un sitio estático de una sola página "
  "(HTML, CSS y JavaScript, sin servidor propio) con un menú lateral de catorce secciones; en pantallas "
  "pequeñas el menú se despliega con el botón «Menú». El código fuente, las consultas y los scripts están en el "
  f"repositorio público <u>{REPO}</u>.")
h2("Secciones del Sitio")
tabla("Secciones del sitio y su contenido", [
    ["Sección", "Contenido"],
    ["1. Identificación", "Título, programa, sede, ciclo, integrantes y aviso de qué es real y qué es simulado."],
    ["2. Planteamiento del problema", "Necesidad, contexto y pregunta del proyecto."],
    ["3. Justificación", "Población beneficiaria y pertinencia de la solución."],
    ["4. Objetivos", "Objetivo general y seis objetivos específicos."],
    ["5. Marco referencial", "Código de colores en Colombia, generación de residuos, antecedente IoT, "
                             "dispositivos, CRISP-DM y modelado dimensional."],
    ["6. Metodología y cronograma", "Fases de CRISP-DM con actividades y evidencia; fechas verificables."],
    ["7. Desarrollo de la solución", "Pines, usuarios, dispositivos, reglas, procesos, arquitectura, tecnologías "
                                     "y actualización de los datos (tramos A y B)."],
    ["8. Gestión de los datos", "Fuente, período, registros, variables, modelo relacional, modelo estrella, "
                                "simulación y ETL en SSIS."],
    ["9. Dashboard y análisis", "Informe de Power BI insertado, preguntas, cinco indicadores, análisis "
                                "univariados, bivariados y multivariado con gráficas."],
    ["10. Conocimientos evidentes", "Cinco conocimientos, cada uno con visualización y ocho elementos."],
    ["11. Validación y decisiones", "Validación, tamaño de grupos, faltantes, atípicos y dos decisiones."],
    ["12. Productos y resultados", "Productos esperados y alcanzados; galería de evidencias."],
    ["13. Conclusiones", "Cumplimiento de objetivos, limitaciones y oportunidades de mejora."],
    ["14. Referencias", "Fuentes consultadas con su enlace."],
], [2.0, 4.5])
h2("Archivos del Sitio")
tabla("Archivos que componen el sitio publicado (carpeta docs/ del repositorio)", [
    ["Archivo", "Función"],
    ["index.html", "Contenido de las catorce secciones."],
    ["css/estilos.css", "Diseño: menú lateral, tablas, tarjetas de indicadores, modo claro y oscuro, "
                        "adaptación a celular."],
    ["js/config.js", "Vínculo público del informe de Power BI (POWERBI_URL) y texto de la frecuencia de "
                     "actualización. Si el vínculo está vacío, el sitio muestra un aviso de pendiente."],
    ["js/datos.js", "Valores de las consultas que alimentan las gráficas del sitio y lista de evidencias."],
    ["js/graficos.js", "Dibuja las gráficas y los diagramas de los modelos, e inserta el iframe de Power BI."],
    ["img/evidencias/", "Capturas y fotografías de evidencia (el sitio muestra las que existan)."],
    ["informe/", "Este informe en PDF."],
    [".nojekyll", "Indica a GitHub Pages que publique los archivos tal como están."],
], [1.5, 5.0])
h2("Organización del Repositorio")
tabla("Carpetas del repositorio", [
    ["Carpeta", "Contenido"],
    ["docs/", "Sitio publicado (fuente de GitHub Pages: rama main, carpeta /docs)."],
    ["consultas/", "Siete consultas T-SQL numeradas (00 a 06) y sus resultados en consultas/resultados/."],
    ["automatizacion/", "Scripts de la tarea programada del ETL: instalación de Integration Services, "
                        "ejecución, registro de la tarea y guardado cifrado de la credencial."],
    ["powerbi/", "Proyecto de Power BI (formato PBIP: informe en PBIR y modelo en TMDL), tema visual y guía."],
    ["informe/", "Generador de este PDF y capturas usadas en él."],
], [1.5, 5.0], nota="La contraseña de SQL Server no está en el repositorio: el archivo del servidor Python que "
                    "la contiene está excluido con .gitignore y la tarea programada la lee cifrada con la "
                    "cuenta de Windows.")

# ================================================================== ORIGEN Y PREPARACIÓN
h1("Origen y Preparación de los Datos")
h2("Captura en la Maqueta")
p("Una ESP32 DevKit V1 controla las tres canecas. Cada caneca tiene un sensor infrarrojo FC-51 que detecta la "
  "mano, un sensor láser VL53L0X que mide la distancia de la tapa a los residuos y un servo SG90 que abre la tapa "
  "a 85°; un buzzer compartido da la alarma. La distancia se convierte en porcentaje entre la caneca vacía "
  "(80 mm) y la llena (30 mm). Desde 95 % la tapa ya no abre y cada intento se registra como evento "
  "<i>bloqueo_llena</i>; la alarma suena cuando las tres canecas superan 90 % al mismo tiempo. Cada 10 segundos "
  "se guarda una lectura por caneca.")
p("La ESP32 envía cada lectura, evento y alarma por WiFi, en JSON, a un servidor en Python con Flask y pyodbc "
  "(Pallets, s. f.), que valida el mensaje (porcentaje entre 0 y 100, caneca entre 1 y 3, tipo de evento "
  "permitido) y lo inserta en la base operacional <i>Vertedero</i> de SQL Server 2022. Una distancia de −1 (el "
  "láser no midió) se guarda como valor nulo.")
tabla("Recorrido del dato", [
    ["Paso", "Componente", "Función"],
    ["1", "ESP32 con sensores y servos", "Mide cada 10 s y registra aperturas, cierres, bloqueos y alarmas."],
    ["2", "WiFi, HTTP", "JSON a /lectura, /evento y /alarma."],
    ["3", "Servidor Python (Flask y pyodbc)", "Valida e inserta."],
    ["4", "Vertedero (SQL Server)", "Base operacional: seis tablas."],
    ["5", "ETL en SSIS (VertederoETL)", "Nueve paquetes; carga incremental cada 5 minutos."],
    ["6", "VertederoDW (SQL Server)", "Data warehouse en modelo estrella."],
    ["7", "Power BI", "Dashboard publicado e insertado en el sitio."],
], [0.5, 2.3, 3.7])
figura("Maqueta con las tres canecas", "Fotografía tomada por el equipo.",
       pendiente=("01_maqueta_general.jpg",
                  "La maqueta completa con las tres canecas (blanca, negra y verde) montadas en la ciudad.",
                  "Fotografía de frente, con buena luz, en la que se vean las tres tapas y los sensores."))
figura("Servidor Python recibiendo datos de la ESP32",
       "Captura de la consola del servidor durante una prueba con la maqueta.",
       pendiente=("05_servidor_python.png",
                  "La consola de servidor_canecas.py con varias líneas de lecturas y eventos recibidos de la ESP32.",
                  "Ejecutar el servidor, encender la maqueta, esperar unos 30 segundos y capturar la ventana "
                  "(Windows + Shift + S). Verificar que no se vea ninguna contraseña."))
h2("Fuente, Período, Registros y Variables")
tabla("Características de los datos analizados", [
    ["Elemento", "Detalle"],
    ["Fuente", "Data warehouse VertederoDW (SQL Server 2022), cargado desde la base operacional Vertedero por "
               "el ETL en SSIS."],
    ["Período simulado (el que se analiza)", "27 de septiembre de 2026 00:00:00 a 4 de noviembre de 2026 "
                                             "13:55:30: 39 días con datos (38 completos; el 4 de noviembre tiene "
                                             "15.040 de 25.920 lecturas)."],
    ["Período real", "6 de noviembre de 2026 22:59:55 a 7 de noviembre de 2026 10:17:12."],
    ["Registros", "Lecturas: 1.000.933 (1.000.000 simuladas y 933 reales). Eventos: 7.741 (7.495 simulados y "
                  "246 reales). Alarmas: 3 (todas simuladas)."],
    ["Variables de medida", "Porcentaje de llenado (0–100), distancia (mm), peso simulado (g), cantidad de "
                            "eventos, duración de alarma (min)."],
    ["Variables de análisis", "Caneca y tipo de residuo, fecha, día de la semana, tipo de día (laborable o fin "
                              "de semana), hora, franja horaria, estado de llenado, tipo de evento."],
], [1.9, 4.6], nota="El 13 de noviembre de 2026 se cargaron además tres lecturas de prueba (identificadores "
                    "1.000.934 a 1.000.936) para verificar la carga automática de punta a punta; no hacen parte "
                    "de las 933 lecturas reales ni del período analizado.")
h2("Simulación del Millón de Mediciones")
p("La maqueta solo produce unas pocas lecturas reales por sesión de pruebas. Para tener un volumen analizable "
  "se generó un millón de lecturas simuladas, con sus eventos y alarmas, que se cargaron en <i>Vertedero</i> "
  "con BULK INSERT desde archivos CSV. Los supuestos fueron:")
lista([
    "<b>Período y frecuencia:</b> 27 de septiembre a 4 de noviembre de 2026, una lectura por caneca cada 10 "
    "segundos (333.334, 333.333 y 333.333 lecturas por caneca).",
    "<b>Uso durante el día:</b> más aperturas en la mañana, al almuerzo y al final de la tarde.",
    "<b>Fin de semana:</b> 30 % menos uso que en días laborables.",
    "<b>Recolección:</b> todos los días a las 6:00, excepto los domingos; al recolectar, la caneca queda casi "
    "vacía.",
    "<b>Fallas del sensor:</b> 0,05 % de lecturas sin distancia (resultaron 521).",
    "<b>Reglas del dispositivo:</b> aperturas con llenado menor a 95 %, bloqueos con 95 % o más, y alarma "
    "cuando las tres canecas pasan de 90 %, que se apaga con la recolección de las 6:00.",
    "<b>Peso:</b> calculado a partir del volumen de la caneca (409,5 cm³) y de la densidad del cartón y el "
    "papel, en proporción al llenado (entre 0 y 49,8 g). Las lecturas reales tienen el peso nulo.",
])
p("Consecuencia: los patrones de los datos (picos de uso, efecto del domingo, diferencias entre canecas) son "
  "los que la simulación introdujo. El análisis demuestra que el proceso completo —medir, cargar, calcular e "
  "interpretar— funciona y qué decisiones permitiría tomar; no demuestra cómo se comportan canecas reales.")
h2("Modelo Relacional y Modelo Estrella")
p("La base operacional <i>Vertedero</i> tiene seis tablas. <i>Canecas</i> es la tabla central; sensores, "
  "actuadores, lecturas y eventos se relacionan con ella por <i>id_caneca</i>. <i>Alarmas</i> no tiene llave "
  "foránea porque una alarma corresponde a las tres canecas a la vez. El data warehouse <i>VertederoDW</i> es "
  "un modelo estrella con tres tablas de hechos y cinco dimensiones; cada dimensión tiene una fila "
  "«Desconocido» con llave −1 para que ningún hecho quede sin dimensión.")
tabla("Tablas del data warehouse VertederoDW", [
    ["Tabla", "Grano o contenido", "Filas"],
    ["FactLecturas", "Una fila por lectura de un sensor de nivel", "1.000.933"],
    ["FactEventos", "Una fila por evento de tapa (apertura, cierre, bloqueo)", "7.741"],
    ["FactAlarmas", "Una fila por alarma conjunta, con su duración", "3"],
    ["DimFecha", "Calendario desde el 27 de septiembre de 2026, con día de la semana y tipo de día", "462"],
    ["DimHora", "24 horas con franja (madrugada 0–5, mañana 6–11, tarde 12–17, noche 18–23) y jornada", "25"],
    ["DimCaneca", "Las tres canecas con residuo, color y pines", "4"],
    ["DimEstadoLlenado", "Sin lectura; Con espacio (0–89); Casi llena (90–94); Llena (95–100)", "5"],
    ["DimTipoEvento", "apertura, cierre, bloqueo_llena", "4"],
], [1.5, 4.2, 0.8], nota="Conteos de las consultas del 13 de noviembre de 2026, antes de la lectura de prueba. "
                         "Los conteos de las dimensiones incluyen la fila «Desconocido».")
h2("Proceso ETL en SQL Server Integration Services")
p("El ETL es el proyecto <i>VertederoETL</i> de SQL Server Integration Services (Microsoft, s. f.-a), con "
  "dos conexiones OLE DB de proyecto (<i>Origen</i> y <i>DW</i>) cuyos datos de conexión vienen de parámetros; "
  "la contraseña es un parámetro sensible cifrado. El paquete maestro <i>00_Maestro.dtsx</i> abre un lote en "
  "el registro <i>etl.LogEjecucion</i>, ejecuta los paquetes de dimensiones (01 a 05), luego los de hechos "
  "(11 a 13) y cierra el lote como «OK» o «Error». Un controlador <i>OnError</i> escribe cualquier falla en el "
  "registro.")
tabla("Paquetes del ETL y sus transformaciones", [
    ["Paquete", "Transformaciones principales"],
    ["01_DimFecha", "Calendario generado; columnas derivadas (llave aaaammdd, mes y día en español, semana, fin "
                    "de semana, tipo de día); búsqueda y detección de cambios."],
    ["02_DimHora", "24 horas; franja y jornada derivadas; búsqueda y detección de cambios."],
    ["03_DimCaneca", "Rechaza llave nula o nombre vacío; normaliza textos; homologa residuo y color con tabla "
                     "de equivalencias; deriva es_aprovechable."],
    ["04_DimTipoEvento", "Rechaza tipo vacío; consolida sinónimos (búsqueda y agregación); deriva grupo y "
                         "es_alerta."],
    ["05_DimEstadoLlenado", "Cuatro rangos de la regla de negocio; deriva requiere_atencion."],
    ["11_FactLecturas", "Carga incremental por marca de agua; reglas R1 a R5 (llave nula, porcentaje fuera de "
                        "0–100, valores negativos, fecha futura, fecha anterior a 2020); conversión del peso; "
                        "estado de llenado; búsquedas de llaves (−1 si no hay coincidencia)."],
    ["12_FactEventos", "Carga incremental; reglas R1 a R4; normalización del tipo; búsquedas de llaves."],
    ["13_FactAlarmas", "Carga completa y sincronización (inserta, actualiza o elimina); reglas R1 a R5; duración "
                       "en minutos y porcentaje máximo."],
], [1.6, 4.9], nota="Las dimensiones aplican dimensión lentamente cambiante de tipo 1: una búsqueda separa las "
                    "filas nuevas y una división condicional envía a una tabla temporal solo las que cambiaron. "
                    "Las filas que incumplen una regla se guardan en tablas etl.Rechazo_* con la etapa y el motivo.")
p("<b>Resultado de las reglas de calidad en la carga:</b> 0 filas rechazadas, 0 filas con llave desconocida "
  "(−1) y 0 duplicados; los conteos del data warehouse coinciden con los de la base operacional (diferencia 0 "
  "en el registro).", "sin")
h2("Actualización Automática")
p("<b>Tramo A (de Vertedero a VertederoDW).</b> Desde el 13 de noviembre de 2026 una tarea del Programador de "
  "tareas de Windows, «Canecas - ETL VertederoDW», ejecuta <i>00_Maestro.dtsx</i> cada 5 minutos con la "
  "utilidad dtexec (Microsoft, s. f.-c), sin abrir Visual Studio. La primera prueba falló con el error "
  "0xC000F427, porque fuera de Visual Studio los flujos de datos requieren Integration Services de una edición "
  "Standard o superior y el equipo solo tenía SQL Server Express; se instaló la característica Integration "
  "Services de SQL Server 2022 Developer Edition (Microsoft, s. f.-d), que es gratuita para desarrollo y "
  "pruebas. La tarea corre solo con el computador encendido y la sesión iniciada.")
p("<b>Tramo B (de VertederoDW a Power BI).</b> El modelo de Power BI está en modo Importar y el informe se "
  "publicó con «Publicar en la web» (Microsoft, s. f.-e), cuya vista pública se guarda en caché durante una "
  "hora. Para que el informe publicado se actualice solo desde el SQL Server local hace falta una puerta de "
  "enlace y una actualización programada, con un máximo de 8 actualizaciones diarias en capacidad compartida "
  "(Microsoft, s. f.-f, s. f.-g). La puerta de enlace no está instalada: hoy el informe publicado se actualiza "
  "de forma manual, volviendo a publicar desde Power BI Desktop.")

# ================================================================== INDICADORES Y PROCEDIMIENTOS
h1("Indicadores y Procedimientos de Análisis")
h2("Procedimiento")
p("Todos los valores se calcularon con consultas T-SQL sobre <i>VertederoDW</i> para el período simulado (27 de "
  "septiembre a 4 de noviembre de 2026). Las consultas están numeradas en la carpeta <i>consultas/</i> del "
  "repositorio, cada una con su salida en <i>consultas/resultados/</i>, de modo que cualquier valor del informe "
  "puede repetirse. El dashboard de Power BI calcula los mismos indicadores con medidas DAX y se comprobó que "
  "coinciden con las consultas (valores de control en powerbi/LEEME.md).")
tabla("Consultas de análisis", [
    ["Archivo", "Contenido"],
    ["00_alcance_y_calidad.sql", "Período, conteos, faltantes, rangos y duplicados."],
    ["01_indicadores.sql", "Los cinco indicadores generales, en total y por caneca."],
    ["02_univariados.sql", "U1 distribución del llenado; U2 eventos por tipo; U3 aperturas por hora."],
    ["03_bivariados.sql", "B1 caneca × llenado; B2 día de la semana × bloqueos; B3 hora × llenado por caneca."],
    ["04_multivariado.sql", "Caneca × franja horaria × tipo de día (24 celdas) en una sola consulta."],
    ["05_conocimientos_y_decisiones.sql", "Comprobaciones de los cinco conocimientos y de las dos decisiones."],
    ["06_datos_reales_esp32.sql", "Resumen de los datos reales de la maqueta (excluye las lecturas de prueba)."],
], [2.4, 4.1])
h2("Preguntas que Orientan el Análisis")
lista([
    "¿Qué tan llenas permanecen las canecas y cuánto tiempo pasan en estado crítico?",
    "¿A qué horas se usan más y a qué horas están más llenas?",
    "¿Hay diferencias entre las tres canecas según el tipo de residuo?",
    "¿En qué días se concentran los intentos fallidos por caneca llena?",
    "¿En qué combinación de caneca, franja horaria y tipo de día es más probable encontrar la caneca llena?",
], numerada=True)
h2("Cinco Indicadores Generales")
tabla("Indicadores generales del período simulado", [
    ["Indicador", "Valor", "Cálculo y detalle"],
    ["Llenado promedio", "57,36 %", "Promedio del porcentaje en 1.000.000 de lecturas. C1 60,89; C2 50,92; "
                                    "C3 60,29."],
    ["Lecturas en estado crítico (≥ 90 %)", "16,26 %", "162.580 lecturas. C1 22,79; C2 5,98; C3 20,00."],
    ["Aperturas por día", "93,41", "3.643 aperturas en 39 días. C1 31,74; C2 24,95; C3 36,72."],
    ["Tasa de bloqueo", "5,43 %", "209 bloqueos ÷ 3.852 intentos (aperturas + bloqueos)."],
    ["Alarmas conjuntas", "3", "44,32 horas en total; 14,77 horas en promedio (de 10,32 a 17,82)."],
], [1.9, 0.8, 3.8], nota="La tasa de bloqueo divide los bloqueos entre los intentos de uso (aperturas más "
                         "bloqueos). Las aperturas por día dividen entre los 39 días con datos, uno de ellos "
                         "incompleto.")
h2("Análisis Univariados")
tabla("Resultados de los análisis univariados", [
    ["Análisis", "Resultado"],
    ["U1. Distribución del porcentaje de llenado (n = 1.000.000)",
     "Promedio 57,36 %, mediana 62 %, cuartiles 33 % y 83 %, desviación estándar 28,48, mínimo 0 % y máximo "
     "97 %. Por estado: Con espacio 83,69 %, Casi llena 3,52 %, Llena 12,74 %, Sin lectura 0,05 %. La mediana "
     "supera al promedio: la cola de valores bajos (horas posteriores a la recolección) reduce el promedio."],
    ["U2. Eventos por tipo (n = 7.495)",
     "Aperturas 3.643 (48,61 %), cierres 3.643 (48,61 %), bloqueos por caneca llena 209 (2,79 %)."],
    ["U3. Aperturas por hora (n = 3.643)",
     "Máximo a las 12 h (509; 13,97 %), luego 7 h (437; 12,00 %) y 18 h (403; 11,06 %). Entre las 0 y las 5 h "
     "hay 39 aperturas en total."],
], [2.2, 4.3])
h2("Análisis Bivariados")
tabla("Bivariado 1: caneca × llenado", [
    ["Caneca", "Promedio", "Mediana", "Lecturas ≥ 90 %", "Aperturas por día", "Tasa de bloqueo"],
    ["C1 Aprovechables", "60,89 %", "68 %", "22,79 %", "31,74", "5,06 % (66 de 1.304)"],
    ["C2 No aprovechables", "50,92 %", "54 %", "5,98 %", "24,95", "2,70 % (27 de 1.000)"],
    ["C3 Orgánicos", "60,29 %", "65 %", "20,00 %", "36,72", "7,49 % (116 de 1.548)"],
], [1.5, 0.8, 0.75, 1.05, 1.0, 1.4], nota="Unas 333.333 lecturas por caneca.")
tabla("Bivariado 2: día de la semana × bloqueos", [
    ["Día", "Días", "Aperturas por día", "Bloqueos", "% de los bloqueos", "Tasa de bloqueo"],
    ["Lunes", "6", "105,67", "10", "4,78 %", "1,55 %"],
    ["Martes", "6", "107,17", "14", "6,70 %", "2,13 %"],
    ["Miércoles", "6", "102,00", "13", "6,22 %", "2,08 %"],
    ["Jueves", "5", "101,60", "22", "10,53 %", "4,15 %"],
    ["Viernes", "5", "110,40", "16", "7,66 %", "2,82 %"],
    ["Sábado", "5", "77,20", "1", "0,48 %", "0,26 %"],
    ["Domingo", "6", "51,33", "133", "63,64 %", "30,16 %"],
], [1.1, 0.6, 1.3, 0.9, 1.3, 1.3], nota="n = 209 bloqueos. Por tipo de día: laborable 105,32 aperturas por día "
                                       "(28 días) y fin de semana 63,09 (11 días).")
p("<b>Bivariado 3: hora del día × llenado promedio, por caneca.</b> Unas 42.000 lecturas por hora. En todo el "
  "período el promedio más bajo es 10,77 % a las 6 h y el más alto 78,82 % a las 23 h; entre las 0 y las 5 h se "
  "mantiene entre 77,07 % y 77,72 %.", "sin")
h2("Análisis Multivariado")
p("Una sola consulta (<i>04_multivariado.sql</i>) agrupa por caneca, franja horaria y tipo de día (24 celdas) y "
  "calcula el llenado, las aperturas, los bloqueos y la tasa de bloqueo de cada celda. Las celdas tienen entre "
  "23.760 y 60.480 lecturas, pero en la madrugada los eventos son escasos (entre 2 y 13 aperturas por celda), así "
  "que esas tasas se marcan como no confiables. La celda más crítica con suficientes intentos es C3 × noche × "
  "fin de semana, con una tasa de bloqueo de 49,45 % (45 bloqueos y 46 aperturas en 11 días); se detalla en el "
  "conocimiento 5.")
h2("Dashboard en Power BI")
p("El informe de Power BI (Microsoft, s. f.-b) tiene cuatro páginas sobre un lienzo de 1280 × 720, con un "
  "filtro de página para el período simulado y segmentaciones de caneca y tipo de día.")
tabla("Páginas del dashboard", [
    ["Página", "Contenido", "Análisis que cubre"],
    ["Estado actual", "Medidores de llenado actual por caneca con umbral de 90 %, última lectura cargada, "
                      "calidad y alarmas.", "Estado del módulo"],
    ["Uso y llenado", "Llenado por hora y caneca, distribución por tramo, llenado por día, aperturas por hora, "
                      "llenado por caneca, aperturas por día y franja.",
     "Indicadores 1 a 3; U1, U3; B1, B3"],
    ["Bloqueos y alarmas", "Bloqueos y tasa por día de la semana, matriz caneca × tipo de día × franja, eventos "
                           "por tipo, bloqueos por caneca, tabla de alarmas.",
     "Indicadores 4 y 5; U2; B2; multivariado"],
    ["Más detalle", "Lecturas por estado, relación llenado–peso simulado, peso por día.", "Apoyo"],
], [1.4, 3.4, 1.7])

# ================================================================== CONOCIMIENTOS
h1("Documentación de los Cinco Conocimientos")
p("Cada conocimiento es un hallazgo verificable del escenario simulado y se documenta con ocho elementos: "
  "pregunta, variables, procedimiento, resultado, hallazgo, interpretación, utilidad y limitación.")
K = [
    ("Conocimiento 1. El Llenado Sigue un Ciclo Diario que se Reinicia con la Recolección de las 6:00, Excepto "
     "el Domingo", [
        ("Pregunta", "¿A qué horas están más llenas y más vacías las canecas? Saberlo indica si la hora de "
                     "recolección es adecuada."),
        ("Variables", "Porcentaje de llenado (FactLecturas.porcentaje), hora (DimHora) y día de la semana "
                      "(DimFecha)."),
        ("Procedimiento", "Promedio del porcentaje agrupado por hora sobre 1.000.000 de lecturas; después, el "
                          "mismo promedio separando los domingos (6 días) del resto (33 días). Consulta "
                          "03_bivariados.sql, bloques B3 y B3.b."),
        ("Resultado", "En todo el período, el promedio más bajo es 10,77 % a las 6 h y el más alto 78,82 % a las "
                      "23 h; entre las 0 y las 5 h se mantiene entre 77,07 % y 77,72 %. De lunes a sábado, el "
                      "promedio a las 6 h es 3,35 %; los domingos es 51,58 % a esa hora y llega a 89,09 % a las "
                      "22 h."),
        ("Hallazgo", "El llenado cae a su mínimo a las 6 h y crece durante el día hasta la noche. Los domingos "
                     "esa caída no ocurre: la curva parte de la mitad y termina cerca del 90 %."),
        ("Interpretación", "Las canecas pasan la noche y la madrugada con el nivel más alto del día, cuando casi "
                           "nadie las usa, y quedan vacías justo antes del primer pico de uso. El domingo acumula "
                           "lo del sábado más lo propio."),
        ("Utilidad", "Permite evaluar la hora de recolección y muestra que el día sin recolección es el punto "
                     "débil del esquema."),
        ("Limitación", "La recolección a las 6:00 y su ausencia el domingo son supuestos de la simulación; el "
                       "resultado confirma que los datos los reflejan, no que una ciudad real se comporte así. El "
                       "promedio por hora oculta la variación entre días."),
    ]),
    ("Conocimiento 2. La Caneca de No Aprovechables (C2) se Llena Menos y Pasa Menos Tiempo en Estado Crítico", [
        ("Pregunta", "¿Las tres canecas se comportan igual o alguna necesita más atención?"),
        ("Variables", "Caneca y tipo de residuo (DimCaneca), porcentaje de llenado, y eventos de apertura y "
                      "bloqueo (FactEventos)."),
        ("Procedimiento", "Por caneca: promedio y mediana del llenado, porcentaje de lecturas con 90 % o más, "
                          "aperturas por día y tasa de bloqueo. Consultas 03_bivariados.sql (B1) y "
                          "01_indicadores.sql (I3 e I4). Cada caneca tiene unas 333.333 lecturas."),
        ("Resultado", "C1: promedio 60,89 %, mediana 68 %, 22,79 % de lecturas ≥ 90 %, 31,74 aperturas por día, "
                      "tasa de bloqueo 5,06 % (66 de 1.304). C2: 50,92 %, 54 %, 5,98 %, 24,95 y 2,70 % (27 de "
                      "1.000). C3: 60,29 %, 65 %, 20,00 %, 36,72 y 7,49 % (116 de 1.548)."),
        ("Hallazgo", "C2 tiene unos 10 puntos menos de llenado promedio que C1 y C3, y pasa en estado crítico "
                     "menos de una tercera parte del tiempo que ellas. C3 es la más usada y la de mayor tasa de "
                     "bloqueo."),
        ("Interpretación", "En las tres canecas la mediana supera al promedio, por las horas de la mañana con la "
                           "caneca casi vacía. La presión sobre la capacidad se concentra en C1 y C3; C2 tiene "
                           "holgura."),
        ("Utilidad", "Indica cuáles canecas priorizar si solo se puede hacer un vaciado adicional o ampliar la "
                     "capacidad."),
        ("Limitación", "La diferencia entre canecas proviene de los ritmos de llenado que definió la simulación. "
                       "No demuestra que los residuos no aprovechables se generen menos en la realidad."),
    ]),
    ("Conocimiento 3. Ocho de Cada Diez Aperturas Ocurren en Tres Bloques de Tres Horas", [
        ("Pregunta", "¿El uso de las canecas se reparte durante el día o se concentra en pocas horas?"),
        ("Variables", "Eventos de tipo apertura (FactEventos con DimTipoEvento) y hora del evento (DimHora)."),
        ("Procedimiento", "Conteo de aperturas por hora y porcentaje sobre el total; después, suma por bloques. "
                          "Consulta 02_univariados.sql, bloques U3 y U3.b."),
        ("Resultado", "De 6 a 8 h: 972 aperturas (26,68 %). De 11 a 13 h: 1.096 (30,09 %). De 17 a 19 h: 872 "
                      "(23,94 %). Las otras 15 horas suman 703 (19,30 %)."),
        ("Hallazgo", "Nueve horas del día reúnen 2.940 de las 3.643 aperturas, el 80,70 %."),
        ("Interpretación", "El uso coincide con la mañana, el almuerzo y el final de la tarde. Fuera de esos "
                           "bloques las canecas casi no se usan."),
        ("Utilidad", "Señala las horas en que una caneca llena afecta a más personas y las horas valle en que un "
                     "vaciado o un mantenimiento estorbaría menos."),
        ("Limitación", "Los tres picos son un supuesto de la simulación. Los bloqueos no cuentan como aperturas, "
                       "de modo que en las horas con canecas llenas el uso intentado es mayor que el que se "
                       "muestra."),
    ]),
    ("Conocimiento 4. Los Domingos Concentran el 63,64 % de los Bloqueos por Caneca Llena", [
        ("Pregunta", "¿En qué días las personas encuentran más veces la caneca llena?"),
        ("Variables", "Eventos de apertura y de bloqueo (FactEventos), día de la semana (DimFecha) y alarmas "
                      "(FactAlarmas)."),
        ("Procedimiento", "Conteo de bloqueos y aperturas por día de la semana, dividido entre el número de días "
                          "de cada grupo; tasa de bloqueo = bloqueos ÷ (aperturas + bloqueos). Luego se revisó "
                          "cada domingo por separado. Consultas 03_bivariados.sql (B2.a) y "
                          "05_conocimientos_y_decisiones.sql (K4)."),
        ("Resultado", "Los 6 domingos reúnen 133 de los 209 bloqueos (63,64 %), con 22,17 bloqueos por día y una "
                      "tasa de 30,16 %. En los demás días la tasa está entre 0,26 % (sábado) y 4,15 % (jueves). "
                      "Cinco de los seis domingos tuvieron entre 19 y 37 bloqueos; el primero (27 de septiembre, "
                      "inicio de la simulación) tuvo 0. Dos de las tres alarmas conjuntas empezaron en domingo. "
                      "El llenado promedio del domingo es 70,28 %, frente a 54,99 % de lunes a sábado."),
        ("Hallazgo", "El 15 % de los días (6 de 39) concentra casi dos tercios de los bloqueos, aunque el "
                     "domingo es el día con menos aperturas (51,33 por día)."),
        ("Interpretación", "En el escenario simulado, el día con más intentos fallidos coincide con el único día "
                           "sin recolección. Menos aperturas el domingo no significa menos demanda: parte de los "
                           "intentos termina en bloqueo."),
        ("Utilidad", "Sustenta la primera decisión: revisar la recolección del domingo."),
        ("Limitación", "Es una asociación entre el día y los bloqueos dentro de datos simulados, con solo 6 "
                       "domingos. No se puede afirmar cuánto bajarían los bloqueos con una recolección dominical "
                       "sin probarlo."),
    ]),
    ("Conocimiento 5. La Combinación más Crítica es la Caneca de Orgánicos (C3), en la Noche, en Fin de Semana", [
        ("Pregunta", "¿En qué combinación de caneca, franja horaria y tipo de día es más probable que alguien "
                     "encuentre la caneca llena?"),
        ("Variables", "Caneca (DimCaneca), franja horaria (DimHora), tipo de día (DimFecha), aperturas y "
                      "bloqueos (FactEventos) y porcentaje de llenado (FactLecturas)."),
        ("Procedimiento", "Una sola consulta agrupa por las tres variables a la vez (24 celdas) y calcula llenado, "
                          "aperturas, bloqueos y tasa de bloqueo. Consulta 04_multivariado.sql; el fin de semana "
                          "se separó después en sábado y domingo (05, bloque K5.a)."),
        ("Resultado", "C3 × noche × fin de semana: 45 bloqueos y 46 aperturas en 11 días, tasa de 49,45 % y "
                      "45,44 % de las lecturas con 90 % o más. La misma caneca y franja en día laborable: 9,03 % "
                      "(26 bloqueos, 262 aperturas). En la noche de fin de semana, C1 tiene 32,69 % y C2 19,23 %. "
                      "Al separar el fin de semana, los 45 bloqueos de C3 en la noche son todos de domingo (45 "
                      "bloqueos frente a 5 aperturas); el sábado tuvo 41 aperturas y ningún bloqueo."),
        ("Hallazgo", "La tasa de bloqueo más alta con un número suficiente de intentos está en C3, de 18 a 23 h, "
                     "en fin de semana: uno de cada dos intentos falla. Ese resultado no se deduce de mirar por "
                     "separado la caneca (7,49 %), la franja o el tipo de día (16,18 %)."),
        ("Interpretación", "El problema no es «el fin de semana» en general sino la noche del domingo, y afecta "
                           "sobre todo a la caneca más usada."),
        ("Utilidad", "Permite dirigir una acción a un punto preciso (qué caneca, cuándo) en lugar de aumentar la "
                     "recolección en general."),
        ("Limitación", "Algunas celdas tienen muy pocos casos: las de madrugada muestran tasas de 30,77 % con "
                       "solo 13 intentos y no son confiables. La celda destacada tiene 91 intentos en 11 días. "
                       "Los datos son simulados."),
    ]),
]
for titulo, elementos in K:
    h2(titulo)
    tabla("Elementos del " + titulo.split(".")[0].lower(),
          [["Elemento", "Contenido"]] + [[a, b] for a, b in elementos], [1.3, 5.2])

# ================================================================== VALIDACIONES
h1("Validaciones")
h2("Validación de los Hallazgos")
tabla("Preguntas de validación aplicadas a los cinco conocimientos", [
    ["Pregunta de validación", "Respuesta"],
    ["¿Se obtiene directamente de los datos?", "Sí. Cada valor sale de una consulta sobre VertederoDW; no hay "
                                               "cifras estimadas."],
    ["¿El procedimiento puede repetirse?", "Sí. Las siete consultas están numeradas en consultas/, con la salida "
                                           "obtenida el 13 de noviembre de 2026."],
    ["¿La gráfica corresponde a las variables?", "Sí. Cada gráfica del sitio usa los valores de su consulta e "
                                                 "indica unidad, período y tamaño del grupo."],
    ["¿Se compararon cantidades y porcentajes?", "Sí. Los bloqueos se presentan como conteo, porcentaje del total "
                                                 "y tasa sobre los intentos; las aperturas, como total y por día."],
    ["¿Los grupos tienen suficientes registros?", "Ver «Tamaño de los grupos comparados»."],
    ["¿Influyen faltantes o valores atípicos?", "Ver «Valores faltantes» y «Valores atípicos e inusuales»."],
    ["¿Se evitó afirmar causalidad?", "Sí. Las relaciones se describen como asociaciones dentro del escenario "
                                      "simulado."],
    ["¿Responde al problema del proyecto?", "Sí. Los cinco conocimientos tratan del llenado, el uso y los "
                                            "intentos fallidos, base para programar la recolección."],
], [2.4, 4.1])
h2("Tamaño de los Grupos Comparados")
lista([
    "<b>Canecas:</b> 333.334, 333.333 y 333.333 lecturas; grupos equilibrados.",
    "<b>Días de la semana:</b> entre 5 y 6 días por grupo (lunes, martes, miércoles y domingo 6; jueves, "
    "viernes y sábado 5). Son pocos días; por eso se revisó cada domingo por separado.",
    "<b>Tipo de día:</b> 28 días laborables y 11 de fin de semana; se comparan valores por día y tasas, no "
    "totales.",
    "<b>Franjas horarias:</b> entre 246.240 y 252.720 lecturas por franja.",
    "<b>Celdas del multivariado:</b> entre 23.760 y 60.480 lecturas, pero pocos eventos en la madrugada (entre 2 "
    "y 13 aperturas por celda); esas tasas no se usan en las decisiones.",
    "<b>Alarmas:</b> solo 3; se describen una por una, sin promedios concluyentes.",
])
h2("Valores Faltantes")
lista([
    "<b>Distancia nula:</b> 521 lecturas simuladas (0,05 %), repartidas entre las tres canecas (189, 175 y 157), "
    "con porcentaje 0 y clasificadas como «Sin lectura». No se eliminaron: el llenado promedio con todas las "
    "lecturas es 57,36 % y con solo las válidas, 57,39 %.",
    "<b>Peso nulo:</b> las 933 lecturas reales no tienen peso porque la maqueta no tiene sensor de peso. El peso "
    "no se usa en ningún conocimiento ni decisión.",
])
h2("Valores Atípicos e Inusuales")
lista([
    "<b>Rangos:</b> en los datos simulados el porcentaje va de 0 a 97 y la distancia de 28 a 83 mm; ningún "
    "porcentaje está fuera de 0–100.",
    "<b>Día incompleto:</b> el 4 de noviembre de 2026 tiene 15.040 lecturas en lugar de 25.920; se conservó.",
    "<b>Primer día:</b> el domingo 27 de septiembre no tuvo bloqueos porque la simulación empieza con las "
    "canecas vacías; se conservó y se menciona en el conocimiento 4.",
    "<b>Jueves 8 de octubre:</b> 21 bloqueos, inusual para un día laborable; coincide con la segunda alarma "
    "conjunta (empezó ese día a las 19:41). Es coherente y se conservó.",
    "<b>Cierres con 95 % o más:</b> 28 cierres; la caneca llegó al umbral con ese mismo depósito. Ninguna "
    "apertura ocurre con 95 % o más y ningún bloqueo con menos.",
    "<b>Datos reales:</b> en las pruebas la distancia llega a 153 mm, más que la caneca vacía (80 mm), y C1 "
    "registró los 24 bloqueos reales. Son pruebas manuales de calibración; por eso no se mezclan con el análisis.",
])
h2("Validación del ETL y de la Carga Automática")
log = leer_log_etl()
filas_v = [
    ["Validación", "Resultado"],
    ["Conciliación origen–destino", "Diferencia 0 entre Vertedero y VertederoDW; 0 rechazos, 0 llaves "
                                    "desconocidas y 0 duplicados."],
    ["Carga incremental", "Una segunda ejecución del 12 de noviembre extrajo 0 lecturas y 0 eventos nuevos y los "
                          "conteos no cambiaron (1.000.933 lecturas y 7.741 eventos)."],
    ["Prueba de punta a punta", "Se envió una lectura de prueba al servidor Python a la 1:09 del 13 de noviembre "
                                "(identificadores 1.000.934 a 1.000.936). La ejecución programada de la 1:11 "
                                "(lote 79) la cargó: FactLecturas pasó de 1.000.933 a 1.000.936 filas, sin "
                                "rechazos."],
]
if log:
    texto = (f"Registro del script entre {log['primera']} y {log['ultima']}: {log['n']} ejecuciones, "
             f"{log['ok']} terminadas en OK y {len(log['err'])} con error.")
    if log["err"]:
        detalles = []
        for e in log["err"]:
            m = re.search(r"^(\S+ \S+) \|.*lote (\d+)", e)
            detalles.append(f"lote {m.group(2)} ({m.group(1)})" if m else e[:40])
        texto += (" Error en " + ", ".join(detalles) + ": falla del flujo de datos de DimCaneca («Unspecified "
                  "error»), sin causa identificada; no tocó las tablas de hechos y la ejecución siguiente "
                  "terminó en OK.")
    filas_v.append(["Ejecuciones de la tarea programada", texto])
    filas_v.append(["Suspensión del equipo", "Una ejecución iniciada a la 1:56 terminó con 17.223,2 s de "
                                             "duración porque el computador entró en suspensión; al reanudar, "
                                             "la tarea siguió cada 5 minutos."])
tabla("Validación del ETL y de la carga automática", filas_v, [2.0, 4.5],
      nota="Fuente: registro etl.LogEjecucion y archivo automatizacion/logs/etl_2026-11.log (horas de Colombia).")

# ================================================================== DECISIONES
h1("Decisiones")
p("Las dos decisiones corresponden al escenario simulado y muestran cómo el análisis orientaría la gestión del "
  "módulo. Cada una se documenta con sus cinco elementos.")
D = [
    ("Decisión 1. Agregar una Recolección el Domingo", [
        ("Acción propuesta", "Programar la recolección de las 6:00 también los domingos, igual que el resto de "
                             "la semana."),
        ("Hallazgo y valores", "Los domingos reúnen 133 de 209 bloqueos (63,64 %) en 6 de 39 días, con una tasa "
                               "de bloqueo de 30,16 % frente a un máximo de 4,15 % en los demás días "
                               "(conocimiento 4). El llenado a las 6 h es 51,58 % en promedio los domingos, frente "
                               "a 3,35 % de lunes a sábado (conocimiento 1), y el 29,22 % de las lecturas "
                               "dominicales tiene 90 % o más, frente a 13,87 % el resto de la semana. Dos de las "
                               "tres alarmas conjuntas empezaron en domingo."),
        ("A qué se dirige", "Al proceso de recolección de las tres canecas, el día domingo."),
        ("Mejora esperada e indicador", "Que la tasa de bloqueo del domingo se acerque a la de los demás días. "
                                        "Indicador: tasa de bloqueo dominical (línea base 30,16 %; referencia de "
                                        "los otros días, entre 0,26 % y 4,15 %). Secundario: bloqueos por domingo "
                                        "(línea base 22,17)."),
        ("Limitaciones", "Datos simulados y solo 6 domingos. La relación entre la falta de recolección y los "
                         "bloqueos es una asociación en el escenario, no un efecto medido. No se evaluó el costo "
                         "de una jornada adicional."),
    ]),
    ("Decisión 2. Hacer un Vaciado Adicional de C1 y C3 antes de las 18:00, de Lunes a Sábado", [
        ("Acción propuesta", "Vaciar las canecas de aprovechables (C1) y de orgánicos (C3) al final de la tarde, "
                             "antes del pico de uso de las 18 h. C2 se mantiene con una sola recolección diaria."),
        ("Hallazgo y valores", "De lunes a sábado, entre las 18 y las 23 h, C1 tiene un llenado promedio de "
                               "78,05 % con 29,53 % de las lecturas en 90 % o más, y C3 tiene 76,97 % y 21,87 %; "
                               "C2 tiene 64,88 % y 4,46 %. La tasa de bloqueo en ese horario es 10,51 % en C1, "
                               "7,90 % en C3 y 4,23 % en C2. El 84,21 % de los bloqueos de lunes a sábado (64 de "
                               "76) ocurre en la franja de la noche (conocimientos 2 y 5), y el bloque de 17 a 19 h "
                               "reúne el 23,94 % de las aperturas (conocimiento 3)."),
        ("A qué se dirige", "A las canecas C1 y C3, en la franja de 18 a 23 h, de lunes a sábado."),
        ("Mejora esperada e indicador", "Menos tiempo en estado crítico y menos intentos fallidos en la noche. "
                                        "Indicador: porcentaje de lecturas con 90 % o más entre las 18 y las 23 h "
                                        "en C1 y C3 (línea base 29,53 % y 21,87 %; referencia, C2 con 4,46 %). "
                                        "Secundario: bloqueos nocturnos de lunes a sábado (línea base 64 en 33 "
                                        "días)."),
        ("Limitaciones", "Datos simulados; la hora del vaciado se eligió con promedios por hora, que ocultan la "
                         "variación entre días. Un segundo vaciado tiene un costo que no se evaluó. Si se aplica la "
                         "decisión 1, hay que volver a medir."),
    ]),
]
for titulo, elementos in D:
    h2(titulo)
    tabla("Elementos de la " + titulo.split(".")[0].lower(),
          [["Elemento", "Contenido"]] + [[a, b] for a, b in elementos], [1.6, 4.9])

# ================================================================== EVIDENCIAS
h1("Evidencias de Publicación e Integración")
p("Las figuras de esta sección son capturas reales. Las tomadas por el equipo de desarrollo del informe se "
  "obtuvieron el 13 de noviembre de 2026 con Microsoft Edge sobre el sitio publicado y sobre el vínculo público "
  "del informe; los recuadros marcados como «Espacio para captura» indican la captura exacta que el equipo "
  "debe agregar.")
h2("Publicación del Sitio en GitHub Pages")
tabla("Configuración de la publicación del sitio", [
    ["Elemento", "Valor verificado"],
    ["Dirección pública", SITIO],
    ["Origen de la publicación", "Rama main, carpeta /docs del repositorio Juan747-art/canecas-inteligentes"],
    ["HTTPS", "Activado"],
    ["Estado de GitHub Pages", "built (publicado)"],
    ["Despliegue verificado", "Ejecución «pages build and deployment» terminada con éxito el 13 de noviembre de "
                              "2026 (commit {commit})"],
], [2.0, 4.5], nota="Datos consultados con la API de GitHub (gh api repos/Juan747-art/canecas-inteligentes/pages "
                    "y gh run list).")
figura("Portada del sitio publicado", f"Captura de {SITIO} con Microsoft Edge, 1280 × 900 píxeles.",
       archivo=os.path.join(FIG, "sitio_portada.png"))
h2("Publicación del Informe de Power BI")
p("El informe se publicó desde Power BI Desktop en «Mi área de trabajo» y, en el servicio de Power BI, se creó "
  "un vínculo con «Publicar en la web» (Microsoft, s. f.-e). Ese vínculo permite ver el informe sin iniciar "
  "sesión.")
figura("Cuadro de diálogo de «Publicar en la web» en el servicio de Power BI",
       "Captura del servicio de Power BI tomada por el equipo al crear el vínculo público.",
       pendiente=("14_powerbi_servicio.png",
                  "El cuadro «Publicar en la web» con el mensaje de que el vínculo se creó correctamente, el "
                  "vínculo que empieza por https://app.powerbi.com/view?r= y la vista previa del informe.",
                  "Es la captura que el equipo ya tomó al publicar; guardarla con este nombre. Si hay que "
                  "repetirla: app.powerbi.com → informe → Archivo → Insertar informe → Publicar en la web."))
figura("Informe en Power BI Desktop",
       "Captura de Power BI Desktop con el proyecto Tablero Vertedero abierto.",
       pendiente=("13_powerbi_desktop.png",
                  "Power BI Desktop con la página «Uso y llenado» abierta y el panel Datos desplegado, donde se "
                  "vean la tabla Medidas y las tablas del modelo.",
                  "Abrir powerbi/proyecto/Tablero Vertedero.pbip, ir a «Uso y llenado», abrir el panel Datos y "
                  "capturar la ventana completa."))
for i, nombre_pag in enumerate(["Estado actual", "Uso y llenado", "Bloqueos y alarmas", "Más detalle"], 1):
    figura(f"Página «{nombre_pag}» del informe publicado",
           "Captura del vínculo público del informe (https://app.powerbi.com/view?r=…) con Microsoft Edge, sin "
           f"iniciar sesión; página {i} de 4.",
           archivo=os.path.join(FIG, f"pbi_pagina{i}.png"))
h2("Integración del Dashboard en el Sitio")
p("El vínculo público se guardó en <i>docs/js/config.js</i> (constante POWERBI_URL). Al cargar el sitio, "
  "<i>js/graficos.js</i> inserta un iframe con ese vínculo en la sección «Dashboard y análisis», y debajo "
  "muestra el texto de la frecuencia de actualización. Se verificó leyendo el documento que genera el navegador "
  "a partir del sitio publicado.")
tabla("Verificación de la integración en el sitio publicado", [
    ["Comprobación", "Resultado"],
    ["Título de la página", "Ciudad Inteligente · Proyecto de Gestión del Conocimiento"],
    ["Iframe del dashboard", "Presente en la sección Dashboard, con title «Dashboard Canecas Inteligentes en "
                             "Power BI», allowfullscreen y src igual al vínculo de Publicar en la web"],
    ["Aviso «Dashboard pendiente de integrar»", "No aparece (solo se muestra si POWERBI_URL está vacío)"],
    ["Frecuencia de actualización mostrada", "Actualización manual: el informe se publicó el 13 de noviembre de "
                                             "2026; el ETL carga el data warehouse cada 5 minutos, pero el informe "
                                             "publicado solo cambia al volver a publicar."],
], [2.2, 4.3], nota="Lectura del DOM del sitio con Microsoft Edge sin interfaz (--dump-dom).")
figura("Sección «Dashboard y análisis» del sitio con el informe insertado",
       f"Captura de {SITIO}#dashboard con Microsoft Edge, después de esperar la carga del iframe.",
       archivo=os.path.join(FIG, "sitio_dashboard.png"))
figura("Dashboard integrado en el sitio con un filtro aplicado",
       "Captura tomada por el equipo para mostrar que el informe insertado es interactivo.",
       pendiente=("15_sitio_publicado.png",
                  "El sitio publicado, en la sección Dashboard, con la segmentación «Caneca» del informe en C3 "
                  "(o «Tipo de día» en Fin de semana) y los visuales ya filtrados; que se vea la barra de "
                  "direcciones con github.io.",
                  f"Abrir {SITIO}#dashboard en el navegador, aplicar el filtro dentro del informe y capturar la "
                  "ventana completa."))
h2("Ejecución Automática del ETL")
figura("Tarea programada del ETL en el Programador de tareas de Windows",
       "Captura del Programador de tareas tomada por el equipo.",
       pendiente=("12_programador_tareas.png",
                  "La tarea «Canecas - ETL VertederoDW» seleccionada, con las columnas Desencadenadores (cada 5 "
                  "minutos), Hora de la última ejecución y Resultado de la última ejecución («La operación se "
                  "completó correctamente. (0x0)»).",
                  "Windows → Programador de tareas → Biblioteca del Programador de tareas → seleccionar la tarea "
                  "y capturar la ventana."))
figura("Registro de ejecuciones del ETL en SQL Server",
       "Captura de SQL Server Management Studio tomada por el equipo.",
       pendiente=("11_ssms_log_ejecucion.png",
                  "El resultado de SELECT TOP 10 id_lote, paquete, inicio, fin, duracion_seg, estado FROM "
                  "etl.LogEjecucion WHERE paquete = '00_Maestro' ORDER BY id_lote DESC; en VertederoDW, con los "
                  "lotes recientes en estado OK cada 5 minutos.",
                  "SSMS → conectar a localhost\\SQLEXPRESS → Nueva consulta sobre VertederoDW → ejecutar la "
                  "consulta y capturar el editor con los resultados."))

# ================================================================== LIMITACIONES
h1("Limitaciones")
lista([
    "Casi todos los datos son simulados. Los hallazgos describen los supuestos de la simulación y no el "
    "comportamiento de canecas reales en una ciudad.",
    "El período es de 39 días: hay entre 5 y 6 repeticiones de cada día de la semana y solo 3 alarmas.",
    "El peso es simulado y los datos reales son pruebas cortas de calibración (933 lecturas).",
    "La maqueta es de cartón y a escala; las distancias (30 a 80 mm) no representan una caneca de tamaño real.",
    "No hay tiempo real en el sitio: el informe publicado muestra los datos de la última publicación y la vista "
    "pública puede tardar hasta una hora más en reflejar un cambio. La puerta de enlace de Power BI no está "
    "instalada.",
    "La carga automática del ETL depende de que el computador esté encendido y con la sesión iniciada; durante "
    "una suspensión no hay ejecuciones.",
    "No se pudo abrir la ficha técnica oficial del sensor VL53L0X, por lo que no se cita; lo que se dice de ese "
    "sensor proviene del firmware y de las pruebas del equipo.",
])

# ================================================================== CONCLUSIONES
h1("Conclusiones")
lista([
    "El recorrido completo del dato funciona: de la ESP32 a la base operacional, de allí al data warehouse por "
    "medio del ETL en SSIS, y del data warehouse al dashboard de Power BI publicado en el sitio.",
    "El ETL carga 1.000.933 lecturas, 7.741 eventos y 3 alarmas sin rechazos ni duplicados, es incremental y se "
    "ejecuta solo cada 5 minutos; una lectura enviada al servidor llegó al data warehouse en la siguiente "
    "ejecución programada.",
    "El análisis del escenario simulado produjo cinco conocimientos verificables: el ciclo diario del llenado, la "
    "holgura de C2, la concentración del uso en tres bloques horarios, el peso de los domingos en los bloqueos y "
    "la combinación crítica C3 × noche × fin de semana.",
    "De esos conocimientos salen dos decisiones con línea base e indicador de seguimiento: recolectar también el "
    "domingo y hacer un vaciado adicional de C1 y C3 antes de las 18:00.",
    "El dashboard está publicado con «Publicar en la web» e integrado en el sitio; su actualización automática "
    "(puerta de enlace) quedó documentada pero no instalada.",
], numerada=True)
h2("Oportunidades de Mejora")
lista([
    "Dejar la maqueta encendida varios días para reunir datos reales suficientes y contrastarlos con la "
    "simulación.",
    "Instalar la puerta de enlace de Power BI para que el informe publicado se actualice solo.",
    "Agregar un sensor de peso (celda de carga) para dejar de simular esa variable.",
    "Declarar en la base la relación entre FactAlarmas.fecha_fin_key y DimFecha.",
    "Guardar el usuario y la contraseña del servidor Python fuera del código.",
])

# ================================================================== REFERENCIAS
h1("Referencias", nueva_pagina=True)
REFS = [
    "Alsayaydeh, J. A. J., Bacarra, R., Khang, A. W. Y., Yaacob, N. B. M., y Herawan, S. G. (2025). IoT-based "
    "smart waste management system: A solution for urban sustainability. <i>International Journal of Safety and "
    "Security Engineering</i>, 1173–1183. https://doi.org/10.18280/ijsse.150609",
    "Espressif Systems. (s. f.). <i>ESP32 Wi-Fi &amp; Bluetooth SoC</i>. "
    "https://www.espressif.com/en/products/socs/esp32",
    "IBM. (s. f.). <i>CRISP-DM help overview</i>. IBM SPSS Modeler Documentation. "
    "https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview",
    "Kimball Group. (s. f.). <i>Dimensional modeling techniques</i>. https://www.kimballgroup.com/data-warehouse-"
    "business-intelligence-resources/kimball-techniques/dimensional-modeling/",
    "Microsoft. (s. f.-a). <i>SQL Server Integration Services</i>. Microsoft Learn. https://learn.microsoft.com/"
    "en-us/sql/integration-services/sql-server-integration-services",
    "Microsoft. (s. f.-b). <i>What is Power BI?</i> Microsoft Learn. https://learn.microsoft.com/en-us/power-bi/"
    "fundamentals/power-bi-overview",
    "Microsoft. (s. f.-c). <i>dtexec utility</i>. Microsoft Learn. https://learn.microsoft.com/en-us/sql/"
    "integration-services/packages/dtexec-utility",
    "Microsoft. (s. f.-d). <i>Editions and supported features of SQL Server 2022</i>. Microsoft Learn. "
    "https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2022",
    "Microsoft. (s. f.-e). <i>Publish to web from Power BI</i>. Microsoft Learn. https://learn.microsoft.com/"
    "en-us/power-bi/collaborate-share/service-publish-to-web",
    "Microsoft. (s. f.-f). <i>Data refresh in Power BI</i>. Microsoft Learn. https://learn.microsoft.com/en-us/"
    "power-bi/connect-data/refresh-data",
    "Microsoft. (s. f.-g). <i>Use a personal gateway in Power BI</i>. Microsoft Learn. https://learn.microsoft.com/"
    "en-us/power-bi/connect-data/service-gateway-personal-mode",
    "Ministerio de Ambiente y Desarrollo Sostenible. (2019a, 26 de diciembre). <i>Resolución 2184 de 2019, por la "
    "cual se modifica la Resolución 668 de 2016 sobre uso racional de bolsas plásticas y se adoptan otras "
    "disposiciones</i>. Diario Oficial 51.179. https://normas.cra.gov.co/gestor/docs/"
    "resolucion_minambienteds_2184_2019.htm",
    "Ministerio de Ambiente y Desarrollo Sostenible. (2019b, 27 de diciembre). <i>Gobierno unifica el código de "
    "colores para la separación de residuos en la fuente a nivel nacional</i>. https://www.minambiente.gov.co/"
    "gobierno-unifica-el-codigo-de-colores-para-la-separacion-de-residuos-en-la-fuente-a-nivel-nacional/",
    "Pallets. (s. f.). <i>Welcome to Flask</i>. Flask Documentation (3.1.x). https://flask.palletsprojects.com/"
    "en/stable/",
    "Wirth, R., y Hipp, J. (2000). CRISP-DM: Towards a standard process model for data mining. En <i>Proceedings "
    "of the 4th International Conference on the Practical Applications of Knowledge Discovery and Data Mining</i> "
    "(pp. 29–39).",
    "World Bank. (s. f.). <i>What a waste 3.0: Global snapshot of solid waste management toward circularity until "
    "2050</i>. https://www.worldbank.org/what-a-waste",
]
for r in REFS:
    H.append(Paragraph(r, st["ref"]))

# ================================================================== CONSTRUCCIÓN
if __name__ == "__main__":
    import subprocess
    try:
        commit = subprocess.run(["gh", "run", "list", "--limit", "1", "--workflow", "pages-build-deployment",
                                 "--json", "headSha,conclusion", "--jq", ".[0].headSha[0:7]"], cwd=RAIZ,
                                capture_output=True, text=True, timeout=30).stdout.strip() or "no consultado"
    except Exception:
        commit = "no consultado"
    for f in H:
        if isinstance(f, KeepTogether):
            for g in f._content:
                if isinstance(g, Table):
                    for fila in g._cellvalues:
                        for c in fila:
                            if isinstance(c, Paragraph) and "{commit}" in c.text:
                                c.__init__(c.text.replace("{commit}", commit), c.style)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    doc = Doc(SALIDA)
    doc.multiBuild(H)
    print("PDF:", SALIDA)
    print("Páginas:", doc.page)
    if PENDIENTES:
        print("Capturas pendientes:")
        for n, nombre, que in PENDIENTES:
            print(f"  Figura {n}: docs/img/evidencias/{nombre}")

/* Valores obtenidos con las consultas de la carpeta /consultas sobre VertederoDW.
   Periodo simulado: 2026-09-27 a 2026-11-04. No modificar a mano: si cambian
   los datos, vuelva a ejecutar las consultas y actualice estos arreglos. */
const DATOS = {
  // 03_bivariados.sql - B3
  horas: ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"],
  llenadoHora: {
    todas: [77.07,77.20,77.35,77.41,77.57,77.72,10.77,18.23,25.23,28.45,30.23,32.68,39.69,48.88,53.68,55.72,57.30,60.47,67.41,73.96,76.76,78.12,78.75,78.82],
    c1: [81.43,81.54,81.75,81.83,82.00,81.98,10.79,19.10,26.99,30.45,32.05,34.27,41.85,52.68,58.27,60.10,61.76,65.02,71.86,78.19,81.26,82.44,83.24,83.39],
    c2: [69.06,69.14,69.22,69.31,69.52,69.81,10.02,16.28,21.67,24.62,26.13,28.73,35.02,42.14,46.49,48.47,49.95,53.32,59.68,65.78,68.76,70.13,70.56,70.58],
    c3: [80.72,80.92,81.07,81.10,81.20,81.36,11.51,19.31,27.02,30.28,32.52,35.03,42.19,51.83,56.27,58.58,60.18,63.08,70.70,77.92,80.25,81.80,82.46,82.50],
    // B3.b
    lunSab: [81.99,82.14,82.30,82.39,82.54,82.69,3.35,11.29,18.40,21.74,23.59,26.10,33.43,43.37,48.36,50.60,52.45,56.07,63.98,71.43,74.56,76.11,76.81,76.90],
    domingo: [49.98,50.04,50.09,50.07,50.25,50.39,51.58,56.37,62.76,65.39,66.79,68.85,74.13,79.14,82.01,82.99,83.19,83.95,85.73,87.45,88.46,88.86,89.09,89.07]
  },
  // 02_univariados.sql - U3
  aperturasHora: [4,10,4,6,5,10,271,437,264,99,102,207,509,380,124,84,98,242,403,227,87,62,3,5],
  // 02_univariados.sql - U1.b
  histograma: {
    tramos: ["0-9","10-19","20-29","30-39","40-49","50-59","60-69","70-79","80-89","90-100"],
    lecturas: [56422,76559,88691,70772,84383,87104,146892,116139,110458,162580],
    pct: [5.64,7.66,8.87,7.08,8.44,8.71,14.69,11.61,11.05,16.26]
  },
  // 02_univariados.sql - U2
  eventosTipo: { tipos: ["apertura","cierre","bloqueo_llena"], n: [3643,3643,209], pct: [48.61,48.61,2.79] },
  // 03_bivariados.sql - B1 ; 01_indicadores.sql - I3, I4
  canecas: {
    nombres: ["C1 Aprovechables","C2 No aprovechables","C3 Orgánicos"],
    promedio: [60.89,50.92,60.29], mediana: [68,54,65], pct90: [22.79,5.98,20.00],
    aperturasDia: [31.74,24.95,36.72], tasaBloqueo: [5.06,2.70,7.49]
  },
  // 03_bivariados.sql - B2.a
  diaSemana: {
    dias: ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"],
    nDias: [6,6,6,5,5,5,6],
    aperturasDia: [105.67,107.17,102.00,101.60,110.40,77.20,51.33],
    bloqueos: [10,14,13,22,16,1,133],
    pctBloqueos: [4.78,6.70,6.22,10.53,7.66,0.48,63.64],
    tasaBloqueo: [1.55,2.13,2.08,4.15,2.82,0.26,30.16]
  },
  // 04_multivariado.sql  [caneca, franja, tipo_dia, dias, llenado, pct90, aperturas, aperturas/dia, bloqueos, tasa]
  multivariado: [
    ["C1","Madrugada","Laborable",28,88.24,59.71,9,0.32,4,30.77],
    ["C1","Madrugada","Fin de semana",11,65.25,9.08,2,0.18,0,0.00],
    ["C1","Mañana","Laborable",28,19.71,0.00,367,13.11,0,0.00],
    ["C1","Mañana","Fin de semana",11,40.63,0.00,101,9.18,0,0.00],
    ["C1","Tarde","Laborable",28,54.06,1.93,404,14.43,2,0.49],
    ["C1","Tarde","Fin de semana",11,62.67,31.62,97,8.82,14,12.61],
    ["C1","Noche","Laborable",27,81.87,35.00,223,8.26,29,11.51],
    ["C1","Noche","Fin de semana",11,75.62,36.36,35,3.18,17,32.69],
    ["C2","Madrugada","Laborable",28,72.51,10.71,13,0.46,0,0.00],
    ["C2","Madrugada","Fin de semana",11,61.28,9.09,2,0.18,0,0.00],
    ["C2","Mañana","Laborable",28,16.01,0.00,284,10.14,0,0.00],
    ["C2","Mañana","Fin de semana",11,34.57,0.35,80,7.27,0,0.00],
    ["C2","Tarde","Laborable",28,42.83,0.24,301,10.75,1,0.33],
    ["C2","Tarde","Fin de semana",11,53.29,15.40,72,6.55,7,8.86],
    ["C2","Noche","Laborable",27,68.00,5.29,179,6.63,9,4.79],
    ["C2","Noche","Fin de semana",11,66.56,18.17,42,3.82,10,19.23],
    ["C3","Madrugada","Laborable",28,85.79,46.41,9,0.32,4,30.77],
    ["C3","Madrugada","Fin de semana",11,69.03,9.09,4,0.36,1,20.00],
    ["C3","Mañana","Laborable",28,18.83,0.00,431,15.39,0,0.00],
    ["C3","Mañana","Fin de semana",11,44.05,1.66,117,10.64,0,0.00],
    ["C3","Tarde","Laborable",28,51.13,0.17,467,16.68,0,0.00],
    ["C3","Tarde","Fin de semana",11,65.59,42.27,96,8.73,40,29.41],
    ["C3","Noche","Laborable",27,79.93,25.92,262,9.70,26,9.03],
    ["C3","Noche","Fin de semana",11,77.66,45.44,46,4.18,45,49.45]
  ]
};

/* Evidencias esperadas. Guarde cada imagen con ESE nombre en docs/img/evidencias/.
   Si el archivo existe, el sitio lo muestra; si no, aparece como "pendiente". */
const EVIDENCIAS = [
  ["01_maqueta_general.jpg", "Maqueta: las tres canecas (blanca, negra y verde) montadas en la ciudad"],
  ["02_maqueta_electronica.jpg", "ESP32 DevKit V1, sensores FC-51 y VL53L0X, servos SG90 y buzzer conectados"],
  ["03_tapa_abierta.jpg", "Una tapa abierta al acercar la mano al sensor infrarrojo"],
  ["04_monitor_serie.png", "Monitor Serie del IDE de Arduino con distancia, porcentaje y estado de cada caneca"],
  ["05_servidor_python.png", "Consola de servidor_canecas.py recibiendo lecturas y eventos de la ESP32"],
  ["06_ssms_vertedero.png", "SSMS: tablas de la base Vertedero y un SELECT de las últimas lecturas"],
  ["07_ssms_vertederodw.png", "SSMS: tablas de VertederoDW y conteo de FactLecturas"],
  ["08_ssms_diagrama_dw.png", "SSMS: diagrama de base de datos del modelo estrella"],
  ["09_ssis_maestro_verde.png", "Visual Studio: 00_Maestro.dtsx ejecutado con todas las tareas en verde"],
  ["10_ssis_factlecturas_flujo.png", "Visual Studio: flujo de datos de 11_FactLecturas.dtsx con conteo de filas"],
  ["11_ssms_log_ejecucion.png", "SSMS: SELECT de etl.LogEjecucion con el último lote en estado OK"],
  ["12_programador_tareas.png", "Programador de tareas de Windows con la tarea del ETL y su último resultado"],
  ["13_powerbi_desktop.png", "Power BI Desktop con el modelo y una página del dashboard"],
  ["14_powerbi_servicio.png", "Servicio de Power BI: informe publicado y código de Publicar en la web"],
  ["15_sitio_publicado.png", "Sitio publicado en GitHub Pages con el dashboard integrado y un filtro aplicado"]
];

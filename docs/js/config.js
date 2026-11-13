/* =====================================================================
   CONFIGURACION DEL SITIO
   ---------------------------------------------------------------------
   1) Pegue aqui, entre las comillas, la URL que entrega Power BI en
      Archivo > Insertar informe > Publicar en la web (publico).
      Es la direccion que empieza por https://app.powerbi.com/view?r=...
      (solo la URL, no todo el codigo <iframe>).
   2) Guarde el archivo y publique de nuevo (git add, commit, push).
   Mientras este vacia, la seccion Dashboard muestra un aviso de pendiente.
   ===================================================================== */
const POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiZWY5YmZhZGQtNGIwNS00N2I0LThmNWUtZmE3NDhlZTcyMmIxIiwidCI6IjA3ZGE2N2EwLTFmNDMtNGU4Yy05NzdmLTVmODhiNjQ3MGVlNiIsImMiOjR9";

/* Texto que aparece debajo del dashboard. Cambielo cuando cambie la
   forma real de actualizacion (por ejemplo, al activar la puerta de enlace). */
const POWERBI_ACTUALIZACION = "Actualización manual: el informe se publicó el 13 de noviembre de 2026 con los datos del data warehouse a esa fecha. El ETL carga el data warehouse cada 5 minutos, pero el informe publicado solo cambia cuando se vuelve a publicar (aún no hay puerta de enlace ni actualización programada).";

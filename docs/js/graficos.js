/* Graficos SVG sin dependencias externas. Todos leen los valores de datos.js. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const fmt = (v, d = 2) => Number(v).toLocaleString("es-CO", { minimumFractionDigits: d, maximumFractionDigits: d });
  const fmt0 = (v) => Number(v).toLocaleString("es-CO");
  const COL = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"];

  function el(tag, attrs, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function base(id, titulo, W = 720, H = 320) {
    const host = document.getElementById(id);
    if (!host) return null;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": titulo });
    host.appendChild(svg);
    return { svg, W, H, m: { l: 52, r: 16, t: 14, b: 44 } };
  }
  function ejes(g, max, etiquetas, unidadY, cada = 1) {
    const { svg, W, H, m } = g;
    const pw = W - m.l - m.r, ph = H - m.t - m.b;
    for (let i = 0; i <= 4; i++) {
      const v = (max * i) / 4, y = m.t + ph - (ph * i) / 4;
      svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y, y2: y, class: "rejilla" }));
      svg.appendChild(el("text", { x: m.l - 6, y: y + 4, "text-anchor": "end", class: "eje" }, fmt0(Math.round(v))));
    }
    svg.appendChild(el("text", { x: 12, y: m.t + ph / 2, class: "eje", transform: `rotate(-90 12 ${m.t + ph / 2})`, "text-anchor": "middle" }, unidadY));
    etiquetas.forEach((t, i) => {
      if (i % cada) return;
      const x = m.l + (pw * (i + 0.5)) / etiquetas.length;
      svg.appendChild(el("text", { x, y: H - m.b + 16, "text-anchor": "middle", class: "eje" }, t));
    });
    return { pw, ph };
  }
  function leyenda(id, series) {
    const host = document.getElementById(id);
    const d = document.createElement("div");
    d.className = "leyenda";
    series.forEach((s, i) => {
      const sp = document.createElement("span");
      sp.innerHTML = `<i style="background:${s.color || COL[i]}"></i>${s.nombre}`;
      d.appendChild(sp);
    });
    host.appendChild(d);
  }

  function lineas(id, titulo, etiquetas, series, unidadY, ejeX, max = 100) {
    const g = base(id, titulo); if (!g) return;
    const { svg, m, H } = g;
    const { pw, ph } = ejes(g, max, etiquetas, unidadY, 2);
    series.forEach((s, k) => {
      const pts = s.valores.map((v, i) => `${m.l + (pw * (i + 0.5)) / etiquetas.length},${m.t + ph - (ph * v) / max}`).join(" ");
      svg.appendChild(el("polyline", { points: pts, fill: "none", stroke: s.color || COL[k], "stroke-width": 2.5, "stroke-linejoin": "round" }));
      s.valores.forEach((v, i) => {
        const c = el("circle", { cx: m.l + (pw * (i + 0.5)) / etiquetas.length, cy: m.t + ph - (ph * v) / max, r: 3, fill: s.color || COL[k] });
        c.appendChild(el("title", {}, `${s.nombre} · ${etiquetas[i]} h: ${fmt(v)} ${unidadY}`));
        svg.appendChild(c);
      });
    });
    svg.appendChild(el("text", { x: m.l + pw / 2, y: H - 6, "text-anchor": "middle", class: "eje" }, ejeX));
    leyenda(id, series);
  }

  function barras(id, titulo, etiquetas, valores, unidadY, ejeX, opc = {}) {
    const g = base(id, titulo); if (!g) return;
    const { svg, m, H } = g;
    const max = opc.max || Math.max(...valores) * 1.15;
    const { pw, ph } = ejes(g, max, etiquetas, unidadY, opc.cada || 1);
    const bw = (pw / etiquetas.length) * 0.72;
    valores.forEach((v, i) => {
      const x = m.l + (pw * (i + 0.5)) / etiquetas.length - bw / 2, h = (ph * v) / max;
      const dest = opc.destacar && opc.destacar.includes(i);
      const r = el("rect", { x, y: m.t + ph - h, width: bw, height: Math.max(h, 0.5), rx: 2, fill: dest ? "var(--s2)" : "var(--s1)" });
      r.appendChild(el("title", {}, `${etiquetas[i]}: ${opc.dec === 0 ? fmt0(v) : fmt(v)} ${unidadY}${opc.extra ? " · " + opc.extra[i] : ""}`));
      svg.appendChild(r);
      if (opc.rotulos) svg.appendChild(el("text", { x: x + bw / 2, y: m.t + ph - h - 4, "text-anchor": "middle", class: "rotulo" }, opc.dec === 0 ? fmt0(v) : fmt(v, opc.dec ?? 2)));
    });
    svg.appendChild(el("text", { x: m.l + pw / 2, y: H - 6, "text-anchor": "middle", class: "eje" }, ejeX));
  }

  function barrasAgrupadas(id, titulo, etiquetas, series, unidadY, ejeX, max) {
    const g = base(id, titulo); if (!g) return;
    const { svg, m, H } = g;
    const { pw, ph } = ejes(g, max, etiquetas, unidadY);
    const gw = (pw / etiquetas.length) * 0.78, bw = gw / series.length;
    series.forEach((s, k) => s.valores.forEach((v, i) => {
      const x = m.l + (pw * (i + 0.5)) / etiquetas.length - gw / 2 + k * bw, h = (ph * v) / max;
      const r = el("rect", { x: x + 1, y: m.t + ph - h, width: bw - 2, height: Math.max(h, 0.5), rx: 2, fill: COL[k] });
      r.appendChild(el("title", {}, `${etiquetas[i]} · ${s.nombre}: ${fmt(v)} ${unidadY}`));
      svg.appendChild(r);
      svg.appendChild(el("text", { x: x + bw / 2, y: m.t + ph - h - 4, "text-anchor": "middle", class: "rotulo" }, fmt(v, 1)));
    }));
    svg.appendChild(el("text", { x: m.l + pw / 2, y: H - 6, "text-anchor": "middle", class: "eje" }, ejeX));
    leyenda(id, series);
  }

  /* Tabla de calor del multivariado: caneca x franja x tipo de dia */
  function calor(id, indice, unidad, dec, maxEscala) {
    const host = document.getElementById(id); if (!host) return;
    const franjas = ["Madrugada", "Mañana", "Tarde", "Noche"], horas = ["00–05 h", "06–11 h", "12–17 h", "18–23 h"];
    let h = `<div class="tabla-scroll"><table class="calor"><thead><tr><th rowspan="2">Caneca</th><th rowspan="2">Tipo de día</th>`;
    franjas.forEach((f, i) => (h += `<th>${f}<br><small>${horas[i]}</small></th>`));
    h += `</tr></thead><tbody>`;
    ["C1", "C2", "C3"].forEach((c) => ["Laborable", "Fin de semana"].forEach((t, k) => {
      h += `<tr>${k === 0 ? `<th rowspan="2">${c}</th>` : ""}<td>${t}</td>`;
      franjas.forEach((f) => {
        const r = DATOS.multivariado.find((x) => x[0] === c && x[1] === f && x[2] === t);
        const v = r[indice], a = Math.min(v / maxEscala, 1);
        const intentos = r[6] + r[8];
        const pocos = indice === 9 && intentos < 30;
        h += `<td class="celda${pocos ? " pocos" : ""}" style="--a:${a.toFixed(2)}" title="${c} · ${f} · ${t}: ${r[8]} bloqueos y ${r[6]} aperturas en ${r[3]} días; llenado promedio ${fmt(r[4])} %">${fmt(v, dec)} ${unidad}${pocos ? "*" : ""}</td>`;
      });
      h += `</tr>`;
    }));
    host.innerHTML = h + `</tbody></table></div>`;
  }

  /* Diagramas de modelos de datos */
  function diagrama(id, titulo, W, H, tablas, rels) {
    const host = document.getElementById(id); if (!host) return;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": titulo, class: "modelo" });
    const pos = {};
    tablas.forEach((t) => (pos[t.n] = { x: t.x, y: t.y, w: t.w || 170, h: 26 + t.c.length * 16 + 8 }));
    rels.forEach(([a, b, txt]) => {
      const A = pos[a], B = pos[b];
      const ax = A.x + A.w / 2, ay = A.y + A.h / 2, bx = B.x + B.w / 2, by = B.y + B.h / 2;
      svg.appendChild(el("line", { x1: ax, y1: ay, x2: bx, y2: by, class: "rel" }));
      if (txt) svg.appendChild(el("text", { x: (ax + bx) / 2, y: (ay + by) / 2 - 4, "text-anchor": "middle", class: "reltxt" }, txt));
    });
    tablas.forEach((t) => {
      const p = pos[t.n];
      svg.appendChild(el("rect", { x: p.x, y: p.y, width: p.w, height: p.h, rx: 6, class: "caja" + (t.hecho ? " hecho" : "") }));
      svg.appendChild(el("rect", { x: p.x, y: p.y, width: p.w, height: 24, rx: 6, class: "cab" + (t.hecho ? " hecho" : "") }));
      svg.appendChild(el("text", { x: p.x + p.w / 2, y: p.y + 17, "text-anchor": "middle", class: "tit" }, t.n));
      t.c.forEach((c, i) => svg.appendChild(el("text", { x: p.x + 8, y: p.y + 42 + i * 16, class: "campo" + (/^(PK|FK)/.test(c) ? " clave" : "") }, c)));
    });
    host.appendChild(svg);
  }

  function modelos() {
    diagrama("dg-relacional", "Modelo relacional de la base Vertedero", 760, 430, [
      { n: "Canecas", x: 295, y: 150, c: ["PK id_caneca int", "nombre nvarchar(10)", "tipo_residuo nvarchar(30)", "color nvarchar(15)", "dist_vacia_mm int"] },
      { n: "Sensores", x: 20, y: 20, c: ["PK id_sensor int", "FK id_caneca int", "tipo nvarchar(20)", "funcion nvarchar(40)", "pin nvarchar(10)", "direccion_i2c nvarchar(5)"] },
      { n: "Actuadores", x: 570, y: 20, c: ["PK id_actuador int", "FK id_caneca int (NULL)", "tipo nvarchar(20)", "pin nvarchar(10)"] },
      { n: "Lecturas", x: 20, y: 270, c: ["PK id_lectura int", "FK id_caneca int", "fecha_hora datetime2(0)", "distancia_mm int (NULL)", "porcentaje int", "peso_g decimal(5,1) (NULL)"] },
      { n: "Eventos", x: 570, y: 180, c: ["PK id_evento int", "FK id_caneca int", "fecha_hora datetime2(0)", "tipo nvarchar(20)", "porcentaje int"] },
      { n: "Alarmas", x: 570, y: 310, c: ["PK id_alarma int", "fecha_inicio datetime2(0)", "fecha_fin datetime2(0) (NULL)", "pct_c1, pct_c2, pct_c3 int"] }
    ], [["Canecas", "Sensores", "1 : N"], ["Canecas", "Actuadores", "1 : N"], ["Canecas", "Lecturas", "1 : N"], ["Canecas", "Eventos", "1 : N"]]);

    diagrama("dg-estrella", "Modelo multidimensional (estrella) de VertederoDW", 760, 640, [
      { n: "FactLecturas", hecho: 1, x: 20, y: 250, w: 190, c: ["PK lectura_key bigint", "id_lectura_origen int", "FK fecha_key", "FK hora_key", "FK caneca_key", "FK estado_key", "porcentaje int", "distancia_mm int", "peso_g, peso_kg", "lectura_valida bit", "peso_informado bit"] },
      { n: "FactEventos", hecho: 1, x: 285, y: 290, w: 190, c: ["PK evento_key bigint", "id_evento_origen int", "FK fecha_key", "FK hora_key", "FK caneca_key", "FK tipo_evento_key", "porcentaje int", "cantidad int"] },
      { n: "FactAlarmas", hecho: 1, x: 550, y: 250, w: 190, c: ["PK alarma_key int", "id_alarma_origen int", "FK fecha_key", "FK hora_key", "fecha_fin_key int", "duracion_min int", "pct_c1, pct_c2, pct_c3", "pct_max int", "activa bit", "rango_duracion"] },
      { n: "DimFecha", x: 195, y: 15, w: 170, c: ["PK fecha_key int (aaaammdd)", "fecha date", "anio, mes, dia", "nombre_mes, nombre_dia", "dia_semana (1 = lunes)", "semana_anio, trimestre", "es_fin_de_semana bit", "tipo_dia"] },
      { n: "DimHora", x: 400, y: 15, w: 170, c: ["PK hora_key int (0-23)", "hora_texto", "franja", "jornada"] },
      { n: "DimCaneca", x: 150, y: 490, w: 190, c: ["PK caneca_key int", "id_caneca int", "nombre, tipo_residuo, color", "pines y direccion_i2c", "dist_vacia_mm, num_sensores", "es_aprovechable bit"] },
      { n: "DimEstadoLlenado", x: 20, y: 80, w: 150, c: ["PK estado_key int", "estado", "desde_pct, hasta_pct", "requiere_atencion bit"] },
      { n: "DimTipoEvento", x: 420, y: 500, w: 170, c: ["PK tipo_evento_key int", "tipo", "descripcion", "grupo", "es_alerta bit"] }
    ], [["FactLecturas", "DimFecha"], ["FactLecturas", "DimHora"], ["FactLecturas", "DimCaneca"], ["FactLecturas", "DimEstadoLlenado"],
        ["FactEventos", "DimFecha"], ["FactEventos", "DimHora"], ["FactEventos", "DimCaneca"], ["FactEventos", "DimTipoEvento"],
        ["FactAlarmas", "DimFecha"], ["FactAlarmas", "DimHora"]]);
  }

  function evidencias() {
    const host = document.getElementById("galeria"); if (!host) return;
    EVIDENCIAS.forEach(([archivo, desc]) => {
      const fig = document.createElement("figure");
      fig.className = "evidencia pendiente";
      fig.innerHTML = `<div class="hueco">Pendiente<br><code>${archivo}</code></div><figcaption>${desc}</figcaption>`;
      const img = new Image();
      img.alt = desc;
      img.onload = () => { fig.className = "evidencia"; fig.querySelector(".hueco").replaceWith(img); actualizarConteo(); };
      img.src = "img/evidencias/" + archivo;
      host.appendChild(fig);
    });
    actualizarConteo();
  }
  function actualizarConteo() {
    const c = document.getElementById("conteo-evidencias"); if (!c) return;
    const falt = document.querySelectorAll(".evidencia.pendiente").length;
    c.textContent = falt === 0 ? "Todas las evidencias están cargadas." : `Faltan ${falt} de ${EVIDENCIAS.length} evidencias. Cada recuadro indica el nombre exacto del archivo que se espera.`;
  }

  function powerbi() {
    const host = document.getElementById("pbi-marco"), nota = document.getElementById("pbi-frecuencia");
    if (nota) nota.textContent = POWERBI_ACTUALIZACION;
    if (!host) return;
    if (POWERBI_URL && /^https:\/\/app\.powerbi\.com\//.test(POWERBI_URL)) {
      host.innerHTML = `<iframe title="Dashboard de Ciudad Inteligente (módulo vertedero) en Power BI" src="${POWERBI_URL}" allowfullscreen loading="lazy"></iframe>`;
    } else {
      host.innerHTML = `<div class="pbi-pendiente"><strong>Dashboard pendiente de integrar</strong><p>Aquí se mostrará el informe interactivo de Power BI cuando se publique con «Publicar en la web» y se pegue su URL en <code>docs/js/config.js</code>.</p></div>`;
    }
  }

  function menu() {
    const btn = document.getElementById("btn-menu"), nav = document.getElementById("menu");
    btn.addEventListener("click", () => { const a = nav.classList.toggle("abierto"); btn.setAttribute("aria-expanded", a); });
    nav.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => { nav.classList.remove("abierto"); btn.setAttribute("aria-expanded", "false"); }));
    const enlaces = [...nav.querySelectorAll("a")];
    const obs = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) enlaces.forEach((a) => a.classList.toggle("activo", a.getAttribute("href") === "#" + e.target.id));
    }), { rootMargin: "-20% 0px -70% 0px" });
    document.querySelectorAll("main > section[id]").forEach((s) => obs.observe(s));
  }

  document.addEventListener("DOMContentLoaded", () => {
    const D = DATOS, H = D.horas;
    menu(); modelos(); evidencias(); powerbi();

    barras("g-u1", "Histograma del porcentaje de llenado", D.histograma.tramos, D.histograma.pct, "% de lecturas", "Tramo de llenado (%)", { rotulos: true, dec: 1, extra: D.histograma.lecturas.map((n) => fmt0(n) + " lecturas") });
    barras("g-u2", "Eventos por tipo", D.eventosTipo.tipos, D.eventosTipo.n, "eventos", "Tipo de evento", { rotulos: true, dec: 0, extra: D.eventosTipo.pct.map((p) => fmt(p) + " %") });
    barras("g-u3", "Aperturas por hora del día", H, D.aperturasHora, "aperturas", "Hora del día", { dec: 0, cada: 2, destacar: [6, 7, 8, 11, 12, 13, 17, 18, 19] });
    barrasAgrupadas("g-b1", "Llenado por caneca", D.canecas.nombres, [{ nombre: "Promedio (%)", valores: D.canecas.promedio }, { nombre: "Mediana (%)", valores: D.canecas.mediana }, { nombre: "Lecturas ≥ 90 % (% del tiempo)", valores: D.canecas.pct90 }], "%", "Caneca", 80);
    barras("g-b2", "Bloqueos por día de la semana", D.diaSemana.dias, D.diaSemana.bloqueos, "bloqueos", "Día de la semana", { rotulos: true, dec: 0, destacar: [6], extra: D.diaSemana.tasaBloqueo.map((t, i) => `tasa ${fmt(t)} % · ${D.diaSemana.nDias[i]} días`) });
    lineas("g-b3", "Llenado promedio por hora y caneca", H, [{ nombre: "C1 Aprovechables", valores: D.llenadoHora.c1 }, { nombre: "C2 No aprovechables", valores: D.llenadoHora.c2 }, { nombre: "C3 Orgánicos", valores: D.llenadoHora.c3 }], "%", "Hora del día");
    calor("g-multi", 9, "%", 2, 50);
    calor("g-multi-llenado", 4, "%", 1, 100);

    lineas("g-k1", "Llenado promedio por hora: lunes a sábado frente a domingo", H, [{ nombre: "Lunes a sábado (33 días)", valores: D.llenadoHora.lunSab }, { nombre: "Domingo (6 días)", valores: D.llenadoHora.domingo, color: "var(--s2)" }], "%", "Hora del día");
    barrasAgrupadas("g-k2", "Comparación entre canecas", D.canecas.nombres, [{ nombre: "Llenado promedio (%)", valores: D.canecas.promedio }, { nombre: "Lecturas ≥ 90 % (%)", valores: D.canecas.pct90 }, { nombre: "Tasa de bloqueo (%)", valores: D.canecas.tasaBloqueo }], "%", "Caneca", 80);
    barras("g-k3", "Aperturas por hora del día", H, D.aperturasHora, "aperturas", "Hora del día (en color distinto: 06–08, 11–13 y 17–19 h)", { dec: 0, cada: 2, destacar: [6, 7, 8, 11, 12, 13, 17, 18, 19] });
    barras("g-k4", "Tasa de bloqueo por día de la semana", D.diaSemana.dias, D.diaSemana.tasaBloqueo, "% de intentos", "Día de la semana", { rotulos: true, dec: 2, destacar: [6], extra: D.diaSemana.bloqueos.map((b, i) => `${b} bloqueos en ${D.diaSemana.nDias[i]} días`) });
    calor("g-k5", 9, "%", 2, 50);
  });
})();

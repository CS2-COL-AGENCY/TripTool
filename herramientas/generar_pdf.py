"""Genera el informe PDF de un viaje a partir de su expediente.json.

Uso: python3 herramientas/generar_pdf.py viajes/<slug>/expediente.json [salida.pdf]
"""
import json
import sys
from pathlib import Path

from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DV", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVB", str(FONT_DIR / "DejaVuSans-Bold.ttf")))

AZUL = colors.HexColor("#0B3C5D")
TURQUESA = colors.HexColor("#1D9A96")
CORAL = colors.HexColor("#E8505B")
GRIS = colors.HexColor("#F2F4F5")
TEXTO = colors.HexColor("#1F2933")

base = getSampleStyleSheet()
S = {
    "h1": ParagraphStyle("h1", fontName="DVB", fontSize=20, leading=24, textColor=AZUL, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="DVB", fontSize=13.5, leading=17, textColor=AZUL,
                         spaceBefore=12, spaceAfter=6),
    "p": ParagraphStyle("p", fontName="DV", fontSize=9.5, leading=13.5, textColor=TEXTO),
    "small": ParagraphStyle("small", fontName="DV", fontSize=8, leading=10.5, textColor=colors.grey),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8.5, leading=11, textColor=TEXTO),
    "cellb": ParagraphStyle("cellb", fontName="DVB", fontSize=8.5, leading=11, textColor=colors.white),
    "bullet": ParagraphStyle("bullet", fontName="DV", fontSize=9.5, leading=13.5, leftIndent=12,
                             bulletIndent=2, textColor=TEXTO, spaceAfter=3),
    "kpi": ParagraphStyle("kpi", fontName="DVB", fontSize=15, leading=18, alignment=TA_CENTER,
                          textColor=AZUL),
    "kpil": ParagraphStyle("kpil", fontName="DV", fontSize=8, leading=10, alignment=TA_CENTER,
                           textColor=colors.grey),
}


def cop(v):
    return "COP " + f"{round(v):,}".replace(",", ".")


def usd(v):
    return "USD " + f"{v:,.0f}".replace(",", ".")


def link(url, texto="abrir enlace"):
    return f'<link href="{url}" color="#1D9A96"><u>{texto}</u></link>'


def tabla(filas, anchos, cabecera=True):
    datos = []
    for i, fila in enumerate(filas):
        estilo = S["cellb"] if cabecera and i == 0 else S["cell"]
        datos.append([c if not isinstance(c, str) else Paragraph(c, estilo) for c in fila])
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilos = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DADD")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecera:
        estilos.append(("BACKGROUND", (0, 0), (-1, 0), AZUL))
        estilos += [("BACKGROUND", (0, r), (-1, r), GRIS) for r in range(2, len(datos), 2)]
    t.setStyle(TableStyle(estilos))
    return t


def calcular(pres, tasa):
    """Devuelve rubros en COP y el total de cada escenario."""
    def a_cop(r):
        return r["cop"] if "cop" in r else r["usd"] * tasa

    base_total = sum(a_cop(r) for r in pres["rubros"])
    escenarios = []
    for e in pres["escenarios"]:
        total = 0
        for r in pres["rubros"]:
            total += a_cop(e["ajustes"].get(r["rubro"], r))
        if e["nombre"].startswith("Recomendado +"):
            total = base_total
        total += e["extras_usd"] * tasa
        escenarios.append({**e, "total": total})
    return base_total, escenarios


def mapa_ruta():
    """Esquema de la ruta en Florida (no a escala)."""
    d = Drawing(17 * cm, 7.2 * cm)
    d.add(Rect(0, 0, 17 * cm, 7.2 * cm, fillColor=colors.HexColor("#EAF6F6"), strokeColor=None))
    pts = {
        "Orlando (amigos)": (13.0, 6.1), "Wekiwa Springs": (11.4, 6.4),
        "Aventura Mall": (14.6, 2.9), "Design District / PAMM": (13.6, 2.25),
        "Doral (Airbnb / tía)": (11.6, 2.0), "MIA": (12.6, 1.75), "Zoo Miami": (11.3, 0.8),
    }
    ruta = ["Doral (Airbnb / tía)", "Zoo Miami", "Doral (Airbnb / tía)", "Wekiwa Springs",
            "Orlando (amigos)", "Aventura Mall", "MIA"]
    coords = []
    for n in ruta:
        x, y = pts[n]
        coords += [x * cm, y * cm]
    d.add(PolyLine(coords, strokeColor=CORAL, strokeWidth=2, strokeDashArray=[4, 3]))
    for n, (x, y) in pts.items():
        d.add(Circle(x * cm, y * cm, 4, fillColor=AZUL, strokeColor=colors.white))
        izquierda = n in ("Wekiwa Springs", "Doral (Airbnb / tía)", "Zoo Miami")
        d.add(String((x - 0.25) * cm if izquierda else (x + 0.25) * cm, (y - 0.12) * cm, n,
                     fontName="DV", fontSize=7.5, fillColor=TEXTO,
                     textAnchor="end" if izquierda else "start"))
    d.add(Line(1.0 * cm, 1.2 * cm, 9.5 * cm, 1.75 * cm, strokeColor=TURQUESA, strokeWidth=1.5))
    d.add(Circle(1.0 * cm, 1.2 * cm, 4, fillColor=TURQUESA, strokeColor=colors.white))
    d.add(String(0.6 * cm, 0.55 * cm, "Medellín (MDE)", fontName="DVB", fontSize=8, fillColor=TEXTO))
    d.add(String(3.6 * cm, 1.75 * cm, "✈ Avianca directo 3h25", fontName="DV", fontSize=7.5,
                 fillColor=TURQUESA))
    d.add(String(0.5 * cm, 6.5 * cm, "Ruta en carro 20–23 dic (esquema, no a escala)",
                 fontName="DVB", fontSize=9, fillColor=AZUL))
    d.add(String(0.5 * cm, 5.9 * cm, "≈ 650 millas · Zoo → Wekiwa → Orlando → Aventura → MIA",
                 fontName="DV", fontSize=8, fillColor=TEXTO))
    return d


def barras(escenarios, limite):
    ancho, alto = 17 * cm, 0.9 * cm * len(escenarios) + 1.2 * cm
    d = Drawing(ancho, alto)
    maximo = max(max(e["total"] for e in escenarios), limite) * 1.05
    x0, w = 5.2 * cm, 9.3 * cm
    for i, e in enumerate(escenarios):
        y = alto - (i + 1) * 0.9 * cm - 0.2 * cm
        largo = w * e["total"] / maximo
        color = TURQUESA if e["total"] <= limite else CORAL
        d.add(String(x0 - 0.2 * cm, y + 0.18 * cm, e["nombre"], fontName="DV", fontSize=8,
                     textAnchor="end", fillColor=TEXTO))
        d.add(Rect(x0, y, largo, 0.55 * cm, fillColor=color, strokeColor=None))
        d.add(String(x0 + largo + 0.15 * cm, y + 0.18 * cm, f"{e['total'] / 1e6:.2f} M",
                     fontName="DVB", fontSize=8, fillColor=TEXTO))
    xl = x0 + w * limite / maximo
    d.add(Line(xl, 0.35 * cm, xl, alto, strokeColor=AZUL, strokeWidth=1.2, strokeDashArray=[3, 2]))
    d.add(String(xl, 0.05 * cm, f"Presupuesto {limite / 1e6:.1f} M COP", fontName="DV",
                 fontSize=7.5, textAnchor="middle", fillColor=AZUL))
    return d


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(1.8 * cm, 1.1 * cm, "TripTool · Agencia multi-agente · Informe de Comunicaciones")
    canvas.drawRightString(letter[0] - 1.8 * cm, 1.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def construir(exp_path, salida):
    exp_path = Path(exp_path)
    carpeta = exp_path.parent
    e = json.loads(exp_path.read_text(encoding="utf-8"))
    v, tasa = e["viaje"], e["tasa"]["planeacion"]
    limite = v["presupuesto"]["monto"]
    base_total, escenarios = calcular(e["presupuesto"], tasa)
    rec = next(x for x in escenarios if x["nombre"] == "Recomendado")
    vr = e["vuelos"]["recomendado"]
    H = []

    H.append(Paragraph(v["titulo"], S["h1"]))
    H.append(Paragraph(f"Cotización preparada por Luisito y el equipo de agentes · precios consultados "
                       f"{e['consultado']} · 2 adultos · equipaje: {v['equipaje']}", S["small"]))
    H.append(Spacer(1, 8))
    kpis = [[Paragraph(usd(vr["total_usd"]), S["kpi"]), Paragraph(cop(rec["total"]), S["kpi"]),
             Paragraph("4 de 17", S["kpi"])],
            [Paragraph("Vuelos ida y vuelta, los dos", S["kpil"]),
             Paragraph("Gastos en destino, plan recomendado", S["kpil"]),
             Paragraph("noches pagadas (16 dic → 2 ene)", S["kpil"])]]
    tk = Table(kpis, colWidths=[5.6 * cm] * 3)
    tk.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GRIS),
                            ("BOX", (0, 0), (-1, -1), 0.5, TURQUESA),
                            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    H.append(tk)
    H.append(Paragraph("Recomendación", S["h2"]))
    for r in e["resumen"]:
        H.append(Paragraph(r, S["bullet"], bulletText="•"))
    H.append(Spacer(1, 6))
    H.append(mapa_ruta())

    H.append(Paragraph("1 · Vuelos (agente Vuelos)", S["h2"]))
    filas = [["Tramo", "Detalle"], ["Ida", vr["ida"]], ["Regreso", vr["regreso"]],
             ["Total", f"<b>{usd(vr['total_usd'])}</b> los dos ({usd(vr['por_persona_usd'])} por persona) "
                       f"≈ {cop(vr['total_usd'] * tasa)} · {vr['aerolinea']} [observado]"],
             ["Comprar", link(vr["enlace"], "Checkout Avianca para estos vuelos") + " · " +
              link(e["vuelos"]["busqueda"], "ver búsqueda completa")]]
    H.append(tabla(filas, [2.6 * cm, 14.4 * cm]))
    H.append(Paragraph(vr["nota"], S["small"]))
    H.append(Spacer(1, 4))
    filas = [["Alternativa", "Total los dos", "Comentario"]] + [
        [a["opcion"], usd(a["total_usd"]), a["detalle"]] for a in e["vuelos"]["alternativas"]]
    H.append(tabla(filas, [8 * cm, 2.6 * cm, 6.4 * cm]))

    H.append(Paragraph("2 · Alojamiento (agente Alojamiento)", S["h2"]))
    a = e["alojamiento"]
    H.append(Paragraph(f"<b>Objetivo:</b> {a['objetivo']}.", S["p"]))
    H.append(Paragraph(f"<b>Observado:</b> {a['observado_airbnb']}. "
                       + link(a["busqueda_airbnb"], "Abrir la búsqueda en Airbnb con filtros"), S["p"]))
    for c in a["criterios"]:
        H.append(Paragraph(c, S["bullet"], bulletText="✓"))
    for img in e.get("imagenes", []):
        ruta = carpeta / img["archivo"]
        if ruta.exists():
            im = Image(str(ruta))
            escala = 17 * cm / im.imageWidth
            im.drawWidth, im.drawHeight = 17 * cm, im.imageHeight * escala
            H.append(KeepTogether([Spacer(1, 4), im, Paragraph(img["pie"], S["small"])]))
    filas = [["Comparativo SlickTrip (mismas fechas)", "Total 4 noches", "Calificación", "Extras"]] + [
        [o["nombre"], usd(o["total_usd"]), o["rating"], o["extras"]] for o in a["opciones_slicktrip"]]
    H.append(Spacer(1, 4))
    H.append(tabla(filas, [6.4 * cm, 2.8 * cm, 2.6 * cm, 5.2 * cm]))
    H.append(Paragraph(a["nota"], S["small"]))

    H.append(Paragraph("3 · Transporte (agente Transporte)", S["h2"]))
    filas = [["Concepto", "Detalle"]] + [
        [t["item"], t["detalle"] + (" · " + link(t["enlace"]) if t.get("enlace") else "")]
        for t in e["transporte"]]
    H.append(tabla(filas, [5.6 * cm, 11.4 * cm]))

    H.append(PageBreak())
    H.append(Paragraph("4 · Itinerario (agente Destinos)", S["h2"]))
    filas = [["Día", "Plan", "Dormir"]] + [[i["fecha"], i["plan"], i["dormir"]] for i in e["itinerario"]]
    H.append(tabla(filas, [2.9 * cm, 11 * cm, 3.1 * cm]))

    H.append(Paragraph("5 · Presupuesto en destino (agente Presupuesto)", S["h2"]))
    H.append(Paragraph(f"Tasa de planeación: COP {tasa:,} por USD ({e['tasa']['nota']}; "
                       f"{e['tasa']['trm_fuente']}: COP {e['tasa']['trm']:,}). {e['presupuesto']['nota']}"
                       .replace(",", "."), S["small"]))
    filas = [["Rubro", "USD", "COP", "Tipo"]]
    for r in e["presupuesto"]["rubros"]:
        c = r["cop"] if "cop" in r else r["usd"] * tasa
        filas.append([r["rubro"] + f'<br/><font size="7" color="grey">{r["fuente"]}</font>',
                      usd(r["usd"]) if "usd" in r else "—", cop(c), r["tipo"]])
    filas.append(["<b>Total plan recomendado</b>", "", f"<b>{cop(base_total)}</b>", ""])
    H.append(tabla(filas, [8.6 * cm, 2.2 * cm, 3.6 * cm, 2.6 * cm]))
    H.append(Spacer(1, 8))
    H.append(Paragraph("Escenarios frente al presupuesto de COP 4.000.000", S["p"]))
    H.append(barras(escenarios, limite))
    filas = [["Escenario", "Qué incluye", "Total COP", "¿Cabe?"]] + [
        [x["nombre"], x["descripcion"], cop(x["total"]),
         "Sí" if x["total"] <= limite else f"Falta {cop(x['total'] - limite)}"] for x in escenarios]
    H.append(tabla(filas, [3.8 * cm, 7.2 * cm, 3 * cm, 3 * cm]))

    H.append(Paragraph("6 · Decisiones de Luisito", S["h2"]))
    filas = [["Tema", "Decisión", "Por qué"]] + [[d["tema"], d["decision"], d["porque"]]
                                                 for d in e["decisiones"]]
    H.append(tabla(filas, [3 * cm, 4.2 * cm, 9.8 * cm]))

    H.append(Paragraph("7 · Cómo reservar (agente Reservas)", S["h2"]))
    H.append(Paragraph("Nada se ha comprado. Cada enlace abre la página oficial para que pagues tú "
                       "cuando confirmes.", S["small"]))
    filas = [["#", "Qué", "Precio esperado", "Enlace", "Cuándo"]] + [
        [str(r["orden"]), r["item"], r["precio"], link(r["enlace"], "reservar"), r["cuando"]]
        for r in e["reservas"]]
    H.append(tabla(filas, [0.7 * cm, 6 * cm, 3 * cm, 2 * cm, 5.3 * cm]))

    H.append(Paragraph("8 · Verificación: fuentes y pendientes", S["h2"]))
    for f in e["fuentes"]:
        H.append(Paragraph(f, S["bullet"], bulletText="•"))
    H.append(Spacer(1, 4))
    for p in e["pendientes"]:
        H.append(Paragraph(p, S["bullet"], bulletText="⚠"))

    doc = SimpleDocTemplate(str(salida), pagesize=letter, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.8 * cm, title=v["titulo"],
                            author="TripTool – Comunicaciones")
    doc.build(H, onFirstPage=pie, onLaterPages=pie)
    return base_total, escenarios


if __name__ == "__main__":
    exp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(Path(exp).parent / "informe.pdf")
    total, esc = construir(exp, out)
    print(f"PDF: {out}")
    for x in esc:
        print(f"  {x['nombre']}: {cop(x['total'])}")

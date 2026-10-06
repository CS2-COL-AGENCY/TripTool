# TripTool — Agencia de viajes multi-agente

Nueve agentes de Claude Code que trabajan como una agencia de viajes: buscan los tiquetes más baratos,
alojamiento (Airbnb/hoteles), carros (Hertz, etc.), destinos y actividades, arman el presupuesto,
verifican fuentes, preparan enlaces de reserva y entregan un informe PDF.

| Agente | Modelo | Función |
|---|---|---|
| **luisito** | Opus · esfuerzo medio | Entrevista, planea, delega y decide. No busca precios. |
| vuelos | Haiku | Tarifas más baratas, horarios, aerolíneas, equipaje, checkout |
| alojamiento | Haiku | Airbnb, hoteles, rentas; total con tarifas |
| transporte | Haiku | Carros, peajes, gasolina, trenes, buses |
| destinos | Haiku | Atracciones, Tripadvisor, horarios, orden de visitas |
| presupuesto | Haiku | Consolida, convierte con TRM, escenarios |
| verificacion | Haiku | Audita fuentes, fechas, sumas |
| reservas | Haiku | Enlaces exactos de compra y alertas de precio |
| comunicaciones | Haiku | Informe PDF con tablas, mapa e imágenes |

## Uso
```bash
pip install reportlab
claude --agent luisito      # o en una sesión: "Luisito, organiza mi viaje"
```
Luisito hace las preguntas (presupuesto, origen, destino, ciudades, personas, equipaje, alojamiento
familiar, puntos de encuentro…), lanza a los especialistas en paralelo y coordina la pizarra
compartida `viajes/<slug>/` (ver `agencia/PROTOCOLO.md`).

Regenerar un informe:
```bash
python3 herramientas/generar_pdf.py viajes/miami-dic-2026/expediente.json
```

## Herramientas que usan los agentes
- SlickTrip (MCP): vuelos y hoteles/rentas con precios en vivo y enlaces de checkout.
- Booking.com (MCP): alojamientos y atracciones.
- WebSearch/WebFetch: fuentes oficiales (`agencia/FUENTES.md`).

## Reservas
Los agentes **no pagan**. Entregan el enlace exacto al checkout oficial; el viajero confirma y paga.

## Primer viaje
`viajes/miami-dic-2026/informe.pdf` — Medellín → Miami, 16 dic 2026 – 2 ene 2027, pareja.

# TripTool — Agencia de viajes multi-agente

- Punto de entrada: el agente **luisito** (`.claude/agents/luisito.md`, Opus esfuerzo medio).
  Solo planea, pregunta, delega y decide. Arranca con `claude --agent luisito`.
- Especialistas (Haiku, económicos): vuelos, alojamiento, transporte, destinos, presupuesto,
  verificacion, reservas, comunicaciones.
- Comunicación: pizarra compartida en `viajes/<slug>/` según `agencia/PROTOCOLO.md`.
- Fuentes permitidas: `agencia/FUENTES.md`. Cifras siempre etiquetadas [observado]/[estimado].
- PDF: `python3 herramientas/generar_pdf.py viajes/<slug>/expediente.json` (requiere reportlab).
- Nunca pagar ni reservar sin confirmación explícita del viajero; entregar enlaces exactos.

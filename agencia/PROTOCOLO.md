# Protocolo de comunicación entre agentes

```
                    Viajero
                       │
                  ┌────▼────┐   Opus (esfuerzo medio): solo planea, delega y decide
                  │ LUISITO │
                  └────┬────┘
   ┌──────────┬────────┼─────────┬───────────┐        Haiku (económico)
 vuelos  alojamiento transporte destinos      │
   └──────────┴────────┬─────────┘            │
                 presupuesto ──► verificacion ─┤
                                              ▼
                               comunicaciones (PDF) · reservas (enlaces)
```

## Pizarra compartida
Cada viaje vive en `viajes/<slug>/`:

| Archivo | Quién escribe | Contenido |
|---|---|---|
| `expediente.json` | Luisito (perfil, decisiones), Presupuesto (cifras) | Fuente única de verdad |
| `resultados/<agente>.md` | Cada especialista | Opciones, recomendación, fuentes, pendientes |
| `img/` | Cualquiera | Imágenes para el PDF |
| `informe.pdf` | Comunicaciones | Entregable final |

## Mensajes entre agentes
- Un agente pide algo a otro escribiendo en su archivo una sección `## Para <agente>`.
- Luisito lee esas secciones después de cada ronda y relanza al destinatario con el pedido exacto.
- Verificación responde con `OK / CORREGIR / PENDIENTE` por ítem.

## Etiquetas obligatorias
- **[observado]** precio visto en el proveedor (con URL y fecha/hora UTC).
- **[estimado]** cálculo propio (con el supuesto).

## Plantilla de expediente.json
```json
{
  "viaje": {"slug": "", "titulo": "", "viajeros": [], "origen": [], "destino": [],
             "fechas": {}, "equipaje": "", "presupuesto": {"monto": 0, "moneda": "COP", "excluye": []}},
  "alojamiento_familiar": [], "intereses": [], "opcionales": [],
  "decisiones": [], "vuelos": {}, "alojamiento": {}, "transporte": {},
  "itinerario": [], "presupuesto": {"tasa": 0, "rubros": [], "escenarios": []},
  "reservas": [], "fuentes": [], "pendientes": []
}
```

## Reglas de reserva
Nada se compra sin la confirmación explícita del viajero sobre ese ítem y ese monto. El pago
siempre lo hace el viajero en el sitio oficial; los agentes entregan el enlace exacto.

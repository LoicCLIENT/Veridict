"""Specialists invocados por el Perito coordinador via tool_use.

Cada specialist:
- recibe inputs estructurados,
- consulta sus fuentes (APIs externas, seeds, Claude visión),
- devuelve un dict serializable con `_log: ToolCallLog`,
- si no puede responder, devuelve `falta_info` indicando qué necesita del perito.
"""

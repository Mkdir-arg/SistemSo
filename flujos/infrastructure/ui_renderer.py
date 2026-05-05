"""Renderizado server-side de pantallas declarativas (ui_form v3).

Convierte el `ui_schema` crudo guardado en el nodo del flujo en una estructura
lista para iterar desde un template Django, opcionalmente resolviendo las
variables `{{ path.to.value }}` contra el contexto de una `InstanciaFlujo`.

Uso tipico desde una view:

    from flujos.infrastructure.ui_renderer import build_display_only_sections

    sections = build_display_only_sections(node.config.ui, instancia=inst)
    return render(request, 'tu_template.html', {'sections': sections})

Solo se incluyen bloques de display (info, summary, table). Los campos
editables (text, textarea, select, etc.) se omiten porque este renderer
es para vista de lectura, no de edicion.
"""

from .runtime_actions import (
    build_flow_template_context,
    render_flow_template_value,
)

INFO_TONE_TAILWIND = {
    'info': 'border-blue-200 bg-blue-50 text-blue-800',
    'success': 'border-green-200 bg-green-50 text-green-800',
    'warning': 'border-amber-200 bg-amber-50 text-amber-800',
    'danger': 'border-red-200 bg-red-50 text-red-800',
    'neutral': 'border-gray-200 bg-gray-50 text-gray-800',
}

DISPLAY_KINDS = {'info', 'summary', 'table'}


def _build_table_item(field):
    columns = list(field.get('columns') or [])
    rows = []
    for row in field.get('rows') or []:
        cells = [
            {
                'key': column.get('key', ''),
                'label': column.get('label', ''),
                'value': row.get(column.get('key', ''), '') if isinstance(row, dict) else '',
            }
            for column in columns
        ]
        rows.append({'cells': cells})

    return {
        'display_kind': 'table',
        'label': field.get('label', ''),
        'columns': columns,
        'rows': rows,
        'empty_message': field.get('empty_message') or 'Sin datos para mostrar.',
    }


def _build_summary_item(field):
    items = [
        {
            'label': item.get('label', '') if isinstance(item, dict) else '',
            'value': item.get('value', '') if isinstance(item, dict) else '',
        }
        for item in (field.get('items') or [])
    ]
    return {
        'display_kind': 'summary',
        'label': field.get('label', ''),
        'items': items,
        'empty_message': field.get('empty_message') or 'Sin datos para mostrar.',
    }


def _build_info_item(field):
    tone = field.get('tone', 'info')
    return {
        'display_kind': 'info',
        'label': field.get('label', ''),
        'content': field.get('content', ''),
        'tone': tone,
        'tone_classes': INFO_TONE_TAILWIND.get(tone, INFO_TONE_TAILWIND['info']),
    }


def _build_section(section):
    items = []
    for field in section.get('fields') or []:
        if not isinstance(field, dict):
            continue
        kind = field.get('kind')
        if kind not in DISPLAY_KINDS:
            continue
        if kind == 'info':
            items.append(_build_info_item(field))
        elif kind == 'summary':
            items.append(_build_summary_item(field))
        elif kind == 'table':
            items.append(_build_table_item(field))

    if not items:
        return None

    return {
        'id': section.get('id'),
        'title': section.get('title', ''),
        'description': section.get('description', ''),
        'items': items,
    }


def build_display_only_sections(ui_schema, instancia=None):
    """Devuelve secciones de display listas para template.

    Si `instancia` no es None, las variables `{{ ... }}` del schema se
    resuelven contra el contexto del caso. Si es None, el schema se devuelve
    con los placeholders sin tocar (util para preview vacia).
    """
    if not isinstance(ui_schema, dict):
        return []
    if ui_schema.get('type') != 'form':
        return []

    schema = ui_schema
    if instancia is not None:
        context = build_flow_template_context(instancia)
        schema = render_flow_template_value(ui_schema, context)

    sections = []
    for raw_section in schema.get('sections') or []:
        if not isinstance(raw_section, dict):
            continue
        built = _build_section(raw_section)
        if built is not None:
            sections.append(built)
    return sections


def has_display_blocks(ui_schema):
    """True si el schema tiene al menos un bloque info/summary/table."""
    if not isinstance(ui_schema, dict) or ui_schema.get('type') != 'form':
        return False
    for section in ui_schema.get('sections') or []:
        if not isinstance(section, dict):
            continue
        for field in section.get('fields') or []:
            if isinstance(field, dict) and field.get('kind') in DISPLAY_KINDS:
                return True
    return False

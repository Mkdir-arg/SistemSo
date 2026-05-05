"""DTOs y contratos del modulo de flujos."""

FLOW_DEFINITION_SCHEMA_VERSION = 2
SUPPORTED_FLOW_SCHEMA_VERSIONS = frozenset({1, 2, 3, 4})

SUPPORTED_NODE_TYPES = frozenset(
	{
		"inicio",
		"fin",
		"accion_humana",
		"accion_email",
		"accion_http",
		"espera",
		"decision",
	}
)

SUPPORTED_CONDITION_OPERATORS = frozenset({"==", "!=", ">", ">=", "<", "<=", "in"})
SUPPORTED_ACTION_FORM_TYPES = frozenset({"boolean_decision", "text_input", "choice_select"})
SUPPORTED_ACTION_ACTOR_MODES = frozenset({"group"})
SUPPORTED_ACTION_SURFACES = frozenset({"backoffice"})
SUPPORTED_ACTION_UI_TYPES = frozenset({"form"})
SUPPORTED_ACTION_UI_LAYOUTS = frozenset({"single_column"})
SUPPORTED_ACTIONABLE_SCHEMA_VERSIONS = frozenset({4})
SUPPORTED_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
SUPPORTED_ACTION_UI_FIELD_KINDS = frozenset(
	{"text", "textarea", "number", "date", "radio", "select", "checkbox"}
)


def _adjacency_map(node_ids, transitions):
	adjacency = {node_id: set() for node_id in node_ids}
	for transicion in transitions:
		adjacency[transicion["desde"]].add(transicion["hasta"])
	return adjacency


def _reachable_nodes(start_node_id, adjacency):
	visited = set()
	pending = [start_node_id]
	while pending:
		node_id = pending.pop()
		if node_id in visited:
			continue
		visited.add(node_id)
		pending.extend(adjacency.get(node_id, ()))
	return visited


def _normalize_condition(condicion, transicion_idx):
	if not isinstance(condicion, dict):
		raise ValueError(
			f'La condicion de la transicion #{transicion_idx} debe ser un objeto JSON o null.'
		)

	campo = condicion.get("campo")
	if not isinstance(campo, str) or not campo.strip():
		raise ValueError(
			f'La condicion de la transicion #{transicion_idx} debe incluir un "campo" no vacio.'
		)

	operador = condicion.get("operador")
	if operador not in SUPPORTED_CONDITION_OPERATORS:
		raise ValueError(
			f'La condicion de la transicion #{transicion_idx} usa un operador no soportado: "{operador}".'
		)

	if "valor" not in condicion:
		raise ValueError(
			f'La condicion de la transicion #{transicion_idx} debe incluir la clave "valor".'
		)

	return {
		**condicion,
		"campo": campo.strip(),
		"operador": operador,
	}


def _normalize_action_form_config(node_id, node_type, config):
	formulario = config.get("formulario")
	if formulario is None:
		return config

	if node_type != "accion_humana":
		raise ValueError(
			f'El nodo "{node_id}" solo puede definir "config.formulario" si es de tipo "accion_humana".'
		)

	if not isinstance(formulario, dict):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.formulario" como un objeto JSON.'
		)

	form_type = formulario.get("type")
	if form_type not in SUPPORTED_ACTION_FORM_TYPES:
		raise ValueError(
			f'El nodo "{node_id}" usa un tipo de formulario no soportado: "{form_type}".'
		)

	field_name = formulario.get("field_name")
	if not isinstance(field_name, str) or not field_name.strip():
		raise ValueError(
			f'El nodo "{node_id}" debe incluir un "field_name" no vacio en "config.formulario".'
		)

	if form_type == "text_input":
		required = formulario.get("required", True)
		if not isinstance(required, bool):
			raise ValueError(
				f'El nodo "{node_id}" debe definir "required" como booleano.'
			)

		multiline = formulario.get("multiline", False)
		if not isinstance(multiline, bool):
			raise ValueError(
				f'El nodo "{node_id}" debe definir "multiline" como booleano.'
			)

		normalized_form = {
			"type": form_type,
			"field_name": field_name.strip(),
			"required": required,
			"multiline": multiline,
		}

		rows = formulario.get("rows")
		if rows is not None:
			if not isinstance(rows, int) or rows <= 0:
				raise ValueError(
					f'El nodo "{node_id}" debe definir "rows" como entero positivo.'
				)
			normalized_form["rows"] = rows

		for key in ("field_label", "placeholder", "help_text"):
			value = formulario.get(key)
			if value is None:
				continue
			if not isinstance(value, str) or not value.strip():
				raise ValueError(
					f'El nodo "{node_id}" debe definir "{key}" como string no vacio cuando se informa.'
				)
			normalized_form[key] = value.strip()

		return {
			**config,
			"formulario": normalized_form,
		}

	if form_type == "choice_select":
		required = formulario.get("required", True)
		if not isinstance(required, bool):
			raise ValueError(
				f'El nodo "{node_id}" debe definir "required" como booleano.'
			)

		opciones = formulario.get("options")
		if not isinstance(opciones, list) or not opciones:
			raise ValueError(
				f'El nodo "{node_id}" debe definir "options" como una lista no vacia.'
			)

		normalized_options = []
		seen_values = set()
		for option_index, opcion in enumerate(opciones, start=1):
			if not isinstance(opcion, dict):
				raise ValueError(
					f'El nodo "{node_id}" debe definir la opcion #{option_index} como objeto JSON.'
				)

			value = opcion.get("value")
			label = opcion.get("label")
			if not isinstance(value, str) or not value.strip():
				raise ValueError(
					f'El nodo "{node_id}" debe definir un "value" no vacio para la opcion #{option_index}.'
				)
			if not isinstance(label, str) or not label.strip():
				raise ValueError(
					f'El nodo "{node_id}" debe definir un "label" no vacio para la opcion #{option_index}.'
				)

			value = value.strip()
			if value in seen_values:
				raise ValueError(
					f'El nodo "{node_id}" no puede repetir valores de opcion en "config.formulario.options": "{value}".'
				)
			seen_values.add(value)
			normalized_options.append({
				"value": value,
				"label": label.strip(),
			})

		normalized_form = {
			"type": form_type,
			"field_name": field_name.strip(),
			"required": required,
			"options": normalized_options,
		}

		for key in ("field_label", "placeholder", "help_text"):
			value = formulario.get(key)
			if value is None:
				continue
			if not isinstance(value, str) or not value.strip():
				raise ValueError(
					f'El nodo "{node_id}" debe definir "{key}" como string no vacio cuando se informa.'
				)
			normalized_form[key] = value.strip()

		return {
			**config,
			"formulario": normalized_form,
		}

	include_observacion = formulario.get("include_observacion", True)
	if not isinstance(include_observacion, bool):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "include_observacion" como booleano.'
		)

	observacion_required = formulario.get("observacion_required", False)
	if not isinstance(observacion_required, bool):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "observacion_required" como booleano.'
		)
	if observacion_required and not include_observacion:
		raise ValueError(
			f'El nodo "{node_id}" no puede requerir observacion si "include_observacion" es false.'
		)

	normalized_form = {
		"type": form_type,
		"field_name": field_name.strip(),
		"include_observacion": include_observacion,
		"observacion_required": observacion_required,
	}

	for key in ("field_label", "true_label", "false_label", "observacion_label"):
		value = formulario.get(key)
		if value is None:
			continue
		if not isinstance(value, str) or not value.strip():
			raise ValueError(
				f'El nodo "{node_id}" debe definir "{key}" como string no vacio cuando se informa.'
			)
		normalized_form[key] = value.strip()

	return {
		**config,
		"formulario": normalized_form,
	}


def _normalize_string_list(value, *, field_label, node_id):
	if not isinstance(value, list) or not value:
		raise ValueError(
			f'El nodo "{node_id}" debe definir "{field_label}" como una lista no vacia.'
		)

	normalized_items = []
	for index, item in enumerate(value, start=1):
		if not isinstance(item, str) or not item.strip():
			raise ValueError(
				f'El nodo "{node_id}" debe definir strings no vacios en "{field_label}" (item #{index}).'
			)
		normalized_items.append(item.strip())
	return normalized_items


def _normalize_email_action_config(node_id, node_type, schema_version, config):
	email_config = config.get("email")
	if node_type != "accion_email":
		if email_config is not None:
			raise ValueError(
				f'El nodo "{node_id}" solo puede definir "config.email" si es de tipo "accion_email".'
			)
		return config

	if schema_version not in SUPPORTED_ACTIONABLE_SCHEMA_VERSIONS:
		raise ValueError(
			f'El nodo "{node_id}" requiere "schema_version": 4 para acciones automaticas.'
		)

	if not isinstance(email_config, dict):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.email" como objeto JSON.'
		)

	subject = _normalize_optional_string(
		email_config.get("subject"),
		field_label="config.email.subject",
		node_id=node_id,
	)
	body = _normalize_optional_string(
		email_config.get("body"),
		field_label="config.email.body",
		node_id=node_id,
	)

	return {
		**config,
		"email": {
			"to": _normalize_string_list(
				email_config.get("to"),
				field_label="config.email.to",
				node_id=node_id,
			),
			"subject": subject,
			"body": body,
		},
	}


def _normalize_http_headers(node_id, headers):
	if headers is None:
		return []
	if not isinstance(headers, list):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.http.headers" como lista de pares key/value.'
		)

	normalized_headers = []
	seen_keys = set()
	for index, header in enumerate(headers, start=1):
		if not isinstance(header, dict):
			raise ValueError(
				f'El nodo "{node_id}" debe definir el header #{index} como objeto JSON.'
			)
		key = _normalize_optional_string(
			header.get("key"),
			field_label=f"config.http.headers[{index}].key",
			node_id=node_id,
		)
		value = header.get("value", "")
		if not isinstance(value, str):
			raise ValueError(
				f'El nodo "{node_id}" debe definir el valor del header #{index} como string.'
			)
		key_lower = key.lower()
		if key_lower in seen_keys:
			raise ValueError(
				f'El nodo "{node_id}" no puede repetir headers HTTP: "{key}".'
			)
		seen_keys.add(key_lower)
		normalized_headers.append({
			"key": key,
			"value": value,
		})
	return normalized_headers


def _normalize_http_action_config(node_id, node_type, schema_version, config):
	http_config = config.get("http")
	if node_type != "accion_http":
		if http_config is not None:
			raise ValueError(
				f'El nodo "{node_id}" solo puede definir "config.http" si es de tipo "accion_http".'
			)
		return config

	if schema_version not in SUPPORTED_ACTIONABLE_SCHEMA_VERSIONS:
		raise ValueError(
			f'El nodo "{node_id}" requiere "schema_version": 4 para acciones automaticas.'
		)

	if not isinstance(http_config, dict):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.http" como objeto JSON.'
		)

	method = (http_config.get("method") or "POST").upper()
	if method not in SUPPORTED_HTTP_METHODS:
		raise ValueError(
			f'El nodo "{node_id}" usa un metodo HTTP no soportado: "{method}".'
		)

	timeout_seconds = http_config.get("timeout_seconds", 10)
	if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
		raise ValueError(
			f'El nodo "{node_id}" debe definir "timeout_seconds" como entero positivo.'
		)

	body = http_config.get("body", "")
	if not isinstance(body, str):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.http.body" como string.'
		)

	return {
		**config,
		"http": {
			"method": method,
			"url": _normalize_optional_string(
				http_config.get("url"),
				field_label="config.http.url",
				node_id=node_id,
			),
			"headers": _normalize_http_headers(node_id, http_config.get("headers")),
			"body": body,
			"timeout_seconds": timeout_seconds,
		},
	}


def _normalize_optional_string(value, *, field_label, node_id, allow_blank=False):
	if value is None:
		return None
	if not isinstance(value, str):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "{field_label}" como string.'
		)
	value = value.strip()
	if not value and not allow_blank:
		raise ValueError(
			f'El nodo "{node_id}" debe definir "{field_label}" como string no vacio.'
		)
	return value


def _normalize_ui_options(node_id, field_id, options):
	if not isinstance(options, list) or not options:
		raise ValueError(
			f'El nodo "{node_id}" debe definir "options" como lista no vacia para el campo "{field_id}".'
		)

	normalized_options = []
	seen_values = set()
	for option_index, option in enumerate(options, start=1):
		if not isinstance(option, dict):
			raise ValueError(
				f'El nodo "{node_id}" debe definir la opcion #{option_index} del campo "{field_id}" como objeto JSON.'
			)

		value = _normalize_optional_string(
			option.get("value"),
			field_label=f'options[{option_index}].value',
			node_id=node_id,
		)
		label = _normalize_optional_string(
			option.get("label"),
			field_label=f'options[{option_index}].label',
			node_id=node_id,
		)

		if value in seen_values:
			raise ValueError(
				f'El nodo "{node_id}" no puede repetir valores de opcion en el campo "{field_id}": "{value}".'
			)
		seen_values.add(value)
		normalized_options.append({
			"value": value,
			"label": label,
		})

	return normalized_options


def _normalize_ui_field(node_id, field, seen_field_ids):
	if not isinstance(field, dict):
		raise ValueError(f'El nodo "{node_id}" debe definir cada campo de UI como objeto JSON.')

	field_id = _normalize_optional_string(field.get("id"), field_label="field.id", node_id=node_id)
	if field_id in seen_field_ids:
		raise ValueError(f'El nodo "{node_id}" no puede repetir field.id en "config.ui": "{field_id}".')
	seen_field_ids.add(field_id)

	kind = field.get("kind")
	if kind not in SUPPORTED_ACTION_UI_FIELD_KINDS:
		raise ValueError(
			f'El nodo "{node_id}" usa un tipo de campo UI no soportado en "{field_id}": "{kind}".'
		)

	label = _normalize_optional_string(field.get("label"), field_label=f'field.label ({field_id})', node_id=node_id)
	required = field.get("required", False)
	if not isinstance(required, bool):
		raise ValueError(
			f'El nodo "{node_id}" debe definir "required" como booleano en el campo "{field_id}".'
		)

	normalized_field = {
		**field,
		"id": field_id,
		"kind": kind,
		"label": label,
		"required": required,
	}

	for key in ("placeholder", "help_text"):
		value = field.get(key)
		if value is None:
			continue
		normalized_field[key] = _normalize_optional_string(
			value,
			field_label=f"field.{key} ({field_id})",
			node_id=node_id,
		)

	if kind == "textarea":
		rows = field.get("rows")
		if rows is not None:
			if not isinstance(rows, int) or rows <= 0:
				raise ValueError(
					f'El nodo "{node_id}" debe definir "rows" como entero positivo en el campo "{field_id}".'
				)
			normalized_field["rows"] = rows

	if kind in {"radio", "select"}:
		normalized_field["options"] = _normalize_ui_options(node_id, field_id, field.get("options"))

	return normalized_field


def _normalize_action_ui_config(node_id, ui_config):
	if not isinstance(ui_config, dict):
		raise ValueError(f'El nodo "{node_id}" debe definir "config.ui" como objeto JSON.')

	ui_type = ui_config.get("type")
	if ui_type not in SUPPORTED_ACTION_UI_TYPES:
		raise ValueError(
			f'El nodo "{node_id}" usa un tipo de pantalla no soportado en "config.ui.type": "{ui_type}".'
		)

	layout = ui_config.get("layout", "single_column")
	if layout not in SUPPORTED_ACTION_UI_LAYOUTS:
		raise ValueError(
			f'El nodo "{node_id}" usa un layout no soportado en "config.ui.layout": "{layout}".'
		)

	title = _normalize_optional_string(ui_config.get("title"), field_label="config.ui.title", node_id=node_id)
	description = _normalize_optional_string(
		ui_config.get("description"),
		field_label="config.ui.description",
		node_id=node_id,
		allow_blank=True,
	)

	sections = ui_config.get("sections")
	if not isinstance(sections, list) or not sections:
		raise ValueError(
			f'El nodo "{node_id}" debe definir "config.ui.sections" como lista no vacia.'
		)

	normalized_sections = []
	seen_section_ids = set()
	seen_field_ids = set()
	for section_index, section in enumerate(sections, start=1):
		if not isinstance(section, dict):
			raise ValueError(
				f'El nodo "{node_id}" debe definir cada seccion de UI como objeto JSON.'
			)

		section_id = _normalize_optional_string(
			section.get("id"),
			field_label=f"config.ui.sections[{section_index}].id",
			node_id=node_id,
		)
		if section_id in seen_section_ids:
			raise ValueError(
				f'El nodo "{node_id}" no puede repetir ids de seccion en "config.ui": "{section_id}".'
			)
		seen_section_ids.add(section_id)

		fields = section.get("fields")
		if not isinstance(fields, list) or not fields:
			raise ValueError(
				f'El nodo "{node_id}" debe definir la seccion "{section_id}" con al menos un campo.'
			)

		normalized_fields = [
			_normalize_ui_field(node_id, field, seen_field_ids)
			for field in fields
		]

		normalized_section = {
			**section,
			"id": section_id,
			"fields": normalized_fields,
		}
		section_title = section.get("title")
		if section_title is not None:
			normalized_section["title"] = _normalize_optional_string(
				section_title,
				field_label=f"config.ui.sections[{section_index}].title",
				node_id=node_id,
			)
		normalized_sections.append(normalized_section)

	submit = ui_config.get("submit")
	normalized_submit = {"label": "Guardar y continuar"}
	if submit is not None:
		if not isinstance(submit, dict):
			raise ValueError(f'El nodo "{node_id}" debe definir "config.ui.submit" como objeto JSON.')
		label = submit.get("label", "Guardar y continuar")
		normalized_submit["label"] = _normalize_optional_string(
			label,
			field_label="config.ui.submit.label",
			node_id=node_id,
		)

	return {
		**ui_config,
		"type": ui_type,
		"title": title,
		"description": description or "",
		"layout": layout,
		"sections": normalized_sections,
		"submit": normalized_submit,
	}


def _normalize_action_runtime_contract(node_id, node_type, schema_version, actor, surface, config):
	has_v3_contract = actor is not None or surface is not None or config.get("ui") is not None
	if not has_v3_contract:
		return None, None, config

	if schema_version < 3:
		raise ValueError(
			f'El nodo "{node_id}" usa actor, surface o config.ui, pero requiere "schema_version": 3.'
		)

	if node_type != "accion_humana":
		raise ValueError(
			f'El nodo "{node_id}" solo puede definir actor, surface o config.ui si es de tipo "accion_humana".'
		)

	if actor is None:
		raise ValueError(f'El nodo "{node_id}" debe definir "actor" cuando usa "config.ui".')
	if not isinstance(actor, dict):
		raise ValueError(f'El nodo "{node_id}" debe definir "actor" como objeto JSON.')
	mode = actor.get("mode")
	if mode not in SUPPORTED_ACTION_ACTOR_MODES:
		raise ValueError(
			f'El nodo "{node_id}" usa un actor.mode no soportado: "{mode}".'
		)
	value = _normalize_optional_string(actor.get("value"), field_label="actor.value", node_id=node_id)
	normalized_actor = {
		**actor,
		"mode": mode,
		"value": value,
	}

	if not isinstance(surface, list) or not surface:
		raise ValueError(f'El nodo "{node_id}" debe definir "surface" como lista no vacia.')
	normalized_surface = []
	for item in surface:
		if not isinstance(item, str) or not item.strip():
			raise ValueError(f'El nodo "{node_id}" debe definir valores string no vacios en "surface".')
		item = item.strip()
		if item not in SUPPORTED_ACTION_SURFACES:
			raise ValueError(
				f'El nodo "{node_id}" usa una surface no soportada: "{item}".'
			)
		if item not in normalized_surface:
			normalized_surface.append(item)

	ui_config = config.get("ui")
	if ui_config is None:
		raise ValueError(f'El nodo "{node_id}" debe definir "config.ui" en schema_version 3.')

	return normalized_actor, normalized_surface, {
		**config,
		"ui": _normalize_action_ui_config(node_id, ui_config),
	}


def _validate_action_form_contracts(normalized_nodes, normalized_transitions):
	transiciones_por_nodo = {}
	for transicion in normalized_transitions:
		transiciones_por_nodo.setdefault(transicion["desde"], []).append(transicion)

	for nodo in normalized_nodes:
		formulario = nodo.get("config", {}).get("formulario")
		if not formulario:
			continue

		if formulario["type"] != "boolean_decision":
			continue

		node_id = nodo["id"]
		transiciones = transiciones_por_nodo.get(node_id, [])
		condicionales = [
			transicion for transicion in transiciones if transicion.get("condicion") is not None
		]
		if len(transiciones) != 2 or len(condicionales) != 2:
			raise ValueError(
				f'El nodo "{node_id}" con formulario booleano debe tener exactamente dos transiciones condicionales de salida.'
			)

		condiciones = [transicion["condicion"] for transicion in condicionales]
		campos = {condicion.get("campo") for condicion in condiciones}
		operadores = {condicion.get("operador") for condicion in condiciones}
		valores = {condicion.get("valor") for condicion in condiciones}
		if (
			campos != {formulario["field_name"]}
			or operadores != {"=="}
			or valores != {True, False}
		):
			raise ValueError(
				f'El nodo "{node_id}" con formulario booleano debe mapear dos salidas sobre el campo "{formulario["field_name"]}" con valores True/False.'
			)


def normalize_flow_definition(definicion, *, validation_mode="draft"):
	if validation_mode not in {"draft", "publish"}:
		raise ValueError(f'Modo de validacion no soportado: "{validation_mode}".')

	if not isinstance(definicion, dict):
		raise ValueError("La definicion debe ser un objeto JSON.")

	schema_version = definicion.get("schema_version", FLOW_DEFINITION_SCHEMA_VERSION)
	if not isinstance(schema_version, int) or schema_version < 1:
		raise ValueError('La definicion debe incluir un "schema_version" numerico valido.')
	if schema_version not in SUPPORTED_FLOW_SCHEMA_VERSIONS:
		raise ValueError(
			f'La definicion usa un "schema_version" no soportado: "{schema_version}".'
		)

	nodos = definicion.get("nodos")
	if not isinstance(nodos, list):
		raise ValueError('La definicion debe incluir una lista "nodos".')

	transiciones = definicion.get("transiciones")
	if not isinstance(transiciones, list):
		raise ValueError('La definicion debe incluir una lista "transiciones".')

	normalized_nodes = []
	node_ids = set()
	for index, nodo in enumerate(nodos, start=1):
		if not isinstance(nodo, dict):
			raise ValueError(f"El nodo #{index} debe ser un objeto JSON.")

		node_id = nodo.get("id")
		if not isinstance(node_id, str) or not node_id.strip():
			raise ValueError(f'El nodo #{index} debe incluir un "id" no vacio.')
		node_id = node_id.strip()

		if node_id in node_ids:
			raise ValueError(f'El flujo no puede tener nodos con id duplicado: "{node_id}".')
		node_ids.add(node_id)

		tipo = nodo.get("tipo")
		if tipo not in SUPPORTED_NODE_TYPES:
			raise ValueError(f'El nodo "{node_id}" usa un tipo no soportado: "{tipo}".')

		nombre = nodo.get("nombre", "")
		if not isinstance(nombre, str):
			raise ValueError(f'El nodo "{node_id}" debe incluir un "nombre" string.')

		config = nodo.get("config") or {}
		if not isinstance(config, dict):
			raise ValueError(f'El nodo "{node_id}" debe incluir un "config" objeto.')
		config = _normalize_action_form_config(node_id, tipo, config)
		config = _normalize_email_action_config(node_id, tipo, schema_version, config)
		config = _normalize_http_action_config(node_id, tipo, schema_version, config)
		actor, surface, config = _normalize_action_runtime_contract(
			node_id,
			tipo,
			schema_version,
			nodo.get("actor"),
			nodo.get("surface"),
			config,
		)

		normalized_node = {
			**nodo,
			"id": node_id,
			"tipo": tipo,
			"nombre": nombre.strip(),
			"config": config,
		}
		if actor is not None:
			normalized_node["actor"] = actor
		if surface is not None:
			normalized_node["surface"] = surface

		normalized_nodes.append(normalized_node)

	tipos_inicio = [n for n in normalized_nodes if n.get("tipo") == "inicio"]
	if len(tipos_inicio) > 1:
		raise ValueError('El flujo no puede tener mas de un nodo de tipo "inicio".')

	tipos_fin = [n for n in normalized_nodes if n.get("tipo") == "fin"]
	if validation_mode == "publish":
		if len(tipos_inicio) != 1:
			raise ValueError('El flujo debe tener exactamente un nodo de tipo "inicio" para publicarse.')
		if len(tipos_fin) < 1:
			raise ValueError('El flujo debe tener al menos un nodo de tipo "fin" para publicarse.')

	normalized_transitions = []
	for index, transicion in enumerate(transiciones, start=1):
		if not isinstance(transicion, dict):
			raise ValueError(f"La transicion #{index} debe ser un objeto JSON.")

		desde = transicion.get("desde")
		hasta = transicion.get("hasta")
		if not isinstance(desde, str) or not desde.strip():
			raise ValueError(f'La transicion #{index} debe incluir un "desde" no vacio.')
		if not isinstance(hasta, str) or not hasta.strip():
			raise ValueError(f'La transicion #{index} debe incluir un "hasta" no vacio.')

		desde = desde.strip()
		hasta = hasta.strip()
		if desde not in node_ids:
			raise ValueError(f'La transicion #{index} referencia un nodo origen inexistente: "{desde}".')
		if hasta not in node_ids:
			raise ValueError(f'La transicion #{index} referencia un nodo destino inexistente: "{hasta}".')

		condicion = transicion.get("condicion")
		if condicion is not None:
			condicion = _normalize_condition(condicion, index)

		normalized_transitions.append(
			{
				**transicion,
				"desde": desde,
				"hasta": hasta,
				"condicion": condicion,
			}
		)

	if validation_mode == "publish":
		node_types = {nodo["id"]: nodo["tipo"] for nodo in normalized_nodes}
		incoming_counts = {node_id: 0 for node_id in node_ids}
		outgoing_counts = {node_id: 0 for node_id in node_ids}
		for transicion in normalized_transitions:
			outgoing_counts[transicion["desde"]] += 1
			incoming_counts[transicion["hasta"]] += 1

		for node_id, node_type in node_types.items():
			if node_type != "fin" and outgoing_counts[node_id] == 0:
				raise ValueError(
					f'El nodo "{node_id}" debe tener al menos una transicion de salida para publicarse.'
				)
			if node_type != "inicio" and incoming_counts[node_id] == 0:
				raise ValueError(
					f'El nodo "{node_id}" debe tener al menos una transicion de entrada para publicarse.'
				)

		start_node_id = tipos_inicio[0]["id"]
		adjacency = _adjacency_map(node_ids, normalized_transitions)
		reachable = _reachable_nodes(start_node_id, adjacency)
		unreachable = sorted(node_id for node_id in node_ids if node_id not in reachable)
		if unreachable:
			raise ValueError(
				"El flujo no puede publicarse con nodos desconectados del inicio: "
				+ ", ".join(f'"{node_id}"' for node_id in unreachable)
			)

		_validate_action_form_contracts(normalized_nodes, normalized_transitions)

	return {
		**definicion,
		"schema_version": schema_version,
		"nodos": normalized_nodes,
		"transiciones": normalized_transitions,
	}

from django.test import SimpleTestCase

from flujos.interfaces.web.forms import DefinicionFlujoForm


def build_definition():
    return {
        "nodos": [
            {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
            {"id": "revision", "tipo": "decision", "nombre": "Revisar caso"},
            {"id": "fin_ok", "tipo": "fin", "nombre": "Caso cerrado"},
        ],
        "transiciones": [
            {"desde": "inicio", "hasta": "revision", "condicion": None},
            {
                "desde": "revision",
                "hasta": "fin_ok",
                "condicion": {"campo": "aprobado", "operador": "==", "valor": True},
            },
        ],
    }


class DefinicionFlujoFormTests(SimpleTestCase):
    def test_accepts_valid_definition_and_normalizes_schema_version(self):
        form = DefinicionFlujoForm({"definicion": build_definition()})

        self.assertTrue(form.is_valid(), form.errors)
        definicion = form.cleaned_data["definicion"]
        self.assertEqual(definicion["schema_version"], 2)
        self.assertEqual(definicion["nodos"][0]["config"], {})

    def test_accepts_schema_v3_action_node_with_actor_surface_and_form_ui(self):
        definicion = {
            "schema_version": 3,
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision",
                    "actor": {"mode": "group", "value": "programaOperar"},
                    "surface": ["backoffice"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision operativa",
                            "description": "Completa la revision inicial.",
                            "sections": [
                                {
                                    "id": "principal",
                                    "title": "Datos principales",
                                    "fields": [
                                        {
                                            "id": "resultado",
                                            "kind": "radio",
                                            "label": "Resultado",
                                            "required": True,
                                            "options": [
                                                {"value": "aprobado", "label": "Aprobado"},
                                                {"value": "observado", "label": "Observado"},
                                            ],
                                        },
                                        {
                                            "id": "observacion",
                                            "kind": "textarea",
                                            "label": "Observacion",
                                            "required": False,
                                            "rows": 4,
                                        },
                                    ],
                                }
                            ],
                            "submit": {"label": "Guardar y continuar"},
                        }
                    },
                },
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "revision", "condicion": None},
                {"desde": "revision", "hasta": "fin", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        nodo = form.cleaned_data["definicion"]["nodos"][1]
        self.assertEqual(form.cleaned_data["definicion"]["schema_version"], 3)
        self.assertEqual(nodo["actor"], {"mode": "group", "value": "programaOperar"})
        self.assertEqual(nodo["surface"], ["backoffice"])
        self.assertEqual(nodo["config"]["ui"]["type"], "form")
        self.assertEqual(nodo["config"]["ui"]["sections"][0]["fields"][0]["id"], "resultado")

    def test_rejects_v3_runtime_contract_when_schema_version_is_2(self):
        definicion = {
            "schema_version": 2,
            "nodos": [
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision",
                    "actor": {"mode": "group", "value": "programaOperar"},
                    "surface": ["backoffice"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision",
                            "sections": [
                                {
                                    "id": "principal",
                                    "fields": [
                                        {"id": "observacion", "kind": "textarea", "label": "Observacion"},
                                    ],
                                }
                            ],
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('schema_version', form.errors["definicion"][0])

    def test_rejects_v3_action_node_with_unsupported_actor_mode(self):
        definicion = {
            "schema_version": 3,
            "nodos": [
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision",
                    "actor": {"mode": "dynamic", "value": "responsable"},
                    "surface": ["backoffice"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision",
                            "sections": [
                                {
                                    "id": "principal",
                                    "fields": [
                                        {"id": "observacion", "kind": "textarea", "label": "Observacion"},
                                    ],
                                }
                            ],
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('actor.mode no soportado', form.errors["definicion"][0])

    def test_rejects_v3_action_node_with_unsupported_surface(self):
        definicion = {
            "schema_version": 3,
            "nodos": [
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision",
                    "actor": {"mode": "group", "value": "programaOperar"},
                    "surface": ["portal"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision",
                            "sections": [
                                {
                                    "id": "principal",
                                    "fields": [
                                        {"id": "observacion", "kind": "textarea", "label": "Observacion"},
                                    ],
                                }
                            ],
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('surface no soportada', form.errors["definicion"][0])

    def test_rejects_v3_action_node_with_duplicate_ui_field_ids(self):
        definicion = {
            "schema_version": 3,
            "nodos": [
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision",
                    "actor": {"mode": "group", "value": "programaOperar"},
                    "surface": ["backoffice"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision",
                            "sections": [
                                {
                                    "id": "principal",
                                    "fields": [
                                        {"id": "resultado", "kind": "text", "label": "Resultado"},
                                        {"id": "resultado", "kind": "text", "label": "Resultado repetido"},
                                    ],
                                }
                            ],
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('repetir field.id', form.errors["definicion"][0])

    def test_accepts_action_node_with_explicit_boolean_form_config(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "validacion",
                    "tipo": "accion_humana",
                    "nombre": "Validacion",
                    "config": {
                        "formulario": {
                            "type": "boolean_decision",
                            "field_name": "aprobado",
                            "field_label": "Resultado de la validacion",
                            "true_label": "Aprobar caso",
                            "false_label": "Solicitar ajustes",
                            "observacion_label": "Fundamento operativo",
                            "include_observacion": True,
                            "observacion_required": True,
                        }
                    },
                },
                {"id": "fin_ok", "tipo": "fin", "nombre": "Caso cerrado"},
                {"id": "fin_rechazo", "tipo": "fin", "nombre": "Caso observado"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "validacion", "condicion": None},
                {
                    "desde": "validacion",
                    "hasta": "fin_ok",
                    "condicion": {"campo": "aprobado", "operador": "==", "valor": True},
                },
                {
                    "desde": "validacion",
                    "hasta": "fin_rechazo",
                    "condicion": {"campo": "aprobado", "operador": "==", "valor": False},
                },
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        formulario = form.cleaned_data["definicion"]["nodos"][1]["config"]["formulario"]
        self.assertEqual(formulario["type"], "boolean_decision")
        self.assertEqual(formulario["field_name"], "aprobado")
        self.assertEqual(formulario["true_label"], "Aprobar caso")
        self.assertTrue(formulario["observacion_required"])

    def test_accepts_action_node_with_text_input_form_config(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "dictamen",
                    "tipo": "accion_humana",
                    "nombre": "Dictamen",
                    "config": {
                        "formulario": {
                            "type": "text_input",
                            "field_name": "dictamen_tecnico",
                            "field_label": "Dictamen tecnico",
                            "placeholder": "Escribi el dictamen",
                            "help_text": "Este texto queda en el runtime.",
                            "required": True,
                            "multiline": True,
                            "rows": 5,
                        }
                    },
                },
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "dictamen", "condicion": None},
                {"desde": "dictamen", "hasta": "fin", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        formulario = form.cleaned_data["definicion"]["nodos"][1]["config"]["formulario"]
        self.assertEqual(formulario["type"], "text_input")
        self.assertEqual(formulario["field_name"], "dictamen_tecnico")
        self.assertTrue(formulario["required"])
        self.assertEqual(formulario["rows"], 5)

    def test_accepts_action_node_with_choice_select_form_config(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "prioridad",
                    "tipo": "accion_humana",
                    "nombre": "Asignar prioridad",
                    "config": {
                        "formulario": {
                            "type": "choice_select",
                            "field_name": "prioridad",
                            "field_label": "Prioridad del caso",
                            "placeholder": "Elegi una prioridad",
                            "help_text": "Impacta el seguimiento operativo.",
                            "required": True,
                            "options": [
                                {"value": "alta", "label": "Alta"},
                                {"value": "media", "label": "Media"},
                            ],
                        }
                    },
                },
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "prioridad", "condicion": None},
                {"desde": "prioridad", "hasta": "fin", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        formulario = form.cleaned_data["definicion"]["nodos"][1]["config"]["formulario"]
        self.assertEqual(formulario["type"], "choice_select")
        self.assertEqual(formulario["field_name"], "prioridad")
        self.assertEqual(formulario["options"][0]["value"], "alta")

    def test_accepts_draft_without_start_or_end_nodes(self):
        definicion = {
            "nodos": [
                {"id": "revision", "tipo": "decision", "nombre": ""},
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["definicion"]["nodos"][0]["nombre"], "")

    def test_rejects_publish_without_start_or_end_nodes(self):
        definicion = {
            "nodos": [
                {"id": "revision", "tipo": "decision", "nombre": ""},
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertFalse(form.is_valid())
        self.assertIn("inicio", form.errors["definicion"][0])

    def test_rejects_publish_with_disconnected_nodes(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
                {"id": "espera_1", "tipo": "espera", "nombre": "Espera 1"},
                {"id": "decision_1", "tipo": "decision", "nombre": "Decision 1"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "fin", "condicion": None},
                {"desde": "espera_1", "hasta": "decision_1", "condicion": None},
                {"desde": "decision_1", "hasta": "espera_1", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertFalse(form.is_valid())
        self.assertIn("desconectados", form.errors["definicion"][0])
        self.assertIn("espera_1", form.errors["definicion"][0])

    def test_rejects_publish_when_non_terminal_node_has_no_outgoing_transition(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {"id": "decision", "tipo": "decision", "nombre": "Decision"},
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "decision", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertFalse(form.is_valid())
        self.assertIn("salida", form.errors["definicion"][0])

    def test_rejects_duplicate_node_ids(self):
        definicion = build_definition()
        definicion["nodos"].append({"id": "revision", "tipo": "espera", "nombre": "Duplicado"})

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn("id duplicado", form.errors["definicion"][0])

    def test_rejects_transition_to_unknown_node(self):
        definicion = build_definition()
        definicion["transiciones"][0]["hasta"] = "no_existe"

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn("nodo destino inexistente", form.errors["definicion"][0])

    def test_rejects_unknown_node_type(self):
        definicion = build_definition()
        definicion["nodos"][1]["tipo"] = "formulario"

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn("tipo no soportado", form.errors["definicion"][0])

    def test_rejects_invalid_condition_operator(self):
        definicion = build_definition()
        definicion["transiciones"][1]["condicion"]["operador"] = "contains"

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn("operador no soportado", form.errors["definicion"][0])

    def test_rejects_publish_when_boolean_form_config_does_not_match_transitions(self):
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "validacion",
                    "tipo": "accion_humana",
                    "nombre": "Validacion",
                    "config": {
                        "formulario": {
                            "type": "boolean_decision",
                            "field_name": "aprobado",
                        }
                    },
                },
                {"id": "fin_ok", "tipo": "fin", "nombre": "Caso cerrado"},
                {"id": "fin_rechazo", "tipo": "fin", "nombre": "Caso observado"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "validacion", "condicion": None},
                {
                    "desde": "validacion",
                    "hasta": "fin_ok",
                    "condicion": {"campo": "resultado", "operador": "==", "valor": True},
                },
                {
                    "desde": "validacion",
                    "hasta": "fin_rechazo",
                    "condicion": {"campo": "resultado", "operador": "==", "valor": False},
                },
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertFalse(form.is_valid())
        self.assertIn('campo "aprobado"', form.errors["definicion"][0])

    def test_rejects_invalid_text_input_rows(self):
        definicion = {
            "nodos": [
                {
                    "id": "dictamen",
                    "tipo": "accion_humana",
                    "nombre": "Dictamen",
                    "config": {
                        "formulario": {
                            "type": "text_input",
                            "field_name": "dictamen",
                            "rows": 0,
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('rows', form.errors["definicion"][0])

    def test_rejects_choice_select_with_duplicate_option_values(self):
        definicion = {
            "nodos": [
                {
                    "id": "prioridad",
                    "tipo": "accion_humana",
                    "nombre": "Asignar prioridad",
                    "config": {
                        "formulario": {
                            "type": "choice_select",
                            "field_name": "prioridad",
                            "options": [
                                {"value": "alta", "label": "Alta"},
                                {"value": "alta", "label": "Muy alta"},
                            ],
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('repetir valores', form.errors["definicion"][0])

    def test_accepts_schema_v4_email_action_node(self):
        definicion = {
            "schema_version": 4,
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "notificar",
                    "tipo": "accion_email",
                    "nombre": "Notificar ciudadano",
                    "config": {
                        "email": {
                            "to": ["{{ ciudadano.email }}"],
                            "subject": "Actualizacion",
                            "body": "Hola {{ ciudadano.nombre_completo }}",
                        }
                    },
                },
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "notificar", "condicion": None},
                {"desde": "notificar", "hasta": "fin", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        nodo = form.cleaned_data["definicion"]["nodos"][1]
        self.assertEqual(nodo["config"]["email"]["to"], ["{{ ciudadano.email }}"])

    def test_accepts_schema_v4_http_action_node(self):
        definicion = {
            "schema_version": 4,
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "integrar",
                    "tipo": "accion_http",
                    "nombre": "Sincronizar",
                    "config": {
                        "http": {
                            "method": "POST",
                            "url": "https://example.com/api/flujo",
                            "headers": [
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": '{"dni": "{{ ciudadano.dni }}"}',
                            "timeout_seconds": 15,
                        }
                    },
                },
                {"id": "fin", "tipo": "fin", "nombre": "Fin"},
            ],
            "transiciones": [
                {"desde": "inicio", "hasta": "integrar", "condicion": None},
                {"desde": "integrar", "hasta": "fin", "condicion": None},
            ],
        }

        form = DefinicionFlujoForm({"definicion": definicion}, validation_mode="publish")

        self.assertTrue(form.is_valid(), form.errors)
        nodo = form.cleaned_data["definicion"]["nodos"][1]
        self.assertEqual(nodo["config"]["http"]["method"], "POST")

    def test_rejects_automatic_actions_without_schema_version_4(self):
        definicion = {
            "schema_version": 3,
            "nodos": [
                {
                    "id": "notificar",
                    "tipo": "accion_email",
                    "nombre": "Notificar",
                    "config": {
                        "email": {
                            "to": ["mail@example.com"],
                            "subject": "Asunto",
                            "body": "Cuerpo",
                        }
                    },
                }
            ],
            "transiciones": [],
        }

        form = DefinicionFlujoForm({"definicion": definicion})

        self.assertFalse(form.is_valid())
        self.assertIn('schema_version": 4', form.errors["definicion"][0])
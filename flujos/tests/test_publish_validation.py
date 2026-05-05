from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
import json

from flujos.models import Flujo, VersionFlujo
from legajos.models_programas import Programa
from system_modules.infrastructure.services import sync_installed_modules


class FlujosPublishValidationTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username="flujos-publisher",
            password="clave-segura-123",
            is_staff=True,
        )
        self.user.groups.add(Group.objects.create(name="programaConfigurar"))
        self.programa = Programa.objects.create(
            codigo="PROG-FLUJO-001",
            nombre="Programa Flujo",
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.flujo = Flujo.objects.create(
            programa=self.programa,
            nombre="Flujo Programa Flujo",
        )

    def _create_draft(self, definicion):
        return VersionFlujo.objects.create(
            flujo=self.flujo,
            definicion=definicion,
            creado_por=self.user,
        )

    def test_publish_rejects_incomplete_draft(self):
        self._create_draft(
            {
                "nodos": [
                    {"id": "decision_1", "tipo": "decision", "nombre": ""},
                ],
                "transiciones": [],
            }
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("flujos:api_publicar", args=[self.programa.pk]))

        self.assertEqual(response.status_code, 400)
        self.assertIn("inicio", response.json()["error"])

    def test_publish_rejects_disconnected_draft(self):
        self._create_draft(
            {
                "nodos": [
                    {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                    {"id": "fin", "tipo": "fin", "nombre": "Fin"},
                    {"id": "espera_1", "tipo": "espera", "nombre": "Espera"},
                    {"id": "decision_1", "tipo": "decision", "nombre": "Decision"},
                ],
                "transiciones": [
                    {"desde": "inicio", "hasta": "fin", "condicion": None},
                    {"desde": "espera_1", "hasta": "decision_1", "condicion": None},
                    {"desde": "decision_1", "hasta": "espera_1", "condicion": None},
                ],
            }
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("flujos:api_publicar", args=[self.programa.pk]))

        self.assertEqual(response.status_code, 400)
        self.assertIn("desconectados", response.json()["error"])

    def test_publish_accepts_connected_graph(self):
        version = self._create_draft(
            {
                "nodos": [
                    {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                    {"id": "espera_1", "tipo": "espera", "nombre": "Espera"},
                    {"id": "fin", "tipo": "fin", "nombre": "Fin"},
                ],
                "transiciones": [
                    {"desde": "inicio", "hasta": "espera_1", "condicion": None},
                    {"desde": "espera_1", "hasta": "fin", "condicion": None},
                ],
            }
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("flujos:api_publicar", args=[self.programa.pk]))

        self.assertEqual(response.status_code, 200)
        version.refresh_from_db()
        self.assertEqual(version.estado, VersionFlujo.Estado.PUBLICADA)

    def test_editor_round_trip_preserves_typed_form_config_after_publish(self):
        self.client.force_login(self.user)
        definicion = {
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision documental",
                    "config": {
                        "formulario": {
                            "type": "choice_select",
                            "field_name": "resultado_revision",
                            "field_label": "Resultado de la revision",
                            "placeholder": "Selecciona una opcion",
                            "help_text": "Define el siguiente paso operativo.",
                            "required": True,
                            "options": [
                                {"value": "aprobado", "label": "Aprobado"},
                                {"value": "observado", "label": "Observado"},
                            ],
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

        save_response = self.client.post(
            reverse("flujos:api_definicion", args=[self.programa.pk]),
            data=json.dumps(definicion),
            content_type="application/json",
        )

        self.assertEqual(save_response.status_code, 200)

        draft = VersionFlujo.objects.get(pk=save_response.json()["version_id"])
        self.assertEqual(draft.estado, VersionFlujo.Estado.BORRADOR)
        self.assertEqual(draft.definicion["schema_version"], 2)

        publish_response = self.client.post(reverse("flujos:api_publicar", args=[self.programa.pk]))

        self.assertEqual(publish_response.status_code, 200)

        get_response = self.client.get(reverse("flujos:api_definicion", args=[self.programa.pk]))

        self.assertEqual(get_response.status_code, 200)
        payload = get_response.json()
        self.assertEqual(payload["estado"], VersionFlujo.Estado.PUBLICADA)
        self.assertEqual(payload["version_id"], draft.pk)

        formulario = payload["definicion"]["nodos"][1]["config"]["formulario"]
        self.assertEqual(formulario["type"], "choice_select")
        self.assertEqual(formulario["field_name"], "resultado_revision")
        self.assertEqual(formulario["options"][0], {"value": "aprobado", "label": "Aprobado"})
        self.assertEqual(formulario["options"][1], {"value": "observado", "label": "Observado"})

    def test_api_round_trip_preserves_schema_v3_ui_contract_after_publish(self):
        self.client.force_login(self.user)
        definicion = {
            "schema_version": 3,
            "nodos": [
                {"id": "inicio", "tipo": "inicio", "nombre": "Inicio"},
                {
                    "id": "revision",
                    "tipo": "accion_humana",
                    "nombre": "Revision de ingreso",
                    "actor": {"mode": "group", "value": "programaOperar"},
                    "surface": ["backoffice"],
                    "config": {
                        "ui": {
                            "type": "form",
                            "title": "Revision de ingreso",
                            "description": "Valida el caso antes de continuar.",
                            "sections": [
                                {
                                    "id": "principal",
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

        save_response = self.client.post(
            reverse("flujos:api_definicion", args=[self.programa.pk]),
            data=json.dumps(definicion),
            content_type="application/json",
        )

        self.assertEqual(save_response.status_code, 200)

        draft = VersionFlujo.objects.get(pk=save_response.json()["version_id"])
        self.assertEqual(draft.definicion["schema_version"], 3)

        publish_response = self.client.post(reverse("flujos:api_publicar", args=[self.programa.pk]))

        self.assertEqual(publish_response.status_code, 200)

        get_response = self.client.get(reverse("flujos:api_definicion", args=[self.programa.pk]))

        self.assertEqual(get_response.status_code, 200)
        payload = get_response.json()
        self.assertEqual(payload["definicion"]["schema_version"], 3)
        nodo = payload["definicion"]["nodos"][1]
        self.assertEqual(nodo["actor"], {"mode": "group", "value": "programaOperar"})
        self.assertEqual(nodo["surface"], ["backoffice"])
        self.assertEqual(nodo["config"]["ui"]["type"], "form")
        self.assertEqual(nodo["config"]["ui"]["sections"][0]["fields"][0]["id"], "resultado")
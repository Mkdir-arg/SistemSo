from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from flujos.interfaces.module_api import iniciar_flujo_inscripcion
from flujos.models import Flujo, TareaFlujo, VersionFlujo
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa
from system_modules.infrastructure.services import sync_installed_modules


class FlujosBackofficeTasksTests(TestCase):
    def setUp(self):
        sync_installed_modules()
        self.user = User.objects.create_user(
            username='flujos-operador',
            password='clave-segura-123',
            is_staff=True,
        )
        self.assigned_user = User.objects.create_user(
            username='flujos-asignado',
            password='clave-segura-123',
            is_staff=True,
            first_name='Ana',
            last_name='Gomez',
        )
        self.user.groups.add(Group.objects.create(name='programaOperar'))
        self.assigned_user.groups.add(Group.objects.get(name='programaOperar'))
        self.ciudadano = Ciudadano.objects.create(
            dni='30144556',
            nombre='Mario',
            apellido='Suarez',
            genero=Ciudadano.Genero.MASCULINO,
        )
        self.programa = Programa.objects.create(
            codigo='PROG-TASK-001',
            nombre='Programa Tareas',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo = Flujo.objects.create(
            programa=self.programa,
            nombre='Flujo Tareas',
        )
        self.version = VersionFlujo.objects.create(
            flujo=self.flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {'id': 'revision_manual', 'tipo': 'accion_humana', 'nombre': 'Revision manual', 'config': {}},
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision_manual', 'condicion': None},
                    {'desde': 'revision_manual', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        self.programa_condicional = Programa.objects.create(
            codigo='PROG-TASK-002',
            nombre='Programa Tareas Condicionales',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_condicional = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_condicional,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_condicional = Flujo.objects.create(
            programa=self.programa_condicional,
            nombre='Flujo Tareas Condicionales',
        )
        self.version_condicional = VersionFlujo.objects.create(
            flujo=self.flujo_condicional,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'validacion',
                        'tipo': 'accion_humana',
                        'nombre': 'Validacion',
                        'config': {
                            'formulario': {
                                'type': 'boolean_decision',
                                'field_name': 'aprobado',
                                'field_label': 'Resultado de la validacion',
                                'true_label': 'Aprobar caso',
                                'false_label': 'Solicitar ajustes',
                                'include_observacion': True,
                                'observacion_label': 'Fundamento operativo',
                                'observacion_required': True,
                            }
                        },
                    },
                    {'id': 'fin_aprobado', 'tipo': 'fin', 'nombre': 'Fin aprobado', 'config': {}},
                    {'id': 'fin_rechazado', 'tipo': 'fin', 'nombre': 'Fin rechazado', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'validacion', 'condicion': None},
                    {
                        'desde': 'validacion',
                        'hasta': 'fin_aprobado',
                        'condicion': {'campo': 'aprobado', 'operador': '==', 'valor': True},
                    },
                    {
                        'desde': 'validacion',
                        'hasta': 'fin_rechazado',
                        'condicion': {'campo': 'aprobado', 'operador': '==', 'valor': False},
                    },
                ],
            },
            creado_por=self.user,
        )
        self.programa_texto = Programa.objects.create(
            codigo='PROG-TASK-003',
            nombre='Programa Tareas Texto',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_texto = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_texto,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_texto = Flujo.objects.create(
            programa=self.programa_texto,
            nombre='Flujo Tareas Texto',
        )
        self.version_texto = VersionFlujo.objects.create(
            flujo=self.flujo_texto,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'dictamen',
                        'tipo': 'accion_humana',
                        'nombre': 'Dictamen tecnico',
                        'config': {
                            'formulario': {
                                'type': 'text_input',
                                'field_name': 'dictamen_tecnico',
                                'field_label': 'Dictamen tecnico',
                                'placeholder': 'Escribi una conclusion breve',
                                'help_text': 'Este texto se guarda en el contexto del caso.',
                                'required': True,
                                'multiline': True,
                                'rows': 5,
                            }
                        },
                    },
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'dictamen', 'condicion': None},
                    {'desde': 'dictamen', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        self.programa_select = Programa.objects.create(
            codigo='PROG-TASK-004',
            nombre='Programa Tareas Seleccion',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_select = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_select,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_select = Flujo.objects.create(
            programa=self.programa_select,
            nombre='Flujo Tareas Seleccion',
        )
        self.version_select = VersionFlujo.objects.create(
            flujo=self.flujo_select,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'prioridad',
                        'tipo': 'accion_humana',
                        'nombre': 'Asignar prioridad',
                        'config': {
                            'formulario': {
                                'type': 'choice_select',
                                'field_name': 'prioridad',
                                'field_label': 'Prioridad del caso',
                                'placeholder': 'Elegi una prioridad',
                                'help_text': 'Esto ordena el seguimiento posterior.',
                                'required': True,
                                'options': [
                                    {'value': 'alta', 'label': 'Alta'},
                                    {'value': 'media', 'label': 'Media'},
                                    {'value': 'baja', 'label': 'Baja'},
                                ],
                            }
                        },
                    },
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'prioridad', 'condicion': None},
                    {'desde': 'prioridad', 'hasta': 'fin', 'condicion': None},
                ],
            },
            creado_por=self.user,
        )
        self.programa_ui = Programa.objects.create(
            codigo='PROG-TASK-005',
            nombre='Programa Tareas UI',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.inscripcion_ui = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa_ui,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        self.flujo_ui = Flujo.objects.create(
            programa=self.programa_ui,
            nombre='Flujo Tareas UI',
        )
        self.version_ui = VersionFlujo.objects.create(
            flujo=self.flujo_ui,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'schema_version': 3,
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'revision_ui',
                        'tipo': 'accion_humana',
                        'nombre': 'Revision UI',
                        'actor': {'mode': 'group', 'value': 'programaOperar'},
                        'surface': ['backoffice'],
                        'config': {
                            'ui': {
                                'type': 'form',
                                'title': 'Revision de ingreso',
                                'description': 'Completa la revision inicial del caso.',
                                'sections': [
                                    {
                                        'id': 'principal',
                                        'title': 'Datos principales',
                                        'fields': [
                                            {
                                                'id': 'resultado',
                                                'kind': 'radio',
                                                'label': 'Resultado',
                                                'required': True,
                                                'options': [
                                                    {'value': 'aprobado', 'label': 'Aprobado'},
                                                    {'value': 'observado', 'label': 'Observado'},
                                                ],
                                            },
                                            {
                                                'id': 'observacion',
                                                'kind': 'textarea',
                                                'label': 'Observacion',
                                                'required': False,
                                                'rows': 4,
                                            },
                                        ],
                                    }
                                ],
                                'submit': {'label': 'Guardar y continuar'},
                            }
                        },
                    },
                    {'id': 'fin_aprobado', 'tipo': 'fin', 'nombre': 'Fin aprobado', 'config': {}},
                    {'id': 'fin_observado', 'tipo': 'fin', 'nombre': 'Fin observado', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision_ui', 'condicion': None},
                    {
                        'desde': 'revision_ui',
                        'hasta': 'fin_aprobado',
                        'condicion': {'campo': 'resultado', 'operador': '==', 'valor': 'aprobado'},
                    },
                    {
                        'desde': 'revision_ui',
                        'hasta': 'fin_observado',
                        'condicion': {'campo': 'resultado', 'operador': '==', 'valor': 'observado'},
                    },
                ],
            },
            creado_por=self.user,
        )
        self.client.force_login(self.user)
        from flujos.runtime import FlowRuntime

        self.instancia = FlowRuntime.iniciar(self.inscripcion)
        self.tarea = self.instancia.tareas.get()
        self.instancia_condicional = iniciar_flujo_inscripcion(self.inscripcion_condicional)
        self.tarea_condicional = self.instancia_condicional.tareas.get()
        self.instancia_texto = iniciar_flujo_inscripcion(self.inscripcion_texto)
        self.tarea_texto = self.instancia_texto.tareas.get()
        self.instancia_select = iniciar_flujo_inscripcion(self.inscripcion_select)
        self.tarea_select = self.instancia_select.tareas.get()
        self.instancia_ui = iniciar_flujo_inscripcion(self.inscripcion_ui)
        self.tarea_ui = self.instancia_ui.tareas.get()
        self.tarea_condicional.asignado_a = self.assigned_user
        self.tarea_condicional.save(update_fields=['asignado_a'])
        self.tarea_resuelta = TareaFlujo.objects.create(
            instancia=self.instancia,
            nodo_id='revision_manual',
            nombre='Revision archivada',
            descripcion='Tarea historica de prueba',
            estado=TareaFlujo.Estado.RESUELTA,
            asignado_a=self.assigned_user,
            resuelto_por=self.user,
            datos={'origen': 'test'},
        )

    def test_bandeja_lists_pending_tasks(self):
        response = self.client.get(reverse('flujos_editor:bandeja_tareas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Panel operativo')
        self.assertContains(response, 'Abrir detalle')
        self.assertContains(response, 'Resolver ahora')
        self.assertContains(response, 'Revision manual')
        self.assertContains(response, 'Programa Tareas')

    def test_bandeja_shows_complete_data_action_for_text_input_task(self):
        response = self.client.get(
            reverse('flujos_editor:bandeja_tareas'),
            {'programa': self.programa_texto.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dictamen tecnico')
        self.assertContains(response, 'Completar datos')
        self.assertNotContains(response, 'Resolver ahora')

    def test_bandeja_shows_complete_data_action_for_ui_form_task(self):
        response = self.client.get(
            reverse('flujos_editor:bandeja_tareas'),
            {'programa': self.programa_ui.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Revision UI')
        self.assertContains(response, 'Completar datos')
        self.assertNotContains(response, 'Resolver ahora')

    def test_bandeja_filters_by_program_assignee_and_state(self):
        response = self.client.get(
            reverse('flujos_editor:bandeja_tareas'),
            {
                'programa': self.programa.pk,
                'asignado': self.assigned_user.pk,
                'estado': TareaFlujo.Estado.RESUELTA,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Revision archivada')
        self.assertNotContains(response, 'Validacion')
        self.assertContains(response, 'Vista filtrada')
        self.assertContains(response, 'Programa: Programa Tareas (PROG-TASK-001)')
        self.assertContains(response, 'Asignado: Ana Gomez')
        self.assertContains(response, 'Estado: Resuelta')

    def test_tarea_detalle_resuelve_con_formulario_tipado(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_condicional.pk]),
            {
                'decision': 'true',
                'observacion': 'Apto',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.tarea_condicional.refresh_from_db()
        self.instancia_condicional.refresh_from_db()
        self.assertEqual(self.tarea_condicional.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia_condicional.estado, self.instancia_condicional.Estado.COMPLETADA)
        self.assertEqual(self.instancia_condicional.datos['aprobado'], True)
        self.assertEqual(self.instancia_condicional.datos['observacion'], 'Apto')

    def test_tarea_detalle_muestra_historial_y_contexto_tipado(self):
        self.client.post(
            reverse('flujos_editor:tarea_asignar', args=[self.tarea_condicional.pk]),
            {
                'asignado_a': str(self.user.pk),
                'next': reverse('flujos_editor:tarea_detalle', args=[self.tarea_condicional.pk]),
            },
        )

        response = self.client.get(reverse('flujos_editor:tarea_detalle', args=[self.tarea_condicional.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Historial')
        self.assertContains(response, 'Reasignacion de tarea')
        self.assertContains(response, 'Contexto del caso')
        self.assertContains(response, 'Resultado de la validacion')
        self.assertContains(response, 'Aprobar caso')
        self.assertContains(response, 'Fundamento operativo')
        self.assertContains(response, 'La decisión se traducirá automáticamente al campo')

    def test_tarea_detalle_respects_required_observation_from_node_schema(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_condicional.pk]),
            {
                'decision': 'false',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.tarea_condicional.refresh_from_db()
        self.assertEqual(self.tarea_condicional.estado, TareaFlujo.Estado.PENDIENTE)
        self.assertContains(response, 'Fundamento operativo')
        self.assertIn('observacion', response.context['form'].errors)

    def test_api_tarea_detalle_exposes_typed_resolution_form(self):
        response = self.client.get(reverse('flujos:api_tarea_detalle', args=[self.tarea_condicional.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['task']['resolution_form']['type'], 'boolean_decision')
        self.assertEqual(payload['task']['resolution_form']['field_name'], 'aprobado')
        self.assertEqual(payload['task']['resolution_form']['field_label'], 'Resultado de la validacion')
        self.assertEqual(payload['task']['resolution_form']['true_label'], 'Aprobar caso')
        self.assertEqual(payload['task']['resolution_form']['false_label'], 'Solicitar ajustes')
        self.assertEqual(payload['task']['resolution_form']['observacion_label'], 'Fundamento operativo')
        self.assertTrue(payload['task']['resolution_form']['observacion_required'])

    def test_api_tarea_detalle_exposes_text_input_form(self):
        response = self.client.get(reverse('flujos:api_tarea_detalle', args=[self.tarea_texto.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['task']['resolution_form']['type'], 'text_input')
        self.assertEqual(payload['task']['resolution_form']['field_name'], 'dictamen_tecnico')
        self.assertEqual(payload['task']['resolution_form']['field_label'], 'Dictamen tecnico')
        self.assertTrue(payload['task']['resolution_form']['required'])
        self.assertTrue(payload['task']['resolution_form']['multiline'])

    def test_api_tarea_detalle_exposes_choice_select_form(self):
        response = self.client.get(reverse('flujos:api_tarea_detalle', args=[self.tarea_select.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['task']['resolution_form']['type'], 'choice_select')
        self.assertEqual(payload['task']['resolution_form']['field_name'], 'prioridad')
        self.assertEqual(payload['task']['resolution_form']['field_label'], 'Prioridad del caso')
        self.assertEqual(payload['task']['resolution_form']['options'][0]['value'], 'alta')

    def test_api_tarea_detalle_exposes_ui_form_schema(self):
        response = self.client.get(reverse('flujos:api_tarea_detalle', args=[self.tarea_ui.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['task']['resolution_form']['type'], 'ui_form')
        self.assertEqual(payload['task']['resolution_form']['title'], 'Revision de ingreso')
        self.assertEqual(payload['task']['resolution_form']['sections'][0]['fields'][0]['id'], 'resultado')

    def test_runtime_snapshots_ui_schema_when_creating_task(self):
        self.assertEqual(self.tarea_ui.datos['ui_schema']['type'], 'form')
        self.assertEqual(self.tarea_ui.datos['actor'], {'mode': 'group', 'value': 'programaOperar'})
        self.assertEqual(self.tarea_ui.datos['surface'], ['backoffice'])

    def test_tarea_detalle_renders_and_resolves_ui_form(self):
        response = self.client.get(reverse('flujos_editor:tarea_detalle', args=[self.tarea_ui.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Revision de ingreso')
        self.assertContains(response, 'Datos principales')
        self.assertContains(response, 'Resultado')
        self.assertContains(response, 'Observacion')

        post_response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_ui.pk]),
            {
                'resultado': 'aprobado',
                'observacion': 'Caso listo para continuar',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(post_response.status_code, 302)
        self.tarea_ui.refresh_from_db()
        self.instancia_ui.refresh_from_db()
        self.assertEqual(self.tarea_ui.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia_ui.estado, self.instancia_ui.Estado.COMPLETADA)
        self.assertEqual(self.instancia_ui.datos['resultado'], 'aprobado')
        self.assertEqual(self.instancia_ui.datos['observacion'], 'Caso listo para continuar')
        self.assertEqual(self.tarea_ui.datos['response']['resultado'], 'aprobado')

    def test_tarea_detalle_resuelve_con_formulario_texto_tipado(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_texto.pk]),
            {
                'value': 'Documentacion completa y coherente.',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.tarea_texto.refresh_from_db()
        self.instancia_texto.refresh_from_db()
        self.assertEqual(self.tarea_texto.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia_texto.estado, self.instancia_texto.Estado.COMPLETADA)
        self.assertEqual(
            self.instancia_texto.datos['dictamen_tecnico'],
            'Documentacion completa y coherente.',
        )

    def test_tarea_detalle_requires_text_input_when_schema_says_so(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_texto.pk]),
            {
                'value': '',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.tarea_texto.refresh_from_db()
        self.assertEqual(self.tarea_texto.estado, TareaFlujo.Estado.PENDIENTE)
        self.assertContains(response, 'Dictamen tecnico')
        self.assertIn('value', response.context['form'].errors)

    def test_tarea_detalle_resuelve_con_formulario_select_tipado(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_select.pk]),
            {
                'value': 'alta',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.tarea_select.refresh_from_db()
        self.instancia_select.refresh_from_db()
        self.assertEqual(self.tarea_select.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia_select.estado, self.instancia_select.Estado.COMPLETADA)
        self.assertEqual(self.instancia_select.datos['prioridad'], 'alta')

    def test_tarea_detalle_requires_select_value_when_schema_says_so(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_detalle', args=[self.tarea_select.pk]),
            {
                'value': '',
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.tarea_select.refresh_from_db()
        self.assertEqual(self.tarea_select.estado, TareaFlujo.Estado.PENDIENTE)
        self.assertContains(response, 'Prioridad del caso')
        self.assertContains(response, 'Alta')
        self.assertIn('value', response.context['form'].errors)

    def test_api_bandeja_returns_filtered_json(self):
        response = self.client.get(
            reverse('flujos:api_bandeja_tareas'),
            {
                'programa': self.programa_condicional.pk,
                'asignado': self.assigned_user.pk,
                'estado': TareaFlujo.Estado.PENDIENTE,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['total'], 1)
        self.assertEqual(payload['results'][0]['id'], self.tarea_condicional.pk)
        self.assertEqual(payload['results'][0]['campos_requeridos'], ['aprobado'])
        self.assertTrue(payload['results'][0]['requiere_payload'])

    def test_api_tarea_detalle_returns_metadata_and_timeline(self):
        self.client.post(
            reverse('flujos:api_tarea_asignar', args=[self.tarea.pk]),
            data='{"asignado_a": %s}' % self.assigned_user.pk,
            content_type='application/json',
        )

        response = self.client.get(reverse('flujos:api_tarea_detalle', args=[self.tarea.pk]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['task']['id'], self.tarea.pk)
        self.assertEqual(payload['task']['nodo']['id'], 'revision_manual')
        self.assertTrue(payload['task']['acciones']['puede_asignar'])
        self.assertTrue(payload['task']['acciones']['puede_resolver'])
        self.assertEqual(payload['timeline'][0]['motivo'], 'Asignacion de tarea')
        self.assertEqual(payload['timeline'][0]['datos_transicion']['tarea_id'], self.tarea.pk)
        self.assertTrue(any(user['id'] == self.assigned_user.pk for user in payload['assignable_users']))
        self.assertEqual(
            payload['links']['assign'],
            reverse('flujos:api_tarea_asignar', args=[self.tarea.pk]),
        )
        self.assertEqual(
            payload['links']['resolve'],
            reverse('flujos:api_tarea_resolver', args=[self.tarea.pk]),
        )

    def test_api_tarea_asignar_updates_task_and_returns_payload(self):
        response = self.client.post(
            reverse('flujos:api_tarea_asignar', args=[self.tarea.pk]),
            data='{"asignado_a": %s}' % self.assigned_user.pk,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.asignado_a, self.assigned_user)
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['task']['id'], self.tarea.pk)
        self.assertEqual(payload['task']['asignado_a']['id'], self.assigned_user.pk)

    def test_api_tarea_asignar_rejects_invalid_json(self):
        response = self.client.post(
            reverse('flujos:api_tarea_asignar', args=[self.tarea.pk]),
            data='{"asignado_a":',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'JSON invalido.')

    def test_api_tarea_resolver_updates_task_and_instance(self):
        response = self.client.post(
            reverse('flujos:api_tarea_resolver', args=[self.tarea_condicional.pk]),
            data='{"datos": {"aprobado": true, "observacion": "Apto API"}}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.tarea_condicional.refresh_from_db()
        self.instancia_condicional.refresh_from_db()
        self.assertTrue(payload['ok'])
        self.assertEqual(self.tarea_condicional.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia_condicional.estado, self.instancia_condicional.Estado.COMPLETADA)
        self.assertEqual(payload['task']['id'], self.tarea_condicional.pk)
        self.assertEqual(payload['instance']['id'], self.instancia_condicional.pk)
        self.assertEqual(payload['instance']['datos']['aprobado'], True)
        self.assertEqual(payload['instance']['datos']['observacion'], 'Apto API')

    def test_api_tarea_resolver_rejects_invalid_json(self):
        response = self.client.post(
            reverse('flujos:api_tarea_resolver', args=[self.tarea.pk]),
            data='{"datos":',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'JSON invalido.')

    def test_asignar_tarea_desde_bandeja(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_asignar', args=[self.tarea.pk]),
            {
                'asignado_a': str(self.assigned_user.pk),
                'next': reverse('flujos_editor:bandeja_tareas'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.asignado_a, self.assigned_user)
        ultimo_log = self.instancia.logs.order_by('-timestamp', '-pk').first()
        self.assertEqual(ultimo_log.motivo, 'Asignacion de tarea')
        self.assertEqual(ultimo_log.usuario, self.user)
        self.assertEqual(ultimo_log.datos_transicion['tarea_id'], self.tarea.pk)
        self.assertEqual(
            ultimo_log.datos_transicion['asignado_nuevo_id'],
            self.assigned_user.pk,
        )

    def test_reasignar_tarea_desde_detalle(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_asignar', args=[self.tarea_condicional.pk]),
            {
                'asignado_a': str(self.user.pk),
                'next': reverse('flujos_editor:tarea_detalle', args=[self.tarea_condicional.pk]),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.tarea_condicional.refresh_from_db()
        self.assertEqual(self.tarea_condicional.asignado_a, self.user)
        ultimo_log = self.instancia_condicional.logs.order_by('-timestamp', '-pk').first()
        self.assertEqual(ultimo_log.motivo, 'Reasignacion de tarea')
        self.assertEqual(ultimo_log.usuario, self.user)
        self.assertEqual(
            ultimo_log.datos_transicion['asignado_anterior_id'],
            self.assigned_user.pk,
        )
        self.assertEqual(ultimo_log.datos_transicion['asignado_nuevo_id'], self.user.pk)

    def test_resolver_task_advances_flow(self):
        response = self.client.post(
            reverse('flujos_editor:tarea_resolver', args=[self.tarea.pk]),
            {'next': reverse('flujos_editor:bandeja_tareas')},
        )

        self.assertEqual(response.status_code, 302)
        self.tarea.refresh_from_db()
        self.instancia.refresh_from_db()
        self.assertEqual(self.tarea.estado, TareaFlujo.Estado.RESUELTA)
        self.assertEqual(self.instancia.estado, self.instancia.Estado.COMPLETADA)
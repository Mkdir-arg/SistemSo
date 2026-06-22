from django.contrib.auth.models import Group, User
from django.test import TestCase

from flujos.application.services import (
    FlowTaskActionError,
    asignar_tarea_flujo,
    resolver_tarea_flujo,
)
from flujos.infrastructure.selectors import rol_programa_esta_en_uso
from flujos.models import AsignacionRolPrograma, Flujo, RolPrograma, VersionFlujo
from flujos.runtime import FlowRuntime
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa


class RolProgramaEnforcementTests(TestCase):
    """Cubre el enforcement de RolPrograma sobre TareaFlujo."""

    def setUp(self):
        self.programa_operar_group = Group.objects.create(name='programaOperar')

        self.usuario_con_rol = User.objects.create_user(
            username='operador-con-rol',
            password='clave-segura-123',
            is_staff=True,
        )
        self.usuario_con_rol.groups.add(self.programa_operar_group)

        self.usuario_sin_rol = User.objects.create_user(
            username='operador-sin-rol',
            password='clave-segura-123',
            is_staff=True,
        )
        self.usuario_sin_rol.groups.add(self.programa_operar_group)

        self.ciudadano = Ciudadano.objects.create(
            dni='30199890',
            nombre='Lucas',
            apellido='Fontana',
            genero=Ciudadano.Genero.MASCULINO,
        )
        self.programa = Programa.objects.create(
            codigo='PROG-ROL-001',
            nombre='Programa Roles',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        self.rol = RolPrograma.objects.create(programa=self.programa, nombre='Evaluador')
        AsignacionRolPrograma.objects.create(rol=self.rol, usuario=self.usuario_con_rol)

        self.inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=self.programa,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        flujo = Flujo.objects.create(programa=self.programa, nombre='Flujo Roles')
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {
                        'id': 'revision',
                        'tipo': 'accion_humana',
                        'nombre': 'Revision',
                        'config': {'rol_programa_id': self.rol.pk},
                    },
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision', 'condicion': None},
                    {'desde': 'revision', 'hasta': 'fin', 'condicion': None},
                ],
            },
        )

        self.instancia = FlowRuntime.iniciar(self.inscripcion)
        self.tarea = self.instancia.tareas.get()

    def test_usuario_sin_rol_no_puede_resolver_la_tarea(self):
        with self.assertRaises(FlowTaskActionError):
            resolver_tarea_flujo(tarea=self.tarea, usuario=self.usuario_sin_rol, datos={})

    def test_usuario_con_rol_puede_resolver_la_tarea(self):
        resolver_tarea_flujo(tarea=self.tarea, usuario=self.usuario_con_rol, datos={})

        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.estado, self.tarea.Estado.RESUELTA)

    def test_usuario_sin_rol_no_puede_asignarse_la_tarea(self):
        with self.assertRaises(FlowTaskActionError):
            asignar_tarea_flujo(tarea=self.tarea, usuario_asignado=self.usuario_sin_rol)

    def test_usuario_con_rol_puede_asignarse_la_tarea(self):
        asignar_tarea_flujo(tarea=self.tarea, usuario_asignado=self.usuario_con_rol)

        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.asignado_a, self.usuario_con_rol)

    def test_nodo_sin_rol_configurado_no_restringe_a_nadie(self):
        programa_libre = Programa.objects.create(
            codigo='PROG-ROL-002',
            nombre='Programa Sin Rol',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=self.ciudadano,
            programa=programa_libre,
            estado=InscripcionPrograma.Estado.PENDIENTE,
        )
        flujo = Flujo.objects.create(programa=programa_libre, nombre='Flujo Sin Rol')
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.PUBLICADA,
            definicion={
                'nodos': [
                    {'id': 'inicio', 'tipo': 'inicio', 'nombre': 'Inicio', 'config': {}},
                    {'id': 'revision', 'tipo': 'accion_humana', 'nombre': 'Revision', 'config': {}},
                    {'id': 'fin', 'tipo': 'fin', 'nombre': 'Fin', 'config': {}},
                ],
                'transiciones': [
                    {'desde': 'inicio', 'hasta': 'revision', 'condicion': None},
                    {'desde': 'revision', 'hasta': 'fin', 'condicion': None},
                ],
            },
        )
        instancia = FlowRuntime.iniciar(inscripcion)
        tarea = instancia.tareas.get()

        resolver_tarea_flujo(tarea=tarea, usuario=self.usuario_sin_rol, datos={})

        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, tarea.Estado.RESUELTA)


class RolProgramaUsoTests(TestCase):
    def test_rol_sin_asignaciones_ni_referencias_no_esta_en_uso(self):
        programa = Programa.objects.create(
            codigo='PROG-ROL-USO-001',
            nombre='Programa Uso Rol',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        rol = RolPrograma.objects.create(programa=programa, nombre='Sin uso')

        self.assertFalse(rol_programa_esta_en_uso(rol))

    def test_rol_con_asignacion_esta_en_uso(self):
        usuario = User.objects.create_user(username='con-asignacion', password='clave-segura-123')
        programa = Programa.objects.create(
            codigo='PROG-ROL-USO-002',
            nombre='Programa Uso Rol 2',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        rol = RolPrograma.objects.create(programa=programa, nombre='Con asignacion')
        AsignacionRolPrograma.objects.create(rol=rol, usuario=usuario)

        self.assertTrue(rol_programa_esta_en_uso(rol))

    def test_rol_referenciado_en_definicion_esta_en_uso(self):
        programa = Programa.objects.create(
            codigo='PROG-ROL-USO-003',
            nombre='Programa Uso Rol 3',
            tipo=Programa.TipoPrograma.ACOMPANAMIENTO_SEDRONAR,
        )
        rol = RolPrograma.objects.create(programa=programa, nombre='Referenciado')
        flujo = Flujo.objects.create(programa=programa, nombre='Flujo Uso Rol')
        VersionFlujo.objects.create(
            flujo=flujo,
            estado=VersionFlujo.Estado.BORRADOR,
            definicion={
                'nodos': [
                    {
                        'id': 'revision',
                        'tipo': 'accion_humana',
                        'nombre': 'Revision',
                        'config': {'rol_programa_id': rol.pk},
                    },
                ],
                'transiciones': [],
            },
        )

        self.assertTrue(rol_programa_esta_en_uso(rol))

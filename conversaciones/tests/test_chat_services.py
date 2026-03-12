from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from conversaciones.forms_chat import IniciarConversacionForm, MensajeConversacionForm
from conversaciones.models import Conversacion, HistorialAlertaConversacion, Mensaje
from conversaciones.selectors_conversaciones import get_alertas_conversaciones_count
from conversaciones.services_chat import (
    crear_mensaje_operador,
    iniciar_conversacion_publica,
    marcar_mensajes_ciudadano_leidos,
)


class IniciarConversacionFormTests(TestCase):
    def test_acepta_conversacion_personal_sin_endurecer_contrato_legacy(self):
        form = IniciarConversacionForm({
            'tipo': 'personal',
            'prioridad': 'normal',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tipo'], 'personal')

    def test_mensaje_form_normaliza_espacios(self):
        form = MensajeConversacionForm({'mensaje': '  hola  '})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['mensaje'], 'hola')


class ChatServicesTests(TestCase):
    def setUp(self):
        self.operador = User.objects.create_user(
            username='operador-chat',
            password='secret',
            first_name='Operador',
            last_name='Chat',
        )

    @patch('conversaciones.services_chat.NotificacionService.notificar_nueva_conversacion')
    @patch('conversaciones.services_chat.AsignadorAutomatico.asignar_conversacion_automatica', return_value=False)
    def test_iniciar_conversacion_publica_crea_conversacion_activa(self, mock_asignar, mock_notificar):
        conversacion = iniciar_conversacion_publica({
            'tipo': 'anonima',
            'dni': '',
            'sexo': '',
            'datos_renaper': {},
            'prioridad': 'alta',
        })

        self.assertEqual(conversacion.estado, 'activa')
        self.assertEqual(conversacion.prioridad, 'alta')
        mock_asignar.assert_called_once_with(conversacion)
        mock_notificar.assert_called_once_with(conversacion)

    def test_crear_mensaje_operador_autoasigna_si_no_tiene_operador(self):
        conversacion = Conversacion.objects.create(tipo='anonima', prioridad='normal', estado='activa')

        mensaje = crear_mensaje_operador(conversacion, self.operador, 'respuesta')

        conversacion.refresh_from_db()
        self.assertEqual(mensaje.remitente, 'operador')
        self.assertEqual(conversacion.operador_asignado, self.operador)
        self.assertEqual(Mensaje.objects.filter(conversacion=conversacion).count(), 1)

    def test_crear_mensaje_operador_falla_si_esta_asignada_a_otro(self):
        otro_operador = User.objects.create_user(username='otro-operador', password='secret')
        conversacion = Conversacion.objects.create(
            tipo='anonima',
            prioridad='normal',
            estado='activa',
            operador_asignado=otro_operador,
        )

        with self.assertRaises(PermissionError):
            crear_mensaje_operador(conversacion, self.operador, 'respuesta')

    def test_marcar_mensajes_ciudadano_leidos_actualiza_solo_no_leidos(self):
        conversacion = Conversacion.objects.create(
            tipo='anonima',
            prioridad='normal',
            estado='activa',
            operador_asignado=self.operador,
        )
        Mensaje.objects.create(conversacion=conversacion, remitente='ciudadano', contenido='uno', leido=False)
        Mensaje.objects.create(conversacion=conversacion, remitente='ciudadano', contenido='dos', leido=True)
        Mensaje.objects.create(conversacion=conversacion, remitente='operador', contenido='tres', leido=False)

        actualizados = marcar_mensajes_ciudadano_leidos(conversacion)

        self.assertEqual(actualizados, 1)
        self.assertEqual(
            Mensaje.objects.filter(conversacion=conversacion, remitente='ciudadano', leido=False).count(),
            0,
        )

    def test_selector_alertas_count_devuelve_solo_no_vistas_del_operador(self):
        conversacion = Conversacion.objects.create(
            tipo='anonima',
            prioridad='normal',
            estado='activa',
            operador_asignado=self.operador,
        )
        HistorialAlertaConversacion.objects.create(
            conversacion=conversacion,
            operador=self.operador,
            tipo='NUEVO_MENSAJE',
            mensaje='alerta 1',
            vista=False,
        )
        HistorialAlertaConversacion.objects.create(
            conversacion=conversacion,
            operador=self.operador,
            tipo='NUEVA_CONVERSACION',
            mensaje='alerta 2',
            vista=True,
        )

        self.assertEqual(get_alertas_conversaciones_count(self.operador), 1)

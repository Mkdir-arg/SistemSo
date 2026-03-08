import random
import string

from django.db import models


class RecursoTurnos(models.Model):
    """Entidad que ofrece turnos: institución NODO, organismo de gobierno, o profesional."""

    class Tipo(models.TextChoices):
        INSTITUCION_NODO = 'NODO', 'Institución NODO'
        ORGANISMO = 'ORGANISMO', 'Organismo de Gobierno'
        PROFESIONAL = 'PROFESIONAL', 'Profesional'

    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(max_length=20, choices=Tipo.choices, verbose_name='Tipo')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    direccion = models.CharField(max_length=300, blank=True, verbose_name='Dirección')
    telefono = models.CharField(max_length=50, blank=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, verbose_name='Email de contacto')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    requiere_aprobacion = models.BooleanField(
        default=False,
        verbose_name='Requiere aprobación',
        help_text='Si está activo, el turno queda pendiente hasta ser confirmado por el backoffice.',
    )

    class Meta:
        verbose_name = 'Recurso de turnos'
        verbose_name_plural = 'Recursos de turnos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'


class DisponibilidadTurnos(models.Model):
    """Configuración semanal de disponibilidad de un recurso."""

    DIAS = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    recurso = models.ForeignKey(
        RecursoTurnos,
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        verbose_name='Recurso',
    )
    dia_semana = models.IntegerField(choices=DIAS, verbose_name='Día de la semana')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    duracion_turno_min = models.PositiveIntegerField(
        default=30, verbose_name='Duración del turno (minutos)'
    )
    cupo_maximo = models.PositiveIntegerField(default=1, verbose_name='Cupo máximo por slot')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Disponibilidad de turnos'
        verbose_name_plural = 'Disponibilidades de turnos'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = [['recurso', 'dia_semana', 'hora_inicio']]

    def __str__(self):
        return (
            f'{self.recurso.nombre} — {self.get_dia_semana_display()} '
            f'{self.hora_inicio}-{self.hora_fin}'
        )


class TurnoCiudadano(models.Model):
    """Turno solicitado por un ciudadano."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de confirmación'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        CANCELADO_CIUDADANO = 'CANCELADO_CIU', 'Cancelado por el ciudadano'
        CANCELADO_SISTEMA = 'CANCELADO_SIS', 'Cancelado por el sistema'
        COMPLETADO = 'COMPLETADO', 'Completado'

    ciudadano = models.ForeignKey(
        'legajos.Ciudadano',
        on_delete=models.PROTECT,
        related_name='turnos',
        verbose_name='Ciudadano',
    )
    recurso = models.ForeignKey(
        RecursoTurnos,
        on_delete=models.PROTECT,
        related_name='turnos',
        verbose_name='Recurso',
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado',
    )
    motivo_consulta = models.TextField(
        blank=True,
        verbose_name='Motivo de la consulta',
        help_text='Descripción opcional del motivo del turno.',
    )
    notas_backoffice = models.TextField(
        blank=True,
        verbose_name='Notas internas',
        help_text='Solo visible para el personal del backoffice.',
    )
    codigo_turno = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Código de turno',
    )
    recordatorio_enviado = models.BooleanField(default=False, verbose_name='Recordatorio enviado')
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora_inicio']
        indexes = [
            models.Index(fields=['ciudadano', 'estado']),
            models.Index(fields=['recurso', 'fecha']),
            models.Index(fields=['fecha', 'hora_inicio']),
        ]

    def save(self, *args, **kwargs):
        if not self.codigo_turno:
            self.codigo_turno = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Turno {self.codigo_turno} — {self.ciudadano} — {self.fecha} {self.hora_inicio}'

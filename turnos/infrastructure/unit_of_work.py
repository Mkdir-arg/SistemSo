"""Adaptador Django para transacciones y reloj de la aplicacion de turnos."""

from django.db import transaction
from django.utils import timezone


atomic = transaction.atomic
on_commit = transaction.on_commit
now = timezone.now

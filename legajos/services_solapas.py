"""
Servicio para gestionar solapas dinámicas de programas
"""
from django.db.models import Q
from .models_programas import Programa, InscripcionPrograma, DerivacionPrograma


class SolapasService:
    """Servicio para obtener las solapas dinámicas de un ciudadano"""
    
    # Solapas estáticas (siempre visibles)
    SOLAPAS_ESTATICAS = [
        {
            'id': 'resumen',
            'nombre': 'Resumen',
            'icono': 'dashboard',
            'url_name': 'legajos:ciudadano_detalle',
            'orden': 0,
            'estatica': True
        },
        {
            'id': 'cursos_actividades',
            'nombre': 'Cursos y Actividades',
            'icono': 'school',
            'url_name': 'legajos:actividades_inscrito',
            'orden': 900,
            'estatica': True
        },
        {
            'id': 'red_familiar',
            'nombre': 'Red Familiar',
            'icono': 'people',
            'url_name': 'legajos:red_contactos',
            'orden': 998,
            'estatica': True
        },
        {
            'id': 'archivos',
            'nombre': 'Archivos',
            'icono': 'folder',
            'url_name': 'legajos:archivos',
            'orden': 999,
            'estatica': True
        }
    ]
    
    @classmethod
    def obtener_solapas_ciudadano(cls, ciudadano):
        """
        Obtiene todas las solapas (estáticas + dinámicas) para un ciudadano
        
        Args:
            ciudadano: Instancia de Ciudadano
            
        Returns:
            Lista de diccionarios con información de cada solapa
        """
        solapas = []
        
        # 1. Agregar solapa de Resumen (siempre primera)
        solapas.append(cls.SOLAPAS_ESTATICAS[0])
        
        # 2. Obtener programas activos del ciudadano
        inscripciones_activas = InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
        ).select_related('programa').order_by('programa__orden')
        
        # 3. Agregar solapas dinámicas de programas (entre Resumen y Cursos)
        for inscripcion in inscripciones_activas:
            programa = inscripcion.programa
            solapa = {
                'id': f'programa_{programa.tipo}',
                'nombre': programa.nombre,
                'icono': programa.icono or 'assignment',
                'color': programa.color,
                'url_name': cls._obtener_url_programa(programa.tipo),
                'url_params': {'ciudadano_id': ciudadano.id, 'inscripcion_id': inscripcion.id},
                'orden': 100 + programa.orden,  # Orden entre 100-899 para programas dinámicos
                'estatica': False,
                'programa': programa,
                'inscripcion': inscripcion,
                'badge': cls._obtener_badge_programa(inscripcion)
            }
            solapas.append(solapa)
        
        # 4. Agregar solapas estáticas finales (Cursos, Red Familiar, Archivos)
        solapas.extend(cls.SOLAPAS_ESTATICAS[1:])
        
        # 5. Ordenar por campo 'orden'
        solapas.sort(key=lambda x: x['orden'])
        
        return solapas
    
    @classmethod
    def obtener_programas_activos(cls, ciudadano):
        """
        Obtiene solo los programas activos del ciudadano
        
        Args:
            ciudadano: Instancia de Ciudadano
            
        Returns:
            QuerySet de InscripcionPrograma
        """
        return InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
        ).select_related('programa').order_by('programa__orden')
    
    @classmethod
    def obtener_programas_disponibles_derivacion(cls, ciudadano, programa_origen=None):
        """
        Obtiene programas disponibles para derivación (que el ciudadano NO tiene activos)
        
        Args:
            ciudadano: Instancia de Ciudadano
            programa_origen: Programa desde el cual se deriva (opcional)
            
        Returns:
            QuerySet de Programa
        """
        # Obtener IDs de programas donde ya está inscrito
        programas_inscritos = InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
        ).values_list('programa_id', flat=True)
        
        # Obtener programas activos que NO tiene
        programas_disponibles = Programa.objects.filter(
            activo=True
        ).exclude(
            id__in=programas_inscritos
        )
        
        # Si hay programa origen, excluirlo también
        if programa_origen:
            programas_disponibles = programas_disponibles.exclude(id=programa_origen.id)
        
        return programas_disponibles.order_by('orden', 'nombre')
    
    @classmethod
    def tiene_derivaciones_pendientes(cls, ciudadano, programa=None):
        """
        Verifica si el ciudadano tiene derivaciones pendientes
        
        Args:
            ciudadano: Instancia de Ciudadano
            programa: Programa específico (opcional)
            
        Returns:
            bool
        """
        query = Q(ciudadano=ciudadano, estado='PENDIENTE')
        
        if programa:
            query &= Q(programa_destino=programa)
        
        return DerivacionPrograma.objects.filter(query).exists()
    
    @classmethod
    def obtener_derivaciones_pendientes(cls, ciudadano):
        """
        Obtiene todas las derivaciones pendientes del ciudadano
        
        Args:
            ciudadano: Instancia de Ciudadano
            
        Returns:
            QuerySet de DerivacionPrograma
        """
        return DerivacionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado='PENDIENTE'
        ).select_related(
            'programa_origen',
            'programa_destino',
            'derivado_por'
        ).order_by('-creado')
    
    @classmethod
    def _obtener_url_programa(cls, tipo_programa):
        """
        Mapea el tipo de programa a su URL name
        
        Args:
            tipo_programa: Tipo del programa
            
        Returns:
            str: URL name
        """
        url_map = {
            'ACOMPANAMIENTO_SEDRONAR': 'legajos:detalle',
            'NACHEC': 'nachec:detalle_caso_ciudadano',
            'ECONOMICO': 'programas:economico_detalle',
            'FAMILIAR': 'programas:familiar_detalle',
        }
        return url_map.get(tipo_programa, 'legajos:programa_detalle')
    
    @classmethod
    def _obtener_badge_programa(cls, inscripcion):
        """
        Obtiene información de badge para mostrar en la solapa
        
        Args:
            inscripcion: InscripcionPrograma
            
        Returns:
            dict o None
        """
        # Ejemplo: mostrar alertas pendientes, seguimientos vencidos, etc.
        # Esto se puede personalizar según el programa
        
        if inscripcion.estado == 'PENDIENTE':
            return {
                'texto': 'Pendiente',
                'color': 'yellow'
            }
        
        # Aquí se pueden agregar más lógicas según el programa
        # Por ejemplo, contar alertas, seguimientos vencidos, etc.
        
        return None
    
    @classmethod
    def crear_inscripcion_directa(cls, ciudadano, programa, responsable, notas=''):
        """
        Crea una inscripción directa a un programa (sin derivación)
        
        Args:
            ciudadano: Instancia de Ciudadano
            programa: Instancia de Programa
            responsable: Usuario responsable
            notas: Notas adicionales
            
        Returns:
            InscripcionPrograma
        """
        # Verificar que no exista inscripción activa
        existe = InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            programa=programa,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
        ).exists()
        
        if existe:
            raise ValueError(f"El ciudadano ya tiene una inscripción activa en {programa.nombre}")
        
        inscripcion = InscripcionPrograma.objects.create(
            ciudadano=ciudadano,
            programa=programa,
            via_ingreso='DIRECTO',
            estado='ACTIVO',
            responsable=responsable,
            notas=notas
        )
        
        return inscripcion
    
    @classmethod
    def obtener_historial_programas(cls, ciudadano):
        """
        Obtiene el historial completo de programas del ciudadano (activos + cerrados)
        
        Args:
            ciudadano: Instancia de Ciudadano
            
        Returns:
            QuerySet de InscripcionPrograma
        """
        return InscripcionPrograma.objects.filter(
            ciudadano=ciudadano
        ).select_related('programa', 'responsable').order_by('-fecha_inscripcion')
    
    @classmethod
    def cerrar_inscripcion(cls, inscripcion, motivo_cierre, usuario):
        """
        Cierra una inscripción a un programa
        
        Args:
            inscripcion: InscripcionPrograma
            motivo_cierre: Motivo del cierre
            usuario: Usuario que cierra
        """
        from django.utils import timezone
        
        if inscripcion.estado == 'CERRADO':
            raise ValueError("La inscripción ya está cerrada")
        
        inscripcion.estado = 'CERRADO'
        inscripcion.fecha_cierre = timezone.now().date()
        inscripcion.motivo_cierre = motivo_cierre
        
        # Agregar nota de cierre
        nota_cierre = f"\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')}] Cerrado por {usuario.get_full_name() or usuario.username}\nMotivo: {motivo_cierre}"
        inscripcion.notas += nota_cierre
        
        inscripcion.save()

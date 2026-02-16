from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Carga todos los datos iniciales del sistema'
    
    def handle(self, *args, **options):
        self.stdout.write('Cargando datos iniciales...')
        
        # 1. Cargar programas
        try:
            self.stdout.write('  → Cargando programas...')
            call_command('loaddata', 'legajos/fixtures/programas_initial.json', verbosity=0)
            self.stdout.write(self.style.SUCCESS('    ✓ Programas cargados'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    ⚠ Programas ya existen o error: {e}'))
        
        # 2. Migrar legajos existentes
        try:
            self.stdout.write('  → Migrando legajos a programas...')
            call_command('migrar_legajos_a_programas', verbosity=0)
            self.stdout.write(self.style.SUCCESS('    ✓ Legajos migrados'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    ⚠ Error en migración: {e}'))
        
        # 3. Otros fixtures si existen
        try:
            self.stdout.write('  → Cargando contactos iniciales...')
            call_command('loaddata', 'contactos_initial_data', verbosity=0)
            self.stdout.write(self.style.SUCCESS('    ✓ Contactos cargados'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    ⚠ Contactos: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Datos iniciales cargados correctamente'))

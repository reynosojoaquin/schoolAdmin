from django.apps import AppConfig


class TimetablingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetabling'
    verbose_name = 'Gestión de Horarios Escolares'

    def ready(self):
        import timetabling.tasks  # noqa: F401

from django.db.utils import OperationalError, ProgrammingError
from django.templatetags.static import static

from .models import SystemConfiguration


def system_branding(request):
    logo_url = static("img/logo-centro-default.jpeg")
    configuration = None
    try:
        configuration = SystemConfiguration.objects.first()
    except (OperationalError, ProgrammingError):
        pass

    if configuration and configuration.logo:
        logo_url = configuration.logo.url

    return {
        "system_configuration": configuration,
        "institution_logo_url": logo_url,
    }


def access_flags(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    can_manage_users = user.is_superuser or user.has_perm("core.manage_users_roles")
    can_manage_people = user.is_superuser or user.has_perm("core.manage_people")
    can_manage_administration = can_manage_people or can_manage_users
    can_manage_academic = user.is_superuser or user.has_perm("core.manage_academic_setup")
    can_view_all_academic = user.is_superuser or user.has_perm("core.view_all_academic")
    can_manage_guidance = can_manage_people or can_view_all_academic or user.has_perm("core.view_all_school_years") or hasattr(user, "teacher_profile")
    is_teacher = user.has_perm("core.view_own_sections") and hasattr(user, "teacher_profile")
    can_view_academic = can_view_all_academic or is_teacher
    can_filter_school_year = user.is_superuser or can_manage_academic or can_view_all_academic or user.has_perm("core.view_all_school_years")

    # Coordinacion Administrativa
    can_manage_admin_inventory = user.is_superuser or user.has_perm("core.manage_admin_inventory")
    can_manage_admin_consumables = user.is_superuser or user.has_perm("core.manage_admin_consumables")
    can_manage_admin_finance = user.is_superuser or user.has_perm("core.manage_admin_finance")
    can_manage_admin_staff = user.is_superuser or user.has_perm("core.manage_admin_staff")
    can_manage_admin_section = can_manage_admin_inventory or can_manage_admin_consumables or can_manage_admin_finance or can_manage_admin_staff

    # Orientacion
    can_manage_guidance_cases = user.is_superuser or user.has_perm("core.manage_guidance_cases")
    can_view_all_people = user.is_superuser or user.has_perm("core.view_all_people")

    # Coordinacion Academica
    can_manage_registry_reports = user.is_superuser or user.has_perm("core.manage_registry_reports")

    return {
        "can_manage_system": can_manage_users,
        "can_manage_people": can_manage_people,
        "can_manage_administration": can_manage_administration,
        "can_manage_guidance": can_manage_guidance,
        "can_manage_academic": can_manage_academic,
        "can_view_academic": can_view_academic,
        "can_edit_grades": user.is_superuser or user.has_perm("core.edit_grades"),
        "can_import_grades": user.is_superuser or user.has_perm("core.import_grades"),
        "can_view_grade_stats": user.is_superuser or user.has_perm("core.view_grade_stats"),
        "is_teacher_access": is_teacher,
        "can_filter_school_year": can_filter_school_year,
        # Coordinacion Administrativa
        "can_manage_admin_inventory": can_manage_admin_inventory,
        "can_manage_admin_consumables": can_manage_admin_consumables,
        "can_manage_admin_finance": can_manage_admin_finance,
        "can_manage_admin_staff": can_manage_admin_staff,
        "can_manage_admin_section": can_manage_admin_section,
        # Orientacion
        "can_manage_guidance_cases": can_manage_guidance_cases,
        "can_view_all_people": can_view_all_people,
        # Coordinacion Academica
        "can_manage_registry_reports": can_manage_registry_reports,
    }

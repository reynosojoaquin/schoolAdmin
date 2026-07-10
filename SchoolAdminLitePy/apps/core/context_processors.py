def access_flags(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    can_manage_users = user.is_superuser or user.has_perm("core.manage_users_roles")
    can_manage_people = user.is_superuser or user.has_perm("core.manage_people")
    can_manage_academic = user.is_superuser or user.has_perm("core.manage_academic_setup")
    can_view_all_academic = user.is_superuser or user.has_perm("core.view_all_academic")
    is_teacher = user.has_perm("core.view_own_sections") and hasattr(user, "teacher_profile")
    can_view_academic = can_view_all_academic or is_teacher
    return {
        "can_manage_system": can_manage_users,
        "can_manage_people": can_manage_people,
        "can_manage_academic": can_manage_academic,
        "can_view_academic": can_view_academic,
        "can_edit_grades": user.is_superuser or user.has_perm("core.edit_grades"),
        "can_import_grades": user.is_superuser or user.has_perm("core.import_grades"),
        "can_view_grade_stats": user.is_superuser or user.has_perm("core.view_grade_stats"),
        "is_teacher_access": is_teacher,
    }

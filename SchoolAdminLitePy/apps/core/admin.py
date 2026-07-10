from django.contrib import admin

from .models import (
    Address,
    AddressType,
    AccessRule,
    AdministrativeEmployee,
    Birthplace,
    City,
    Competency,
    Contact,
    ContactType,
    Course,
    Curriculum,
    CurriculumDetail,
    CurriculumInstitution,
    CurriculumType,
    EmployeePosition,
    EmployeeType,
    Enrollment,
    Grade,
    GradeCompletion,
    Nationality,
    Phone,
    PhoneType,
    Province,
    Sector,
    Section,
    Student,
    Subject,
    SubjectCompetency,
    TeachingAssignment,
    Teacher,
)


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ["name", "province__name"]
    list_display = ["name", "province"]
    list_filter = ["province"]


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    search_fields = ["name", "city__name"]
    list_display = ["name", "city"]
    list_filter = ["city__province", "city"]


@admin.register(Nationality, Birthplace)
class NamedCatalogAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


@admin.register(AddressType, PhoneType, ContactType)
class DescriptionCatalogAdmin(admin.ModelAdmin):
    search_fields = ["description"]
    list_display = ["description"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ["name", "responsible__first_name", "responsible__last_name"]
    list_display = ["name", "responsible", "active"]
    list_filter = ["active"]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    search_fields = ["name", "course__name", "school_year", "responsible__first_name", "responsible__last_name"]
    list_display = ["course", "name", "school_year", "responsible", "active"]
    list_filter = ["school_year", "course", "active"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ["name", "course__name", "responsible__first_name", "responsible__last_name"]
    list_display = ["name", "course", "responsible"]
    list_filter = ["course"]


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    search_fields = [
        "section__name",
        "section__course__name",
        "subject__name",
        "teacher__first_name",
        "teacher__last_name",
    ]
    list_display = ["section", "subject", "teacher", "active"]
    list_filter = ["active", "section__school_year", "section__course", "section", "subject"]


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    search_fields = ["description"]
    list_display = ["description"]


@admin.register(SubjectCompetency)
class SubjectCompetencyAdmin(admin.ModelAdmin):
    search_fields = ["subject__name", "competency__description"]
    list_display = ["subject", "competency"]
    list_filter = ["subject__course", "subject"]


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ["address_type", "province", "city", "sector", "street", "number", "apartment"]


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 0
    fields = ["phone_type", "number"]


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ["contact_type", "first_name", "last_name", "phone"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "document_id", "email"]
    list_display = ["last_name", "first_name", "document_id", "phone", "active"]
    list_filter = ["active", "nationality", "sector__city__province"]
    inlines = [AddressInline, PhoneInline, ContactInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "document_id", "email", "user__username"]
    list_display = ["last_name", "first_name", "document_id", "email", "user", "active"]
    list_filter = ["active", "nationality"]
    inlines = [AddressInline, PhoneInline, ContactInline]


@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    search_fields = ["name", "employee_type__name"]
    list_display = ["name", "employee_type"]
    list_filter = ["employee_type"]


@admin.register(AdministrativeEmployee)
class AdministrativeEmployeeAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "document_id", "email"]
    list_display = ["last_name", "first_name", "document_id", "employee_type", "position", "active"]
    list_filter = ["active", "employee_type", "position", "nationality"]
    inlines = [AddressInline, PhoneInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ["street", "number", "student__first_name", "student__last_name"]
    list_display = ["street", "number", "province", "city", "sector", "address_type"]
    list_filter = ["address_type", "province", "city", "sector"]


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    search_fields = ["number", "student__first_name", "student__last_name"]
    list_display = ["number", "phone_type", "student", "teacher", "administrative_employee"]
    list_filter = ["phone_type"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "phone", "student__first_name", "student__last_name"]
    list_display = ["last_name", "first_name", "phone", "contact_type", "student", "teacher"]
    list_filter = ["contact_type"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    search_fields = ["student__first_name", "student__last_name", "course__name", "section__name", "school_year"]
    list_display = ["student", "course", "section", "school_year", "active"]
    list_filter = ["school_year", "course", "section", "active"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    search_fields = ["enrollment__student__first_name", "enrollment__student__last_name", "subject__name"]
    list_display = ["enrollment", "subject", "subject_competency", "period_1", "period_2", "period_3", "period_4", "average"]
    list_filter = ["subject", "subject_competency", "enrollment__school_year"]


@admin.register(GradeCompletion)
class GradeCompletionAdmin(admin.ModelAdmin):
    search_fields = ["enrollment__student__first_name", "enrollment__student__last_name", "subject__name"]
    list_display = ["enrollment", "subject", "cf", "cef", "ccf", "ceex", "cexf", "approved", "reproved"]
    list_filter = ["subject", "enrollment__school_year"]


class CurriculumDetailInline(admin.TabularInline):
    model = CurriculumDetail
    extra = 0


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    search_fields = ["teacher__first_name", "teacher__last_name", "administrative_employee__first_name"]
    list_display = ["teacher", "administrative_employee", "folder"]
    inlines = [CurriculumDetailInline]


@admin.register(CurriculumDetail)
class CurriculumDetailAdmin(admin.ModelAdmin):
    search_fields = ["description", "institution__description"]
    list_display = ["description", "date", "institution", "curriculum_type", "deleted"]
    list_filter = ["curriculum_type", "institution", "deleted"]


@admin.register(CurriculumInstitution)
class CurriculumInstitutionAdmin(admin.ModelAdmin):
    search_fields = ["description"]
    list_display = ["description", "deleted"]
    list_filter = ["deleted"]


@admin.register(CurriculumType)
class CurriculumTypeAdmin(admin.ModelAdmin):
    search_fields = ["description"]
    list_display = ["description"]

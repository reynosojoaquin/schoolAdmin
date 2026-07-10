from django.contrib import admin

from .models import (
    Address,
    AddressType,
    AccessRule,
    AdministrativeEmployee,
    Attendance,
    BankAccount,
    BankReconciliation,
    Birthplace,
    Cheque,
    City,
    Competency,
    ConsumableItem,
    ConsumableMovement,
    Contact,
    ContactType,
    Course,
    Curriculum,
    CurriculumDetail,
    CurriculumInstitution,
    CurriculumType,
    EmployeePosition,
    EmployeeType,
    EquipmentCategory,
    EquipmentItem,
    EquipmentLoan,
    Enrollment,
    Expense,
    Grade,
    GradeCompletion,
    JournalEntry,
    Nationality,
    Phone,
    PhoneType,
    Province,
    Sector,
    Section,
    StaffAssignment,
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
    search_fields = [
        "name",
        "section__name",
        "section__course__name",
        "responsible__first_name",
        "responsible__last_name",
    ]
    list_display = ["name", "section", "weekly_hours", "responsible"]
    list_filter = ["section__course", "section"]


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
    list_filter = ["subject__section__course", "subject__section", "subject"]


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
    list_display = ["last_name", "first_name", "document_id", "phone", "promoted", "new_admission", "active"]
    list_filter = ["active", "promoted", "new_admission", "nationality", "sector__city__province"]
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


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    list_display = ["name", "active"]
    list_filter = ["active"]


@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    search_fields = ["code", "name", "brand", "model", "serial_number", "location"]
    list_display = ["code", "name", "category", "status", "location"]
    list_filter = ["status", "category"]


@admin.register(EquipmentLoan)
class EquipmentLoanAdmin(admin.ModelAdmin):
    search_fields = ["item__code", "item__name", "borrower_name", "borrowed_by__first_name", "borrowed_by__last_name"]
    list_display = ["item", "borrower_name", "loan_date", "due_date", "return_date", "status"]
    list_filter = ["status", "loan_date"]


@admin.register(ConsumableItem)
class ConsumableItemAdmin(admin.ModelAdmin):
    search_fields = ["name", "category"]
    list_display = ["name", "category", "quantity_available", "minimum_stock", "unit", "active"]
    list_filter = ["active", "category"]


@admin.register(ConsumableMovement)
class ConsumableMovementAdmin(admin.ModelAdmin):
    search_fields = ["item__name", "delivered_to", "notes"]
    list_display = ["date", "item", "movement_type", "quantity", "delivered_to"]
    list_filter = ["movement_type", "date"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    search_fields = ["category", "description", "vendor", "cheque_number"]
    list_display = ["date", "category", "description", "vendor", "amount", "payment_method"]
    list_filter = ["date", "category", "payment_method"]


@admin.register(Cheque)
class ChequeAdmin(admin.ModelAdmin):
    search_fields = ["number", "payee", "concept"]
    list_display = ["number", "date", "payee", "amount", "status"]
    list_filter = ["status", "date"]


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    search_fields = ["name", "bank_name", "account_number"]
    list_display = ["bank_name", "name", "account_number", "account_type", "active"]
    list_filter = ["active", "bank_name"]


@admin.register(BankReconciliation)
class BankReconciliationAdmin(admin.ModelAdmin):
    search_fields = ["period", "bank_account__name", "bank_account__bank_name", "bank_account__account_number"]
    list_display = ["period", "bank_account", "statement_balance", "book_balance", "difference", "status"]
    list_filter = ["status", "period", "bank_account"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    search_fields = ["reference", "description", "debit_account", "credit_account"]
    list_display = ["date", "reference", "description", "debit_account", "credit_account", "amount"]
    list_filter = ["date", "debit_account", "credit_account"]


@admin.register(StaffAssignment)
class StaffAssignmentAdmin(admin.ModelAdmin):
    search_fields = ["employee__first_name", "employee__last_name", "area", "role"]
    list_display = ["employee", "area", "role", "start_date", "end_date", "active"]
    list_filter = ["active", "area"]


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


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    search_fields = ["enrollment__student__first_name", "enrollment__student__last_name", "enrollment__student__document_id"]
    list_display = ["date", "enrollment", "status", "recorded_by"]
    list_filter = ["date", "status", "enrollment__section", "enrollment__course"]


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

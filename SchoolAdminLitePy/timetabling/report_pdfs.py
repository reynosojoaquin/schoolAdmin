from collections import defaultdict
from io import BytesIO
import re
from xml.sax.saxutils import escape

from apps.core.models import Section, Subject, SystemConfiguration, TeachingAssignment


def _reportlab():
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    return {
        "colors": colors,
        "TA_CENTER": TA_CENTER,
        "TA_LEFT": TA_LEFT,
        "letter": letter,
        "getSampleStyleSheet": getSampleStyleSheet,
        "ParagraphStyle": ParagraphStyle,
        "inch": inch,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
    }


def _section_sort_key(section):
    match = re.search(r"\d+", section.course.name)
    course_number = int(match.group()) if match else 999
    return course_number, section.course.name, section.name


def _row_color(subject_names, colors):
    text = " ".join(subject_names).lower()
    if any(word in text for word in ("lengua", "español", "espanol", "lectoescritura")):
        return colors.HexColor("#f4b183")
    if any(word in text for word in ("inglés", "ingles", "francés", "frances", "idioma")):
        return colors.HexColor("#ffc000")
    if "matem" in text:
        return colors.HexColor("#12afe0")
    if "social" in text:
        return colors.HexColor("#cf5a0b")
    if any(word in text for word in ("natural", "ciencia")):
        return colors.HexColor("#92d050")
    if any(word in text for word in ("artística", "artistica", "arte")):
        return colors.HexColor("#bfbfbf")
    if any(word in text for word in ("física", "fisica", "deporte")):
        return colors.HexColor("#00b050")
    return colors.HexColor("#d9e2f3")


def build_teaching_load_pdf(school_year, teacher_id=None):
    rl = _reportlab()
    colors = rl["colors"]
    sections = sorted(
        Section.objects.filter(active=True, course__active=True, school_year=school_year).select_related("course"),
        key=_section_sort_key,
    )
    if teacher_id:
        assigned_section_ids = set(
            TeachingAssignment.objects.filter(
                active=True,
                teacher_id=teacher_id,
                section__school_year=school_year,
            ).values_list("section_id", flat=True)
        )
        sections = [section for section in sections if section.pk in assigned_section_ids]
    section_ids = [section.pk for section in sections]
    subjects = list(
        Subject.objects.filter(section_id__in=section_ids, weekly_hours__gt=0)
        .select_related("section", "section__course")
        .order_by("name")
    )
    assignment_queryset = TeachingAssignment.objects.filter(
        active=True,
        teacher__active=True,
        section_id__in=section_ids,
    )
    if teacher_id:
        assignment_queryset = assignment_queryset.filter(teacher_id=teacher_id)
    assignments = {
        assignment.subject_id: assignment
        for assignment in assignment_queryset.select_related("teacher", "subject", "section")
    }

    rows = defaultdict(lambda: {"teacher": None, "subjects": set(), "hours": defaultdict(int)})
    missing_count = 0
    for subject in subjects:
        assignment = assignments.get(subject.pk)
        if teacher_id and assignment is None:
            continue
        assigned_teacher_id = assignment.teacher_id if assignment else None
        row_key = assigned_teacher_id if assigned_teacher_id is not None else "missing"
        row = rows[row_key]
        row["teacher"] = assignment.teacher if assignment else None
        row["subjects"].add(subject.name)
        row["hours"][subject.section_id] += subject.weekly_hours
        if assignment is None:
            missing_count += 1

    ordered_rows = sorted(
        rows.values(),
        key=lambda row: (
            row["teacher"] is None,
            getattr(row["teacher"], "last_name", ""),
            getattr(row["teacher"], "first_name", ""),
        ),
    )
    section_labels = [f"{section.course.name}{section.name}" for section in sections]
    header = ["Profesor", "Asignaturas", *section_labels, "T"]
    data = [header]
    section_totals = defaultdict(int)
    styles = rl["getSampleStyleSheet"]()
    teacher_style = rl["ParagraphStyle"](
        "load_teacher",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.4,
        leading=7.2,
        alignment=rl["TA_LEFT"],
    )
    subjects_style = rl["ParagraphStyle"](
        "load_subjects",
        parent=styles["Normal"],
        fontSize=5.8,
        leading=6.6,
        alignment=rl["TA_LEFT"],
    )
    row_colors = []
    for row_index, row in enumerate(ordered_rows, start=1):
        subject_names = sorted(row["subjects"])
        if row["teacher"] is None:
            teacher_name = f"SIN DOCENTE ({missing_count})"
        else:
            teacher_name = str(row["teacher"])
        values = []
        for section in sections:
            hours = row["hours"].get(section.pk, 0)
            values.append(hours or "")
            section_totals[section.pk] += hours
        total = sum(value for value in values if isinstance(value, int))
        data.append(
            [
                rl["Paragraph"](escape(teacher_name), teacher_style),
                rl["Paragraph"]("<br/>".join(escape(name) for name in subject_names), subjects_style),
                *values,
                total,
            ]
        )
        row_colors.append((row_index, colors.HexColor("#f4cccc") if row["teacher"] is None else _row_color(subject_names, colors)))

    grand_total = sum(section_totals.values())
    data.append(["", "Total", *[section_totals[section.pk] for section in sections], grand_total])
    total_row = len(data) - 1

    buffer = BytesIO()
    doc = rl["SimpleDocTemplate"](
        buffer,
        pagesize=rl["letter"],
        rightMargin=0.18 * rl["inch"],
        leftMargin=0.18 * rl["inch"],
        topMargin=0.22 * rl["inch"],
        bottomMargin=0.22 * rl["inch"],
    )
    configuration = SystemConfiguration.get_solo()
    institution_name = configuration.institution_name or "Liceo Coronel Rafael Tomas Fernandez Dominguez"
    title_style = rl["ParagraphStyle"](
        "load_title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=17,
        alignment=rl["TA_CENTER"],
    )
    year_style = rl["ParagraphStyle"](
        "load_year",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=rl["TA_CENTER"],
    )
    warning = f"{missing_count} asignaciones sin docente" if missing_count else "Carga docente completa"
    story = [
        rl["Table"](
            [[rl["Paragraph"](f"CARGA LECTIVA {escape(school_year)}", year_style)]],
            colWidths=[7.5 * rl["inch"]],
            style=rl["TableStyle"]([("BACKGROUND", (0, 0), (-1, -1), colors.yellow), ("ALIGN", (0, 0), (-1, -1), "CENTER")]),
        ),
        rl["Paragraph"](escape(institution_name), title_style),
        rl["Paragraph"](warning, year_style),
        rl["Spacer"](1, 8),
    ]
    section_width = 0.26 * rl["inch"]
    table = rl["Table"](
        data,
        repeatRows=1,
        colWidths=[1.08 * rl["inch"], 1.58 * rl["inch"], *([section_width] * len(sections)), 0.4 * rl["inch"]],
    )
    table_style = [
        ("GRID", (0, 0), (-1, -1), 0.55, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("BACKGROUND", (0, total_row), (1, total_row), colors.black),
        ("TEXTCOLOR", (0, total_row), (1, total_row), colors.white),
        ("FONTNAME", (0, total_row), (-1, total_row), "Helvetica-Bold"),
        ("BACKGROUND", (2, total_row), (-2, total_row), colors.HexColor("#f4cccc")),
        ("BACKGROUND", (-1, total_row), (-1, total_row), colors.black),
        ("TEXTCOLOR", (-1, total_row), (-1, total_row), colors.white),
    ]
    for row_index, color in row_colors:
        table_style.append(("BACKGROUND", (0, row_index), (-1, row_index), color))
    for section_index, section in enumerate(sections, start=2):
        course_number = _section_sort_key(section)[0]
        if course_number >= 4:
            header_color = colors.red if section.name.upper() == "A" else colors.HexColor("#00b050")
            table_style.append(("TEXTCOLOR", (section_index, 0), (section_index, 0), header_color))
        else:
            table_style.append(("TEXTCOLOR", (section_index, 0), (section_index, 0), colors.HexColor("#00b0f0")))
    table.setStyle(rl["TableStyle"](table_style))
    story.append(table)
    doc.build(story)
    return buffer.getvalue()

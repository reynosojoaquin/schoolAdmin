from collections import defaultdict
from io import BytesIO
from xml.sax.saxutils import escape

from django.db.models import Count, Prefetch
from django.contrib.staticfiles import finders

from .models import Attendance, Enrollment, Grade, Subject, SystemConfiguration


INSTITUTION_NAME = "LICEO CORONEL RAFAEL TOMAS FERNANDEZ DOMINGUEZ"
INSTITUTION_MOTTO = "APRENDAMOS JUNTOS"
COMPETENCY_LABELS = [
    "Comunicativa",
    "Pensamiento logico, creativo y critico",
    "Cientifica y tecnologica / Ambiental y salud",
    "Etica y ciudadana / Desarrollo personal",
]


def _reportlab():
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    return {
        "colors": colors,
        "TA_CENTER": TA_CENTER,
        "landscape": landscape,
        "letter": letter,
        "getSampleStyleSheet": getSampleStyleSheet,
        "ParagraphStyle": ParagraphStyle,
        "inch": inch,
        "Image": Image,
        "KeepTogether": KeepTogether,
        "PageBreak": PageBreak,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
    }


def _school_year_label(school_year):
    if not school_year:
        return ""
    parts = school_year.split("-")
    if len(parts) == 2:
        return f"{parts[0]} - {parts[1][-2:]}"
    return school_year


def _fmt(value):
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}"


def _is_failing_grade(value):
    if value is None:
        return False
    try:
        return float(value) < 70
    except (TypeError, ValueError):
        return False


def _text(value):
    if value is None:
        return ""
    return escape(str(value)).replace("\n", "<br/>")


def _avg(values):
    clean_values = [float(value) for value in values if value is not None]
    if not clean_values:
        return None
    return sum(clean_values) / len(clean_values)


def _subject_grade_matrix(enrollment, section=None):
    section = section or enrollment.section
    subjects = Subject.objects.filter(section=section, include_in_registry_reports=True).order_by("name")
    grades = (
        Grade.objects.filter(enrollment=enrollment, subject__section=section)
        .select_related("subject", "subject_competency", "subject_competency__competency")
        .order_by("subject__name", "subject_competency__competency__description")
    )
    by_subject = defaultdict(list)
    for grade in grades:
        by_subject[grade.subject_id].append(grade)

    rows = []
    for subject in subjects:
        subject_grades = by_subject.get(subject.pk, [])
        period_values = []
        for period_index in range(4):
            period_values.append(_avg([grade.effective_periods[period_index] for grade in subject_grades]))
        final_average = _avg(period_values)
        rows.append(
            {
                "subject": subject,
                "grades": subject_grades,
                "periods": period_values,
                "final": final_average,
                "approved": final_average is not None and final_average >= 70,
            }
        )
    return rows


def _header_elements(rl, section, title, horizontal=False, report_configuration=None, compact=False):
    styles = rl["getSampleStyleSheet"]()
    center = rl["ParagraphStyle"](
        "centered",
        parent=styles["Normal"],
        alignment=rl["TA_CENTER"],
        fontName="Helvetica-Bold",
        fontSize=8 if compact else 10,
        leading=9 if compact else 12,
    )
    title_style = rl["ParagraphStyle"](
        "title",
        parent=center,
        fontSize=11 if compact else (14 if horizontal else 13),
        textColor=rl["colors"].darkgreen,
        leading=12 if compact else 16,
    )
    system_configuration = SystemConfiguration.get_solo()
    institution_name = (
        report_configuration.center_name
        if report_configuration and report_configuration.center_name
        else system_configuration.institution_name or INSTITUTION_NAME
    )
    annual_phrase = (
        report_configuration.annual_phrase
        if report_configuration and report_configuration.annual_phrase
        else INSTITUTION_MOTTO
    )
    heading = [
        rl["Paragraph"](_text(institution_name).upper(), center),
        rl["Paragraph"](f'"{_text(annual_phrase)}"', center),
        rl["Spacer"](1, 3 if compact else 8),
        rl["Paragraph"](title, title_style),
        rl["Paragraph"](f"Ano escolar: {_school_year_label(section.school_year)}", center),
    ]
    def logo_image(logo, fallback_static=None, width=1.1, height=None):
        path = None
        if logo:
            try:
                path = logo.path
            except (AttributeError, NotImplementedError, ValueError):
                path = None
        if not path and fallback_static:
            path = finders.find(fallback_static)
        if not path:
            return ""
        try:
            return rl["Image"](
                path,
                width=width * rl["inch"],
                height=(height or width) * rl["inch"],
                kind="proportional",
            )
        except (OSError, ValueError):
            return ""

    ministry_logo = logo_image(None, "img/logo-minerd.png", width=1.5 if compact else 2.15, height=0.5 if compact else 0.85)
    grade_logo = logo_image(report_configuration.logo if report_configuration else None, width=1.04 if compact else 1.8)
    school_logo = logo_image(system_configuration.logo, "img/logo-centro-default.jpeg", width=1.04 if compact else 1.35)
    ministry_header = rl["Table"]([[ministry_logo]], colWidths=[1.7 * rl["inch"] if compact else 2.3 * rl["inch"]])
    ministry_header.hAlign = "CENTER"
    ministry_header.setStyle(rl["TableStyle"]([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2 if compact else 6)]))
    side_width = (1.35 if compact else 1.9) * rl["inch"]
    center_width = (7.8 if compact else 6.7) * rl["inch"] if horizontal else 4.0 * rl["inch"]
    header = rl["Table"](
        [[grade_logo, heading, school_logo]],
        colWidths=[side_width, center_width, side_width],
    )
    header.hAlign = "CENTER"
    header.setStyle(
        rl["TableStyle"](
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return [ministry_header, header, rl["Spacer"](1, 5 if compact else 14)]


def _attendance_counts(enrollments):
    enrollment_ids = [enrollment.pk for enrollment in enrollments]
    counts = {Attendance.PRESENT: 0, Attendance.ABSENT: 0, Attendance.LATE: 0}
    if not enrollment_ids:
        return counts
    rows = (
        Attendance.objects.filter(enrollment_id__in=enrollment_ids)
        .values("status")
        .annotate(total=Count("id"))
    )
    for row in rows:
        if row["status"] in counts:
            counts[row["status"]] = row["total"]
    return counts


def _attendance_summary(rl, enrollments, title="ASISTENCIA A CLASE", compact=False):
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.shapes import Drawing, String

    counts = _attendance_counts(enrollments)
    labels = ["Presencias", "Ausencias", "Tardanzas"]
    values = [counts[Attendance.PRESENT], counts[Attendance.ABSENT], counts[Attendance.LATE]]
    colors = [rl["colors"].HexColor("#2e7d32"), rl["colors"].HexColor("#c62828"), rl["colors"].HexColor("#f9a825")]

    metric_data = [[title, "Total"], *[[label, value] for label, value in zip(labels, values)]]
    metrics = rl["Table"](metric_data, colWidths=[1.55 * rl["inch"], 0.65 * rl["inch"]])
    metrics.setStyle(
        rl["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.45, rl["colors"].HexColor("#9ca3af")),
                ("BACKGROUND", (0, 0), (-1, 0), rl["colors"].HexColor("#dcead7")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )

    drawing = Drawing(180 if compact else 250, 78 if compact else 125)
    drawing.add(String(90 if compact else 125, 68 if compact else 112, "Distribucion de asistencia", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7 if compact else 8))
    pie = Pie()
    pie.x = 3 if compact else 10
    pie.y = 2 if compact else 8
    pie.width = 62 if compact else 100
    pie.height = 58 if compact else 95
    pie.data = values if sum(values) else [1]
    pie.labels = [f"{label}: {value}" for label, value in zip(labels, values)] if sum(values) else ["Sin registros"]
    pie.slices.strokeWidth = 0.5
    pie.slices.strokeColor = rl["colors"].white
    if sum(values):
        for index, color in enumerate(colors):
            pie.slices[index].fillColor = color
    else:
        pie.slices[0].fillColor = rl["colors"].HexColor("#d1d5db")
    drawing.add(pie)
    return rl["KeepTogether"]([rl["Table"]([[metrics, drawing]], colWidths=[2.25 * rl["inch"], (2.6 if compact else 3.5) * rl["inch"]])])


def _student_line(rl, enrollment, section=None):
    section = section or enrollment.section
    styles = rl["getSampleStyleSheet"]()
    student_style = rl["ParagraphStyle"](
        "student_data",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
    )
    table = rl["Table"](
        [
            [
                rl["Paragraph"](f"Nombre(s) y Apellido(s): {_text(enrollment.student)}", student_style),
                "",
            ],
            [
                rl["Paragraph"](f"Grado: {_text(enrollment.course.name)}", student_style),
                rl["Paragraph"](f"Seccion: {_text(section.name if section else '-')}", student_style),
            ],
        ],
        colWidths=[3.4 * rl["inch"], 3.4 * rl["inch"]],
    )
    table.setStyle(
        rl["TableStyle"](
            [
                ("SPAN", (0, 0), (1, 0)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _periodic_table(rl, enrollment, section=None):
    colors = rl["colors"]
    data = [["ASIGNATURAS", "P1", "P2", "P3", "P4", "PROM."]]
    grade_styles = []
    for row in _subject_grade_matrix(enrollment, section):
        table_row = len(data)
        data.append(
            [
                row["subject"].name,
                *[_fmt(value) for value in row["periods"]],
                _fmt(row["final"]),
            ]
        )
        for column, value in enumerate([*row["periods"], row["final"]], start=1):
            if _is_failing_grade(value):
                grade_styles.extend(
                    [
                        ("TEXTCOLOR", (column, table_row), (column, table_row), colors.HexColor("#c62828")),
                        ("FONTNAME", (column, table_row), (column, table_row), "Helvetica-Bold"),
                    ]
                )
    table = rl["Table"](data, repeatRows=1, colWidths=[3.1 * rl["inch"], 0.55 * rl["inch"], 0.55 * rl["inch"], 0.55 * rl["inch"], 0.55 * rl["inch"], 0.7 * rl["inch"]])
    table.setStyle(
        rl["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#9ac483")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTSIZE", (0, 1), (0, -1), 7),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fb")]),
                *grade_styles,
            ]
        )
    )
    return table


def _signature_block(rl, report_configuration=None):
    def signature_image(file_field):
        if not file_field:
            return ""
        try:
            return rl["Image"](
                file_field.path,
                width=1.5 * rl["inch"],
                height=0.45 * rl["inch"],
                kind="proportional",
            )
        except (AttributeError, NotImplementedError, OSError, ValueError):
            return ""

    teacher_signature = signature_image(report_configuration.teacher_signature if report_configuration else None)
    director_signature = signature_image(report_configuration.director_signature if report_configuration else None)
    data = [
        [teacher_signature, "", director_signature],
        ["____________________________", "", "____________________________"],
        ["Profesor(a) responsable", "", "Director(a)"],
    ]
    table = rl["Table"](data, colWidths=[2.4 * rl["inch"], 1.5 * rl["inch"], 2.4 * rl["inch"]])
    table.setStyle(
        rl["TableStyle"](
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
            ]
        )
    )
    return table


def build_periodic_report_pdf(section, enrollments, report_configuration=None):
    rl = _reportlab()
    buffer = BytesIO()
    doc = rl["SimpleDocTemplate"](
        buffer,
        pagesize=rl["letter"],
        rightMargin=0.35 * rl["inch"],
        leftMargin=0.35 * rl["inch"],
        topMargin=0.35 * rl["inch"],
        bottomMargin=0.35 * rl["inch"],
    )
    story = []
    for index, enrollment in enumerate(enrollments):
        if index:
            story.append(rl["PageBreak"]())
        story.extend(_header_elements(rl, section, "BOLETIN DE CALIFICACIONES", report_configuration=report_configuration))
        story.append(_student_line(rl, enrollment, section))
        story.append(rl["Spacer"](1, 10))
        story.append(_periodic_table(rl, enrollment, section))
        story.append(rl["Spacer"](1, 16))
        story.append(_attendance_summary(rl, [enrollment]))
        story.append(rl["Spacer"](1, 28))
        story.append(_signature_block(rl, report_configuration))
    doc.build(story)
    return buffer.getvalue()


def build_rcf_report_pdf(enrollment, section=None, report_configuration=None):
    return build_rcf_reports_pdf([enrollment], section or enrollment.section, report_configuration=report_configuration)


def build_rcf_reports_pdf(enrollments, section, report_configuration=None):
    enrollments = list(enrollments)
    rl = _reportlab()
    colors = rl["colors"]
    buffer = BytesIO()
    doc = rl["SimpleDocTemplate"](
        buffer,
        pagesize=rl["landscape"](rl["letter"]),
        rightMargin=0.25 * rl["inch"],
        leftMargin=0.25 * rl["inch"],
        topMargin=0.25 * rl["inch"],
        bottomMargin=0.25 * rl["inch"],
    )
    story = []
    for enrollment_index, enrollment in enumerate(enrollments):
        if enrollment_index:
            story.append(rl["PageBreak"]())
        story.extend(
            _header_elements(
                rl,
                section,
                "REPORTE DE CALIFICACIONES FINALES (RCF)",
                horizontal=True,
                report_configuration=report_configuration,
                compact=True,
            )
        )
        story.append(_student_line(rl, enrollment, section))
        story.append(rl["Spacer"](1, 3))
        styles = rl["getSampleStyleSheet"]()
        competency_style = rl["ParagraphStyle"](
            "rcf_competency_header",
            parent=styles["Normal"],
            alignment=rl["TA_CENTER"],
            fontName="Helvetica-Bold",
            fontSize=5.2,
            leading=5.8,
        )
        group_header = ["ASIGNATURA"]
        detail_header = [""]
        for label in COMPETENCY_LABELS:
            group_header.extend([rl["Paragraph"](label, competency_style), "", "", "", ""])
            detail_header.extend(["Comp.", "P1", "P2", "P3", "P4"])
        group_header.extend(["RESULTADO", "", ""])
        detail_header.extend(["Final", "A", "R"])
        data = [group_header, detail_header]
        grade_styles = []
        for row in _subject_grade_matrix(enrollment, section):
            table_row = len(data)
            line = [row["subject"].name]
            grades = row["grades"][:4]
            for index in range(4):
                grade = grades[index] if index < len(grades) else None
                label = ""
                if grade and grade.subject_competency:
                    label = grade.subject_competency.competency.description[:18]
                effective_periods = grade.effective_periods if grade else [None, None, None, None]
                line.extend([label, *[_fmt(value) for value in effective_periods]])
                for period_offset, value in enumerate(effective_periods, start=1):
                    if _is_failing_grade(value):
                        column = 1 + index * 5 + period_offset
                        grade_styles.extend(
                            [
                                ("TEXTCOLOR", (column, table_row), (column, table_row), colors.HexColor("#c62828")),
                                ("FONTNAME", (column, table_row), (column, table_row), "Helvetica-Bold"),
                            ]
                        )
            final_value = row["final"]
            approved_mark = "X" if final_value is not None and final_value >= 70 else ""
            failed_mark = "X" if _is_failing_grade(final_value) else ""
            line.extend([_fmt(final_value), approved_mark, failed_mark])
            if _is_failing_grade(final_value):
                grade_styles.extend(
                    [
                        ("TEXTCOLOR", (21, table_row), (21, table_row), colors.HexColor("#c62828")),
                        ("FONTNAME", (21, table_row), (21, table_row), "Helvetica-Bold"),
                    ]
                )
            data.append(line)
        widths = [1.55 * rl["inch"]] + [0.38 * rl["inch"]] * 20 + [0.42 * rl["inch"], 0.28 * rl["inch"], 0.28 * rl["inch"]]
        table = rl["Table"](data, repeatRows=2, colWidths=widths)
        table_style = [
            ("GRID", (0, 0), (-1, -1), 0.45, colors.black),
            ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#d9ecf8")),
            ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 5.1),
            ("FONTSIZE", (0, 2), (0, -1), 6),
            ("SPAN", (0, 0), (0, 1)),
            ("SPAN", (21, 0), (23, 0)),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            *grade_styles,
        ]
        for competency_index in range(4):
            start_column = 1 + competency_index * 5
            table_style.append(("SPAN", (start_column, 0), (start_column + 4, 0)))
        table.setStyle(
            rl["TableStyle"](table_style)
        )
        story.append(table)
        story.append(rl["Spacer"](1, 5))
        story.append(_attendance_summary(rl, [enrollment], compact=True))
        story.append(rl["Spacer"](1, 6))
        story.append(_signature_block(rl, report_configuration))
    doc.build(story)
    return buffer.getvalue()


def build_final_act_pdf(section, report_configuration=None):
    rl = _reportlab()
    colors = rl["colors"]
    buffer = BytesIO()
    doc = rl["SimpleDocTemplate"](
        buffer,
        pagesize=rl["landscape"](rl["letter"]),
        rightMargin=0.22 * rl["inch"],
        leftMargin=0.22 * rl["inch"],
        topMargin=0.2 * rl["inch"],
        bottomMargin=0.2 * rl["inch"],
    )
    story = _header_elements(
        rl,
        section,
        "ACTA FINAL DE CALIFICACIONES",
        horizontal=True,
        report_configuration=report_configuration,
        compact=True,
    )
    styles = rl["getSampleStyleSheet"]()
    subject_header_style = rl["ParagraphStyle"](
        "final_act_subject_header",
        parent=styles["Normal"],
        alignment=rl["TA_CENTER"],
        fontName="Helvetica-Bold",
        fontSize=4.8,
        leading=5.2,
    )
    group_header = ["NO", "APELLIDOS", "NOMBRE(S)"]
    detail_header = ["", "", ""]
    subjects = list(Subject.objects.filter(section=section, include_in_registry_reports=True).order_by("name")[:9])
    for subject in subjects:
        group_header.extend([rl["Paragraph"](subject.name, subject_header_style), "", "", ""])
        detail_header.extend(["Final", "Comp.", "Ext.", "Esp."])
    group_header.extend(["RESULTADO", "", ""])
    detail_header.extend(["Prom.", "A", "R"])
    data = [group_header, detail_header]

    enrollments = (
        Enrollment.objects.filter(section=section, school_year=section.school_year, active=True)
        .select_related("student", "course", "section")
        .prefetch_related(Prefetch("grades", queryset=Grade.objects.select_related("subject", "subject_competency")))
        .order_by("student__last_name", "student__first_name")
    )
    grade_styles = []
    for index, enrollment in enumerate(enrollments, start=1):
        table_row = len(data)
        subject_rows = _subject_grade_matrix(enrollment)
        by_subject = {row["subject"].pk: row for row in subject_rows}
        finals = []
        line = [index, enrollment.student.last_name, enrollment.student.first_name]
        for subject_index, subject in enumerate(subjects):
            final = by_subject.get(subject.pk, {}).get("final")
            finals.append(final)
            line.extend([_fmt(final), "", "", ""])
            if _is_failing_grade(final):
                final_column = 3 + subject_index * 4
                grade_styles.extend(
                    [
                        ("TEXTCOLOR", (final_column, table_row), (final_column, table_row), colors.HexColor("#c62828")),
                        ("FONTNAME", (final_column, table_row), (final_column, table_row), "Helvetica-Bold"),
                    ]
                )
        overall = _avg(finals)
        approved_mark = "X" if overall is not None and overall >= 70 else ""
        failed_mark = "X" if _is_failing_grade(overall) else ""
        line.extend([_fmt(overall), approved_mark, failed_mark])
        if _is_failing_grade(overall):
            overall_column = 3 + len(subjects) * 4
            grade_styles.extend(
                [
                    ("TEXTCOLOR", (overall_column, table_row), (overall_column, table_row), colors.HexColor("#c62828")),
                    ("FONTNAME", (overall_column, table_row), (overall_column, table_row), "Helvetica-Bold"),
                ]
            )
        data.append(line)
    result_columns = 3
    detail_columns = len(subjects) * 4 + result_columns
    detail_width = 8.25 / max(detail_columns, 1)
    widths = [0.25 * rl["inch"], 1.0 * rl["inch"], 1.0 * rl["inch"]] + [detail_width * rl["inch"]] * detail_columns
    table = rl["Table"](data, repeatRows=2, colWidths=widths)
    table_style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0, 0), (-1, 1), colors.white),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 4.8),
        ("FONTSIZE", (1, 2), (2, -1), 5.4),
        ("SPAN", (0, 0), (0, 1)),
        ("SPAN", (1, 0), (1, 1)),
        ("SPAN", (2, 0), (2, 1)),
        ("SPAN", (3 + len(subjects) * 4, 0), (5 + len(subjects) * 4, 0)),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        *grade_styles,
    ]
    for subject_index in range(len(subjects)):
        start_column = 3 + subject_index * 4
        table_style.append(("SPAN", (start_column, 0), (start_column + 3, 0)))
    table.setStyle(
        rl["TableStyle"](table_style)
    )
    story.append(table)
    story.append(rl["Spacer"](1, 5))
    story.append(_attendance_summary(rl, list(enrollments), title="ASISTENCIA DE LA SECCION", compact=True))
    story.append(rl["Spacer"](1, 5))
    story.append(_signature_block(rl, report_configuration))
    doc.build(story)
    return buffer.getvalue()


def build_guidance_case_pdf(guidance_case):
    rl = _reportlab()
    buffer = BytesIO()
    doc = rl["SimpleDocTemplate"](
        buffer,
        pagesize=rl["letter"],
        rightMargin=0.45 * rl["inch"],
        leftMargin=0.45 * rl["inch"],
        topMargin=0.45 * rl["inch"],
        bottomMargin=0.45 * rl["inch"],
    )
    styles = rl["getSampleStyleSheet"]()
    title = rl["ParagraphStyle"](
        "guidance_title",
        parent=styles["Title"],
        alignment=rl["TA_CENTER"],
        fontSize=14,
        leading=18,
        textColor=rl["colors"].darkgreen,
    )
    subtitle = rl["ParagraphStyle"](
        "guidance_subtitle",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=rl["colors"].HexColor("#1f2937"),
        spaceBefore=10,
        spaceAfter=6,
    )
    normal = rl["ParagraphStyle"]("guidance_normal", parent=styles["Normal"], fontSize=8, leading=10)
    small = rl["ParagraphStyle"]("guidance_small", parent=styles["Normal"], fontSize=7, leading=9)

    story = [
        rl["Paragraph"](INSTITUTION_NAME, title),
        rl["Paragraph"](INSTITUTION_SUBTITLE, normal),
        rl["Spacer"](1, 8),
        rl["Paragraph"]("EXPEDIENTE DE ORIENTACION Y PSICOLOGIA", title),
        rl["Paragraph"](f"Caso: {_text(guidance_case.case_number)}", normal),
        rl["Spacer"](1, 12),
    ]

    case_rows = [
        ["Estudiante", _text(guidance_case.student or "Pendiente")],
        ["Grado o seccion", _text(guidance_case.section or "-")],
        ["Tipo", _text(guidance_case.get_case_type_display())],
        ["Prioridad", _text(guidance_case.get_priority_display())],
        ["Estado", _text(guidance_case.get_status_display())],
        ["Fecha de apertura", guidance_case.opened_at.strftime("%d/%m/%Y") if guidance_case.opened_at else "-"],
        ["Fecha de cierre", guidance_case.closed_at.strftime("%d/%m/%Y") if guidance_case.closed_at else "-"],
        ["Reportado por", _text(guidance_case.reported_by or "-")],
        ["Docente que refiere", _text(guidance_case.referred_by_teacher or "-")],
        ["Responsable", _text(guidance_case.assigned_to or "-")],
    ]
    case_table = rl["Table"](
        [[rl["Paragraph"](label, small), rl["Paragraph"](value, small)] for label, value in case_rows],
        colWidths=[1.7 * rl["inch"], 4.9 * rl["inch"]],
    )
    case_table.setStyle(
        rl["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.35, rl["colors"].HexColor("#d1d5db")),
                ("BACKGROUND", (0, 0), (0, -1), rl["colors"].HexColor("#eef2f7")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(case_table)
    story.append(rl["Paragraph"]("Descripcion inicial", subtitle))
    story.append(rl["Paragraph"](_text(guidance_case.summary), normal))
    if guidance_case.initial_actions:
        story.append(rl["Paragraph"]("Acciones iniciales", subtitle))
        story.append(rl["Paragraph"](_text(guidance_case.initial_actions), normal))
    if guidance_case.closing_notes:
        story.append(rl["Paragraph"]("Explicacion de cierre", subtitle))
        story.append(rl["Paragraph"](_text(guidance_case.closing_notes), normal))

    story.append(rl["Paragraph"]("Seguimientos y evidencias", subtitle))
    followups = list(guidance_case.followups.select_related("attended_by").order_by("date", "id"))
    if followups:
        data = [["Fecha", "Tipo", "Atendido por", "Participantes", "Notas", "Proximos pasos", "Evidencia"]]
        for followup in followups:
            data.append(
                [
                    followup.date.strftime("%d/%m/%Y") if followup.date else "-",
                    _text(followup.get_intervention_type_display()),
                    _text(followup.attended_by or "-"),
                    _text(followup.participants or "-"),
                    _text(followup.notes),
                    _text(followup.next_steps or "-"),
                    _text(followup.evidence_file.name if followup.evidence_file else "-"),
                ]
            )
        table = rl["Table"](
            [[rl["Paragraph"](cell, small) for cell in row] for row in data],
            repeatRows=1,
            colWidths=[
                0.55 * rl["inch"],
                0.85 * rl["inch"],
                1.05 * rl["inch"],
                1.0 * rl["inch"],
                1.35 * rl["inch"],
                1.15 * rl["inch"],
                0.95 * rl["inch"],
            ],
        )
        table.setStyle(
            rl["TableStyle"](
                [
                    ("GRID", (0, 0), (-1, -1), 0.35, rl["colors"].HexColor("#d1d5db")),
                    ("BACKGROUND", (0, 0), (-1, 0), rl["colors"].HexColor("#dcead7")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl["colors"].white, rl["colors"].HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(table)
    else:
        story.append(rl["Paragraph"]("Este caso todavia no tiene seguimientos registrados.", normal))

    story.append(rl["Spacer"](1, 34))
    story.append(_signature_block(rl))
    doc.build(story)
    return buffer.getvalue()

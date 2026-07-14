from collections import defaultdict
from io import BytesIO

from django.db.models import Prefetch

from .models import Enrollment, Grade, Subject


INSTITUTION_NAME = "LICEO CORONEL RAFAEL TOMAS FERNANDEZ DOMINGUEZ"
INSTITUTION_SUBTITLE = "EDUCACION CON CONCIENCIA Y SOLIDARIDAD"
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
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    return {
        "colors": colors,
        "TA_CENTER": TA_CENTER,
        "landscape": landscape,
        "letter": letter,
        "getSampleStyleSheet": getSampleStyleSheet,
        "ParagraphStyle": ParagraphStyle,
        "inch": inch,
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


def _avg(values):
    clean_values = [float(value) for value in values if value is not None]
    if not clean_values:
        return None
    return sum(clean_values) / len(clean_values)


def _subject_grade_matrix(enrollment):
    subjects = Subject.objects.filter(section=enrollment.section).order_by("name")
    grades = (
        Grade.objects.filter(enrollment=enrollment, subject__section=enrollment.section)
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
        for period in ("period_1", "period_2", "period_3", "period_4"):
            period_values.append(_avg([getattr(grade, period) for grade in subject_grades]))
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


def _header_elements(rl, section, title, horizontal=False):
    styles = rl["getSampleStyleSheet"]()
    center = rl["ParagraphStyle"](
        "centered",
        parent=styles["Normal"],
        alignment=rl["TA_CENTER"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
    )
    title_style = rl["ParagraphStyle"](
        "title",
        parent=center,
        fontSize=14 if horizontal else 13,
        textColor=rl["colors"].darkgreen,
        leading=16,
    )
    return [
        rl["Paragraph"](INSTITUTION_NAME, center),
        rl["Paragraph"](INSTITUTION_SUBTITLE, center),
        rl["Paragraph"](f'"{INSTITUTION_MOTTO}"', center),
        rl["Spacer"](1, 8),
        rl["Paragraph"](title, title_style),
        rl["Paragraph"](f"Ano escolar: {_school_year_label(section.school_year)}", center),
        rl["Spacer"](1, 14),
    ]


def _student_line(rl, enrollment):
    table = rl["Table"](
        [
            [
                f"Nombre(s) y Apellido(s): {enrollment.student}",
                f"Grado: {enrollment.course.name}",
                f"Seccion: {enrollment.section.name}",
            ]
        ],
        colWidths=[3.8 * rl["inch"], 1.4 * rl["inch"], 1.6 * rl["inch"]],
    )
    table.setStyle(
        rl["TableStyle"](
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _periodic_table(rl, enrollment):
    colors = rl["colors"]
    data = [["ASIGNATURAS", "P1", "P2", "P3", "P4", "PROM."]]
    for row in _subject_grade_matrix(enrollment):
        data.append(
            [
                row["subject"].name,
                *[_fmt(value) for value in row["periods"]],
                _fmt(row["final"]),
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
            ]
        )
    )
    return table


def _signature_block(rl):
    data = [["____________________________", "", "____________________________"], ["Profesor(a) responsable", "", "Director(a)"]]
    table = rl["Table"](data, colWidths=[2.4 * rl["inch"], 1.5 * rl["inch"], 2.4 * rl["inch"]])
    table.setStyle(
        rl["TableStyle"](
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build_periodic_report_pdf(section, enrollments):
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
        story.extend(_header_elements(rl, section, "BOLETIN DE CALIFICACIONES"))
        story.append(_student_line(rl, enrollment))
        story.append(rl["Spacer"](1, 10))
        story.append(_periodic_table(rl, enrollment))
        story.append(rl["Spacer"](1, 70))
        story.append(_signature_block(rl))
    doc.build(story)
    return buffer.getvalue()


def build_rcf_report_pdf(enrollment):
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
    story = _header_elements(rl, enrollment.section, "BOLETIN DE CALIFICACIONES", horizontal=True)
    story.append(_student_line(rl, enrollment))
    story.append(rl["Spacer"](1, 6))
    header = ["ASIGNATURA"]
    for label in COMPETENCY_LABELS:
        header.extend([label, "P1", "P2", "P3", "P4"])
    header.extend(["FINAL", "A", "R"])
    data = [header]
    for row in _subject_grade_matrix(enrollment):
        line = [row["subject"].name]
        grades = row["grades"][:4]
        for index in range(4):
            grade = grades[index] if index < len(grades) else None
            label = ""
            if grade and grade.subject_competency:
                label = grade.subject_competency.competency.description[:18]
            line.extend(
                [
                    label,
                    _fmt(grade.period_1 if grade else None),
                    _fmt(grade.period_2 if grade else None),
                    _fmt(grade.period_3 if grade else None),
                    _fmt(grade.period_4 if grade else None),
                ]
            )
        line.extend([_fmt(row["final"]), "X" if row["approved"] else "", "" if row["approved"] else "X"])
        data.append(line)
    widths = [1.55 * rl["inch"]] + [0.38 * rl["inch"]] * 20 + [0.42 * rl["inch"], 0.28 * rl["inch"], 0.28 * rl["inch"]]
    table = rl["Table"](data, repeatRows=1, colWidths=widths)
    table.setStyle(
        rl["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.45, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9ecf8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 5.3),
                ("FONTSIZE", (0, 1), (0, -1), 6.2),
            ]
        )
    )
    story.append(table)
    story.append(rl["Spacer"](1, 28))
    story.append(_signature_block(rl))
    doc.build(story)
    return buffer.getvalue()


def build_final_act_pdf(section):
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
    story = _header_elements(rl, section, "ACTA FINAL DE CALIFICACIONES", horizontal=True)
    data = [["NO", "APELLIDOS", "NOMBRE(S)"]]
    subjects = list(Subject.objects.filter(section=section).order_by("name")[:9])
    for subject in subjects:
        data[0].extend([subject.name[:14], "Final", "Comp.", "Ext.", "Esp."])
    data[0].extend(["Prom.", "A", "R"])

    enrollments = (
        Enrollment.objects.filter(section=section, active=True)
        .select_related("student", "course", "section")
        .prefetch_related(Prefetch("grades", queryset=Grade.objects.select_related("subject", "subject_competency")))
        .order_by("student__last_name", "student__first_name")
    )
    for index, enrollment in enumerate(enrollments, start=1):
        subject_rows = _subject_grade_matrix(enrollment)
        by_subject = {row["subject"].pk: row for row in subject_rows}
        finals = []
        line = [index, enrollment.student.last_name, enrollment.student.first_name]
        for subject in subjects:
            final = by_subject.get(subject.pk, {}).get("final")
            finals.append(final)
            line.extend([_fmt(final), "", "", ""])
        overall = _avg(finals)
        approved = overall is not None and overall >= 70
        line.extend([_fmt(overall), "X" if approved else "", "" if approved else "X"])
        data.append(line)
    for index in range(len(data), 41):
        data.append([index, "", ""] + [""] * (len(data[0]) - 3))

    widths = [0.28 * rl["inch"], 1.15 * rl["inch"], 1.15 * rl["inch"]] + [0.34 * rl["inch"]] * (len(data[0]) - 6) + [0.36 * rl["inch"], 0.25 * rl["inch"], 0.25 * rl["inch"]]
    table = rl["Table"](data, repeatRows=1, colWidths=widths)
    table.setStyle(
        rl["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 4.8),
                ("FONTSIZE", (1, 1), (2, -1), 5.4),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return buffer.getvalue()

import unicodedata


def student_order_key(student):
    surname = (student.last_name or "").strip().split(" ", 1)[0]

    def normalize(value):
        return "".join(
            char for char in unicodedata.normalize("NFKD", value.casefold())
            if not unicodedata.combining(char)
        )

    return normalize(surname), normalize(student.last_name), normalize(student.first_name), student.pk


def enrollment_order_key(enrollment):
    list_order = enrollment.list_order
    return (
        list_order is None,
        list_order if list_order is not None else 0,
        student_order_key(enrollment.student),
    )

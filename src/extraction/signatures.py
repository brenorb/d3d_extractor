import dspy


class LabResultSignature(dspy.Signature):
    """Extract result information from a lab result document."""

    document_text = dspy.InputField(desc="The full text of a lab result PDF.")
    results: dict[str, str] = dspy.OutputField(
        desc="The results of the lab test. The key is the name of the test and the value is the result. "
        "The result can be something like 'Inferior a 7 nmol/L' or 'Desprezível' or just regular number with units."
    )


class ExamsWithoutResult(dspy.Signature):
    """Check if there is a medical exam without a result."""

    document_text = dspy.InputField(desc="The full text of a checkup document.")
    exams_without_result: list[str | None] = dspy.OutputField(
        desc="The name of the medical test without result."
        "Leave a blank list if all exams have results."
    )


class PageDivider(dspy.Signature):
    """Divide the document into pages."""

    document_text = dspy.InputField(desc="The full text of a checkup document.")
    divider: str = dspy.OutputField(desc="The divider of the pages of the document.")
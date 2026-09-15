from app.schemas.audit import AuditResult, ChangedField, HumanReview
from app.schemas.triage import TriageDecision


class AuditEngineError(ValueError):
    """Raised when a human review is inconsistent with the audit result."""


class AuditEngine:
    def audit(
        self,
        ai_decision: TriageDecision,
        human_review: HumanReview,
    ) -> AuditResult:
        changed_fields: list[ChangedField] = []

        if ai_decision.category != human_review.final_category:
            changed_fields.append(ChangedField.CATEGORY)

        if ai_decision.urgency != human_review.final_urgency:
            changed_fields.append(ChangedField.URGENCY)

        if ai_decision.department != human_review.final_department:
            changed_fields.append(ChangedField.DEPARTMENT)

        has_discrepancy = bool(changed_fields)

        self._validate_impact(
            has_discrepancy=has_discrepancy,
            human_review=human_review,
        )

        return AuditResult(
            has_discrepancy=has_discrepancy,
            changed_fields=changed_fields,
            ai_decision=ai_decision,
            human_review=human_review,
        )

    @staticmethod
    def _validate_impact(
        *,
        has_discrepancy: bool,
        human_review: HumanReview,
    ) -> None:
        impact = human_review.discrepancy_impact

        if has_discrepancy and impact is None:
            raise AuditEngineError(
                "Discrepancy impact is required when the human review "
                "changes the AI decision."
            )

        if not has_discrepancy and impact is not None:
            raise AuditEngineError(
                "Discrepancy impact must be empty when there is no discrepancy."
            )


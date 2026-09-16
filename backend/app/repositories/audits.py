from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditRecord
from app.schemas.audit import AuditResult


class AuditRepository:
    def create(
        self,
        session: Session,
        ai_decision_id: UUID,
        result: AuditResult,
    ) -> AuditRecord:
        review = result.human_review

        record = AuditRecord(
            ai_decision_id=ai_decision_id,
            final_category=review.final_category,
            final_urgency=review.final_urgency.value,
            final_department=review.final_department,
            review_note=review.review_note,
            discrepancy_impact=(
                review.discrepancy_impact.value
                if review.discrepancy_impact is not None
                else None
            ),
            has_discrepancy=result.has_discrepancy,
            changed_fields=[field.value for field in result.changed_fields],
        )
        session.add(record)
        session.flush()

        return record

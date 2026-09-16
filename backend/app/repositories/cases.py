from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import AIDecisionRecord, CaseRecord
from app.schemas.case import CaseCreate
from app.schemas.llm import LLMResult


class CaseRepository:
    def create_with_decision(
        self,
        session: Session,
        case: CaseCreate,
        result: LLMResult,
    ) -> tuple[CaseRecord, AIDecisionRecord]:
        case_record = CaseRecord(
            external_id=case.external_id,
            content=case.content,
            input_type=case.input_type.value,
            domain_profile=case.domain_profile,
        )
        session.add(case_record)
        session.flush()

        decision = result.decision
        metrics = result.metrics

        decision_record = AIDecisionRecord(
            case_id=case_record.id,
            category=decision.category,
            urgency=decision.urgency.value,
            summary=decision.summary,
            department=decision.department,
            justification=decision.justification,
            provider=metrics.provider,
            model=metrics.model,
            input_tokens=metrics.input_tokens,
            output_tokens=metrics.output_tokens,
            latency_ms=metrics.latency_ms,
            estimated_cost=Decimal(str(metrics.estimated_cost)),
        )
        session.add(decision_record)
        session.flush()

        return case_record, decision_record

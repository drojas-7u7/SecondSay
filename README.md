# SecondSay

SecondSay is a continuous AI auditing platform designed to analyze the gap between AI-generated decisions and final human decisions.

The product captures AI decisions, human reviews, model evaluations and operational metrics in order to detect recurring discrepancies, high-impact patterns and opportunities to improve AI-assisted workflows.

## Initial use case

The first domain profile focuses on insurance claims triage.

Insurance is used as the initial demonstration environment, while the core architecture remains domain-independent.

## Core capabilities

- Ingest structured and unstructured cases.
- Normalize text and document-based inputs.
- Record decisions produced by an external corporate AI system.
- Capture final human reviews and overrides.
- Audit discrepancies between AI and human decisions.
- Evaluate independent local and cloud LLMs against the same cases.
- Compare quality, latency, token usage and estimated cost.
- Detect recurring patterns in AI-human disagreement.
- Support configurable domain profiles and prompting strategies.
- Expose functionality through a versioned REST API.
- Provide a professional web dashboard.

## Architecture

SecondSay is organized as a modular monolith with clear boundaries between:

- API
- domain logic
- application services
- LLM providers
- ingestion adapters
- persistence
- analytics
- frontend
- external system simulation

The design aims to make infrastructure components replaceable without coupling the core business logic to a specific LLM provider, database or frontend technology.

## Planned stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Pytest

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts

### AI

- Local LLM through an OpenAI-compatible inference server
- Cloud LLM through a provider adapter
- Strict structured outputs
- Configurable prompt and domain profiles

## Repository structure

- `backend/` — API, domain logic and application services
- `frontend/` — SecondSay web interface
- `external-simulator/` — simulated external business system
- `domain-profiles/` — domain-specific configuration
- `data/` — real, synthetic and demo datasets
- `docs/` — architecture and project documentation
- `scripts/` — utilities and data preparation
- `infra/` — infrastructure configuration

## Status

Project under active development for the AI Engineering bootcamp final project.

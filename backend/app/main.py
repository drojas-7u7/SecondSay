from fastapi import FastAPI

from app.api.cases import router as cases_router

app = FastAPI(
    title="SecondSay API",
    version="0.1.0",
    description=(
        "API para auditoría continua de sistemas de inteligencia artificial "
        "y análisis de discrepancias entre decisiones de IA y revisión humana."
    ),
)

app.include_router(cases_router)


@app.get("/health", tags=["Sistema"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "secondsay-backend",
        "version": "0.1.0",
    }

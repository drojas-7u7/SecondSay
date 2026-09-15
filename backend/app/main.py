from fastapi import FastAPI

app = FastAPI(
    title="SecondSay API",
    version="0.1.0",
    description="API for continuous AI auditing and human override analysis.",
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "secondsay-backend",
        "version": "0.1.0",
    }

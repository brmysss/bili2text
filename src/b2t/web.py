from __future__ import annotations

from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from b2t.models import TranscriptResult
from b2t.pipeline import B2TPipeline


def create_app(pipeline_factory: Callable[[], B2TPipeline]) -> FastAPI:
    templates = Jinja2Templates(directory=str(Path(__file__).with_name("templates")))
    app = FastAPI(title="bili2text")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": None,
                "values": {
                    "source": "",
                    "model": "small",
                    "prompt": "",
                },
            },
        )

    @app.post("/transcribe", response_class=HTMLResponse)
    async def transcribe_from_form(
        request: Request,
        source: str = Form(...),
        model: str = Form("small"),
        prompt: str = Form(""),
    ) -> HTMLResponse:
        try:
            result = pipeline_factory().transcribe(source, prompt=prompt or None)
        except Exception as exc:
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "error": str(exc),
                    "values": {
                        "source": source,
                        "model": model,
                        "prompt": prompt,
                    },
                },
                status_code=400,
            )

        return templates.TemplateResponse(request, "result.html", {"result": result})

    @app.post("/api/transcribe")
    async def transcribe_from_api(
        source: str = Form(...),
        model: str = Form("small"),
        prompt: str = Form(""),
    ) -> JSONResponse:
        result = pipeline_factory().transcribe(source, prompt=prompt or None)
        return JSONResponse(_result_payload(result))

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    return app


def _result_payload(result: TranscriptResult) -> dict[str, str]:
    return {
        "engine": result.engine,
        "model": result.model,
        "text": result.text,
        "transcript_path": str(result.transcript_path),
        "metadata_path": str(result.metadata_path),
        "audio_path": str(result.audio_path),
        "video_path": str(result.video_path) if result.video_path else "",
    }

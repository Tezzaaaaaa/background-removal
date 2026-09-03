"""Cutout HTTP API + ChatGPT MCP app."""
from __future__ import annotations

import io
import os
import secrets
import threading
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import BaseModel
from PIL import Image
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from cutout.pipeline import CutoutPipeline

PORT = int(os.getenv("PORT", "8756"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", f"http://localhost:{PORT}").rstrip("/")
MAX_BYTES = 22 * 1024 * 1024
RESULT_DIR = Path(os.getenv("CUTOUT_RESULT_DIR", "/tmp/cutout-results"))
RESULT_DIR.mkdir(parents=True, exist_ok=True)
_pipeline: CutoutPipeline | None = None
_pipeline_lock = threading.Lock()


def load_pipeline() -> CutoutPipeline:
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                _pipeline = CutoutPipeline()
    return _pipeline


class OpenAIFile(BaseModel):
    download_url: str
    file_id: str
    mime_type: str | None = None
    file_name: str | None = None


mcp = MCPServer(
    name="Cutout",
    version="1.2.0",
    instructions=(
        "Use Cutout when the user asks to remove, cut out, isolate, or make the "
        "background of an image transparent. It returns a transparent PNG. "
        "There is one fixed processing engine; do not ask the user to choose a model."
    ),
)


@mcp.tool(
    name="remove_background",
    description=(
        "Use this when the user wants the background removed from an uploaded image. "
        "Process the supplied image automatically with Cutout and return the resulting "
        "transparent PNG. Do not ask the user to choose a model or processing mode."
    ),
    meta={
        "openai/fileParams": ["file"],
        "openai/toolInvocation/invoking": "Removing background…",
        "openai/toolInvocation/invoked": "Background removed.",
    },
)
async def remove_background(file: OpenAIFile) -> CallToolResult:
    if file.mime_type and file.mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        return CallToolResult(content=[TextContent(type="text", text="Use a JPG, PNG, or WebP image.")], is_error=True)
    if not file.download_url.startswith("https://"):
        return CallToolResult(content=[TextContent(type="text", text="The supplied file reference is not a valid HTTPS download URL.")], is_error=True)

    import httpx
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
            response = await client.get(file.download_url)
            response.raise_for_status()
            data = response.content
    except Exception:
        return CallToolResult(content=[TextContent(type="text", text="Could not retrieve the supplied image.")], is_error=True)

    if len(data) > MAX_BYTES:
        return CallToolResult(content=[TextContent(type="text", text="Image is too large. Maximum size is 22 MB.")], is_error=True)
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception:
        return CallToolResult(content=[TextContent(type="text", text="Invalid image file.")], is_error=True)

    try:
        output = load_pipeline().process(image)
        token = secrets.token_urlsafe(24)
        output_path = RESULT_DIR / f"{token}.png"
        output.save(output_path, format="PNG", optimize=True)
    except Exception:
        return CallToolResult(content=[TextContent(type="text", text="Background removal failed.")], is_error=True)

    download_url = f"{PUBLIC_BASE_URL}/files/{token}.png"
    output_name = f"{Path(file.file_name or 'image').stem}-cutout.png"
    return CallToolResult(
        content=[
            ResourceLink(
                type="resource_link",
                uri=download_url,
                name=output_name,
                title="Cutout PNG",
                description="Transparent PNG with the background removed.",
                mime_type="image/png",
            ),
            TextContent(type="text", text="Background removed successfully. The result is a transparent PNG."),
        ],
        structured_content={
            "download_url": download_url,
            "file_name": output_name,
            "mime_type": "image/png",
        },
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "engine": "cutout", "input_size": 1024, "mcp": True})


@mcp.custom_route("/files/{filename}", methods=["GET"])
async def result_file(request: Request) -> Response:
    filename = request.path_params["filename"]
    if not filename.endswith(".png") or Path(filename).name != filename:
        return JSONResponse({"error": "Not found"}, status_code=404)
    path = RESULT_DIR / filename
    if not path.is_file():
        return JSONResponse({"error": "Not found"}, status_code=404)
    return FileResponse(path, media_type="image/png", filename=filename)


@mcp.custom_route("/remove", methods=["POST"])
async def remove_rest(request: Request) -> Response:
    form = await request.form()
    upload = form.get("file")
    if upload is None or not hasattr(upload, "read"):
        return JSONResponse({"error": "Missing file"}, status_code=400)
    content_type = getattr(upload, "content_type", None)
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        return JSONResponse({"error": "Use a JPG, PNG, or WebP image."}, status_code=415)
    data = await upload.read()
    if len(data) > MAX_BYTES:
        return JSONResponse({"error": "Image is too large. Maximum size is 22 MB."}, status_code=413)
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
        output = load_pipeline().process(image)
        buffer = io.BytesIO()
        output.save(buffer, format="PNG", optimize=True)
        return Response(buffer.getvalue(), media_type="image/png")
    except Exception:
        return JSONResponse({"error": "Background removal failed."}, status_code=500)


app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    host="0.0.0.0",
)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", stateless_http=True, host="0.0.0.0", port=PORT)

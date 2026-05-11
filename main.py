import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="python-skynet-1",
    description="Remote Python code execution API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Candidates are tried in order; first found wins.
PYTHON_BINARIES: dict[str, list[str]] = {
    "1": ["python1", "python2"],  # python1 is rare; fall back to python2
    "2": ["python2"],
    "3": ["python3"],
}


class ExecuteRequest(BaseModel):
    version: str
    code: str


class ExecuteResponse(BaseModel):
    output: str
    has_error: bool


def resolve_binary(version: str) -> tuple[str, str]:
    """
    Return (binary, fallback_note).
    Raises ValueError if the version is unsupported or no binary is found.
    """
    candidates = PYTHON_BINARIES.get(version)
    if candidates is None:
        raise ValueError(
            f"Unsupported version '{version}'. Choose '1', '2', or '3'."
        )

    for binary in candidates:
        try:
            subprocess.run(
                [binary, "--version"],
                capture_output=True,
                timeout=5,
            )
            note = (
                "[Note: python1 not found on this system; using python2 as fallback]\n"
                if version == "1" and binary == "python2"
                else ""
            )
            return binary, note
        except FileNotFoundError:
            continue

    raise ValueError(
        f"No Python binary found for version '{version}'. "
        f"Tried: {', '.join(candidates)}"
    )


@app.post("/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest) -> ExecuteResponse:
    """
    Execute a Python code string in the requested interpreter version.

    - **version**: `"1"`, `"2"`, or `"3"`
    - **code**: valid Python source code as a string
    """
    # Resolve interpreter
    try:
        binary, note = resolve_binary(request.version)
    except ValueError as exc:
        return ExecuteResponse(output=str(exc), has_error=True)

    # Run code
    try:
        result = subprocess.run(
            [binary, "-c", request.code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        parts = [note, result.stdout]
        if result.stderr:
            parts.append(result.stderr)
        output = "".join(parts).strip()
        return ExecuteResponse(output=output, has_error=result.returncode != 0)

    except subprocess.TimeoutExpired:
        return ExecuteResponse(
            output="Error: execution timed out after 10 seconds.",
            has_error=True,
        )
    except Exception as exc:  # noqa: BLE001
        return ExecuteResponse(output=f"Unexpected error: {exc}", has_error=True)

# python-skynet-1

A minimal FastAPI server that executes arbitrary Python code via HTTP — supports Python 1 (fallback to 2), Python 2, and Python 3.

---

## Endpoints

### `POST /execute`

**Request**
```json
{
  "version": "3",
  "code": "print('hello world')"
}
```

| Field     | Type                  | Description                        |
|-----------|-----------------------|------------------------------------|
| `version` | `"1"` \| `"2"` \| `"3"` | Python interpreter version to use |
| `code`    | `string`              | Python source code to execute      |

**Response**
```json
{
  "output": "hello world",
  "has_error": false
}
```

| Field       | Type      | Description                                      |
|-------------|-----------|--------------------------------------------------|
| `output`    | `string`  | Combined stdout + stderr                         |
| `has_error` | `boolean` | `true` if the process exited with a non-zero code |

**Notes**
- Execution is capped at **10 seconds**; the process is killed if exceeded.
- Version `"1"` tries `python1` first; falls back to `python2` and prepends a note to `output`.
- CORS is open to all origins (`*`).
- No authentication.

---

## Running locally

**Prerequisites:** Python 3.10+

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Running with Docker

```bash
# Build and start
docker compose up --build

# Or one-liner without Compose
docker build -t python-skynet-1 .
docker run -p 8000:8000 python-skynet-1
```

---

## Example requests

```bash
# Python 3
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"version": "3", "code": "print(2 ** 10)"}'
# → {"output":"1024","has_error":false}

# Intentional error
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"version": "3", "code": "1/0"}'
# → {"output":"Traceback ...ZeroDivisionError...","has_error":true}

# Timeout
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"version": "3", "code": "import time; time.sleep(99)"}'
# → {"output":"Error: execution timed out after 10 seconds.","has_error":true}
```

---

## Project structure

```
python-skynet-1/
├── main.py            # FastAPI app — the whole server
├── requirements.txt   # fastapi + uvicorn
├── Dockerfile         # Container image (includes python2)
├── docker-compose.yml # One-command startup
├── .gitignore
└── README.md
```

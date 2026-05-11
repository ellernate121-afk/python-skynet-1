FROM python:3.12-slim

# Install python2 and python3 side-by-side (python1 is not available via apt)
RUN apt-get update && apt-get install -y --no-install-recommends \
        python2 \
    && ln -sf /usr/bin/python2 /usr/local/bin/python2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

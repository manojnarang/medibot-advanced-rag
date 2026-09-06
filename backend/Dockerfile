FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
# CPU-only torch: this app never touches a GPU, and the default PyPI wheel pulls in the
# full CUDA toolkit. Installed as its own step, from PyTorch's index exclusively, so it
# never affects where any other package in requirements.txt resolves from.
RUN pip install --no-cache-dir torch==2.14.0+cpu torchvision==0.29.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

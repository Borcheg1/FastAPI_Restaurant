FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# uncomment commands below for run pre-commit hooks
# RUN apt-get update; apt-get install -y git
# RUN git init
# RUN pre-commit install-hooks
# RUN pre-commit run --all-files

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

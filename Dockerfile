FROM python:3.11-slim

WORKDIR /app

COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY support_ticket_env/ ./support_ticket_env/
COPY openenv.yaml ./openenv.yaml

EXPOSE 7860

ENV PORT=7860
ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "support_ticket_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]

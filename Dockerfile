FROM rancher/opni-python-base:3.8

EXPOSE 30003

COPY ./opni-insights-service/app /app

WORKDIR "app"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30003"]

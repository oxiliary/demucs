
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /

EXPOSE 80

COPY . .

RUN pip install -r docker-requirements.txt

ENV LD_LIBRARY_PATH=/usr/local/lib

COPY --from=opencoconut/ffmpeg . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"] 
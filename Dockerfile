FROM python:3.11

WORKDIR /ontime

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]  # Assuming your app's main file is named app.py


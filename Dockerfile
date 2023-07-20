FROM python:alpine3.17
WORKDIR .
COPY restMeals.py .
RUN pip install flask
RUN pip install flask_restful
RUN pip install requests
EXPOSE 8000
CMD ["python3", "restMeals.py"]

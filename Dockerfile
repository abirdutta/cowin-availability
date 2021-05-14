#FROM python:3.8
FROM python:3.8-slim-buster
RUN apt-get -y update
RUN apt-get -y install git
RUN git clone https://github.com/abirdutta/cowin-availability.git /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD streamlit run /opt/app/app.py

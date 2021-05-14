FROM python:3.8
EXPOSE 8501
COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
CMD streamlit run /opt/app/app.py
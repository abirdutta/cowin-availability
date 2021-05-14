FROM python:3.8
EXPOSE 8501
RUN git clone https://github.com/abirdutta/cowin-availability.git /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
CMD streamlit run /opt/app/app.py
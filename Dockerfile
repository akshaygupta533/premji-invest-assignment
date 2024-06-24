#Dockerfile
FROM apache/airflow:2.6.0-python3.9
# Install additional dependencies
USER root
COPY requirements.txt ./requirements.txt
USER airflow
RUN pip3 install --user --upgrade pip
# Set up additional Python dependencies
RUN pip3 install --no-cache-dir --user -r ./requirements.txt
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /temp/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /temp/requirements.txt

#
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader wordnet

# Run app.py when the container launches
CMD ["python", "pipeline.py"]
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /temp/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /temp/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV UVICORN_PORT=80

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./airelay /app/airelay
COPY ./config/logging.yaml /app/default_config
COPY ./config/system_roles.yaml /app/default_config

COPY ./pyproject.toml /app
COPY ./LICENSE /app
COPY ./README.md /app

# Make port 8088 available to the world outside this container
EXPOSE 8088

# Run app when the container launches
CMD ["fastapi", "run", "airelay/airelay.py", "--host=0.0.0.0", "--port=8088"]

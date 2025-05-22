FROM python:3.12.3-slim-bullseye

# Create a non-root user and set ownership of the app directory
RUN useradd --create-home appuser

WORKDIR /home/app/

# Copy only the requirements file first for better caching
COPY requirements.txt .

# Install dependencies first
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the copied files to the non-root user
RUN chown -R appuser:appuser /home/app/

# Switch to the non-root user
USER appuser

WORKDIR /home/app/

CMD [ "streamlit", "run", "app.py" ]

FROM python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y \
    usbutils \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Set the environment variable for Django settings
ENV DJANGO_SETTINGS_MODULE=printer.settings

# Expose port 8000
EXPOSE 8000

# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

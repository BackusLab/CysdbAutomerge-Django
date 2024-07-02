FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Django and other required packages
RUN pip install --upgrade pip
RUN pip install django

# Create and set the working directory
WORKDIR /blog

# Create log directory
RUN mkdir -p /blog/logs && chmod -R 777 /blog/logs

# Copy the Django project files into the image
COPY ./ /blog/

# Install project dependencies
COPY ./requirements.txt /blog/
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


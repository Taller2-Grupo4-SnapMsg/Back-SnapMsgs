# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app (control, service, repository, etc...)
COPY . .

# Expose the port that the FastAPI application will run on
EXPOSE 8000

# This one always should be production data base, since it's the one the "onrender" picks up.
ENV DB_URI="postgresql://cwfvbvxl:jtsNDRjbVqGeBgYcYvxGps3LLlX_t-P5@berry.db.elephantsql.com:5432/cwfvbvxl"

# Command to run the FastAPI application
CMD ["uvicorn", "control.controller:app", "--host", "0.0.0.0", "--port", "8000"]
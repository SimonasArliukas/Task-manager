FROM python:3.13-slim
LABEL maintainer="simonas.arliukas@gmail.com"
LABEL description="Python task manager"
LABEL version="1.0.0"

#Creating a user so it doesn't run as root 
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

#Move into app folder
WORKDIR /app

#Copy requirements.txt
COPY requirements.txt .

#Install the libraries for the script
RUN pip install --no-cache-dir -r requirements.txt

#Copy the task manager
COPY task_manager.py .

RUN mkdir -p /data && chown -R appuser /data

#Writing output 
ENV TASKS_FILE=/data/tasks.json
VOLUME ["/data"]
USER appuser

#Run the script 
ENTRYPOINT ["python", "task_manager.py"]
CMD ["--help"]
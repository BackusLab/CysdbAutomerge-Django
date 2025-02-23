# Cysdb Automerge

CysDB AutoMerge is a Django-based web application that allows users to upload CSV files, which will then be processed and stored in the database accordingly.

## Prerequisites

1. Download Docker
2. Set up Environment Variables:
   Create a `.env` file with the following content:

   ```
   SECRET_KEY='django-insecure-q7xr(=os*&ion)%%_6g8uj6g82v@l5(p6^42tcg)1_4c&l))9t'
   DEBUG=True
   ALLOWED_HOSTS=['127.0.0.1', '0.0.0.0']
   ```

3. Build and Run Docker Containers:

```
docker-compose up --build
```

3. Open web browser and go to http://localhost:8000 to access the application.

## DB Diagram

![CysDB-Automerge-Diagram](./assets/db-diagram.png?)

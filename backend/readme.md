To ensure connection to the mySQL server:
1. set up a .env file with the following variables:
DB_USER (your mySQL username)
DB_PASSWORD (your mySQL password)
DB_HOST (your host location, generally localhost)
DB_DATABASE (the database's name)

How to run the backend's FastAPI
1. change directory to "backend"
2. execute "uvicorn main:app --reload"
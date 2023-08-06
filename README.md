# FastAPI Restaurant
![Static Badge](https://img.shields.io/badge/Language-Python_3.11-blue)
![Static Badge](https://img.shields.io/badge/Framework-FastAPI-red)
![Static Badge](https://img.shields.io/badge/SQL_Database-PostgreSQL-ygreen)
![Static Badge](https://img.shields.io/badge/ORM-SQLAlchemy-orange)
![Static Badge](https://img.shields.io/badge/NoSQL_Database-Redis-green)

### An application that allows you to perform CRUD operations for a chain of menus, submenus and dishes.

# Guide for installing and launching the application
## 1. Option for local database


### **1.1 Launch the application**

1. Open a terminal and enter the command
`git clone https://github.com/Borcheg1/FastAPI_Restaurant.git`

2. Change to the project's working directory:
`cd FastAPI_Restaurant`

3. Create a virtual environment:
`py -m venv env` or `python -m venv env`

4. Activate the virtual environment:

    Linux/macOS: `source env/bin/activate`

    Windows: `env\Scripts\activate`

5. Install required libraries:
`pip install -r requirements.txt`

6. Install pre-commit hooks:
`pre-commit install`

7. Rename the `env_example` file to `.env` in the root folder of the project and change the
variables for your database. Including set `DB_HOST=localhost` and `REDIS_HOST=localhost`

8. If you want to manually run all pre-commit hooks on a repository, run `pre-commit run --all-files`

9. Run the application with the command:
`uvicorn src.main:app`

10. Open a browser and go to `localhost:8000/docs#/`

### **1.2 Run tests**

1. Follow steps 1-5 from section [1.1 Launch the application](#11-launch-the-application)

2. Rename the `env_example` file to `.env` in the root folder of the project and change the
variables for your database. Including set `TEST_DB_HOST=localhost` and `REDIS_HOST=localhost`

3. Run the tests with the command:
`pytest`

### **1.3 Terminate the application**

1. Stop the application with a keyboard shortcut `Ctrl+C`


## 2. Option for docker

### **2.1 Launch the application**

1. Open a terminal and enter the command
`git clone https://github.com/Borcheg1/FastAPI_Restaurant.git`

2. Change to the project's working directory:
`cd FastAPI_Restaurant`

3. Rename the `env_example` file to `.env` in the root folder of the project

4. If you want to run all pre-commit hooks when container is building, then uncommenting commands in `Dockerfile`

5. Enter the command `docker-compose up --build` and wait for the containers to build

6. Open a browser and go to `localhost:8000/docs#/`

### **2.2 Terminate the application**

1. Stop the containers with a keyboard shortcut `Ctrl+C`

2. Remove containers and volumes:
`docker-compose down --volumes`

### **2.3 Run tests**

1. Follow steps 1-3 from section [2.1 Launch the application](#21-launch-the-application)

2. Enter the command `docker-compose --file docker-compose-test.yml up --build`
and wait for the containers to be built and the application to be tested

### **2.4 Terminate the tests**

1. Stop the containers with a keyboard shortcut `Ctrl+C`

2. Remove containers and volumes:
`docker-compose --file docker-compose-test.yml down --volumes`<br><br><br>

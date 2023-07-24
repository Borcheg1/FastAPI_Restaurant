# FastAPI Restaurant
![Static Badge](https://img.shields.io/badge/Python-3.11-blue)
![Static Badge](https://img.shields.io/badge/FastAPI-red)
![Static Badge](https://img.shields.io/badge/Database-PostgreSQL-ygreen)
![Static Badge](https://img.shields.io/badge/ORM-SQLAlchemy-orange)

### An application that allows you to perform CRUD operations for a chain of menus, submenus and dishes.

## Guide for installing and launching the application

1. Open a terminal and enter the command
`git clone https://github.com/Borcheg1/FastAPI_Restaurant.git`

2. Change to the project's working directory:
`cd FastAPI_Restaurant`

3. Create a virtual environment:
`py -m venv env` or `python -m venv env`

4. Activate the virtual environment:

    Linux/macOS: `source env/bin/activate`
   
    Windows: `env\Scripts\activate`

6. Install required libraries:
`pip install -r requirements.txt`

7. Rename the `env_example` file to `.env` in the root folder of the project and change the variables for your database.

8. Run the application `uvicorn src.main:app`

9. Open a browser and go to `localhost:8000/docs#/`

**Are you ready for the tests!**

### Thank you for using my app, you are amazing!

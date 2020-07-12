# Full Stack API Final Project

## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a  webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out. 

The application:

1) Displays questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer. 
2) Deletes questions.
3) Adds questions and require that they include question and answer text.
4) Searches for questions based on a text query string.
5) Plays the quiz game, randomizing either all questions or within a specific category.   

## About the Stack

|  database  | backend | frontend |
|:----------:|:-------:|:--------:|
| [PostgreSQL](https://bit.ly/3emfbO2) | [Flask](https://bit.ly/3iNJuAV) | [React.js](https://reactjs.org/) |

- Object Relational Mapping (ORM)
    - [SQLAlchemy](https://www.sqlalchemy.org/)
    - [Alembic](https://alembic.sqlalchemy.org/en/latest/front.html#project-homepage)

### Backend

The `./backend` directory contains a completed Flask and SQLAlchemy server.  
To start it, go to the `./backend` directory and run:
```bash
export FLASK_APP=flaskr.__init__.py
export FLASK_ENV=development
flask run
```

If you're on Windows, go to the `./backend` directory and run:
```batch
SET FLASK_APP="flaskr.__init__.py"
SET FLASK_ENV="development"
py -m flask run
```

[View the README.md within ./backend for more details.](./backend/README.md)

### Frontend

The `./frontend` directory contains a complete React frontend to consume the data from the Flask server.
I edited a few pieces of the frontend using [react-bootstrap](https://www.npmjs.com/package/react-bootstrap).

- Windows: [start.bat](./frontend/start.bat)  
- Linux | macOS: [start.sh](./frontend/start.sh) 

[View the README.md within ./frontend for more details.](./frontend/README.md)

### Postman API Docs

[View the docs for the API here](https://documenter.getpostman.com/view/8697082/SzzkbGb4?version=latest)

## Submission Criteria

### Code Quality & Documentation
- [x] Write Clear, concise and well-documented code
- [x] Write an informative README.md
- [x] Leverage Environment Controls

### Handling HTTP Requests
- [x] Follow RESTful principles
- [x] Utilize multiple HTTP request methods
- [x] Handle common errors

### API Testing & Documentation
- [x] Use unittest to test flask application for expected behavior
- [x] Demonstrate validity of API responses

### Bonus
- [x] Add capability to create new categories.

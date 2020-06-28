import os
import unittest
import json
import base64
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_user = "jayw6"
        self.database_pass = base64.b64decode('anVzdDRtZQ=='.encode('ascii')).decode('ascii')
        self.database_URLPort = 'localhost:5432'
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}"\
            .format(self.database_user, self.database_pass, self.database_URLPort, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            pass
        pass
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each successful operation and for expected errors.
    """
    # region Question Tests
    def test_create_question(self):
        new_question = {
            'question': 'Is this a test?',
            'answer': 'Yes',
            'category': 1,
            'difficulty': 5
        }
        res = self.client().post('/questions/', json=new_question)

        self.assertEqual(res.status_code, 200)
        pass

    def test_get_questions(self):
        res = self.client().get('/questions/')
        data = json.loads(res.data)

        print("test_get_questions: " + json.dumps(data))

        self.assertIsNotNone(data, "Data received was None!")
        self.assertEqual(res.status_code, 200)
        pass

    def test_delete_question(self):
        res = self.client().delete('/questions/0/')

        self.assertEqual(res.status_code, 200)
        pass

    def test_search_questions(self):
        res = self.client().get('/questions/search/', json={'searchTerm': 'What'})

        self.assertEquals(res.status_code, 200)
        pass
    # endregion

    # region Category Tests
    def test_CategoryCreate(self):
        pass

    def test_CategoryRead(self):
        res = self.client().get('/categories/')

        self.assertEqual(res.status_code, 200)
        pass

    def test_CategoryUpdate(self):
        pass

    def test_CategoryDelete(self):
        pass
    # endregion

    def test_QuizPlay(self):
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

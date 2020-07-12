import datetime
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
        self.database_pass = base64.b64decode('cm9vdHNxbA=='.encode('ascii')).decode('ascii')
        self.database_URLPort = 'localhost:5432'
        self.database_name = "trivia_test"
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
            'question': 'What is this, a test?',
            'answer': 'test',
            'category': 1,
            'difficulty': 5
        }
        questions_before_push = self.client().get('/questions/').json["questions"]
        print("q_before:\n " + json.dumps(questions_before_push, indent=2))

        res = self.client().post('/questions/', json=new_question)
        new_question['category'] = str(new_question['category'])
        if questions_before_push is None or len(questions_before_push) == 0:
            new_question['id'] = 1
        else:
            new_question['id'] = questions_before_push[-1]['id'] + 1
        questions_before_push.append(new_question)

        questions_after_push = self.client().get('/questions/').json["questions"]
        print("q_after:\n " + json.dumps(questions_after_push, indent=2))

        self.assertEqual(res.status_code, 200)
        self.assertListEqual(questions_before_push, questions_after_push)
        pass

    def test_get_questions(self):
        res = self.client().get('/questions/')
        data = json.loads(res.data)

        print("test_get_questions: " + json.dumps(data))

        self.assertIsNotNone(data, "Data received was None!")
        self.assertEqual(res.status_code, 200)
        pass

    def test_delete_question(self):
        question = (Question.query.filter_by(answer="test").first())
        if not bool(question):
            self.assertTrue(True)
            print("No test question(s) to delete")
        else:
            print("delete question when answer is just yes: " + str(question.id))
            res = self.client().delete('/questions/' + str(question.id) + '/')

            self.assertEqual(res.status_code, 200)
        pass

    def test_search_questions(self):
        res = self.client().post('/questions/search/', json={"searchTerm": "What"})

        data = res.json
        print("===== Data Returned =====\n" + json.dumps(data, indent=2))
        print("=====   End Data   =====\n")

        for token in data["questions"]:
            self.assertTrue('what' in str(token).lower(), "The token didn't have 'what': "+str(token).lower())

        self.assertEqual(res.status_code, 200)
        pass
    # endregion

    # region Category Tests
    def test_create_category(self):
        res = self.client().post('/categories/', json={"category": "TEST_PLACEHOLDER"+str(datetime.datetime.now())})

        self.assertEqual(res.status_code, 200)
        pass

    def test_read_category(self):
        res = self.client().get('/categories/')

        print("===== Categories =====\n" + json.dumps(res.json, indent=2))
        print("===== End Data =====")

        self.assertEqual(res.status_code, 200)
        pass
    # endregion

    def test_play_quiz(self):
        initial_json = {
            "previous_questions": [],
            "quiz_category": {
                "id": 1,
                "type": "Science"
            }
        }
        res = self.client().post('/quizzes/', json=initial_json)
        data = res.json

        while data is not None and data["question"] is not None:
            self.assertIsNotNone(data["question"]["question"], "Question data has no question")
            self.assertIsNotNone(data["question"]["answer"], "Question data has no answer")
            loop_json = initial_json["previous_questions"].append(str(data["question"]["id"]))
            res = self.client().post('/quizzes/', json=loop_json)
            data = res.json

        self.assertEqual(res.status_code, 200)
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

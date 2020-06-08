import logging
import os
import sys
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logging.getLogger('flask_cors').level = logging.DEBUG

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories/', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formated_categories = [category.format() for category in categories]

        return jsonify({
            'categories': formated_categories
        })

    @app.route('/categories/<int:category>/questions/', methods=['GET'])
    def get_questions_in(category):
        """
        Create an endpoint to handle GET requests
        for questions filtered by any available category.
        :param category: path parameter converted into an int
        :return: JSON with a list of questions, int count of all questions, and current category id
        """
        start, end, page = get_questions_limit(request)
        questions = Question.query.filter_by(category=category).order_by('id').all()
        formatted_questions = [question.format() for question in questions]
        curr_cat = Category.query.get(category)
        return jsonify({
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'current_category': curr_cat.format()
        })

    @app.route('/questions/', methods=['GET'])
    def get_questions():
        """
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.

        :return: JSON with the first 10 questions, number of total questions, and a list of all categories
        """

        '''
        TEST: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions. 
        '''

        start, end, page = get_questions_limit(request)
        questions = Question.query.all()
        categories = Category.query.order_by('id').all()
        formatted_questions = [question.format() for question in questions]
        all_categories = [category.format() for category in categories]
        result = jsonify({
            'questions': formatted_questions[start:end],
            'totalQuestions': len(formatted_questions),
            'categories': all_categories,
            'page': page,
            'currentCategory': all_categories[0]
        })

        print(result)
        return result

    @app.route('/questions/<int:question_id>/', methods=['DELETE'])
    def delete_question(question_id):
        """
        Create an endpoint to DELETE question using a question ID.

        :return:
        """
        '''
        TEST: When you click the trash icon next to a question, the question will be removed.
        This removal will persist in the database and when you refresh the page. 
        '''
        success = True
        try:
            q = Question.query.get(question_id)
            db.session.delete(q)
            db.session.commit()
        except:
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        return jsonify({
            success
        })

    @app.route('/questions/', methods=['POST'])
    def create_question():
        """
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.

        :return: boolean success
        """
        '''
        TEST: When you submit a question on the "Add" tab, 
        the form will clear and the question will appear at the end of the last page
        of the questions list in the "List" tab.  
        '''
        error = False

        try:
            new_question = Question(
                request.get_json()['question'],
                request.get_json()['answer'],
                request.get_json()['category'],
                request.get_json()['difficulty']
            )
            db.session.add(new_question)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            abort(400)
        else:
            return jsonify({
                'success': True
            })

    @app.route('/questions/search/', methods=['POST'])
    def search_questions():
        """
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.

        :return:
        """
        '''
        TEST: Search by any phrase. The questions list will update to include 
        only question that include that string within their question. 
        Try using the word "title" to start. 
        '''
        start, end, page = get_questions_limit(request)
        search_term = request.get_json()['searchTerm']
        sql_search_term = '%{}%'.format(search_term)
        filtered_questions = Question.query.filter(Question.question.like(sql_search_term)).all()

        formatted_questions = [question.format() for question in filtered_questions]

        return jsonify({
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions)
        })

    @app.route('/quizzes/', methods=['POST'])
    def get_quizzes():
        """
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random question within the given category,
        if provided, and that is not one of the previous questions.

        :return:
        """
        '''
        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and be shown whether they were correct or not. 
        '''
        prev_question_ids = request.get_json()['previous_questions']
        curr_category = request.get_json()['quiz_category']
        cat_id = curr_category['id']

        print("Current Category ID: "+str(cat_id))

        curr_category_questions = \
            (Question.query.filter_by(category=int(cat_id)).order_by('id').all(),
             Question.query.order_by('id').all())[cat_id == 0]

        if len(prev_question_ids) == len(curr_category_questions) or len(curr_category_questions) == 0:
            return jsonify({
                'question': None
            })

        rand_index = random.randint(0, len(curr_category_questions)-1)
        # print("\nGot " + str(rand_index) + " from range [0, " + str(len(curr_category_questions)-1) + ']\n')
        next_question = curr_category_questions[rand_index]
        # print(next_question)

        if len(prev_question_ids) != 0:
            while next_question.id in prev_question_ids:
                rand_index = random.randint(0, len(curr_category_questions)-1)
                next_question = curr_category_questions[rand_index]

        next_question = next_question.format()

        return jsonify({
          'question': next_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    return app


# Utilities
# ====================================


def get_questions_limit(passed_request):
    """
    Get the start and end indices of this request
    """
    page = passed_request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return start, end, page

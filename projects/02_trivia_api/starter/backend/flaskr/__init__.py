import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.elements import True_
from sqlalchemy.sql.expression import func

from sqlalchemy.sql.expression import all_, false

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def categories_to_dict(categories):
    cdict = {}
    for cat in categories:
        cdict[cat.id] = cat.type
    return cdict


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        questions = Question.query \
                            .paginate(page=page, per_page=QUESTIONS_PER_PAGE)
        # returns a Paginate object

        current_questions = [q.format() for q in questions.items]
        # print(current_questions)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.all()
        categories_dict = categories_to_dict(categories)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": questions.total,
            "categories": categories_dict,
            # "current_category": None
        })

    @app.route('/categories/<cat_id>/questions', methods=['GET'])
    def get_questions_with_given_category(cat_id):
        cat = Category.query.filter(Category.id == cat_id).one_or_none()
        if cat is None:
            # print("no category exists with id", cat_id)
            abort(404)

        page = request.args.get('page', 1, type=int)
        questions = Question.query \
                            .filter(Question.category == cat_id) \
                            .paginate(page=page, per_page=QUESTIONS_PER_PAGE)
        #  returns a Paginate objects

        current_questions = [q.format() for q in questions.items]

        if len(current_questions) == 0:
            # print("no questions with category ", cat_id)
            abort(404)

        try:
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": questions.total,
                "current_category": cat.type
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/questions', methods=['POST'])
    def search_questions():
        page = request.args.get('page', 1, type=int)
        body = request.get_json()
        term = body.get("searchTerm", None)
        try:
            if term:
                questions = Question.query \
                            .filter(Question.question
                                            .ilike('%{}%'.format(term))) \
                            .order_by(Question.id) \
                            .paginate(page=page, per_page=QUESTIONS_PER_PAGE)
                #  returns a Paginate objects

                current_questions = [q.format() for q in questions.items]
                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    #  it sends [] if there are no results
                    "total_questions": questions.total,
                    # "current_category": None
                })

            else:
                data = request.get_json()

                question = Question(data["question"],
                                    data["answer"],
                                    data["category"],
                                    data["difficulty"])
                question.insert()

                return jsonify({
                    "success": True
                })

        except Exception as e:
            print(e)
            abort(422)

    @app.route('/questions/<q_id>', methods=['DELETE'])
    def delete_question(q_id):
        question = Question.query.get(q_id)
        # print('deleting question with id ', q_id)
        if question is None:
            abort(404)
        question.delete()

        try:
            return jsonify({
                "success": True
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/categories', methods=["GET"])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            categories_dict = categories_to_dict(categories)

            return jsonify({
                "success": True,
                "categories": categories_dict
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        try:
            body = request.get_json()

            category = body["quiz_category"]["id"]
            previous_questions = body["previous_questions"]  # IDs in an array
            all_questions = []

            if category == 0:
                # print('categories: all')
                all_questions = Question.query \
                                                .order_by(func.random()) \
                                                .all()

            else:
                # print('category: ', category)
                all_questions = Question.query \
                                .filter(Question.category == category) \
                                .order_by(func.random()) \
                                .all()
            total = len(all_questions)
            if total == len(previous_questions):
                return jsonify({  # end of questions
                    "success": True,
                    "question": None
                })

            i = 0
            found = False
            while not found and i < total:
                question = all_questions[i]
                if question.id in previous_questions:
                    i = i + 1
                else:
                    found = True
                    return jsonify({
                        "success": True,
                        "question": all_questions[i].format(),
                    })

        except Exception as e:
            print(e)
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        # print('error: bad request')
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        # print('error: not found')
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        # print('error: unprocessable')
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app

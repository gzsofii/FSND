import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.elements import True_
from  sqlalchemy.sql.expression import func

from sqlalchemy.sql.expression import all_, false

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE;
  end = start + QUESTIONS_PER_PAGE
  questions = questions[start:end]
  qs = [q.format() for q in questions]
  return qs

def categories_to_dict(categories):
  cdict = {}
  for cat in categories:
    cdict[cat.id] = cat.type
  return cdict

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
 
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  CORS(app)
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/questions', methods=['GET'])
  def get_questions():
    #page = request.args.get('page', 1, type=int)
    all_questions = Question.query.order_by(Question.id).all()
    total = len(all_questions)
    current_questions = paginate_questions(request, all_questions)
    
    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.all()
    categories_dict = categories_to_dict(categories)

    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": total,
      "categories": categories_dict,
      "current_category": None
    })

  @app.route('/categories/<cat_id>/questions', methods=['GET'])
  def get_questions_with_given_category(cat_id):
    try:
      cat = Category.query.filter(Category.id == cat_id).one_or_none()
      print(cat)
      if cat is None:
        print("no category exists with id", cat_id)
        abort(404)

      questions = Question.query \
                  .filter(Question.category==cat_id) \
                  .order_by(Question.id) \
                  .all()
      total = len(questions)
      current_questions = paginate_questions(request, questions)

      if len(current_questions) == 0:
        print("no questions with category ", cat_id)
        abort(404)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": total,
        "current_category": cat.type
      })
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def search_questions():
    body = request.get_json()
    term = body.get("searchTerm", None)
    
    try:
      if term:
        print(term)

        questions = Question.query \
                      .filter(Question.question.ilike('%{}%'.format(term))) \
                      .order_by(Question.id) \
                      .all()
        total = len(questions)
        current_questions = paginate_questions(request, questions)

        return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": total,
          "current_category": None
        })

      else:
        data = request.get_json()
        
        question = Question(data["question"], data["answer"], data["category"], data["difficulty"])
        question.insert()

        return jsonify({
          "success": True
        })

    except:
      abort(422) 

  @app.route('/questions/<q_id>', methods=['DELETE'])
  def delete_question(q_id):
    try:
      question = Question.query.get(q_id)
      print('deleting question with id ', q_id)
      if question is None:
        abort(404)
      question.delete()

      return jsonify({
        "success": True
      })
    except:
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
    except:
      abort(422)

    '''@TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()

    category = body["quiz_category"]["id"]
    previous_questions = body["previous_questions"] # IDs in an array

    all_questions = Question.query \
                  .filter(Question.category==category) \
                  .order_by(func.random()) \
                  .all()
    total = len(all_questions)

    if total == len(previous_questions):
      return jsonify({ # end of questions
        "success": True,
        "question": None
      })

    i = 0
    found = False
    while not found and i < total:
      question = all_questions[i]
      print(question.id)
      if question.id in previous_questions:
        i = i + 1
      else:
        found = True
        return jsonify({
          "success": True,
          "question": all_questions[i].format(),
        })
    
  @app.errorhandler(400)
  def bad_request(error):
    print('error: bad request')
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    print('error: not found')
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    print('error: unprocessable')
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
    }), 422

  '''
      @TODO: Create an endpoint to handle GET requests  for all available categories.

      @TODO: 
      Create an endpoint to handle GET requests for questions, 
      including pagination (every 10 questions). 
      This endpoint should return a list of questions, 
      number of total questions, current category, categories. 

      TEST: At this point, when you start the application
      you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions. 
      
      @TODO: 
      Create an endpoint to DELETE question using a question ID. 

      TEST: When you click the trash icon next to a question, the question will be removed.
      This removal will persist in the database and when you refresh the page. 
  
      @TODO: 
      Create an endpoint to POST a new question, 
      which will require the question and answer text, 
      category, and difficulty score.

      TEST: When you submit a question on the "Add" tab, 
      the form will clear and the question will appear at the end of the last page
      of the questions list in the "List" tab.  

      @TODO: 
      Create a POST endpoint to get questions based on a search term. 
      It should return any questions for whom the search term 
      is a substring of the question. 

      TEST: Search by any phrase. The questions list will update to include 
      only question that include that string within their question. 
      Try using the word "title" to start. 
 
      @TODO: 
      Create a GET endpoint to get questions based on category. 

      TEST: In the "List" tab / main screen, clicking on one of the 
      categories in the left column will cause only questions of that 
      category to be shown. 
    
      @TODO: 
      Create error handlers for all expected errors 
      including 404 and 422. 
  '''
  
  return app

        
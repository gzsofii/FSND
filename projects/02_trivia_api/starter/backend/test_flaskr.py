import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')  
DB_USER = os.getenv('DB_USER', 'postgres')  
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')  
DB_NAME = os.getenv('DB_NAME', 'trivia_test') 
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        setup_db(self.app, DB_PATH)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

            self.db.drop_all()
            self.db.create_all()
    
    def tearDown(self):
        pass
        

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]),True)
        self.assertTrue(len(data["categories"]), True)


    def test_get_questions_invalid_page(self):
        res = self.client().get('/questions?page=200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions_by_category(self):
        cat_id = 1
        cat_name = "Science"
        res = self.client().get('/categories/' + str(cat_id) + '/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]),True)
        self.assertEqual(data["current_category"], cat_name)

    def test_get_questions_invalid_category(self):
        cat_id = 10
        res = self.client().get('/categories/' + str(cat_id) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    

    def test_search_question_with_result(self):
        term = "what"
        res = self.client().post('/questions', json={'searchTerm': term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_search_question_without_result(self):
        term = "dgdfhtzjnhgn"
        res = self.client().post('/questions', json={'searchTerm': term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_add_new_question(self):
        new_question = {
            "question": "What is the result of 4+6?",
            "answer": "10",
            "category": "1",
            "difficulty": "1"
        }
        res_old_questions = self.client().get('/questions')
        old_length = json.loads(res_old_questions.data)["total_questions"]
       
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        
        res_new_questions = self.client().get('/questions')
        new_length = json.loads(res_new_questions.data)["total_questions"]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(old_length+1, new_length) 

    def test_add_new_question_invalid(self):
        new_question = {
            "question": "What is the result of 3^2?",
            "answer": "9",
            "category": "62", #invalid category
            "difficulty": "2"
        }
        res_old_questions = self.client().get('/questions')
        old_length = json.loads(res_old_questions.data)["total_questions"]
       
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        
        res_new_questions = self.client().get('/questions')
        new_length = json.loads(res_new_questions.data)["total_questions"]

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(old_length, new_length) # number of questions didn't change

    def test_delete_question(self):
        q_id = 2

        res_old_questions = self.client().get('/questions')
        old_length = json.loads(res_old_questions.data)["total_questions"]

        res = self.client().delete('/questions/' + str(q_id))
        data = json.loads(res.data)

        res_new_questions = self.client().get('/questions')
        new_length = json.loads(res_new_questions.data)["total_questions"]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(new_length+1, old_length)
    

    def test_delete_question_fail(self):
        q_id = 20121

        res_old_questions = self.client().get('/questions')
        old_length = json.loads(res_old_questions.data)["total_questions"]

        res = self.client().delete('/questions/' + str(q_id))
        data = json.loads(res.data)

        res_new_questions = self.client().get('/questions')
        new_length = json.loads(res_new_questions.data)["total_questions"]

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(new_length, old_length) # number of questions didn't change

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(type(data["categories"]) is dict)

    def test_get_next_question(self):

        res = self.client().post( \
                        '/quizzes', \
                        json={"quiz_category": {\
                                    "type": "History", \
                                    "id": "4"}, \
                              "previous_questions": [] \
                             })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_get_next_question_over(self):
        res = self.client().post( \
                        '/quizzes', \
                        json={"quiz_category": {\
                                    "type": "History", \
                                    "id": "4"}, \
                              "previous_questions": [5,9,12,23] \
                             })
        #print('itt: ', res.data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertFalse(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
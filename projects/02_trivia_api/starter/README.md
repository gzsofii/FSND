# Documentation
Trivia - a web application to play quizzes.
A project within the Udacity Fullstack Developer Course.
## How to start server
### Installation
Required:
- Python 3.7
- pip 

Install dependencies: 
`pip install -r requirements.txt`

### Run server
`flask run`

## API
### Getting started
Base url: `http://127.0.0.1:5000/`. The app currently can be run only locally. 

### Endpoints
#### GET /questions
- Returns max. 10 questions according to pagination. The page number can be set as a request argument, default is 1.
- Response includes a dict of all categories, an array of the questions from the given page and the number of total questions.
- Sample request: `curl http://127.0.0.1:5000/questions?page=2`
- Sample response:
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
   
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }
  ], 
  "success": true, 
  "total_questions": 20
}
```
#### GET /categories/{cat_id}/questions
- Returns questions belonging to the given category with pagination.
- Sample request: `curl http://127.0.0.1:5000/categories/2/questions`
- Sample response:
```
{
  "current_category": "Art", 
  "questions": [
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```

#### POST /questions
1. Search question
- The search term has to be given in a json object with key `searchTerm`
- Sample request: `curl -X POST http://127.0.0.1:5000/questions -H 'Content-Type: application/json' -d '{"searchTerm": "tom"}'`
- Sample response:
```
{
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  ], 
  "success": true, 
  "total_questions": 1
}
```
2. Add new question
- The details of the new question (question, answer, category, difficulty) have to be given in a json object with the mentioned keys
- Sample request: `curl -X POST http://127.0.0.1:5000/questions -H 'Content-Type: application/json' -d '{"question": "What is the smallest odd number?", "answer": "1", "category": "1", "difficulty": "1"}'`
- Sample response: 
```
{
  "success": true
}
```

#### DELETE /questions/{id}
- Deletes question with given id from the database
- Sample request: `curl -X DELETE http://127.0.0.1:5000/questions/5`
- Sample response:
```
{
  "success": true
}
```

#### GET /categories
- Lists available categories
- Sample request: `curl -X GET http://127.0.0.1:5000/categories`
- Sample response:
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true
}
```
#### POST /quizzes
- Returns a next question from the given category, which is not included in the given list of the previous questions
- Request parameters: 
    -`quiz_category`: josn object with keys `type` and `id`
    -`previous_questions`: array of question IDs
- Sample request: `curl -X POST http://127.0.0.1:5000/quizzes -H 'Content-Type: application/json' -d '{"quiz_category": {"type": "Science", "id": "1"}, "previous_questions": [] }'`
- Sample response:
```
{
  "question": {
    "answer": "Alexander Fleming", 
    "category": 1, 
    "difficulty": 3, 
    "id": 21, 
    "question": "Who discovered penicillin?"
  }, 
  "success": true
}
```
### Error handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```

The following errors are possible:
- 400: bad request
- 404: resource not found
- 422: unprocessable
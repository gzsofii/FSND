from logging import NullHandler
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    # print('get drinks')
    drinks = Drink.query.all()
    # print(drinks)
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        # print('get drink details')
        # print('jwt: ', jwt)
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except:
        abort(500)  # anyway auth.py handles it


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    # print('post drinks')
    # print('jwt ', jwt)
    body = request.get_json()
    # print(body['recipe'])

    new_title = body['title']
    if 'recipe' in body:
        new_recipe = body['recipe']
    else:
        new_recipe = []

    # check if drink is already in database
    drinks = Drink.query.all()
    for d in drinks:
        if new_title == d.title:
            print(new_title, ' already in database')
            abort(422)

    # recipe should be an array of items
    if type(new_recipe) != list:
        new_recipe = [new_recipe]

    drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    drink.insert()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    # print('patch drink with id ', id)
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    body = request.get_json()
    # print('body: ', body)
    # print('drink: ', drink.title, drink.recipe)

    new_title = body['title']

    '''# check if drink is already in database
    drinks = Drink.query.all()
    for d in drinks:
        if new_title == d.title:
            print(new_title, ' already in database')
            abort(422)
    '''

    if 'recipe' in body:
        new_recipe = body['recipe']
    else:
        new_recipe = []

    if type(new_recipe) != list:
        new_recipe = [new_recipe]

    drink.title = new_title
    drink.recipe = json.dumps(new_recipe)

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    # print('deleting drink with id ', id)
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


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
    print('error: not found')
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    })

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

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
"""
db_drop_and_create_all()

# ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks")
def get_drinks():

    # get all drinks in short form
    drinks = [drink.short() for drink in Drink.query.all()]

    # if no drinks return 404
    if len(drinks) == 0:
        abort(404)

    return jsonify({"success": True, "drinks": drinks}), 200


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth(permission="get:drink-details")
def get_drink_details(payload):

    # get all drinks in long form
    drinks = [drink.long() for drink in Drink.query.all()]
    print(drinks)

    # if no drinks return 404
    if len(drinks) == 0:
        abort(404)

    return jsonify({"success": True, "drinks": drinks}), 200


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def create_drink(payload):

    # get info from request
    body = request.get_json()

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    # attempt creating drink otherqise return 400
    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))

        new_drink.insert()
    except Exception as e:
        print(e)
        abort(400)

    # return all drinks including new drink
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({"success": True, "drinks": drinks}), 200


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth(permission="patch:drinks")
def edit_drink(payload, id):
    print(payload)

    # get information to be edited
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    # attempt to edit drink
    try:
        drink = Drink.query.get(id)

        # if drink to edit is not found return 404
        if drink is None:
            abort(404)

        if new_title is not None:
            drink.title = new_title

        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)

        drink.update()

    # if edit drink does not work return 422
    except Exception as error:
        print(error)
        abort(422)

    return jsonify({"success": True, "drinks": [drink.long()]}), 200


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth(permission="delete:drinks")
def delete_drink(payload, id):

    # attempt to find drink
    drink = Drink.query.get(id)
    print(drink)

    # if drink is not found return 404
    if drink is None:
        abort(404)

    # attempt to delete found drink otherwise return 422
    try:
        drink.delete()
    except Exception as error:
        print(error)
        abort(422)

    return jsonify({"success": True, "delete": id})


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


"""
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""

"""
@TODO implement error handler for 404
    error handler should conform to general task above
"""


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def not_authorized(error):
    return (
        jsonify({"success": False, "error": error.status_code, "message": error.error}),
        error.status_code,
    )


if __name__ == "__main__":
    app.debug = True
    app.run()

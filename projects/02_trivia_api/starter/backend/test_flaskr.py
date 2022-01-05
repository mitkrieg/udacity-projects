import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format(
            "127.0.0.1:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # create test question for tests
        self.test_question = {
            "question": "Who was the second US president?",
            "answer": "John Adams",
            "difficulty": 2,
            "category": 4,
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """Test for successful return from /categories"""
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # good response
        self.assertEqual(data["success"], True)  # successful return of json
        self.assertTrue(data["total_categories"])  # returns total categories
        self.assertTrue(len(data["categories"]))  # returns data for each category

    # def test_no_found_categories(self):
    #     res = self.client().get("/categories")
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)  # error response
    #     self.assertEqual(data["success"], False)  # return json indicating failure
    #     self.assertEqual(
    #         data["message"], "unprocessable"  # returns correct error message
    #     )

    def test_get_questions_paginated(self):
        """Test for successful return of a page of questions"""
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # good response
        self.assertEqual(data["success"], True)  # successful return of json
        self.assertEqual(
            len(data["questions"]), 10
        )  # questions returned matches page length
        self.assertTrue(data["total_questions"])  # returns total questions

    def test_404_page_invalid_for_questions(self):
        """Test if requested page is out of range for questions"""
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)  # check for bad response for not found
        self.assertEqual(data["success"], False)  # returns json indicating failure
        self.assertEqual(
            data["message"], "resource not found"  # returns correct error message
        )

    def test_create_question(self):
        """Tests for creation of new question in API using test question"""

        res = self.client().post("/questions", json=self.test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(
            Question.query.filter(
                Question.question == "Who was the second US president?"
            ).all()
        )

    def test_search_question_with_results(self):
        """Tests search functionality with results"""
        res = self.client().post("/questions", json={"search_term": "what"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]), 8)

    def test_search_question_with_results(self):
        """Tests search functionality without results"""
        res = self.client().post("/questions", json={"searchTerm": "qwert"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_deleted_question(self):
        """
        Tests for deletion of requested questions. Deletes test question created by
        test_create_question()
        """
        max_id = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete("/questions/" + str(max_id.id))
        data = json.loads(res.data)

        question = Question.query.get(32)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(int(data["deleted"]), max_id.id)

    def test_get_questions_by_category(self):
        """Tests ability to get questions by category"""
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(int(data["current_category"]), 1)
        self.assertTrue(data["total_questions"], 3)

    def test_404_category_id_invalid(self):
        """Test if requested category id is out of range of categories"""
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)  # check for bad response for not found
        self.assertEqual(data["success"], False)  # returns json indicating failure
        self.assertEqual(
            data["message"], "resource not found"  # returns correct error message
        )


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

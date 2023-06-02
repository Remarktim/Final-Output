import unittest
import json
from FinalHandsOn import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.testing = True

    def test_hello_world(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "<p>Hello, World!</p>")

    def test_get_books(self):
        response = self.app.get("/books?format=json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, list)

    def test_get_book_by_id(self):
        response = self.app.get("/books/1?format=json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")

    def test_delete_book(self):
        response = self.app.delete("/books/1?format=json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")
    
    
    def test_get_books_xml_format(self):
        response = self.app.get("/books?format=xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/xml")

    def test_get_book_by_invalid_id(self):
        response = self.app.get("/books/100?format=json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")

    def test_add_book_with_missing_fields(self):
        data = {
            "title": "Incomplete Book",
            "author": "John Doe"
        }
        response = self.app.post("/books?format=json", json=data)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Missing required fields")

    def test_update_book_with_invalid_id(self):
        data = {
            "title": "Updated Book",
            "author": "Jane Doe",
            "genre": "Sci-Fi"
        }
        response = self.app.put("/books/100?format=json", json=data)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")

    def test_delete_book_with_invalid_id(self):
        response = self.app.delete("/books/100?format=json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")
    
    def test_add_book_with_duplicate_title(self):
        data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Classic"
        }
        response = self.app.post("/books?format=json", json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book added successfully")

    def test_update_book_with_missing_fields(self):
        data = {
            "author": "Jane Doe",
            "genre": "Sci-Fi"
        }
        response = self.app.put("/books/1?format=json", json=data)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")

    def test_delete_book_that_does_not_exist(self):
        response = self.app.delete("/books/100?format=json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["message"], "Book not found")

if __name__ == "__main__":
    unittest.main()

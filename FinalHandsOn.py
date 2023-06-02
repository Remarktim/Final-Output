from flask import Flask, make_response, jsonify, request
import xml.etree.ElementTree as ET
import mysql.connector

app = Flask(__name__)

# Create a MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
)

# Create a cursor object to interact with the database
cursor = db.cursor()

# Create a schema (database) if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS Final_HandsOn")
cursor.execute("USE Final_HandsOn")

# Create a table to store books if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        author VARCHAR(255),
        genre VARCHAR(255)
    )
""")
db.commit()

# Add sample book records to the MySQL database
sample_books = [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic"},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic"},
            {"title": "1984", "author": "George Orwell", "genre": "Dystopian"},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classic"},
            {"title": "Moby-Dick", "author": "Herman Melville", "genre": "Classic"},
            {"title": "Brave New World", "author": "Aldous Huxley", "genre": "Dystopian"},
            {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Classic"},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy"},
            {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy"},
            {"title": "Frankenstein", "author": "Mary Shelley", "genre": "Gothic"},
            {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "genre": "Gothic"},
            {"title": "Fahrenheit 451", "author": "Ray Bradbury", "genre": "Dystopian"},
            {"title": "The Odyssey", "author": "Homer", "genre": "Classic"},
            {"title": "One Hundred Years of Solitude", "author": "Gabriel Garcia Marquez", "genre": "Magical Realism"},
            {"title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fantasy"},
            {"title": "The Kite Runner", "author": "Khaled Hosseini", "genre": "Contemporary"},
            {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "genre": "Classic"},
            {"title": "The Brothers Karamazov", "author": "Fyodor Dostoevsky", "genre": "Classic"},
            {"title": "The Count of Monte Cristo", "author": "Alexandre Dumas", "genre": "Adventure"},
            {"title": "The Hunger Games", "author": "Suzanne Collins", "genre": "Dystopian"}
]

for book in sample_books:
    cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)",
                   (book["title"], book["author"], book["genre"]))

db.commit()


def generate_response(data, response_format):
    if response_format == "xml":
        xml_data = generate_xml(data)
        response = make_response(xml_data, 200)
        response.headers["Content-Type"] = "application/xml"
    else:
        response = make_response(jsonify(data), 200)
    return response



def generate_xml(data):
    root = ET.Element("books")
    for book in data:
        book_element = ET.SubElement(root, "book")
        for key, value in book.items():
            ET.SubElement(book_element, key).text = str(value)
    xml_data = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_data


@app.route("/", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/books", methods=["GET"])
def get_books():
    format = request.args.get("format", "json")

    # Retrieve all books from the MySQL database
    cursor.execute("SELECT * FROM books")
    result = cursor.fetchall()

    # Convert the database result to a list of dictionaries
    books = []
    for row in result:
        book = {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "genre": row[3]
        }
        books.append(book)

    return generate_response(books, format)


@app.route("/books/<int:id>", methods=["GET"])
def get_book_by_id(id):
    format = request.args.get("format", "json")

    # Retrieve the book with the given ID from the MySQL database
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    result = cursor.fetchone()

    if not result:
        return make_response(jsonify({"message": "Book not found"}), 404)

    book = {
        "id": result[0],
        "title": result[1],
        "author": result[2],
        "genre": result[3]
    }

    return generate_response(book, format)


@app.route("/books", methods=["POST"])
def add_book():
    format = request.args.get("format", "json")
    info = request.get_json()
    if "title" not in info or "author" not in info or "genre" not in info:
        return make_response(jsonify({"message": "Missing required fields"}), 400)
    title = info["title"]
    author = info["author"]
    genre = info["genre"]

    # Insert the new book into the MySQL database
    cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)", (title, author, genre))
    db.commit()
    new_book_id = cursor.lastrowid

    # Retrieve the newly added book from the database
    cursor.execute("SELECT * FROM books WHERE id = %s", (new_book_id,))
    result = cursor.fetchone()

    # Convert the database result to a dictionary
    new_book = {
        "id": result[0],
        "title": result[1],
        "author": result[2],
        "genre": result[3]
    }

    return generate_response({"message": "Book added successfully", "book": new_book}, format)


@app.route("/books/<int:id>", methods=["PUT"])
def update_book(id):
    format = request.args.get("format", "json")
    info = request.get_json()

    # Retrieve the book with the given ID from the MySQL database
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    result = cursor.fetchone()

    if not result:
        return make_response(jsonify({"message": "Book not found"}), 404)

    book = {
        "id": result[0],
        "title": result[1],
        "author": result[2],
        "genre": result[3]
    }

    if "title" in info:
        book["title"] = info["title"]
    if "author" in info:
        book["author"] = info["author"]
    if "genre" in info:
        book["genre"] = info["genre"]

    # Update the book in the MySQL database
    cursor.execute("UPDATE books SET title = %s, author = %s, genre = %s WHERE id = %s",
                   (book["title"], book["author"], book["genre"], id))
    db.commit()

    return generate_response({"message": "Book updated successfully", "book": book}, format)


@app.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    format = request.args.get("format", "json")

    # Retrieve the book with the given ID from the MySQL database
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    result = cursor.fetchone()

    if not result:
        return make_response(jsonify({"message": "Book not found"}), 404)

    book = {
        "id": result[0],
        "title": result[1],
        "author": result[2],
        "genre": result[3]
    }

    # Delete the book from the MySQL database
    cursor.execute("DELETE FROM books WHERE id = %s", (id,))
    db.commit()

    return generate_response({"message": "Book deleted successfully", "book": book}, format)


if __name__ == "__main__":
    app.run(debug=True)

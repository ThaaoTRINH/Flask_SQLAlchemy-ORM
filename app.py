# app.py
import os
from datetime import datetime
import time
from flask import Flask, request, render_template, redirect, url_for
from data_models import db, Author, Book

# create a flask instance
app = Flask(__name__)

# get the current directory
current_directory = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(current_directory, 'data', 'library.sqlite')

# set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{file_path}'

# Link the app to the database
db.init_app(app)

"""
# Create the database and tables (Run this line only once!) 
# - and hide after tables were created
with app.app_context():
    db.create_all()"""

# route for interacting with the data
@app.route('/', methods=['GET'])
def home():
    # list and sort the data
    authors = Author.query.order_by(Author.name).all()
    books = Book.query.order_by(Book.title).all()
    return_message = ''
    return render_template('home.html', authors=authors, books=books,
                           return_message=return_message)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    authors = Author.query.all()
    if request.method == 'POST':
        # get data from the form submission
        author_name = request.form.get('author_name')
        birth_date = request.form.get('birth_date')
        date_of_death = request.form.get('date_of_death')

        # convert the date input to Python data object
        birth_date_formatted = datetime.strptime(birth_date, '%Y-%m-%d').date()

        if date_of_death:
            date_death_formatted = datetime.strptime(date_of_death, '%Y-%m-%d').date()
        else:
            date_death_formatted = None

        if author_name in authors:
            return_message = f'{author_name} already exists'
        else:

            # create a new Author
            new_author = Author(name=author_name, birth_date=birth_date_formatted,
                                date_of_death=date_death_formatted)
            # set retry mechanism
            max_entries = 20
            for i in range(max_entries):
                try:
                    # add new_author to database file
                    db.session.add(new_author)
                    db.session.commit()
                    break
                    # Success, exit the loop
                except Exception:
                    if i < max_entries - 1:
                        print(f'Retrying after {i + 1} seconds')
                        time.sleep(i + 1)
                    else:
                        raise
                        # raise the exception if all retries failed

            return_message = f'{author_name} was successfully added!'

        return render_template('add_author.html', return_message=return_message,
                               name=author_name, birth_date=birth_date_formatted,
                               date_of_death=date_death_formatted
                               )
    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    return_message = ''
    if request.method == 'POST':
        book_isbn = request.form.get('book_isbn')
        book_title = request.form.get('book_title')
        publication_year = request.form.get('publication_year')
        author_name = request.form.get('author_name')

        # checking if the author already exists in the databases
        existing_author = Author.query.filter_by(name=author_name).first()
        if existing_author:
            author_id = existing_author.id
        else:
            authors = Author.query.order_by(Author.name).all()
            # get the max of author_id, the next will be +1
            max_author_id = max(author.id for author in authors)
            author_id = max_author_id + 1
            return_message = 'Author is not exist, input please! '

        new_book = Book(isbn=book_isbn, title=book_title, publication_year=publication_year,
                        author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        # with new author, jump to other function to add more details of new author
        return render_template('add_author.html', return_message=return_message)
    return render_template('add_book.html', return_message=return_message)

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_result = None
    # list and sort the data
    authors = Author.query.order_by(Author.name).all()
    books = Book.query.order_by(Book.title).all()
    if request.method == 'POST':
        key_word_search = request.form.get('key_word_search')
        if key_word_search:
            author = Author.query.filter(Author.name.ilike(f'%{key_word_search}%')).first()
            # ilike will match titles regardless of whether they are in uppercase or lowercase
            book = Book.query.filter(Book.title.ilike(f'%{key_word_search}%')).first()
            if author:
                search_result = f'Author: {author.name} | was born in {author.birth_date}'
            elif book:
                search_result = f'Book: {book.title} | was release in {book.publication_year}'
            else:
                search_result = 'No matching results found.'

    return render_template('home.html', authors=authors, books=books,
                           search_result=search_result)

# Route for display the update form and handle form submission
@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get(id)

    if request.method == 'POST':
        # Update book attributes based on form data
        book.title = request.form.get('title')
        book.isbn = request.form.get('isbn')
        book.publication_year = request.form.get('publication_year')

        # Save the changes to the existing database
        db.session.commit()

        # Redirect back to the update form for the same book
        return redirect(url_for('home'))

    return render_template('update_book.html', book=book)

@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(book_id):

    if request.method == 'POST':
        book_to_delete = Book.query.get_or_404(book_id)
        author_has_other_books = Book.query.filter_by(author=book_to_delete.author).count() > 1
        if author_has_other_books:
            db.session.delete(book_to_delete)
            db.session.commit()
        else:
            Book.query.filter_by(author=book_to_delete.author).delete()
            db.session.commit()
        return_message = f'Book with id: {book_id} successfully deleted'
    else:
        return_message = ''
    authors = Author.query.order_by(Author.name).all()
    books = Book.query.order_by(Book.title).all()
    return render_template('home.html', authors=authors, books=books, return_message=return_message)


@app.route('/update_author/<id>', methods=['GET', 'POST'])
def update_author(id):
    author = Author.query.get(id)
    return_message = ''
    if not author:
        return_message = 'Author not found'
    if request.method == 'POST':
        author.name = request.form.get('name')
        new_birth_date = request.form.get('birth_date')
        if new_birth_date:
            author.birth_date = datetime.strptime(new_birth_date, '%Y-%m-%d').date()
        else:
            author.birth_date = None

        new_date_of_death = request.form.get('date_of_death')
        if new_date_of_death:
            author.date_of_death = datetime.strptime(new_date_of_death, '%Y-%m-%d').date()
        else:
            author.date_of_death = None
        # commit to database
        db.session.commit()

        return_message = f'Author was already updated'
    return render_template('update_author.html', author=author, return_message=return_message)

@app.route('/author/<int:author_id>/delete', methods=['GET', 'POST'])
def delete_author(author_id):
    return_message = ''
    if request.method == 'POST':
        author_to_delete = Author.query.get(author_id)

        if author_to_delete:
            db.session.delete(author_to_delete)
            db.session.commit()
            return_message = f'Author with id: {author_id} successfully deleted'
        else:
            return_message = 'Author not found'

    authors = Author.query.order_by(Author.name).all()
    books = Book.query.order_by(Book.title).all()
    return render_template('home.html', authors=authors, books=books, return_message=return_message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5007, debug=True)

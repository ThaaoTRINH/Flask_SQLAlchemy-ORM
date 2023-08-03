# data_models.py
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database_name.db'
db = SQLAlchemy(app)

Base = db.Model
# Session = sessionmaker(bind=db.engine)
# session = Session()

# Define the Author model
class Author(Base):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        return f"<Author id={self.id}, name='{self.name}'>"

    def __str__(self):
        return f'Name of Author is {self.name}, birth_date is {self.birth_date}'

# Define the Book model
class Book(Base):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String)
    # name as 2 first letters of author and 1 first letter of book name
    title = db.Column(db.String)
    publication_year = db.Column(db.Integer)

    # create a foreign key relationship to authors table
    author_id = Column(Integer, db.ForeignKey('authors.id'))

    # define a relationship with the Author model
    author = relationship('Author', backref=db.backref('books'))

    def __repr__(self):
        return f"<Book id={self.id}, title='{self.title}'>"

    def __str__(self):
        return f'Book: {self.title}, is release in {self.publication_year}'

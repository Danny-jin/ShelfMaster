import sqlite3
import PySimpleGUI as sg

def setup_database():
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(author_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')

    conn.commit()
    conn.close()

def execute_db_query(conn, query, params=(), commit=False, fetchone=False, fetchall=False):
    """Generic database query execution helper function."""
    cursor = conn.cursor()
    cursor.execute(query, params)
    if commit:
        conn.commit()
    if fetchone:
        return cursor.fetchone()
    if fetchall:
        return cursor.fetchall()
    
def add_book_to_database(book_data):
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    author_id = get_or_create_author(conn, book_data['-AUTHOR-'])
    category_id = get_or_create_category(conn, book_data['-CATEGORY-'])
    sql = '''
        INSERT INTO books (title, author_id, category_id, isbn, quantity, publication_date, rating, location) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    try:
        c.execute(sql, (
            book_data['-TITLE-'],
            author_id,
            category_id,
            book_data['-ISBN-'],
            1,
            book_data['-PUBDATE-'],
            book_data['-RATING-'],
            book_data['-LOCATION-']
        ))
        conn.commit()
        sg.popup('Book added successfully!', title='Success')
    except sqlite3.IntegrityError:
        sg.popup('Duplicate ISBN entry.', title='Error')
    except Exception as e:
        sg.popup(f'An error occurred: {str(e)}', title='Error')
    finally:
        conn.close()


def get_all_books():
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    c.execute('''
        SELECT b.title, a.author_name, c.category_name, b.isbn
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        JOIN categories c ON b.category_id = c.category_id
    ''')
    books = [{'title': row[0], 'author': row[1], 'category': row[2], 'isbn': row[3]} for row in c.fetchall()]
    conn.close()
    return books

def delete_book(isbn):
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    try:
        c.execute('BEGIN')
        c.execute('SELECT author_id, category_id FROM books WHERE isbn = ?', (isbn,))
        book_info = c.fetchone()
        if not book_info:
            sg.popup('No book found with the given ISBN.', title='Error')
            return
        author_id, category_id = book_info

        c.execute('DELETE FROM books WHERE isbn = ?', (isbn,))

        c.execute('SELECT COUNT(*) FROM books WHERE author_id = ?', (author_id,))
        if c.fetchone()[0] == 0:
            c.execute('DELETE FROM authors WHERE author_id = ?', (author_id,))
            
        c.execute('SELECT COUNT(*) FROM books WHERE category_id = ?', (category_id,))
        if c.fetchone()[0] == 0:
            c.execute('DELETE FROM categories WHERE category_id = ?', (category_id,))
            
        conn.commit()
        sg.popup('Book and associated data deleted successfully!', title='Success')
    except sqlite3.Error as e:
        conn.rollback()
        sg.popup(f'An error occurred: {e}', title='Error')
    finally:
        conn.close()
        
def search_books(search_term):
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    c.execute("""
        SELECT b.*, a.author_name
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        WHERE b.title LIKE ? OR a.author_name LIKE ?
    """, ('%'+search_term+'%', '%'+search_term+'%'))
    books = c.fetchall()
    conn.close()
    return books

def get_book_by_isbn(isbn):
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    c.execute('''
        SELECT title, authors.author_name, categories.category_name, isbn, quantity, publication_date, rating, location
        FROM books
        JOIN authors ON books.author_id = authors.author_id
        JOIN categories ON books.category_id = categories.category_id
        WHERE isbn=?
    ''', (isbn,))
    book = c.fetchone()
    conn.close()
    if book:
        return {
            'title': book[0], 
            'author': book[1], 
            'category': book[2], 
            'isbn': book[3], 
            'quantity': book[4],
            'publication_date': book[5],
            'rating': book[6],
            'location': book[7]
        }
    else:
        return None

def update_book(book_data):
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    author_id = get_or_create_author(conn, book_data['-AUTHOR-'])
    category_id = get_or_create_category(conn, book_data['-CATEGORY-'])
    sql = '''
        UPDATE books
        SET title = ?, author_id = ?, category_id = ?, publication_date = ?, rating = ?, location = ?
        WHERE isbn = ?
    '''
    try:
        c.execute(sql, (
            book_data['-TITLE-'],
            author_id,
            category_id,
            book_data['-PUBDATE-'],
            book_data['-RATING-'],
            book_data['-LOCATION-'],
            book_data['-ISBN-']
        ))
        conn.commit()
        sg.popup('Book updated successfully!', title='Success')
    except sqlite3.Error as e:
        sg.popup(f'An error occurred: {str(e)}', title='Error')
    finally:
        conn.close()

def check_books():
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM books')
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_or_create_author(conn, author_name):
    c = conn.cursor()
    c.execute('SELECT author_id FROM authors WHERE author_name = ?', (author_name,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        c.execute('INSERT INTO authors (author_name) VALUES (?)', (author_name,))
        return c.lastrowid
    
def get_or_create_category(conn, category_name):
    c = conn.cursor()
    c.execute('SELECT category_id FROM categories WHERE category_name = ?', (category_name,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        c.execute('INSERT INTO categories (category_name) VALUES (?)', (category_name,))
        return c.lastrowid

def update_database_schema():
    conn = sqlite3.connect('home_library.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(books)")
    columns = [info[1] for info in c.fetchall()]
    if 'publication_date' not in columns:
        c.execute('ALTER TABLE books ADD COLUMN publication_date TEXT')
    if 'rating' not in columns:
        c.execute('ALTER TABLE books ADD COLUMN rating TEXT')
    if 'location' not in columns:
        c.execute('ALTER TABLE books ADD COLUMN location TEXT')
    conn.commit()
    conn.close()







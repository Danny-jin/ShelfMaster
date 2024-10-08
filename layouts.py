import PySimpleGUI as sg
from database import get_all_books, delete_book

def create_main_layout():
    book_list_column = sg.Column([], key='-BOOK-LIST-')
    layout = [[book_list_column]]
    return [
        [sg.Text('Home Library Management System', size=(30, 1), font=("Helvetica", 25), justification='center')],
        [sg.Button('Add Book'), sg.Button('Search Book'), sg.Button('Delete Book'), sg.Button('Update Book')],
        [sg.Text('_'  * 80)],
        [sg.Button('Exit')],
        layout
    ]

def get_add_book_layout():
    return [
        [sg.Text('Add Book', size=(30, 1), font=("Helvetica", 25), justification='center')],
        [sg.Text('Title', size=(15, 1)), sg.InputText(key='-TITLE-')],
        [sg.Text('Author', size=(15, 1)), sg.InputText(key='-AUTHOR-')],
        [sg.Text('Category', size=(15, 1)), sg.InputText(key='-CATEGORY-')],
        [sg.Text('Publication Date', size=(15, 1)), sg.InputText(key='-PUBDATE-')],
        [sg.Text('Rating', size=(15, 1)), sg.InputText(key='-RATING-')],
        [sg.Text('Location', size=(15, 1)), sg.InputText(key='-LOCATION-')],
        [sg.Text('ISBN', size=(15, 1)), sg.InputText(key='-ISBN-')],
        [sg.Button('Submit'), sg.Button('Return')]
    ]

def create_book_list_layout(action='delete'):
    books = get_all_books()
    if action == 'delete':
        button_text = 'Delete'
        button_key_prefix = '-DELETE-'
    elif action == 'update':
        button_text = 'Update'
        button_key_prefix = '-UPDATE-'
    book_list_elements = [
        [sg.Text(book['title']), sg.Button(button_text, key=f'{button_key_prefix}{book["isbn"]}-')]
        for book in books
    ]
    book_list_column = sg.Column(book_list_elements, key='-BOOK-LIST-')
    return [[book_list_column]]

def create_book_list_layout(action='update'):
    books = get_all_books()
    button_text = 'Update' if action == 'update' else 'Delete'
    button_key_prefix = '-UPDATE-' if action == 'update' else '-DELETE-'
    book_list_elements = [
        [sg.Text(book['title']), sg.Button(button_text, key=f'{button_key_prefix}{book["isbn"]}')]
        for book in books
    ]
    book_list_column = sg.Column(book_list_elements, scrollable=True, vertical_scroll_only=True, size=(300, 200))
    return [[book_list_column]]


def refresh_book_list(window):
    new_books = get_all_books()
    window['-BOOK-LIST-'].update([])
    book_list_layout = [
        [sg.Text(book['title']), sg.Button('Delete', key=f'-DELETE-{book["isbn"]}-')]
        for book in new_books
    ]
    window['-BOOK-LIST-'].update(book_list_layout)

    window.refresh()
    
def create_search_layout():
    return [
        [sg.Text('Enter search term:'), sg.InputText(key='-SEARCH-INPUT-')],
        [sg.Button('Search')],
        [sg.Listbox(values=[], size=(60, 10), key='-SEARCH-RESULTS-')],
        [sg.Button('Return to Main', key='-RETURN-MAIN-')]
    ]

def get_update_book_layout(book_data):
    return [
        [sg.Text('Update Book', size=(30, 1), font=("Helvetica", 25), justification='center')],
        [sg.Text('Title', size=(15, 1)), sg.InputText(book_data['title'], key='-TITLE-')],
        [sg.Text('Author', size=(15, 1)), sg.InputText(book_data['author'], key='-AUTHOR-')],
        [sg.Text('Category', size=(15, 1)), sg.InputText(book_data['category'], key='-CATEGORY-')],
        [sg.Text('Publication Date', size=(15, 1)), sg.InputText(book_data['publication_date'], key='-PUBDATE-')],
        [sg.Text('Rating', size=(15, 1)), sg.InputText(book_data['rating'], key='-RATING-')],
        [sg.Text('Location', size=(15, 1)), sg.InputText(book_data['location'], key='-LOCATION-')],
        [sg.Text('ISBN', size=(15, 1)), sg.InputText(book_data['isbn'], key='-ISBN-', disabled=True)],
        [sg.Button('Save'), sg.Button('Cancel')]
    ]


def delete_book_and_refresh_list(isbn, main_window):
    delete_book(isbn)
    refresh_book_list(main_window)




import PySimpleGUI as sg

from database import (
    setup_database, 
    add_book_to_database, 
    search_books, 
    get_book_by_isbn, 
    update_book, 
    update_database_schema
)

from layouts import (
    create_main_layout, 
    get_add_book_layout, 
    create_book_list_layout, 
    delete_book_and_refresh_list, 
    create_search_layout, 
    get_update_book_layout
)

def main():
    setup_database()
    window = sg.Window('Home Library Management System', create_main_layout())
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Add Book':
            window.hide()
            add_book_window = sg.Window('Add Book', get_add_book_layout())
            while True:
                add_event, add_values = add_book_window.read()
                if add_event in (sg.WIN_CLOSED, 'Return'):
                    break
                if add_event == 'Submit':
                    add_book_to_database(add_values)
                    break
            add_book_window.close()
            window.un_hide()

        elif event == 'Delete Book':
            book_list_layout = create_book_list_layout('delete')
            book_list_window = sg.Window('Delete Book', book_list_layout, modal=True)
            while True:
                del_event, del_values = book_list_window.read()
                if del_event in (sg.WIN_CLOSED, 'Return'):
                    break
                if del_event and del_event.startswith('-DELETE-'):
                    isbn_to_delete = del_event.split('-')[-1]
                    delete_book_and_refresh_list(isbn_to_delete, window)
            book_list_window.close()
            
        elif event == 'Update Book':
            book_list_layout = create_book_list_layout('update') 
            book_list_window = sg.Window('Select Book to Update', book_list_layout, modal=True)
            selected_book_isbn = None
            while True:
                update_event, update_values = book_list_window.read()
                if update_event in (sg.WIN_CLOSED, 'Cancel'):
                    break
                if update_event.startswith('-UPDATE-'):
                    selected_book_isbn = update_event.split('-')[-1]
                    break
            book_list_window.close()

            if selected_book_isbn:
                book_data = get_book_by_isbn(selected_book_isbn)
                if book_data:
                    book_data_dict = {
                        'title': book_data['title'], 
                        'author': book_data['author'], 
                        'category': book_data['category'], 
                        'isbn': book_data['isbn'], 
                        'quantity': book_data['quantity'],
                        'publication_date': book_data['publication_date'],
                        'rating': book_data['rating'],  
                        'location': book_data['location'],  
                    }
                    update_book_window = sg.Window('Update Book', get_update_book_layout(book_data_dict))
                    while True:
                        event, values = update_book_window.read()
                        if event == 'Save':
                            update_book(values)
                            update_book_window.close()
                            break
                        elif event in (sg.WIN_CLOSED, 'Cancel'):
                            update_book_window.close()
                            break

        elif event == 'Search Book':
            search_window_layout = create_search_layout()
            search_window = sg.Window('Search Books', search_window_layout, modal=True)
            while True:
                search_event, search_values = search_window.read()
                if search_event in (sg.WIN_CLOSED, '-RETURN-MAIN-'):
                    break
                elif search_event == 'Search':
                    search_term = search_values['-SEARCH-INPUT-']
                    search_results = search_books(search_term)
                    search_window['-SEARCH-RESULTS-'].update(values=[f"""Title: {book[1]}, 
                                                                     Author: {book[2]}, 
                                                                     ISBN: {book[4]}"""
                                                                     for book in search_results])
            search_window.close()

        elif event == 'Return':
            window.close()
            window = sg.Window('Home Library Management System', create_main_layout(), finalize=True)

    window.close()

if __name__ == "__main__":
    setup_database()
    update_database_schema()
    main()

import json
import requests
import xml.etree.ElementTree as ET

def request_book_data():
    credentials = None
    with open('secrets.json') as json_file:
        credentials = json.load(json_file)

    # request parameters
    url = 'https://www.goodreads.com/review/list.xml?v=2'
    payload = {}
    payload['key'] = credentials['key']
    payload['id'] = credentials['user_id']

    import pickle
    load_from_pickle = True

    if load_from_pickle:
        x = pickle.load(open('response.p', 'rb'))
        print 'Loading from pickle'
    else:
        x = requests.get(url, params=payload)
        pickle.dump(x, open('response.p', 'wb'))
        print 'Sending arequest'

    if x.status_code != 200:
        print 'Request Failed'
        quit()

    return x.content

def parse_book_data(goodreads_content):
    # parse the response XML
    root = ET.fromstring(goodreads_content)
    user_books = root[1]

    for curr_book in user_books:
        curr_book_info = curr_book.find('book')

        # book title
        book_name = curr_book_info.find('title').text
        
        # book authors
        book_authors = []
        book_authors_obj = curr_book_info.find('authors')
        for x in book_authors_obj:
            book_authors.append(x.find('name').text)

        # (0(finished, year), 1(currently reading), 2(future))
        # book bucket
        book_shelves = curr_book.find('shelves')
        shelf_bucket = None
        
        for curr_shelf in book_shelves:
            shelf_name = curr_shelf.get('name')
            
            if shelf_name == 'read':
                shelf_bucket = 0
                break
            elif shelf_name == 'currently-reading':
                shelf_bucket = 1
                break
            elif shelf_name == 'to-read':
                shelf_bucket = 2
                break

        # find year in which read
        if shelf_bucket == 0:
            year_finished = curr_book.find('read_at').text[-4:]
        else:
            year_finished = None

        print book_name, book_authors, shelf_bucket, year_finished

def write_to_readme(book_data):
    pass

def main():
    gr_resp = request_book_data()
    book_data = parse_book_data(gr_resp)
    write_to_readme(book_data)

if __name__ == '__main__':
    main()
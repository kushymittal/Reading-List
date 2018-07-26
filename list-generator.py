import json
import requests
import xml.etree.ElementTree as ET

# @TODO
# sort by date

def request_book_data():
    credentials = None
    with open('secrets.json') as json_file:
        credentials = json.load(json_file)

    # request parameters
    url = 'https://www.goodreads.com/review/list.xml?v=2'
    payload = {}
    payload['key'] = credentials['key']
    payload['id'] = credentials['user_id']
    payload['per_page'] = 200

    import pickle
    load_from_pickle = False

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

    book_data = [{}, {}, {}, {}]

    for curr_book in user_books:
        curr_book_info = curr_book.find('book')

        # book title
        book_name = curr_book_info.find('title').text

        # book authors
        book_authors = []
        book_authors_obj = curr_book_info.find('authors')
        for x in book_authors_obj:
            book_authors.append(x.find('name').text)

        # book rating
        book_rating = int(curr_book.find('rating').text)

        # (0(finished, year), 1(currently reading), 2(future))
        # book bucket
        book_shelves = curr_book.find('shelves')
        shelf_bucket = None
        reread = False
        
        for curr_shelf in book_shelves:
            shelf_name = curr_shelf.get('name')

            if shelf_name == 'read':
                shelf_bucket = 0
                #break
            elif shelf_name == 'currently-reading':
                shelf_bucket = 1
                #break
            elif shelf_name == 'to-read':
                shelf_bucket = 2
                #break
            
            if shelf_name == 'reread':
                reread = True

        book_data[shelf_bucket][book_name] = {}
        book_data[shelf_bucket][book_name]['authors'] = book_authors
        book_data[shelf_bucket][book_name]['rating'] = book_rating

        # find year in which read
        if shelf_bucket == 0:
            year_finished = curr_book.find('read_at').text[-4:]
            book_data[shelf_bucket][book_name]['year'] = year_finished

        # add to re-read section
        if reread or book_rating == 5:
            book_data[3][book_name] = book_data[shelf_bucket][book_name]

    return book_data

def format_for_readme(book_data):
    past, present, future, reread = book_data[0], book_data[1], book_data[2], book_data[3]
    past_sorted = sorted(past.items(), key=lambda x: x[1]['year'])
    ratings = [('', ''), (' :-1:', 'Disliked/Abandoned'), (' :zzz:', 'Slow/boring at times'), (' :+1:', 'Good read'), (' :thought_balloon: :+1: :thought_balloon:', 'Incredibly thought-provoking'), (' :clap: :clap: :clap:', 'Worth a re-read')]

    data_string = '# Reading List\n'

    data_string += '## Books worth re-reading\n'
    for book_name, book_info in reread.items():
        author_str = ', '.join(book_info['authors'])
        data_string += ('- [x] ' + book_name + ', ' + author_str + '\n')

    data_string += '## Key\n'
    for i in reversed(xrange(1, len(ratings))):
        data_string += (ratings[i][0] + '\t\t: ' + ratings[i][1] + '  \n')

    data_string += '\n'

    last_year = None
    for book_name, book_info in past_sorted:
        author_str = ', '.join(book_info['authors'])
        curr_year = book_info['year']

        if curr_year != last_year:
            last_year = curr_year
            data_string += ('\n## ' + curr_year + '\n\n')

        data_string += ('- [x] ' + book_name + ', ' + author_str + ratings[book_info['rating']][0] + '\n')

    data_string += '\n## Currently Reading\n\n'
    for book_name, book_info in present.items():
        author_str = ', '.join(book_info['authors'])
        data_string += ('- [ ] ' + book_name + ', ' + author_str + '\n')

    data_string += '\n## Up Next\n\n'
    for book_name, book_info in future.items():
        author_str = ', '.join(book_info['authors'])
        data_string += ('- [ ] ' + book_name + ', ' + author_str + '\n')
    
    return data_string.encode('utf-8')

def main():
    gr_resp = request_book_data()
    book_data = parse_book_data(gr_resp)
    data_string = format_for_readme(book_data)

    with open('README.md', 'w') as reading_list_file:
        reading_list_file.write(data_string)

if __name__ == '__main__':
    main()
import os
from googleapiclient.discovery import build

os.chdir("C:/Users/chris/OneDrive/Desktop/google_scraper")

def fetch_queries():

    queries = []

    with open('queries.txt', 'r') as queries_file:
        for line in queries_file:
            line = line.rstrip()
            queries.append(line)

    return queries


def open_doi_db():

    temp_dois = []

    # Open the doi database, import and strip the entries
    with open('doi_db.txt', 'r') as doi_database:
        for entry in doi_database:
            entry = entry.rstrip()
            temp_dois.append(entry)
    
    return temp_dois


def doi_checker(doi_to_check, doi_list):
    # Check if the doi is already known and return boolean value
    if doi_to_check in doi_list:
        return True, doi_to_check
    elif doi_to_check not in doi_list:
        with open('doi_db.txt', 'a') as doi_database:
            doi_database.write(doi_to_check + '\n')
        return False, doi_to_check
    

def google_custom_search(api_key, cx, query):
    service = build("customsearch", "v1", developerKey=api_key)

    try:
        response = service.cse().list(q=query, cx=cx, sort='date').execute()

        doi_list = open_doi_db()

        if 'items' in response:
            for item in response['items']:

                url = item['link']

                already_present, doi = doi_checker(url, doi_list)

                if not already_present:
                    print(f"Title: {item['title']}")
                    print(f"Link: {item['link']}")
                    print("\n")
        else:
            print("No results found.")

    except Exception as e:
        print(f"Error: {e}")


def main():

    queries_list = fetch_queries()

    API_key="AIzaSyAR1Dvdd-uHJYCiB5zjyit8mqnTYbBd9GU"
    cx="3300dbc29ad7543ab"
    query='ADS024'

    google_custom_search(API_key, cx, queries_list)


if __name__ == '__main__':
    main()
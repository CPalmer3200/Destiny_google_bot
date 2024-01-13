import os
from googleapiclient.discovery import build
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import ssl
import smtplib

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
    

def google_custom_search(api_key, cx, query, email_body):
    service = build("customsearch", "v1", developerKey=api_key)

    try:
        response = service.cse().list(q=query, cx=cx, sort='date').execute()

        doi_list = open_doi_db()

        if 'items' in response:
            for item in response['items']:

                url = item['link']

                already_present, doi = doi_checker(url, doi_list)

                if not already_present:
                    temp_string = f"{item['title']} {item['link']} + \n"
                    email_body += temp_string
        else:
            print("No results found.")

    except Exception as e:
        print(f"Error: {e}")

    return email_body


def body_format(email_body):

    # Splits the email_body variable into a list
    email_body_list = email_body.split('\n')

    # Formats email body into a numbered list
    email_body_html = '<ol style="color: black; font-size: 16px;">'
    for item in email_body_list:
        if item.strip():
            email_body_html += f'<li>{item.strip()}</li>'
    email_body_html += '</ol>'
    return email_body_html


def html_formatting(email_body):
    # Fetch the current date for email titling
    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    # Explanation of the search queries used to perform this search
    url = 'https://www.destinypharma.com/'

    # html formatting of the push email
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    h1 {{
                        font-size: 22px;
                        color: white;
                        text-align: center;
                        font-family: 'Tw Cen MT', sans-serif; /* Use Tw Cen MT font */
                        text-decoration: underline; /* Underline the text */
                        margin: 0; /* Remove margin from the h1 element */
                    }}
                    .container {{
                        display: flex;
                        flex-direction: column;
                        justify-content: center; /* Center vertically */
                        align-items: center; /* Center horizontally */
                        background-color: #ff7d1d; /* Banner background color */
                        padding: 10px; /* Add padding to the banner */
                        height: auto;
                    }}
                    body {{
                        font-size: 16px;
                        color: black;
                        font-family: 'Tw Cen MT', sans-serif; /* Use Tw Cen MT font */
                        margin: 0; /* Remove default body margin */
                        padding: 0; /* Remove default body padding */
                    }}
                    img {{display: block; margin: 0 auto;
                    }}
                    hr {{
                        background-color: black; /* Black line */
                        height: 1px; /* Line thickness */
                        border: none;
                    }}
                    .small-text {{
                        font-size: 12px;
                        color: black;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <img src="cid:image">
                <div class="container">
                    <h1 style="text-align: center;">New competitor updates are available ({date})</h1>
                </div>
                {email_body}
                <hr> <!-- Black line -->
                <p class="small-text">
                    <br><br>
                    {url}
                </p>
            </body>
            </html>
            """
    return html


def send_email(email_text, email_sender, email_password, email_receiver):

    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    subject = f'New competitor updates ({date})'  # Title of the email
    body = email_text

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body, 'html'))  # Instruct python to expect html content

    # Open and attach the logo (image.jpg) to the file
    try:
        with open('image.JPG', 'rb') as image_file:
            image = MIMEImage(image_file.read())
            image.add_header('Content-ID', '<image>')
            em.attach(image)
    except FileNotFoundError:
        print('"image.JPG" not identified, continuing without it')

    context = ssl.create_default_context()

    # Use SMTP to log in to the sender email and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def main():

    email_body = ""

    queries_list = fetch_queries()

    API_key= os.environ["API_KEY"]
    cx="c7033df14fbab445f"

    for query in queries_list:
        email_body = google_custom_search(API_key, cx, query, email_body)

    # Send email if any high priority papers are recorded
    if email_body != "":

        formatted_email_body = body_format(email_body)

        formatted_email = html_formatting(formatted_email_body)
        email_sender = 'automatedscrapingbot@gmail.com'
        email_password = os.environ["PASSWORD"]
        email_receiver = 'christopher.palmer32@gmail.com'

        send_email(formatted_email, email_sender, email_password, email_receiver)
        print(formatted_email_body)

        print('Query complete - returning to sleep')


if __name__ == '__main__':
    main()
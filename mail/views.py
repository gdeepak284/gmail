from django.http import HttpResponse
from django.template import Template, Context, RequestContext
import base64
import csv
import dateutil.parser as parser
from apiclient import discovery
from bs4 import BeautifulSoup
from httplib2 import Http
from oauth2client import file, client, tools


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def render_html(request, template="index.html"):
    fp = open("/Users/user/Desktop/gmail/mysite/templates/index.html")
    t = Template(fp.read())
    fp.close()
    html = t.render(Context({'current_date': 'Deepak'}))
    return HttpResponse(html)


def request_page(request):
    if request.GET.get('mybtn'):
        counter = "Hello Deepak"
        print(counter)
    # return render_to_response('selected_path.html')
    return HttpResponse("Hello, world. You're at the polls index.")


def submit(request):
    if request.GET.get('mybtn'):
        counter = "Hello Deepak"
        print(counter)
    # Creating a storage.JSON file with authentication details
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
    # SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
    pa = '/Users/user/Desktop/gmail/mysite/credentials.json'
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(pa, SCOPES)
        creds = tools.run_flow(flow, store)
    GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

    user_id = 'me'
    label_id_one = 'INBOX'
    label_id_two = 'UNREAD'

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = GMAIL.users().messages().list(userId='me',
                                                labelIds=[label_id_one,
                                                          label_id_two]).execute()

    # We get a dictonary. Now reading values for the key 'messages'
    mssg_list = unread_msgs['messages']

    print("Total unread messages in inbox: ", str(len(mssg_list)))

    final_list = []

    for mssg in mssg_list:
        temp_dict = {}
        m_id = mssg['id']  # get id of individual message
        message = GMAIL.users().messages().get(userId=user_id,
                                               id=m_id).execute()  # fetch the message using API
        payld = message['payload']  # get payload of the message
        headr = payld['headers']  # get header of the payload

        for one in headr:  # getting the Subject
            if one['name'] == 'Subject':
                msg_subject = one['value']
                temp_dict['Subject'] = msg_subject
            else:
                pass

        for two in headr:  # getting the date
            if two['name'] == 'Date':
                msg_date = two['value']
                date_parse = (parser.parse(msg_date))
                m_date = (date_parse.date())
                temp_dict['Date'] = str(m_date)
            else:
                pass

        for three in headr:  # getting the Sender
            if three['name'] == 'From':
                msg_from = three['value']
                temp_dict['Sender'] = msg_from
            else:
                pass

        temp_dict['Snippet'] = message['snippet']  # fetching message snippet

        try:

            # Fetching message body
            mssg_parts = payld['parts']  # fetching the message parts
            part_one = mssg_parts[0]  # fetching first element of the part
            part_body = part_one['body']  # fetching body of the message
            part_data = part_body['data']  # fetching data from the body
            clean_one = part_data.replace("-",
                                          "+")  # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_",
                                          "/")  # decoding from Base64 to UTF-8
            clean_two = base64.b64decode(
                bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
            soup = BeautifulSoup(clean_two, "lxml")
            mssg_body = soup.body()
            # mssg_body is a readible form of message body
            # depending on the end user's requirements, it can be further cleaned
            # using regex, beautiful soup, or any other method
            temp_dict['Message_body'] = mssg_body

        except:
            pass

        print(temp_dict)
        final_list.append(
            temp_dict)  # This will create a dictonary item in the final list

        # This will mark the messagea as read
        GMAIL.users().messages().modify(userId=user_id, id=m_id, body={
            'removeLabelIds': ['UNREAD']}).execute()

    print("Total messaged retrived: ", str(len(final_list)))

    # exporting the values as .csv
    with open('CSV_NAME.csv', 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['Sender', 'Subject', 'Date', 'Snippet', 'Message_body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for val in final_list:
            writer.writerow(val)
    return HttpResponse(final_list)


def submit_geo():
    return HttpResponse("hello")

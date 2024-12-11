from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from flask import Blueprint
import base64,os,hashlib

# send mail by using **Gmail API**

# setup blueprint
sendmail = Blueprint('sendmail', __name__)
# base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# path for credentials.json
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'mail_authfile', 'credentials.json')
# path for token.json
TOKEN_PATH = os.path.join(BASE_DIR, 'mail_authfile', 'token.json')
# gmailAPI scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
# mail address setup
SEND_FROM ='support@cercil.net'
UNIV_ADDRESS = '@shinshu-u.ac.jp'

# generate(or load) credential to prepare the API
def generate_credentials():
    credential_file = None
    # check if token file exists and load the token if valid
    if os.path.exists(TOKEN_PATH):
        credential_file = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # if credentials are not available or invalid
    if not credential_file or not credential_file.valid:
        if credential_file and credential_file.expired and credential_file.refresh_token: # regenerate token
            credential_file.refresh(Request())
        else: # auth
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            credential_file = flow.run_local_server(port=0)

        # save credentials as token
        with open(TOKEN_PATH, 'w') as token:
            token.write(credential_file.to_json())

    return credential_file

# send email by using the API
def send_email(to, subject, body):
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        # the api needs encoded mime mail message by base64url str
        message = MIMEText(body,"html","utf-8")
        message['to'] = to
        message['from'] = SEND_FROM
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # send
        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()
        print("success(mail)")
    except Exception as error:
        print(f"An error occurred(mail): {error}")

# hash student_id and add StudentInfo table
def hash_student_id(student_id):
    # 循環参照が起きてしまうので、ここで読み込む
    from . import db
    from .models import StudentInfo
    # find existed student
    student = StudentInfo.query.filter_by(student_id=student_id).first()
    # existed, dont generate
    if student:
        print("student already exists")
        return student.hashed_id
    # prepare for new student
    print("student not found, generating...")
    hashed_id = hashlib.md5(student_id.encode()).hexdigest()
    new_student = StudentInfo(student_id=student_id,hashed_id=hashed_id)

    db.session.add(new_student)
    db.session.commit()

    return hashed_id
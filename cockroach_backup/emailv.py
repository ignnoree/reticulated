from cs50 import SQL
from bots import create_key
import ezgmail ,os
from ezgmail import init
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apis  import sender_email,sender_password


def create_email_verify_request(email):
    db=SQL('sqlite:///reticulated.db')
    email_already_sent=db.execute('select email from email_verifications where email = ? ', email)
    email_already_paired=db.execute('select email from reti_databases where email = ?',email)
    if not email_already_sent and not email_already_paired:
        key=create_key(5)
        email=email
        sendemail(email,key)
        if sendemail:
            db.execute('insert into email_verifications (email,verification_code) VALUES (?,?)',email,key)
            return "Verification email sent successfully enter the email and code and file now"
    elif email_already_sent:
        return 'Email already sent try again in 1 minute'
    elif email_already_paired:
        return 'Email already paired with a database'
    
    
    
    




def sendemail(email, key):
    
    

    
    subject = 'Reticulated verification code'
    message = f'Your verification code is: {key}'

   
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    
    msg.attach(MIMEText(message, 'plain'))

    try:
       
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Replace with your SMTP server details
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")




def code_is_valid(email,code):
    db=SQL('sqlite:///reticulated.db')
    verify_code=db.execute('select verification_code from email_verifications where email=? and verification_code = ?',email,code)
    if verify_code:
        key=create_key(50)
        crdatabase(key,email)
        return key



def crdatabase(key,email):
    uploadfolder=r'D:\cockroach\retyculated_databases'
    db=SQL('sqlite:///reticulated.db')
    db_path = os.path.join(uploadfolder,f'{email}.db')
    conn = sqlite3.connect(db_path)
    conn.close()
    db.execute('insert into reti_databases (database_path,database_key,email) VALUES (?,?,?)',db_path,key,email)
    return 'database created,'

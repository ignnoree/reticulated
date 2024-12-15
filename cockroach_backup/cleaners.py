from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from cs50 import SQL
import os
import shutil

def delete_expired_emails():
    db = SQL('sqlite:///reticulated.db')
    expiration_time = datetime.now() - timedelta(minutes=5)
    db.execute("DELETE FROM email_verifications WHERE created_at < ?", expiration_time)
    print("Expired verification emails deleted.")



def find_expired_databases():
    db = SQL('sqlite:///reticulated.db')
    expiration_time = datetime.now() - timedelta(minutes=59)
    expired_database_path=db.execute("select database_path FROM reti_databases WHERE created_at < ?", expiration_time)
    print(f'this is the res = {expired_database_path}')
    if expired_database_path:
        for i in expired_database_path:
            print (f' this is i = {i}')
            p=i['database_path']
            clear_uploaded_databases(p)
            db.execute("DELETE FROM reti_databases WHERE database_path = ?", p)
            print('deleted db')





def clear_uploaded_databases(database_path):
    if os.path.exists(database_path):
        try:
            os.remove(database_path)  # Deletes the file
            print(f"Deleted expired database: {database_path}")
        except OSError as e:
            print(f"Error: {e.strerror}")
    else:
        print(f"File not found: {database_path}")


scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_emails, 'interval', minutes=5)  
scheduler.add_job(find_expired_databases, 'interval', minutes=55)
scheduler.start()



import os
from flask import Flask, request, jsonify
import openai
from apis import chatgpt, concept,concept2
from cs50 import SQL
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string





def check_filename(filename):
    
    dbcheck=filename[-3:]
    
    if dbcheck != ".db":
        return False
    else:
        print("Filename passes.")
        return True




def create_key(length):
    """ Generates a strong random key of specified length. """
    
    random_bytes = os.urandom(length)
   
    return random_bytes.hex()
      

def find_key_path(key):
   db=SQL('sqlite:///reticulated.db')
   try:
        path_ifkeyisvalid=db.execute('select database_path from reti_databases where database_key = ? ',key)[0]['database_path']
   except Exception:
       return None
   if path_ifkeyisvalid:
      return path_ifkeyisvalid
   else:
        return None
   


def create_rety_tables(input,key):
    if key:
        keyisvalid=find_key_path(key)
        if keyisvalid:
            path=keyisvalid
            db=SQL(f'sqlite:///{path}')
            db_schema=get_schema(path)

            messages = [{'role': 'system', 'content': concept2}]    
            messages.append({'role': 'user', 'content': f'user_input={input}, user database schema = {db_schema}'})
            chat = openai.ChatCompletion.create(model='gpt-4', messages=messages)
            reply = chat.choices[0].message.content
            print(reply)
            if reply=='False':
                return ('input not clear enough :( ')  
            elif reply =='table already exist':
                return ('table already exists ! query too see the tables') 
            try:
                db.execute(reply)
                return ('table created succsessfully !')
            
            except Exception:
                return ('input not clear enough :( ')   
        else:
                return None
            


            
        
    

def get_schema(db_path):
    schema = {}
    db = SQL(f'sqlite:///{db_path}')
    tables = db.execute('SELECT name FROM sqlite_master WHERE type="table";')
    
    for table in tables:
        table_name = table['name']
        schema_info = db.execute(f'SELECT sql FROM sqlite_master WHERE name="{table_name}";')[0]['sql']
        
        # Split the CREATE TABLE statement into components
        create_statement = schema_info.split('(')
        columns_section = create_statement[1].strip(');')
        
        column_info = []
        for column in columns_section.split(','):
            column_details = column.strip()
            # Extract column name and any constraints
            parts = column_details.split()
            column_name = parts[0]
            data_type = parts[1] if len(parts) > 1 else ''
            constraints = ' '.join(parts[2:]) if len(parts) > 2 else ''
            column_info.append({
                'name': column_name,
                'data_type': data_type,
                'constraints': constraints
            })
        
        schema[table_name] = {
            "table_name": table_name,
            "columns": column_info
        }
    
    
    return schema
        
   

def sql_retrieve_bot(user_message,db_path):
  #try:
    try:
    
        db = SQL(f'sqlite:///{db_path}')
        
        schema=get_schema(db_path)
    except Exception as e:
        return jsonify({"error": f"Failed to read database schema: {str(e)}"}), 500
        
    
    query_request=f"""sql database type is = sqlite 
  this is the whole database schema, read it so you can provide accurate query = {schema} , 
    the query i want is ={user_message}"""
    
    print(concept)
    messages = [{'role': 'system', 'content': concept}]    
    if query_request:
        messages.append({'role': 'user', 'content': user_message})
        chat = openai.ChatCompletion.create(model='gpt-4', messages=messages)
        reply = chat.choices[0].message.content
        if reply=='False':
          return jsonify('input not clear enough :( ')
        elif reply=="i just do querys":
            return jsonify('go to  /create for crud operations, this section is just for retrieving data')
        print (reply)
        try:
          print (f'testttttttttt 1 = {reply}')
          result=db.execute(reply)
          result2={"query":reply,
                   "result":result}
          return result2
        except Exception:
           return jsonify(':(')
    #except Exception:
        #return jsonify('pls try again in a few hours')
      

def clean_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
        
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print({"error": f"Failed to clean directory: {str(e)}"}), 500
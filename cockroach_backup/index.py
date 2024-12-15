from flask import Flask, request, render_template, session, flash, jsonify,redirect,send_file
import openai
from apis import chatgpt,concept
from cs50 import SQL
import os
from datetime import datetime
from bots import create_rety_tables,sql_retrieve_bot,get_schema,find_key_path,create_key,check_filename
from emailv import create_email_verify_request,code_is_valid,crdatabase
from cleaners import scheduler


openai.api_key = chatgpt
concept=concept
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploaded_databases')
RETICULATED_FOLDER=os.path.join(os.getcwd(), 'retyculated_databases')
os.makedirs(RETICULATED_FOLDER, exist_ok=True) 
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] =RETICULATED_FOLDER
app.config['retyculated_databases']=RETICULATED_FOLDER

@app.route('/',methods=['POST','GET'])
def homee():
    return render_template('home.html')


@app.route('/getkey',methods=['POST','GET'])
def home():
    if request.method=='POST':
        email=request.form.get('email')
        verification_code = request.form.get('verification_code')
        file=request.files['file']
        if email and not verification_code and not file:
            result=create_email_verify_request(email)
            return jsonify({"msg":result})
            

        elif email and verification_code and file:
            db=SQL('sqlite:///reticulated.db')
            verify_code=db.execute('select verification_code from email_verifications where email=? and verification_code = ?',email,verification_code)
            if verify_code:
                print(file.filename)
                cfilename=check_filename(file.filename)
                if cfilename:
                    key = create_key(50)
                    filename=f'{email}_{file.filename}'
                    
                    try:
                        db_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
                        file.save(db_path)
                        db.execute('insert into reti_databases (database_key,database_path,email)VALUES(?,?,?)',key,db_path,email)
                    except Exception as e:
                        print(e)

                    response = {
                
                    "msg": "Database inserted into the servers. You have 1 hour to make changes to your database, then download the edited version. It will be removed after 1 hour from servers.",
                    "key": key}
                    return jsonify(response)
                else:
                    return jsonify({"error": ".db file is required"})
            else:
                return jsonify({"msg":"verification code is wrong "})
       

    return render_template('getkey.html')
    


@app.route('/create',methods=['POST','GET'])
def createtables():
    if request.method=='POST':
        key=request.form.get('key')
        userinput=request.form.get('input')
        result=create_rety_tables(userinput, key=key)
        if result:
            return jsonify({"msg":"succsessfull",
                            "msg":result})
        else :
            return jsonify({"error":" key is not valid !"})
    return render_template('test.html')






@app.route('/createdatabase', methods=['GET', 'POST'])
def getkeys():
    if request.method == 'POST':
        email = request.form.get('email')
        verification_code = request.form.get('verification_code')
        if email and not verification_code:
            
            result=create_email_verify_request(email)
            return jsonify({"msg":result})
        
        
        elif email and verification_code:
            
            key=code_is_valid(email,verification_code)
            if key:

                return render_template('createdatabase.html',key=key,email=email)
                
            else:
                flash("Invalid verification code. Please try again.", "error")         

        else:
            flash("Email is required!", "error")
    return render_template('createdatabase.html')
        

@app.route('/getschema', methods=['GET','POST'])
def get_data():
    if request.method=='POST':
       
        key=request.form.get('key')
        if  key :
            db=SQL('sqlite:///reticulated.db')
            db_path=db.execute('select database_path from reti_databases where database_key = ?',key)[0]['database_path']
            if db_path:
                result=get_schema(db_path)
                return jsonify({
                    "schema":result
                })
            else:
                return jsonify({
                    "msg":"key or email invalid"
                })
        else:
            return jsonify({
                "msg":"key and email required"})
    return render_template('getschema.html')



@app.route('/query_withkey', methods=['GET', 'POST'])
def QUERY_with_key():
    if request.method=='POST':
        key=request.form.get('key')
        userinput=request.form.get('input')
        if key : 
            db=SQL('sqlite:///reticulated.db')
            try:
                db_path=db.execute('select database_path from reti_databases where database_key = ?',key)[0]['database_path']
            except Exception:
                return jsonify({"msg":"key is not valid"})
            print(f'inside 1 ={db_path}')
            if db_path:
                result=sql_retrieve_bot(userinput,db_path)
                return result
            #return jsonify({"error":"invalid key or email"})
        return jsonify({
            "error":"email and key required !"
        })

    return render_template('query2.html')


@app.route('/download', methods=['GET','POST'])
def download_file():
    if request.method=='POST':
        key=request.form.get('key')

        filepath=find_key_path(key)
        print(f'ffff = {filepath}')
        if filepath:
            return send_file(filepath, as_attachment=True)
        else :
            return jsonify({"error":"key is not valid"}),400
    return render_template('key_form.html')
            




if __name__ == '__main__':
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started. Running Flask app...")
    else:
        print("Scheduler is already running.")
    app.run(debug=True)

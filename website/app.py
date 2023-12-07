from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL


app = Flask(__name__)




# MYSQL
DB = Sequel.connect('mysql2://digital_user:goU0oLgYwsc4JXiA@localhost/digital')

# MySQL configurations
app.config['MYSQL_HOST'] = 'mysql2://localhost/digital'
app.config['MYSQL_USER'] = 'digital_user'
app.config['MYSQL_PASSWORD'] = 'goU0oLgYwsc4JXiA'
app.config['MYSQL_DB'] = 'canna_emar'
mysql = MySQL(app)






if __name__ == '__main__':
    app.run(debug=True)




@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/information')
def information():
    return render_template('information.html')

@app.route('/consent')
def consent():
    return render_template('consent.html')

@app.route('/submit-consent', methods=['POST'])
def submit_consent():
    # Code to handle consent submission
    # Redirect to next part of the study or show a confirmation message
    return "Consentimiento recibido. ¡Gracias!"

@app.route('/sociodemographic')
def sociodemographic():
    return render_template('sociodemo.html')

app.route('/submit-sociodemographic', methods=['POST'])
def submit_sociodemographic():
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='mydatabase',
                                       user='myuser',
                                       password='mypassword')
        if conn.is_connected():
            cursor = conn.cursor()

            # Extracting form data
            name = request.form['name']
            age = request.form['age']
            sex = request.form['sex']
            education_level = request.form['education']
            country_of_origin = request.form['country']
            years_in_uruguay = request.form['years_in_uruguay']
            residence = request.form['residence']
            email = request.form['email']
            phone = request.form['phone']

            # Insert data into the database
            sql = """INSERT INTO sociodemographic_data
                     (name, age, sex, education_level, country_of_origin,
                      years_in_uruguay, residence, email, phone)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, age, sex, education_level, country_of_origin,
                                 years_in_uruguay, residence, email, phone))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Data submitted successfully.'
    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'


@app.route('/traumatic-experiences')
def traumatic_experiences():
    return render_template('traumatic_experiences.html')

@app.route('/submit-traumatic-experiences', methods=['POST'])
def submit_traumatic_experiences():
    # Code to handle form submission
    # Save data to database or process as needed
    return "Respuestas recibidas. ¡Gracias!"

@app.route('/traumatic-experiences')
def traumatic_experiences():
    return render_template('traumatic_experiences.html')

@app.route('/submit-traumatic-experiences', methods=['POST'])
def submit_traumatic_experiences():
    # Code to handle form submission
    # Save data to database or process as needed
    return "Respuestas recibidas. ¡Gracias!"


@app.route('/cannabis-questionnaire')
def cannabis_questionnaire():
    return render_template('cannabis_questionnaire.html')

@app.route('/submit-cannabis-questionnaire', methods=['POST'])
def submit_cannabis_questionnaire():
    conn = mysql.connection
    cursor = conn.cursor()

    # Extracting form data
    question_1_response = request.form['question1']
    question_2_response = request.form['question2']
    question_3_response = request.form['question3']
    # Extract more fields as per your form

    # Insert data into the database
    sql = """INSERT INTO cannabis_questionnaire_responses
             (user_id, question_1_response, question_2_response, question_3_response)
             VALUES (%s, %s, %s, %s)"""
    cursor.execute(sql, (user_id, question_1_response, question_2_response, question_3_response))
    conn.commit()
    cursor.close()

    return 'Cannabis questionnaire responses submitted successfully.'


@app.route('/sns-questionnaire')
def sns_questionnaire():
    return render_template('sns_questionnaire.html')

@app.route('/submit-sns-questionnaire', methods=['POST'])
def submit_sns_questionnaire():
    conn = mysql.connection
    cursor = conn.cursor()

    # Extracting form data
    question_1_response = request.form.get('q1')
    question_2_response = request.form.get('q2')
    # Continue extracting other fields as per your form

    # Insert data into the database
    sql = """INSERT INTO sns_questionnaire_responses
             (user_id, question_1_response, question_2_response)
             VALUES (%s, %s, %s)"""
    cursor.execute(sql, (user_id, question_1_response, question_2_response))
    conn.commit()
    cursor.close()

    return 'SNS questionnaire responses submitted successfully.'

@app.route('/ideas-ref-questionnaire')
def ideas_ref_questionnaire():
    return render_template('ref_ideas.html')


@app.route('/submit-self-reference-ideas', methods=['POST'])
def submit_self_reference_ideas():
    conn = mysql.connection
    cursor = conn.cursor()

    # Extracting form data
    question_1_response = request.form.get('q1')
    question_2_response = request.form.get('q2')
    # Continue extracting other fields as per your form

    # Insert data into the database
    sql = """INSERT INTO self_reference_ideas_responses
             (user_id, question_1_response, question_2_response)
             VALUES (%s, %s, %s)"""
    cursor.execute(sql, (user_id, question_1_response, question_2_response))
    conn.commit()
    cursor.close()

    return 'Self-Reference Ideas questionnaire responses submitted successfully.'




@app.route('/sns-questionnaire')
def sns_questionnaire():
    return render_template('sns.html')

@app.route('/submit-sns-questionnaire', methods=['POST'])
def submit_sns_questionnaire():
    # Extract submitted data
    submitted_data = request.form
    # Process the data as needed, like storing in a database
    print(submitted_data)  # For now, just printing the data to console

    return "Respuestas recibidas. ¡Gracias!"


@app.route('/saliencia-questionnaire')
def saliencia_questionnaire():
    return render_template('saliencia.html')

@app.route('/submit-saliencia-questionnaire', methods=['POST'])
def submit_saliencia_questionnaire():
    conn = mysql.connection
    cursor = conn.cursor()

    # Extracting form data
    question_1_response = request.form.get('q1')
    question_2_response = request.form.get('q2')
    # Continue extracting other fields as per your form

    # Insert data into the database
    sql = """INSERT INTO saliency_scale_responses
             (user_id, question_1_response, question_2_response)
             VALUES (%s, %s, %s)"""
    cursor.execute(sql, (user_id, question_1_response, question_2_response))
    conn.commit()
    cursor.close()

    return 'Saliency Scale questionnaire responses submitted successfully.'



@app.route('/open-questions')
def open_questions():
    return render_template('open_questions.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    # You can access the uploaded audio file with request.files['file']
    audio_file = request.files.get('audio')
    if audio_file:
        # Save the audio file or process it as needed
        filename = secure_filename(audio_file.filename)
        audio_file.save(os.path.join('data/audio/', filename))

        # Save file metadata to the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO audio_files (filename, question_id, user_id) VALUES (%s, %s, %s)", (filename, question_id, user_id))
        mysql.connection.commit()
        cursor.close()

    return redirect(url_for('open_questions'))

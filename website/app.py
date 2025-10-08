from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import random, logging, datetime, magic, os, string, re
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
import html

#logging.basicConfig(filename='app.log', level=logging.DEBUG)


# Current file's directory
basedir = os.path.abspath(os.path.dirname(__file__))


def get_path(filename):
    return os.path.join(basedir, filename)


with open(get_path("app_key.txt"), 'r') as file:
    lines = file.readlines()
    app_key = lines[0].strip()

app = Flask(__name__)
app.secret_key = app_key  # Set your secret key here
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=120) # dos horas para hacer la tarea



ALLOWED_EXTENSIONS = {'wav', 'mp3','webm','ogg','oga','m4a','opus'}

def generate_random_string(length=8):
    # Generates a random string of a given length
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def sanitize_text_input(text, max_length=255):
    """Sanitiza inputs de texto para prevenir XSS y limitar longitud"""
    if not text:
        return ""
    # Escapar HTML para prevenir XSS
    sanitized = html.escape(str(text).strip())
    # Limitar longitud
    return sanitized[:max_length]


def validate_email(email):
    """Valida formato de email básico"""
    if not email:
        return False
    # Regex básico para email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_phone(phone):
    """Valida que el teléfono contenga solo números, espacios, guiones y paréntesis"""
    if not phone:
        return True  # El teléfono es opcional
    # Permitir solo números, espacios, guiones, paréntesis y el símbolo +
    phone_pattern = r'^[0-9\s\-\+\(\)]+$'
    return re.match(phone_pattern, phone) is not None


# open mysql server credentials file
with open(get_path('db_credentials.txt'), 'r') as file:
    lines = file.readlines()
    db_user = lines[0].strip()
    db_pass = lines[1].strip()



db_config = {
    'host': '127.0.0.1',
    'user': db_user,
    'password': db_pass,
    #'password': 'goU0oLgYwsc4JXiA_',
    'database': 'emar'
}



def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn




if __name__ == '__main__':
    app.run(debug=True)

#WELCOME / INFORMATION / CONSENT / SOCIODEMO / TRAUMATIC / CANNABIS / SNS / IDEAS REF / SALIENCIA / OPEN Q / thanks

@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/info')
def info():
    return render_template('information.html')

@app.route('/consent')
def consent():
    return render_template('consent.html')

@app.route('/submit-consent', methods=['POST'])
def submit_consent():
    # Code to handle consent submission
    # Redirect to next part of the study or show a confirmation message
    return redirect(url_for('sociodemo'))

@app.route('/sociodemo')
def sociodemo():
    participant_id = generate_random_string()
    # Store the participant ID in session for later use
    session["participant_id"] = participant_id
    session.permanent = True



    return render_template('sociodemo.html')

@app.route('/submit-sociodemo', methods=['POST'])
def submit_sociodemo():
    participant_id = session["participant_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extracting and sanitizing form data
        name = sanitize_text_input(request.form.get('name', ''), max_length=255)
        age = request.form.get('age', '')
        sex = sanitize_text_input(request.form.get('sex', ''), max_length=50)
        education_level = sanitize_text_input(request.form.get('education', ''), max_length=100)
        country_of_origin = sanitize_text_input(request.form.get('country', ''), max_length=100)
        years_in_uruguay = request.form.get('years_in_uruguay', '')
        if years_in_uruguay == '':
            years_in_uruguay = -1
        residence = sanitize_text_input(request.form.get('residence', ''), max_length=100)
        email = request.form.get('email', '').strip()
        phone = sanitize_text_input(request.form.get('phone', ''), max_length=100)
        ejer_sino = sanitize_text_input(request.form.get('ejerSN', ''), max_length=50)
        ejer_freq = sanitize_text_input(request.form.get('ejercicio-freq', ''), max_length=50)

        # Validaciones
        if not name:
            return 'El nombre es requerido.', 400
        
        if not validate_email(email):
            return 'El email no tiene un formato válido.', 400
        
        if not validate_phone(phone):
            return 'El teléfono contiene caracteres no válidos.', 400
        
        # Sanitizar email
        email = sanitize_text_input(email, max_length=255)

        # Insert data into the database
        sql = """INSERT INTO sociodemographic_data
                    (participant_id, name, age, sex, education_level, country_of_origin,
                    years_in_uruguay, residence, ejer_sino, ejer_freq, email, phone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (participant_id, name, age, sex, education_level, country_of_origin, years_in_uruguay, residence, ejer_sino, ejer_freq, email, phone))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('texp'))
    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'


@app.route('/texp')
def texp():
    return render_template('traumatic_experiences.html')

@app.route('/submit-texp', methods=['POST'])
def submit_texp():
    participant_id = session["participant_id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()    
        nQuest = 36
        q_responses = [request.form.get("q"+str(i)) for i in range(1,nQuest+1)]
        q_responses.insert(0,participant_id)

        q_strings = ["q_" + str(i) for i in range(1,nQuest+1)]
        q_strings = ",".join(q_strings)
        
        format_strings = ["%s" for i in range(0,nQuest+1)]
        format_strings = ",".join(format_strings)

        # Insert data into the database
        sql = "INSERT INTO traumatic_experiences_responses \n (participant_id, " +  q_strings + """)
                VALUES (""" + format_strings  + ")"
        cursor.execute(sql, tuple(q_responses))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('cannabis_qst'))

    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'


@app.route('/cannabis_qst')
def cannabis_qst():
    return render_template('cannabis_questionnaire.html')

@app.route('/submit-cq', methods=['POST'])
def submit_cq():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()    

        participant_id = session["participant_id"]

        # Extracting form data
        nQuest = 20
        q_responses = []
        
        for i in range(1, nQuest+1):
            response = request.form.get("q"+str(i), "")
            
            # Sanitizar campos de texto libre
            if i == 2:  # q2: edad (number input)
                # Validar que sea un número válido
                try:
                    age = int(response) if response else 0
                    if age < 0 or age > 120:
                        return 'Edad no válida. Debe estar entre 0 y 120.', 400
                    q_responses.append(str(age))
                except ValueError:
                    return 'La edad debe ser un número válido.', 400
            elif i == 20:  # q20: campo de texto libre "Otros"
                # Sanitizar texto libre
                sanitized = sanitize_text_input(response, max_length=500)
                q_responses.append(sanitized)
            else:
                # Otros campos son radio buttons, pero sanitizamos por seguridad
                q_responses.append(sanitize_text_input(response, max_length=50))
        
        q_responses.insert(0, participant_id)

        q_strings = ["q_" + str(i) for i in range(1,nQuest+1)]
        q_strings = ",".join(q_strings)

        format_strings = ["%s" for i in range(0,nQuest+1)]
        format_strings = ",".join(format_strings)

        # Insert data into the database
        sql = "INSERT INTO cannabis_questionnaire_responses \n (participant_id, " +  q_strings + """)
                VALUES (""" + format_strings + ")"
        cursor.execute(sql, tuple(q_responses))
        conn.commit()        
        cursor.close()
        conn.close()
        return redirect(url_for('sns_questionnaire'))

    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'

@app.route('/sns-questionnaire')
def sns_questionnaire():
    return render_template('sns_questionnaire.html')


@app.route('/submit-sns', methods=['POST'])
def submit_sns():
    participant_id = session["participant_id"]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()    

        
        # Extracting form data
        nQuest = 20
        q_responses = [request.form.get("q"+str(i)) for i in range(1,nQuest+1)]
        q_responses.insert(0, participant_id)

        # Continue extracting other fields as per your form
        q_strings = ["q_" + str(i)  for i in range(1,nQuest+1)]
        q_strings = ",".join(q_strings)

        format_strings = ["%s" for i in range(0,nQuest+1)]
        format_strings = ",".join(format_strings)

        # Insert data into the database
        sql = "INSERT INTO sns_questionnaire_responses \n (participant_id, " +  q_strings + """)
                VALUES (""" + format_strings + ")"
        cursor.execute(sql, tuple(q_responses))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('ideas'))

    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'


@app.route('/ideas')
def ideas():
    return render_template('ref_ideas.html')


@app.route('/submit-ideas', methods=['POST'])
def submit_ideas():


    try:
        conn = get_db_connection()
        cursor = conn.cursor()    

        participant_id = session["participant_id"]

        # Extracting form data

        nQuest = 34
        q_responses = [request.form.get("q"+str(i)) for i in range(1,nQuest+1)]
        q_responses.insert(0,participant_id)
        
        q_vf = [request.form.get( "q"+str(i)+"vof" ) for i in range(1,nQuest+1)]
        
        q_responses = q_responses + q_vf
        
        print(q_responses)
        
        # Continue extracting other fields as per your form
        q_strings = ["q_" + str(i) for i in range(1,nQuest+1)]
        q_strings = ",".join(q_strings)
        
        qvf_strings = ["q" + str(i) + "vof" for i in range(1,nQuest+1)]
        qvf_strings = ",".join(qvf_strings)

        format_strings = ["%s" for i in range(0,(2*nQuest)+1)]
        format_strings = ",".join(format_strings)
                
        # Insert data into the database
        sql = "INSERT INTO self_reference_ideas_responses \n (participant_id, " +  q_strings + ", " + qvf_strings  + """)
                VALUES (""" + format_strings + ")"
        cursor.execute(sql, tuple(q_responses))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('saliencia_questionnaire'))

    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'



@app.route('/saliencia-questionnaire')
def saliencia_questionnaire():
    return render_template('saliencia.html')

@app.route('/submit-saliencia', methods=['POST'])
def submit_saliencia_questionnaire():

    participant_id = session["participant_id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()    

        # Extracting form data - 29 questions
        nQuest = 29
        q_responses = [request.form.get("q"+str(i)) for i in range(1,nQuest+1)]
        q_responses.insert(0,participant_id)

        format_strings = ["%s" for i in range(0,nQuest+1)]
        format_strings = ",".join(format_strings)

        # Continue extracting other fields as per your form
        q_strings = ["q_" + str(i) for i in range(1,nQuest+1)]
        q_strings = ",".join(q_strings)
        # Insert data into the database
        sql = "INSERT INTO saliency_scale_responses \n (participant_id, " +  q_strings + """)
                VALUES (""" + format_strings  + ")"
        cursor.execute(sql, tuple(q_responses))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('open'))
    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'



@app.route('/open')
def open():
    return render_template('open.html')


def allowed_file(filename):
    """Check if the file has one of the allowed extensions and MIME types."""
    allowed_extension = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    allowed_mime = magic.from_file(filename, mime=True) in ['audio/wav', 'video/webm', 'audio/mp4', 'audio/webm', 'audio/ogg', 'audio/vorbis', 'audio/opus','video/mp4', 'application/octet-stream']


    return allowed_extension and allowed_mime




@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    response = {"success": False}
    try:
        participant_id = session["participant_id"]

        for key in request.files:
            audio_file = request.files[key]
            if audio_file and audio_file.filename:
                # Sanitizar nombre de archivo con secure_filename
                original_filename = secure_filename(audio_file.filename)
                print(f"Processing file: {original_filename}")
                
                # Verificar que el archivo tenga extensión
                if '.' not in original_filename:
                    response["error"] = "Archivo sin extensión válida"
                    break
                
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                
                # Verificar extensión permitida
                if file_extension not in ALLOWED_EXTENSIONS:
                    response["error"] = f"Extensión no permitida: {file_extension}"
                    break
                
                if not participant_id:
                    participant_id = generate_random_string()
                
                # Sanitizar el key también
                safe_key = sanitize_text_input(key, max_length=20)
                new_filename = f"{participant_id}_{safe_key}.{file_extension}"
                temp_path = os.path.join(get_path('temp/'), new_filename)
                
                audio_file.save(temp_path)  # Temporarily save file
                
                if allowed_file(temp_path):  # Check MIME type
                    final_path = os.path.join(get_path('data/audio/'), new_filename)
                    os.rename(temp_path, final_path)
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()                            
                        cursor.execute("INSERT INTO audio_files (filename, q_id, participant_id) VALUES (%s, %s, %s)", (new_filename, safe_key, participant_id))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        response["success"] = True
                    except Error as e:
                        print("Error while connecting to MySQL", e)
                        # Limpiar archivo si falla la BD
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        return jsonify({"success": False, "error": "Failed to save to database"})

                else:
                    os.remove(temp_path)  # Remove temp file if not allowed
                    response["error"] = "Invalid file type"
                    break
            else:
                response["error"] = "Invalid file extension or no file found"
                break
    except Exception as e:
        print(f"Error in upload_audio: {str(e)}")
        response["error"] = "Error al procesar el archivo"

    return jsonify(response)

@app.route('/gracias', methods=['GET'])
def gracias():
    return render_template('gracias.html')



@app.route('/og_image.png', methods=['GET'])
def og_image():
    return send_file('static/img/og_image.png')   


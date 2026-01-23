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
    'database': 'canna_emar'
}



def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn


def validate_participant_id(participant_id):
    """Valida que el participant_id exista en la base de datos de ronda 1"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar el participant_id en la tabla de ronda 1
        sql = "SELECT participant_id, name FROM sociodemographic_data_ronda1 WHERE participant_id = %s"
        cursor.execute(sql, (participant_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return True, result[1]  # Retorna True y el nombre del participante
        else:
            return False, None
    except Error as e:
        print(f"Error validating participant_id: {e}")
        return False, None


def get_participant_data_ronda1(participant_id):
    """Obtiene los datos del participante de Ronda 1 para pre-llenar el formulario"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar los datos del participante en la tabla de ronda 1
        sql = """SELECT name, age, sex, education_level, country_of_origin, 
                        residence, email, phone 
                 FROM sociodemographic_data_ronda1 
                 WHERE participant_id = %s"""
        cursor.execute(sql, (participant_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            # Convertir tupla a diccionario
            # Orden: name, age, sex, education_level, country_of_origin, residence, email, phone
            name, age, sex, education_level, country_of_origin, residence, email, phone = result
            
            # Procesar el campo sex si tiene "Prefiero autodescribirme: texto"
            sex_value = sex or ''
            prefiero_text = ''
            if sex_value and 'Prefiero autodescribirme' in sex_value:
                if ':' in sex_value:
                    parts = sex_value.split(':', 1)
                    sex_value = 'Prefiero autodescribirme'
                    prefiero_text = parts[1].strip()
                else:
                    sex_value = 'Prefiero autodescribirme'
            
            return {
                'name': name or '',
                'age': age or '',
                'sex': sex_value,
                'prefiero_text': prefiero_text,
                'education_level': education_level or '',
                'country_of_origin': country_of_origin or '',
                'residence': residence or '',
                'email': email or '',
                'phone': phone or ''
            }
        else:
            return None
    except Error as e:
        print(f"Error getting participant data: {e}")
        return None




if __name__ == '__main__':
    app.run(debug=True)

#WELCOME / INFORMATION / CONSENT / SOCIODEMO / IPAQ / CANNABIS / SNS / IDEAS REF / SALIENCIA / OPEN Q / thanks
# (TRAUMATIC EXPERIENCES QUESTIONNAIRE REMOVED FROM FLOW)

@app.route('/')
def welcome():
    # Capturar participant_id del URL (ej: /?pid=ABC123)
    pid = request.args.get('pid', '').strip()
    
    # Si viene pid en URL, validarlo y guardarlo en sesión
    if pid:
        is_valid, participant_name = validate_participant_id(pid)
        if is_valid:
            session['participant_id'] = pid
            session['participant_name'] = participant_name
            session['pid_validated'] = True
            session.permanent = True
            return render_template('welcome.html', pid_from_url=True, participant_name=participant_name)
        else:
            # PID inválido
            return render_template('welcome.html', pid_from_url=True, pid_invalid=True)
    
    # Si no viene pid, verificar si ya está en sesión
    if session.get('pid_validated'):
        participant_name = session.get('participant_name', '')
        return render_template('welcome.html', pid_from_url=True, participant_name=participant_name)
    
    # Si no hay pid, mostrar modal para pedirlo
    return render_template('welcome.html', pid_from_url=False)


@app.route('/validate-pid', methods=['POST'])
def validate_pid():
    """Valida el participant_id ingresado manualmente"""
    pid = request.form.get('pid', '').strip()
    
    if not pid:
        return jsonify({'valid': False, 'error': 'Por favor ingresa tu código de participante'})
    
    is_valid, participant_name = validate_participant_id(pid)
    
    if is_valid:
        session['participant_id'] = pid
        session['participant_name'] = participant_name
        session['pid_validated'] = True
        session.permanent = True
        return jsonify({'valid': True, 'participant_name': participant_name})
    else:
        return jsonify({'valid': False, 'error': 'Código de participante no encontrado. Por favor verifica el código.'})


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
    # El participant_id ya debe estar en la sesión (validado en welcome)
    if 'participant_id' not in session or not session.get('pid_validated'):
        # Si no está validado, redirigir a welcome
        return redirect(url_for('welcome'))
    
    participant_id = session.get('participant_id')
    participant_name = session.get('participant_name', '')
    
    # Cargar datos de Ronda 1 para pre-llenar el formulario
    existing_data = get_participant_data_ronda1(participant_id)
    
    return render_template('sociodemo.html', 
                         participant_name=participant_name,
                         existing_data=existing_data)

@app.route('/submit-sociodemo', methods=['POST'])
def submit_sociodemo():
    participant_id = session["participant_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extracting and sanitizing basic demographic data
        name = sanitize_text_input(request.form.get('name', ''), max_length=255)
        age = request.form.get('age', '')
        sex = sanitize_text_input(request.form.get('sex', ''), max_length=50)
        prefiero_text = sanitize_text_input(request.form.get('prefiero-text', ''), max_length=100)
        education_level = sanitize_text_input(request.form.get('education', ''), max_length=100)
        country_of_origin = sanitize_text_input(request.form.get('country', ''), max_length=100)
        residence = sanitize_text_input(request.form.get('residence', ''), max_length=100)
        email = request.form.get('email', '').strip()
        phone = sanitize_text_input(request.form.get('phone', ''), max_length=100)

        # Health mental history - familiares (checkboxes)
        fam_hermano = 1 if request.form.get('fam_hermano') else 0
        fam_padre = 1 if request.form.get('fam_padre') else 0
        fam_madre = 1 if request.form.get('fam_madre') else 0
        fam_abuelo = 1 if request.form.get('fam_abuelo') else 0
        fam_ninguno = 1 if request.form.get('fam_ninguno') else 0

        # Psicofármacos
        psicofarmacos = sanitize_text_input(request.form.get('psicofarmacos', ''), max_length=10)
        tiempo_psicofarmacos = sanitize_text_input(request.form.get('tiempo_psicofarmacos', ''), max_length=50)
        
        # Tipos de psicofármacos (checkboxes)
        tipo_antidepresivos = 1 if request.form.get('tipo_antidepresivos') else 0
        tipo_ansioliticos = 1 if request.form.get('tipo_ansioliticos') else 0
        tipo_neurolepticos = 1 if request.form.get('tipo_neurolepticos') else 0
        tipo_reguladores = 1 if request.form.get('tipo_reguladores') else 0

        # Consultas y diagnósticos
        emergencia = sanitize_text_input(request.form.get('emergencia', ''), max_length=10)
        internacion = sanitize_text_input(request.form.get('internacion', ''), max_length=10)
        diagnostico = sanitize_text_input(request.form.get('diagnostico', ''), max_length=10)

        # Tipos de diagnóstico (checkboxes)
        diag_psicosis = 1 if request.form.get('diag_psicosis') else 0
        diag_inducido = 1 if request.form.get('diag_inducido') else 0
        diag_esquizofrenia = 1 if request.form.get('diag_esquizofrenia') else 0
        diag_bipolar = 1 if request.form.get('diag_bipolar') else 0
        diag_ansiedad = 1 if request.form.get('diag_ansiedad') else 0
        diag_depresion = 1 if request.form.get('diag_depresion') else 0
        diag_esquizotipica = 1 if request.form.get('diag_esquizotipica') else 0
        diag_esquizoide = 1 if request.form.get('diag_esquizoide') else 0

        # Validaciones
        if not name:
            return 'El nombre es requerido.', 400
        
        if not validate_email(email):
            return 'El email no tiene un formato válido.', 400
        
        if not validate_phone(phone):
            return 'El teléfono contiene caracteres no válidos.', 400
        
        # Sanitizar email
        email = sanitize_text_input(email, max_length=255)
        
        # Combinar sexo con texto personalizado si aplica
        if sex == "Prefiero autodescribirme" and prefiero_text:
            sex = f"Prefiero autodescribirme: {prefiero_text}"

        # Insert data into the database
        sql = """INSERT INTO sociodemographic_data
                    (participant_id, name, age, sex, education_level, country_of_origin, residence, email, phone,
                     fam_hermano, fam_padre, fam_madre, fam_abuelo, fam_ninguno,
                     psicofarmacos, tiempo_psicofarmacos, 
                     tipo_antidepresivos, tipo_ansioliticos, tipo_neurolepticos, tipo_reguladores,
                     emergencia, internacion, diagnostico,
                     diag_psicosis, diag_inducido, diag_esquizofrenia, diag_bipolar, 
                     diag_ansiedad, diag_depresion, diag_esquizotipica, diag_esquizoide)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (participant_id, name, age, sex, education_level, country_of_origin, residence, email, phone,
                            fam_hermano, fam_padre, fam_madre, fam_abuelo, fam_ninguno,
                            psicofarmacos, tiempo_psicofarmacos,
                            tipo_antidepresivos, tipo_ansioliticos, tipo_neurolepticos, tipo_reguladores,
                            emergencia, internacion, diagnostico,
                            diag_psicosis, diag_inducido, diag_esquizofrenia, diag_bipolar,
                            diag_ansiedad, diag_depresion, diag_esquizotipica, diag_esquizoide))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('ipaq'))  # Redirige al cuestionario IPAQ
    except Error as e:
        print("Error while connecting to MySQL", e)
        return 'Failed to submit data.'


# =============================================================================
# TRAUMATIC EXPERIENCES QUESTIONNAIRE - DISABLED
# Uncomment these routes if you want to restore the traumatic experiences questionnaire
# =============================================================================
#
# @app.route('/texp')
# def texp():
#     return render_template('traumatic_experiences.html')
#
# @app.route('/submit-texp', methods=['POST'])
# def submit_texp():
#     participant_id = session["participant_id"]
#
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()    
#         nQuest = 36
#         q_responses = [request.form.get("q"+str(i)) for i in range(1,nQuest+1)]
#         q_responses.insert(0,participant_id)
#
#         q_strings = ["q_" + str(i) for i in range(1,nQuest+1)]
#         q_strings = ",".join(q_strings)
#         
#         format_strings = ["%s" for i in range(0,nQuest+1)]
#         format_strings = ",".join(format_strings)
#
#         # Insert data into the database
#         sql = "INSERT INTO traumatic_experiences_responses \n (participant_id, " +  q_strings + """)
#                 VALUES (""" + format_strings  + ")"
#         cursor.execute(sql, tuple(q_responses))
#         
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return redirect(url_for('cannabis_qst'))
#
#     except Error as e:
#         print("Error while connecting to MySQL", e)
#         return 'Failed to submit data.'
#
# =============================================================================


@app.route('/ipaq')
def ipaq():
    return render_template('ipaq.html')

@app.route('/submit-ipaq', methods=['POST'])
def submit_ipaq():
    participant_id = session["participant_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Actividades intensas
        dias_intensa = request.form.get('dias_intensa', 0)
        horas_intensa = request.form.get('horas_intensa', 0)
        minutos_intensa = request.form.get('minutos_intensa', 0)

        # Actividades moderadas
        dias_moderada = request.form.get('dias_moderada', 0)
        horas_moderada = request.form.get('horas_moderada', 0)
        minutos_moderada = request.form.get('minutos_moderada', 0)

        # Caminar
        dias_caminar = request.form.get('dias_caminar', 0)
        horas_caminar = request.form.get('horas_caminar', 0)
        minutos_caminar = request.form.get('minutos_caminar', 0)

        # Estar sentado
        horas_sentado = request.form.get('horas_sentado', 0)
        minutos_sentado = request.form.get('minutos_sentado', 0)

        # Validar que sean números
        try:
            dias_intensa = int(dias_intensa)
            horas_intensa = int(horas_intensa)
            minutos_intensa = int(minutos_intensa)
            dias_moderada = int(dias_moderada)
            horas_moderada = int(horas_moderada)
            minutos_moderada = int(minutos_moderada)
            dias_caminar = int(dias_caminar)
            horas_caminar = int(horas_caminar)
            minutos_caminar = int(minutos_caminar)
            horas_sentado = int(horas_sentado)
            minutos_sentado = int(minutos_sentado)
        except ValueError:
            return 'Todos los campos deben ser números válidos.', 400

        # Insert data into the database
        sql = """INSERT INTO ipaq_responses
                    (participant_id, 
                     dias_intensa, horas_intensa, minutos_intensa,
                     dias_moderada, horas_moderada, minutos_moderada,
                     dias_caminar, horas_caminar, minutos_caminar,
                     horas_sentado, minutos_sentado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (participant_id, 
                            dias_intensa, horas_intensa, minutos_intensa,
                            dias_moderada, horas_moderada, minutos_moderada,
                            dias_caminar, horas_caminar, minutos_caminar,
                            horas_sentado, minutos_sentado))
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


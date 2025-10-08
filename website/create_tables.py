#create MySQL tables

import mysql.connector
from mysql.connector import Error


#DB = Sequel.connect('mysql2://digital_user:goU0oLgYwsc4JXiA@localhost/digital')

#open mysql server credentials file
with open('db_credentials.txt', 'r') as file:
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



def create_tables():
    conn = None
    try:
        # Establishing a connection to the database
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Connected to the database")

            cursor = conn.cursor()
            
            # Audio files table
            cursor.execute(''' CREATE TABLE IF NOT EXISTS audio_files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(100),
                        q_id VARCHAR(10),
                        participant_id VARCHAR(255),
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''')
            print("Table audio_files created successfully")


            # Sociodemographic data from Round 1 (for reference/validation)
            cursor.execute(''' CREATE TABLE IF NOT EXISTS sociodemographic_data_ronda1 (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                participant_id VARCHAR(100),
                                name VARCHAR(255),
                                age INT,
                                sex VARCHAR(50),
                                education_level VARCHAR(100),
                                country_of_origin VARCHAR(100),
                                years_in_uruguay INT,
                                residence VARCHAR(100),
                                email VARCHAR(255),
                                phone VARCHAR(100),
                                ejer_sino VARCHAR(50),
                                ejer_freq VARCHAR(50),
                                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            print("Table sociodemographic_data_ronda1 created successfully (reference)")


            # Sociodemographic data table - ROUND 2 - UPDATED with new fields
            cursor.execute(''' CREATE TABLE IF NOT EXISTS sociodemographic_data (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                participant_id VARCHAR(100),
                                name VARCHAR(255),
                                age INT,
                                sex VARCHAR(255),
                                education_level VARCHAR(100),
                                country_of_origin VARCHAR(100),
                                residence VARCHAR(100),
                                email VARCHAR(255),
                                phone VARCHAR(100),
                                
                                -- Familiares con diagnóstico de salud mental
                                fam_hermano TINYINT(1) DEFAULT 0,
                                fam_padre TINYINT(1) DEFAULT 0,
                                fam_madre TINYINT(1) DEFAULT 0,
                                fam_abuelo TINYINT(1) DEFAULT 0,
                                fam_ninguno TINYINT(1) DEFAULT 0,
                                
                                -- Psicofármacos
                                psicofarmacos VARCHAR(10),
                                tiempo_psicofarmacos VARCHAR(50),
                                tipo_antidepresivos TINYINT(1) DEFAULT 0,
                                tipo_ansioliticos TINYINT(1) DEFAULT 0,
                                tipo_neurolepticos TINYINT(1) DEFAULT 0,
                                tipo_reguladores TINYINT(1) DEFAULT 0,
                                
                                -- Consultas y diagnósticos
                                emergencia VARCHAR(10),
                                internacion VARCHAR(10),
                                diagnostico VARCHAR(10),
                                
                                -- Tipos de diagnóstico
                                diag_psicosis TINYINT(1) DEFAULT 0,
                                diag_inducido TINYINT(1) DEFAULT 0,
                                diag_esquizofrenia TINYINT(1) DEFAULT 0,
                                diag_bipolar TINYINT(1) DEFAULT 0,
                                diag_ansiedad TINYINT(1) DEFAULT 0,
                                diag_depresion TINYINT(1) DEFAULT 0,
                                diag_esquizotipica TINYINT(1) DEFAULT 0,
                                diag_esquizoide TINYINT(1) DEFAULT 0,
                                
                                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            print("Table sociodemographic_data created successfully")


            # IPAQ responses table - NEW
            cursor.execute(''' CREATE TABLE IF NOT EXISTS ipaq_responses (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                participant_id VARCHAR(255),
                                
                                -- Actividades intensas
                                dias_intensa INT,
                                horas_intensa INT,
                                minutos_intensa INT,
                                
                                -- Actividades moderadas
                                dias_moderada INT,
                                horas_moderada INT,
                                minutos_moderada INT,
                                
                                -- Caminar
                                dias_caminar INT,
                                horas_caminar INT,
                                minutos_caminar INT,
                                
                                -- Estar sentado
                                horas_sentado INT,
                                minutos_sentado INT,
                                
                                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            print("Table ipaq_responses created successfully")


            # Cannabis questionnaire responses
            nQuest = 20
            q_strings = ["q_" + str(i) + " VARCHAR(500)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS cannabis_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')
            print("Table cannabis_questionnaire_responses created successfully")


            # Traumatic experiences responses (DISABLED but kept for historical data)
            nQuest = 36
            q_strings = ["q_" + str(i) + " VARCHAR(10)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS traumatic_experiences_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')
            print("Table traumatic_experiences_responses created successfully (DISABLED IN FLOW)")


            # Saliency scale responses
            nQuest = 29
            q_strings = ["q_" + str(i) + " VARCHAR(10)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS saliency_scale_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')
            print("Table saliency_scale_responses created successfully")


            # Self-reference ideas responses
            nQuest = 34
            q_strings = ["q_" + str(i) + " VARCHAR(1),\n q" + str(i) + "vof VARCHAR(1)"  for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS self_reference_ideas_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')
            print("Table self_reference_ideas_responses created successfully")


            # SNS questionnaire responses
            nQuest = 20
            q_strings = ["q_" + str(i) + " VARCHAR(255)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS sns_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')
            print("Table sns_questionnaire_responses created successfully")

            conn.commit()
            cursor.close()
            print("\n✅ All tables created successfully!")
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_tables()

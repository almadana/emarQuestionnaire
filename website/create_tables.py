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
    'database': 'canna_emar'
}



def create_tables():
    conn = None
    try:
        # Establishing a connection to the database
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Connected to the database")

            cursor = conn.cursor()
            cursor.execute(''' CREATE TABLE IF NOT EXISTS audio_files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(100),
                        q_id VARCHAR(10),
                        participant_id VARCHAR(255),
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''')

            print("Table  created successfully")


            cursor.execute(''' CREATE TABLE sociodemographic_data (
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


            nQuest = 20
            q_strings = ["q_" + str(i) + " VARCHAR(15)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)


            # Create table for cannabis questionnaire responses
            cursor.execute(''' CREATE TABLE IF NOT EXISTS cannabis_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')


            nQuest = 36
            q_strings = ["q_" + str(i) + " VARCHAR(10)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS traumatic_experiences_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')


            nQuest = 29
            q_strings = ["q_" + str(i) + " VARCHAR(10)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS saliency_scale_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')


            nQuest = 34
            q_strings = ["q_" + str(i) + " VARCHAR(1),\n q" + str(i) + "vof VARCHAR(1)"  for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS self_reference_ideas_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')


            nQuest = 20
            q_strings = ["q_" + str(i) + " VARCHAR(255)" for i in range(1,nQuest+1)]
            q_strings = ",\n".join(q_strings)

            cursor.execute(''' CREATE TABLE IF NOT EXISTS sns_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    participant_id VARCHAR(255), ''' + q_strings + ''')''')

            conn.commit()
            cursor.close()
            print("Tables created successfully")
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"Error: {e}")
    finally:
        print("Algo no anduvo bien!")
        if conn and conn.is_connected():
            conn.close()

create_tables()

#create MySQL tables

import mysql.connector
from mysql.connector import Error


#DB = Sequel.connect('mysql2://digital_user:goU0oLgYwsc4JXiA@localhost/digital')

db_config = {
    'host': 'mysql2://localhost/digital',
    'user': 'digital_user',
    'password': 'goU0oLgYwsc4JXiA',
    'database': 'canna_emar'
}


def create_tables():
    try:
        # Establishing a connection to the database
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(''' CREATE TABLE IF NOT EXISTS audio_files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(100),
                        question_id INT,
                        user_id INT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''')


            cursor.execute(''' CREATE TABLE sociodemographic_data (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                name VARCHAR(255),
                                age INT,
                                sex VARCHAR(50),
                                education_level VARCHAR(100),
                                country_of_origin VARCHAR(100),
                                years_in_uruguay INT,
                                residence VARCHAR(100),
                                email VARCHAR(255),
                                phone VARCHAR(100)''')

            # Create table for cannabis questionnaire responses
            cursor.execute(''' CREATE TABLE IF NOT EXISTS cannabis_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    question_1_response VARCHAR(255),
                    question_2_response VARCHAR(255),
                    question_3_response VARCHAR(255),
                    -- Add more fields as per your questionnaire
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')


            cursor.execute(''' CREATE TABLE IF NOT EXISTS traumatic_experiences_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    question_1_response INT,
                    question_2_response INT,
                    question_3_response INT,
                    -- Add more fields as per your questionnaire
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            cursor.execute(''' CREATE TABLE IF NOT EXISTS saliency_scale_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    question_1_response VARCHAR(10),
                    question_2_response VARCHAR(10),
                    -- Add fields as per your questionnaire
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            cursor.execute(''' CREATE TABLE IF NOT EXISTS self_reference_ideas_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    question_1_response VARCHAR(10),
                    question_2_response VARCHAR(10),
                    -- Add fields as per your questionnaire
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS sns_questionnaire_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    question_1_response VARCHAR(10),
                    question_2_response VARCHAR(10),
                    -- Add fields as per your questionnaire
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')



            conn.commit()
            cursor.close()
            print("Tables created successfully")
        else:
            print("Failed to connect to the database")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

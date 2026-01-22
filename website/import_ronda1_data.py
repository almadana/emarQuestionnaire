#!/usr/bin/env python3
"""
Script para copiar datos de sociodemographic_data a sociodemographic_data_ronda1

EXPLICACIÓN:
- Copia los datos de la tabla 'sociodemographic_data' (datos actuales/ronda 1)
- A la tabla 'sociodemographic_data_ronda1' (tabla de referencia para validación)
- Ambas tablas están en la MISMA base de datos: 'emar'

Uso:
    python3 import_ronda1_data.py
"""

import mysql.connector
from mysql.connector import Error

# Leer credenciales
with open('db_credentials.txt', 'r') as file:
    lines = file.readlines()
    db_user = lines[0].strip()
    db_pass = lines[1].strip()

# Configuración de base de datos
DATABASE_NAME = 'emar'  # Ajusta si tu base se llama diferente

def import_data():
    """Copia datos de sociodemographic_data a sociodemographic_data_ronda1"""
    conn = None
    try:
        print(f"Conectando a base de datos: {DATABASE_NAME}...")
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user=db_user,
            password=db_pass,
            database=DATABASE_NAME
        )
        
        if conn.is_connected():
            print("✓ Conectado\n")
            cursor = conn.cursor()
            
            # Verificar que existe la tabla origen
            cursor.execute("SHOW TABLES LIKE 'sociodemographic_data'")
            if not cursor.fetchone():
                print("❌ Error: No se encontró la tabla 'sociodemographic_data'")
                return
            
            # Leer datos
            print("Leyendo datos de sociodemographic_data...")
            cursor.execute("""
                SELECT participant_id, name, age, sex, education_level, 
                       country_of_origin, years_in_uruguay, residence, 
                       email, phone, ejer_sino, ejer_freq
                FROM sociodemographic_data
            """)
            
            rows = cursor.fetchall()
            print(f"✓ Encontrados {len(rows)} participantes\n")
            
            if len(rows) == 0:
                print("⚠️  No hay datos para copiar")
                return
            
            # Insertar en tabla de referencia
            print("Copiando a sociodemographic_data_ronda1...")
            sql = """INSERT INTO sociodemographic_data_ronda1 
                     (participant_id, name, age, sex, education_level, 
                      country_of_origin, years_in_uruguay, residence, 
                      email, phone, ejer_sino, ejer_freq)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            count = 0
            for row in rows:
                try:
                    cursor.execute(sql, row)
                    count += 1
                except Error as e:
                    if 'Duplicate entry' in str(e):
                        print(f"⚠️  {row[0]} ya existe, saltando...")
                    else:
                        print(f"⚠️  Error con {row[0]}: {e}")
            
            conn.commit()
            print(f"✓ Copiados {count} participantes\n")
            
            # Mostrar ejemplos
            print("Ejemplos de participant_ids copiados:")
            cursor.execute("SELECT participant_id, name FROM sociodemographic_data_ronda1 LIMIT 5")
            examples = cursor.fetchall()
            for pid, name in examples:
                print(f"  - {pid}: {name}")
            
            cursor.close()
            print("\n✅ Copia completada!")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
        print("Conexión cerrada.")


if __name__ == "__main__":
    print("=" * 70)
    print("COPIA DE DATOS: sociodemographic_data → sociodemographic_data_ronda1")
    print("=" * 70)
    print()
    print(f"Base de datos: {DATABASE_NAME}")
    print(f"Tabla origen:  sociodemographic_data")
    print(f"Tabla destino: sociodemographic_data_ronda1")
    print()
    
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
        print()
        import_data()
    else:
        print("Cancelado.")

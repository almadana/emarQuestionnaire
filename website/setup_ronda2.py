#!/usr/bin/env python3
"""
Script para configurar la migración de Ronda 1 a Ronda 2

PROCESO:
1. En canna_emar (Ronda 1):
   - Mantener sociodemographic_data (con datos históricos)
   - Vaciar todas las demás tablas

2. En emar (Ronda 2):
   - Copiar sociodemographic_data de canna_emar a sociodemographic_data_ronda1
   - Crear/actualizar sociodemographic_data con estructura nueva de Ronda 2
"""

import mysql.connector
from mysql.connector import Error

# Leer credenciales
with open('db_credentials.txt', 'r') as file:
    lines = file.readlines()
    db_user = lines[0].strip()
    db_pass = lines[1].strip()

# Configuración de bases de datos
DB_RONDA1 = 'canna_emar'  # Base de datos de Ronda 1
DB_RONDA2 = 'emar'        # Base de datos de Ronda 2

# Tabla que se preserva en Ronda 1
TABLA_PRESERVAR = 'sociodemographic_data'

# Tablas que se crean en Ronda 2 (según create_tables.py)
TABLAS_RONDA2 = [
    'audio_files',
    'sociodemographic_data_ronda1',
    'sociodemographic_data',
    'ipaq_responses',
    'cannabis_questionnaire_responses',
    'traumatic_experiences_responses',
    'saliency_scale_responses',
    'self_reference_ideas_responses',
    'sns_questionnaire_responses'
]


def get_all_tables(cursor, database):
    """Obtiene lista de todas las tablas en una base de datos"""
    cursor.execute(f"SHOW TABLES FROM {database}")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def count_records(cursor, table):
    """Cuenta registros en una tabla"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]
    except:
        return 0


def vaciar_tabla(cursor, table):
    """Vacía una tabla (DELETE FROM)"""
    try:
        cursor.execute(f"DELETE FROM {table}")
        return True
    except Error as e:
        print(f"  ❌ Error vaciando {table}: {e}")
        return False


def copiar_sociodemo_ronda1_a_ronda2(cursor_ronda1, cursor_ronda2):
    """Copia datos de sociodemographic_data de Ronda 1 a sociodemographic_data_ronda1 en Ronda 2"""
    print("\n📋 Paso 1: Copiando datos sociodemográficos de Ronda 1...")
    
    # Leer datos de Ronda 1
    cursor_ronda1.execute("""
        SELECT participant_id, name, age, sex, education_level, 
               country_of_origin, years_in_uruguay, residence, 
               email, phone, ejer_sino, ejer_freq
        FROM sociodemographic_data
    """)
    
    rows = cursor_ronda1.fetchall()
    print(f"   ✓ Encontrados {len(rows)} participantes en Ronda 1")
    
    if len(rows) == 0:
        print("   ⚠️  No hay datos para copiar")
        return 0
    
    # Verificar que existe la tabla destino
    cursor_ronda2.execute("SHOW TABLES LIKE 'sociodemographic_data_ronda1'")
    if not cursor_ronda2.fetchone():
        print("   ❌ La tabla sociodemographic_data_ronda1 no existe en Ronda 2")
        print("      Ejecuta primero: python3 create_tables.py")
        return 0
    
    # Insertar datos
    sql = """INSERT INTO sociodemographic_data_ronda1 
             (participant_id, name, age, sex, education_level, 
              country_of_origin, years_in_uruguay, residence, 
              email, phone, ejer_sino, ejer_freq)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    count = 0
    skipped = 0
    for row in rows:
        try:
            cursor_ronda2.execute(sql, row)
            count += 1
        except Error as e:
            if 'Duplicate entry' in str(e):
                skipped += 1
            else:
                print(f"   ⚠️  Error con {row[0]}: {e}")
    
    print(f"   ✓ Copiados {count} participantes nuevos")
    if skipped > 0:
        print(f"   ⏭️  Saltados {skipped} participantes (ya existían)")
    
    return count


def limpiar_ronda1(cursor, database):
    """Limpia todas las tablas de Ronda 1 excepto sociodemographic_data"""
    print(f"\n🧹 Paso 2: Limpiando tablas en {database} (excepto {TABLA_PRESERVAR})...")
    
    # Obtener todas las tablas
    tables = get_all_tables(cursor, database)
    
    if TABLA_PRESERVAR not in tables:
        print(f"   ⚠️  La tabla {TABLA_PRESERVAR} no existe")
        return
    
    # Contar registros antes
    records_before = count_records(cursor, TABLA_PRESERVAR)
    print(f"   📊 Registros en {TABLA_PRESERVAR}: {records_before} (se preservan)")
    
    # Vaciar otras tablas
    tables_to_clean = [t for t in tables if t != TABLA_PRESERVAR]
    
    if not tables_to_clean:
        print("   ✓ No hay otras tablas para limpiar")
        return
    
    print(f"   📋 Tablas a limpiar: {len(tables_to_clean)}")
    for table in tables_to_clean:
        records = count_records(cursor, table)
        if records > 0:
            print(f"   🗑️  Limpiando {table} ({records} registros)...")
            if vaciar_tabla(cursor, table):
                print(f"      ✓ {table} limpiada")
        else:
            print(f"   ⏭️  {table} ya está vacía")


def verificar_estructura_sociodemo_ronda2(cursor):
    """Verifica y actualiza la estructura de sociodemographic_data en Ronda 2"""
    print(f"\n🔧 Paso 3: Verificando estructura de sociodemographic_data en Ronda 2...")
    
    # Verificar si la tabla existe
    cursor.execute("SHOW TABLES LIKE 'sociodemographic_data'")
    if not cursor.fetchone():
        print("   ⚠️  La tabla sociodemographic_data no existe")
        print("      Ejecuta: python3 create_tables.py")
        return False
    
    # Obtener columnas existentes
    cursor.execute("DESCRIBE sociodemographic_data")
    existing_columns = {row[0] for row in cursor.fetchall()}
    
    # Campos nuevos que deben existir
    required_new_fields = [
        'fam_hermano', 'fam_padre', 'fam_madre', 'fam_abuelo', 'fam_ninguno',
        'psicofarmacos', 'tiempo_psicofarmacos',
        'tipo_antidepresivos', 'tipo_ansioliticos', 'tipo_neurolepticos', 'tipo_reguladores',
        'emergencia', 'internacion', 'diagnostico',
        'diag_psicosis', 'diag_inducido', 'diag_esquizofrenia', 'diag_bipolar',
        'diag_ansiedad', 'diag_depresion', 'diag_esquizotipica', 'diag_esquizoide'
    ]
    
    missing_fields = [f for f in required_new_fields if f not in existing_columns]
    
    if missing_fields:
        print(f"   ⚠️  Faltan {len(missing_fields)} campos nuevos")
        print("      Ejecuta: python3 create_tables.py para crear la estructura completa")
        return False
    else:
        print("   ✓ La tabla tiene todos los campos necesarios de Ronda 2")
        return True


def main():
    """Función principal"""
    print("=" * 70)
    print("🔧 CONFIGURACIÓN DE MIGRACIÓN RONDA 1 → RONDA 2")
    print("=" * 70)
    print()
    print(f"📖 Base de datos Ronda 1: {DB_RONDA1}")
    print(f"📝 Base de datos Ronda 2: {DB_RONDA2}")
    print()
    print("Este script realizará:")
    print("  1. Copiar sociodemographic_data de Ronda 1 a sociodemographic_data_ronda1 en Ronda 2")
    print(f"  2. Limpiar todas las tablas en {DB_RONDA1} excepto sociodemographic_data")
    print("  3. Verificar estructura de sociodemographic_data en Ronda 2")
    print()
    print("⚠️  ADVERTENCIA: Se eliminarán datos de tablas en Ronda 1 (excepto sociodemographic_data)")
    print()
    
    respuesta = input("¿Continuar? (s/n): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
        print("❌ Cancelado.")
        return
    
    conn_ronda1 = None
    conn_ronda2 = None
    
    try:
        # Conectar a Ronda 1
        print(f"\n📖 Conectando a {DB_RONDA1}...")
        conn_ronda1 = mysql.connector.connect(
            host='127.0.0.1',
            user=db_user,
            password=db_pass,
            database=DB_RONDA1
        )
        cursor_ronda1 = conn_ronda1.cursor()
        print("✓ Conectado a Ronda 1")
        
        # Conectar a Ronda 2
        print(f"\n📝 Conectando a {DB_RONDA2}...")
        conn_ronda2 = mysql.connector.connect(
            host='127.0.0.1',
            user=db_user,
            password=db_pass,
            database=DB_RONDA2
        )
        cursor_ronda2 = conn_ronda2.cursor()
        print("✓ Conectado a Ronda 2")
        
        # Paso 1: Copiar datos
        copiados = copiar_sociodemo_ronda1_a_ronda2(cursor_ronda1, cursor_ronda2)
        conn_ronda2.commit()
        
        # Paso 2: Limpiar Ronda 1
        limpiar_ronda1(cursor_ronda1, DB_RONDA1)
        conn_ronda1.commit()
        
        # Paso 3: Verificar estructura Ronda 2
        verificar_estructura_sociodemo_ronda2(cursor_ronda2)
        
        print("\n" + "=" * 70)
        print("✅ PROCESO COMPLETADO")
        print("=" * 70)
        print(f"\n📊 Resumen:")
        print(f"   - Participantes copiados: {copiados}")
        print(f"   - Base {DB_RONDA1}: sociodemographic_data preservada, otras tablas limpiadas")
        print(f"   - Base {DB_RONDA2}: lista para Ronda 2")
        print()
        print("⚠️  IMPORTANTE: Verifica que la estructura de sociodemographic_data")
        print("   en Ronda 2 tenga todos los campos nuevos. Si falta, ejecuta:")
        print("   python3 create_tables.py")
        
    except Error as e:
        print(f"\n❌ Error: {e}")
        if conn_ronda1:
            conn_ronda1.rollback()
        if conn_ronda2:
            conn_ronda2.rollback()
    finally:
        if conn_ronda1 and conn_ronda1.is_connected():
            cursor_ronda1.close()
            conn_ronda1.close()
        if conn_ronda2 and conn_ronda2.is_connected():
            cursor_ronda2.close()
            conn_ronda2.close()
        print("\n🔌 Conexiones cerradas")


if __name__ == "__main__":
    main()


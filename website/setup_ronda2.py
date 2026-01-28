#!/usr/bin/env python3
"""
Script para configurar la migración de Ronda 1 a Ronda 2

PROCESO (todo en la base emar):
1. Copiar sociodemographic_data a sociodemographic_data_ronda1 (para validación)
2. Vaciar TODAS las tablas (incluyendo sociodemographic_data)
3. Solo se preserva sociodemographic_data_ronda1 (para validación de participant_ids)
4. Las tablas quedan listas para empezar Ronda 2 desde cero
"""

import mysql.connector
from mysql.connector import Error

# Leer credenciales
with open('db_credentials.txt', 'r') as file:
    lines = file.readlines()
    db_user = lines[0].strip()
    db_pass = lines[1].strip()

# Configuración de base de datos
DATABASE = 'emar'  # Única base de datos

# Tabla que se preserva (solo para validación)
TABLA_PRESERVAR = 'sociodemographic_data_ronda1'

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
    cursor.execute("SHOW TABLES")
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


def copiar_sociodemo_a_ronda1(cursor):
    """Copia datos de sociodemographic_data a sociodemographic_data_ronda1 (en la misma base)"""
    print("\n📋 Paso 1: Copiando datos sociodemográficos a tabla de referencia...")
    
    # Verificar que existe la tabla origen
    cursor.execute("SHOW TABLES LIKE 'sociodemographic_data'")
    if not cursor.fetchone():
        print("   ❌ La tabla sociodemographic_data no existe")
        return 0
    
    # Leer datos
    cursor.execute("""
        SELECT participant_id, name, age, sex, education_level, 
               country_of_origin, years_in_uruguay, residence, 
               email, phone, ejer_sino, ejer_freq
        FROM sociodemographic_data
    """)
    
    rows = cursor.fetchall()
    print(f"   ✓ Encontrados {len(rows)} participantes")
    
    if len(rows) == 0:
        print("   ⚠️  No hay datos para copiar")
        return 0
    
    # Verificar que existe la tabla destino
    cursor.execute("SHOW TABLES LIKE 'sociodemographic_data_ronda1'")
    if not cursor.fetchone():
        print("   ❌ La tabla sociodemographic_data_ronda1 no existe")
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
            cursor.execute(sql, row)
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


def limpiar_otras_tablas(cursor, database):
    """Limpia todas las tablas excepto sociodemographic_data_ronda1 (que se usa para validación)"""
    print(f"\n🧹 Paso 2: Limpiando todas las tablas excepto sociodemographic_data_ronda1...")
    
    # Obtener todas las tablas
    tables = get_all_tables(cursor, database)
    
    # Solo preservar sociodemographic_data_ronda1 (tabla de referencia para validación)
    tables_to_preserve = ['sociodemographic_data_ronda1']
    tables_to_clean = [t for t in tables if t not in tables_to_preserve]
    
    if not tables_to_clean:
        print("   ✓ No hay tablas para limpiar")
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
    
    # Verificar que sociodemographic_data_ronda1 se preservó
    records_ronda1 = count_records(cursor, 'sociodemographic_data_ronda1')
    print(f"\n   ✅ Tabla preservada: sociodemographic_data_ronda1 ({records_ronda1} registros)")


def verificar_estructura_sociodemo_ronda2(cursor):
    """Verifica y actualiza la estructura de sociodemographic_data para Ronda 2"""
    print(f"\n🔧 Paso 3: Verificando estructura de sociodemographic_data para Ronda 2...")
    
    # Verificar si la tabla existe
    cursor.execute("SHOW TABLES LIKE 'sociodemographic_data'")
    if not cursor.fetchone():
        print("   ⚠️  La tabla sociodemographic_data no existe")
        print("      Ejecuta: python3 create_tables.py")
        return False
    
    # Obtener columnas existentes
    cursor.execute("DESCRIBE sociodemographic_data")
    existing_columns = {row[0] for row in cursor.fetchall()}
    
    # Campos nuevos que deben existir para Ronda 2
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
        print(f"   ⚠️  Faltan {len(missing_fields)} campos nuevos de Ronda 2")
        print("      Campos faltantes:", ', '.join(missing_fields[:5]), '...' if len(missing_fields) > 5 else '')
        print("      Ejecuta: python3 create_tables.py para actualizar la estructura")
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
    print(f"📊 Base de datos: {DATABASE}")
    print()
    print("Este script realizará:")
    print("  1. Copiar sociodemographic_data a sociodemographic_data_ronda1 (para validación)")
    print(f"  2. Limpiar TODAS las tablas en {DATABASE} excepto sociodemographic_data_ronda1")
    print("  3. Verificar estructura de sociodemographic_data para Ronda 2")
    print()
    print("⚠️  ADVERTENCIA: Se eliminarán TODOS los datos de todas las tablas")
    print("   Solo se preservará: sociodemographic_data_ronda1 (para validación)")
    print()
    
    respuesta = input("¿Continuar? (s/n): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
        print("❌ Cancelado.")
        return
    
    conn = None
    
    try:
        # Conectar a la base de datos
        print(f"\n📊 Conectando a {DATABASE}...")
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user=db_user,
            password=db_pass,
            database=DATABASE
        )
        cursor = conn.cursor()
        print("✓ Conectado")
        
        # Paso 1: Copiar datos
        copiados = copiar_sociodemo_a_ronda1(cursor)
        conn.commit()
        
        # Paso 2: Limpiar otras tablas
        limpiar_otras_tablas(cursor, DATABASE)
        conn.commit()
        
        # Paso 3: Verificar estructura
        estructura_ok = verificar_estructura_sociodemo_ronda2(cursor)
        
        print("\n" + "=" * 70)
        print("✅ PROCESO COMPLETADO")
        print("=" * 70)
        print(f"\n📊 Resumen:")
        print(f"   - Participantes copiados a sociodemographic_data_ronda1: {copiados}")
        print(f"   - Base {DATABASE}: Solo sociodemographic_data_ronda1 preservada, todas las demás tablas limpiadas")
        if not estructura_ok:
            print()
            print("⚠️  IMPORTANTE: La estructura de sociodemographic_data necesita actualizarse")
            print("   Ejecuta: python3 create_tables.py para agregar los campos de Ronda 2")
        
    except Error as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        print("\n🔌 Conexión cerrada")


if __name__ == "__main__":
    main()


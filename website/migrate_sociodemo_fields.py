#!/usr/bin/env python3
"""
Script para agregar los campos nuevos de Ronda 2 a la tabla sociodemographic_data existente
"""

import mysql.connector
from mysql.connector import Error

# Leer credenciales
with open('db_credentials.txt', 'r') as file:
    lines = file.readlines()
    db_user = lines[0].strip()
    db_pass = lines[1].strip()

db_config = {
    'host': '127.0.0.1',
    'user': db_user,
    'password': db_pass,
    'database': 'emar'
}


def check_column_exists(cursor, table_name, column_name):
    """Verifica si una columna existe en la tabla"""
    try:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{db_config['database']}' 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        print(f"Error verificando columna {column_name}: {e}")
        return False


def migrate_table():
    """Agrega los campos nuevos de Ronda 2 a sociodemographic_data"""
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("✅ Conectado a la base de datos")
            cursor = conn.cursor()

            # Verificar que la tabla existe
            cursor.execute("SHOW TABLES LIKE 'sociodemographic_data'")
            if not cursor.fetchone():
                print("❌ La tabla sociodemographic_data no existe.")
                return False

            # Contar registros existentes
            cursor.execute("SELECT COUNT(*) FROM sociodemographic_data")
            records = cursor.fetchone()[0]
            print(f"📊 Registros existentes: {records} (se preservarán)\n")

            # Campos nuevos que deben agregarse
            new_fields = [
                # Familiares con diagnóstico de salud mental
                ('fam_hermano', 'TINYINT(1) DEFAULT 0', 'Familiares - Hermano/a'),
                ('fam_padre', 'TINYINT(1) DEFAULT 0', 'Familiares - Padre'),
                ('fam_madre', 'TINYINT(1) DEFAULT 0', 'Familiares - Madre'),
                ('fam_abuelo', 'TINYINT(1) DEFAULT 0', 'Familiares - Abuelo/a'),
                ('fam_ninguno', 'TINYINT(1) DEFAULT 0', 'Familiares - Ninguno'),
                
                # Psicofármacos
                ('psicofarmacos', 'VARCHAR(10)', 'Psicofármacos - Sí/No'),
                ('tiempo_psicofarmacos', 'VARCHAR(50)', 'Psicofármacos - Tiempo'),
                ('tipo_antidepresivos', 'TINYINT(1) DEFAULT 0', 'Tipo - Antidepresivos'),
                ('tipo_ansioliticos', 'TINYINT(1) DEFAULT 0', 'Tipo - Ansiolíticos'),
                ('tipo_neurolepticos', 'TINYINT(1) DEFAULT 0', 'Tipo - Neurolépticos'),
                ('tipo_reguladores', 'TINYINT(1) DEFAULT 0', 'Tipo - Reguladores'),
                
                # Consultas y diagnósticos
                ('emergencia', 'VARCHAR(10)', 'Consulta - Emergencia'),
                ('internacion', 'VARCHAR(10)', 'Consulta - Internación'),
                ('diagnostico', 'VARCHAR(10)', 'Diagnóstico - Sí/No'),
                
                # Tipos de diagnóstico
                ('diag_psicosis', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Psicosis'),
                ('diag_inducido', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Inducido'),
                ('diag_esquizofrenia', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Esquizofrenia'),
                ('diag_bipolar', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Bipolar'),
                ('diag_ansiedad', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Ansiedad'),
                ('diag_depresion', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Depresión'),
                ('diag_esquizotipica', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Esquizotípica'),
                ('diag_esquizoide', 'TINYINT(1) DEFAULT 0', 'Diagnóstico - Esquizoide'),
            ]

            # Verificar y agregar campos faltantes
            fields_added = 0
            for field_name, field_type, description in new_fields:
                if not check_column_exists(cursor, 'sociodemographic_data', field_name):
                    try:
                        # Agregar columna al final (antes de date)
                        # Primero obtenemos la última columna antes de date
                        cursor.execute("""
                            SELECT COLUMN_NAME 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = %s 
                            AND TABLE_NAME = 'sociodemographic_data' 
                            AND ORDINAL_POSITION < (
                                SELECT ORDINAL_POSITION 
                                FROM INFORMATION_SCHEMA.COLUMNS 
                                WHERE TABLE_SCHEMA = %s 
                                AND TABLE_NAME = 'sociodemographic_data' 
                                AND COLUMN_NAME = 'date'
                            )
                            ORDER BY ORDINAL_POSITION DESC 
                            LIMIT 1
                        """, (db_config['database'], db_config['database']))
                        result = cursor.fetchone()
                        after_column = result[0] if result else 'phone'
                        
                        alter_sql = f"""
                            ALTER TABLE sociodemographic_data 
                            ADD COLUMN {field_name} {field_type} 
                            AFTER {after_column}
                        """
                        cursor.execute(alter_sql)
                        print(f"  ✅ Agregado: {field_name} ({description})")
                        fields_added += 1
                    except Error as e:
                        print(f"  ❌ Error agregando {field_name}: {e}")
                else:
                    print(f"  ⏭️  Ya existe: {field_name}")

            # Verificar si el campo 'sex' necesita ser expandido
            cursor.execute("""
                SELECT CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'sociodemographic_data' 
                AND COLUMN_NAME = 'sex'
            """, (db_config['database'],))
            result = cursor.fetchone()
            if result and result[0] and result[0] < 255:
                try:
                    cursor.execute("ALTER TABLE sociodemographic_data MODIFY COLUMN sex VARCHAR(255)")
                    print("  ✅ Actualizado: campo 'sex' expandido a VARCHAR(255)")
                except Error as e:
                    print(f"  ❌ Error actualizando campo 'sex': {e}")

            # Commit los cambios
            conn.commit()
            
            # Verificar que los registros se mantuvieron
            cursor.execute("SELECT COUNT(*) FROM sociodemographic_data")
            records_after = cursor.fetchone()[0]
            
            if fields_added > 0:
                print(f"\n✅ Migración completada: {fields_added} campos agregados")
            else:
                print("\n✅ La tabla ya tiene todos los campos necesarios")
            
            if records != records_after:
                print(f"\n⚠️  ADVERTENCIA: El número de registros cambió!")
                print(f"   Antes: {records}, Después: {records_after}")
            else:
                print(f"\n✅ Integridad de datos verificada: {records_after} registros preservados")
            
            cursor.close()
            return True
        else:
            print("❌ No se pudo conectar a la base de datos")
            return False
            
    except Error as e:
        print(f"❌ Error durante la migración: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("\n🔌 Conexión cerrada")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Migración de Campos - sociodemographic_data")
    print("   Agregando campos de Ronda 2")
    print("=" * 60)
    
    success = migrate_table()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Migración completada exitosamente")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ La migración falló. Revisa los errores arriba.")
        print("=" * 60)


# 📋 Instrucciones - Sistema Ronda 2

## 🎯 Objetivo

Este sistema permite que participantes de la **Ronda 1** del estudio continúen con la **Ronda 2**, usando su `participant_id` existente para vincular sus datos entre ambas rondas.

---

## 🔑 Características Principales

### 1. **Validación de Participant ID**
- Los participantes deben tener un `participant_id` de la Ronda 1
- El sistema valida que el ID exista en la base de datos antes de permitir continuar
- Se muestra el nombre del participante para confirmar su identidad

### 2. **Dos formas de ingresar el Participant ID**

#### **Opción A: URL personalizada** ✅ Recomendada
```
https://emar.cicea.uy/?pid=ABC12345
```

**Ventajas:**
- Experiencia más fluida para el participante
- No necesita recordar/escribir su código
- Reduce errores de tipeo

**Cómo generar enlaces:**
```python
# Ejemplo para generar enlaces personalizados
base_url = "https://emar.cicea.uy/?pid="
participants = [
    ("ABC12345", "Juan Pérez", "juan@example.com"),
    ("XYZ67890", "María García", "maria@example.com"),
    # ...
]

for pid, name, email in participants:
    link = f"{base_url}{pid}"
    print(f"Enviar a {name} ({email}): {link}")
```

#### **Opción B: Modal de ingreso manual**
- Si el participante entra sin el parámetro `pid` en el URL
- Se muestra un modal pidiendo el código
- El sistema valida el código contra la base de datos

---

## 🗄️ Estructura de Base de Datos

### **Tabla de Referencia: `sociodemographic_data_ronda1`**
Contiene los datos básicos de participantes de Ronda 1 para validación:

```sql
CREATE TABLE sociodemographic_data_ronda1 (
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
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Tabla Nueva: `sociodemographic_data` (Ronda 2)**
Estructura expandida con 22 campos adicionales de salud mental:
- Familiares con diagnósticos (5 campos)
- Psicofármacos (6 campos)
- Consultas y diagnósticos (11 campos)

### **Tabla Nueva: `ipaq_responses`**
Cuestionario de actividad física IPAQ (11 campos de datos)

---

## 🚀 Configuración Inicial

### **Paso 1: Crear las tablas**
```bash
cd /home/perezoso/Dropbox/projects/emar/webRichard/website
python3 create_tables.py
```

### **Paso 2: Importar datos de Ronda 1**

**Antes de ejecutar**, ajusta el nombre de la base de datos en `import_ronda1_data.py`:
```python
db_config_ronda1 = {
    'host': '127.0.0.1',
    'user': db_user,
    'password': db_pass,
    'database': 'emar_ronda1'  # ← Ajusta este nombre
}
```

Luego ejecuta:
```bash
python3 import_ronda1_data.py
```

Este script:
1. Lee datos de `sociodemographic_data` de Ronda 1
2. Los copia a `sociodemographic_data_ronda1` en Ronda 2
3. Permite validar participant_ids

---

## 📨 Envío de Invitaciones

### **Opción 1: Enlaces personalizados por email**

**Plantilla de email:**
```
Asunto: Invitación a participar en Ronda 2 - Estudio Cannabis

Hola [NOMBRE],

Gracias por haber participado en la primera ronda de nuestro estudio 
sobre los efectos del cannabis. Te invitamos a participar en la segunda 
ronda, que nos ayudará a comprender mejor los cambios a lo largo del tiempo.

Tu enlace personalizado:
https://emar.cicea.uy/?pid=[PARTICIPANT_ID]

La encuesta tomará aproximadamente 25-30 minutos.

Si tienes alguna duda, contacta a: psirjrodriguez@gmail.com

Saludos,
Equipo de Investigación
```

### **Opción 2: Email general con código**

Si prefieres no usar enlaces personalizados:
```
Tu código de participante es: [PARTICIPANT_ID]
Ingresa a: https://emar.cicea.uy
```

---

## 🔒 Seguridad y Validación

### **Protecciones implementadas:**

1. **Validación en backend:**
   - El `participant_id` debe existir en `sociodemographic_data_ronda1`
   - Se verifica antes de permitir acceso al cuestionario

2. **Sesiones seguras:**
   - El ID se guarda en la sesión de Flask
   - Tiempo de expiración: 2 horas
   - Flag `pid_validated` para confirmar validación

3. **Sanitización de datos:**
   - Todos los inputs sanitizados con `sanitize_text_input()`
   - Validación de email y teléfono
   - Protección XSS implementada

4. **Redirección automática:**
   - Si un usuario intenta acceder a `/sociodemo` sin validación
   - Se redirige automáticamente a `/` para validar su ID

---

## 🔄 Flujo Completo del Sistema

```
1. Usuario recibe link: https://emar.cicea.uy/?pid=ABC123
   ↓
2. Sistema captura PID del URL
   ↓
3. Validación contra sociodemographic_data_ronda1
   ↓
   SI ES VÁLIDO:
   - Guarda en sesión: participant_id, participant_name, pid_validated=True
   - Muestra: "¡Bienvenid@ de nuevo, [NOMBRE]!"
   - Botón "¡Quiero participar!" habilitado
   ↓
   SI NO ES VÁLIDO:
   - Muestra error: "Código no válido"
   ↓
4. Usuario hace clic en "¡Quiero participar!"
   ↓
5. Info → Consent → Sociodemográfico → IPAQ → Cannabis → SNS → Ideas → Saliencia → Audio → Gracias
   ↓
6. Todos los datos se guardan con el mismo participant_id
```

### **Flujo alternativo (sin PID en URL):**

```
1. Usuario entra a: https://emar.cicea.uy
   ↓
2. Sistema detecta que no hay ?pid=...
   ↓
3. Muestra modal: "Ingresa tu código de participante"
   ↓
4. Usuario ingresa código manualmente
   ↓
5. Sistema valida vía AJAX (/validate-pid)
   ↓
6. Si es válido → Recarga página con sesión validada
   ↓
7. Continúa flujo normal
```

---

## 📊 Consultas SQL Útiles

### **Ver participantes validados en Ronda 2:**
```sql
SELECT DISTINCT participant_id, name 
FROM sociodemographic_data 
ORDER BY date DESC;
```

### **Comparar datos entre rondas:**
```sql
SELECT 
    r1.participant_id,
    r1.name,
    r1.age as edad_r1,
    r2.age as edad_r2,
    r1.date as fecha_r1,
    r2.date as fecha_r2
FROM sociodemographic_data_ronda1 r1
LEFT JOIN sociodemographic_data r2 ON r1.participant_id = r2.participant_id;
```

### **Ver quién ha completado ambas rondas:**
```sql
SELECT 
    r1.participant_id,
    r1.name,
    COUNT(DISTINCT r2.id) as completado_r2
FROM sociodemographic_data_ronda1 r1
LEFT JOIN sociodemographic_data r2 ON r1.participant_id = r2.participant_id
GROUP BY r1.participant_id, r1.name
ORDER BY r1.name;
```

---

## ⚠️ Troubleshooting

### **Problema: "Código de participante no encontrado"**
**Solución:**
1. Verificar que se ejecutó `import_ronda1_data.py`
2. Verificar que la tabla `sociodemographic_data_ronda1` tiene datos:
   ```sql
   SELECT COUNT(*) FROM sociodemographic_data_ronda1;
   ```
3. Verificar que el participant_id está bien escrito

### **Problema: Modal no aparece**
**Solución:**
- Verificar que no hay parámetro `?pid=` en el URL
- Revisar la consola del navegador (F12) para errores JavaScript

### **Problema: Sesión expira muy rápido**
**Solución:**
Ajustar en `app.py`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=3)
```

---

## 📝 Notas Importantes

1. **No se generan nuevos IDs:** El sistema usa el participant_id de Ronda 1
2. **Base de datos separadas:** Ronda 1 y Ronda 2 están en bases diferentes
3. **Tabla de referencia:** `sociodemographic_data_ronda1` es solo para validación
4. **Nuevos campos:** Ronda 2 tiene 22 campos adicionales sobre salud mental
5. **IPAQ:** Nueva sección completa de actividad física

---

## 📞 Contacto

Para cualquier problema técnico o consulta sobre el sistema:
- **Email:** psirjrodriguez@gmail.com
- **Equipo:** Richard Rodríguez, Álvaro Cabana, Paul Ruiz, Juan Fco. Rodriguez Testal

---

**Última actualización:** Octubre 2025  
**Versión del sistema:** 2.0


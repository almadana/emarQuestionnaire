# 🔒 Correcciones de Seguridad - Sanitización de Inputs

## Resumen Ejecutivo

Se identificaron y corrigieron **5 vulnerabilidades** en los formularios del sistema:
- **3 en formulario sociodemográfico** (name, email, phone)
- **2 en formulario de cannabis** (edad, campo "otros")
- **1 en upload de archivos** (path traversal)

Todos los formularios restantes (traumatic experiences, SNS, ref_ideas, saliencia) **solo usan radio buttons y están seguros**.

---

## Vulnerabilidades Identificadas y Corregidas

### 1. **Cross-Site Scripting (XSS) - CRÍTICO**

#### Problema Original:
Los campos de texto libre no se sanitizaban, permitiendo inyección de código malicioso:

```python
# ❌ ANTES (VULNERABLE)
name = request.form['name']
email = request.form['email']
phone = request.form['phone']
```

Un atacante podría enviar:
- `<script>alert('XSS')</script>` en el nombre
- `<img src=x onerror=alert('hack')>` en cualquier campo
- Código malicioso que se ejecutaría al visualizar los datos

#### Solución Implementada:
```python
# ✅ DESPUÉS (SEGURO)
name = sanitize_text_input(request.form.get('name', ''), max_length=255)
email = sanitize_text_input(email, max_length=255)
phone = sanitize_text_input(request.form.get('phone', ''), max_length=100)
```

**Función de sanitización:**
```python
def sanitize_text_input(text, max_length=255):
    """Sanitiza inputs de texto para prevenir XSS y limitar longitud"""
    if not text:
        return ""
    # Escapar HTML para prevenir XSS
    sanitized = html.escape(str(text).strip())
    # Limitar longitud
    return sanitized[:max_length]
```

Ahora todos los caracteres HTML se escapan:
- `<` se convierte en `&lt;`
- `>` se convierte en `&gt;`
- `"` se convierte en `&quot;`
- Etc.

---

### 2. **Validación de Email - IMPORTANTE**

#### Problema Original:
```python
# ❌ ANTES (SIN VALIDACIÓN)
email = request.form['email']
```

Aceptaba cualquier string como email.

#### Solución Implementada:
```python
# ✅ DESPUÉS (CON VALIDACIÓN)
email = request.form.get('email', '').strip()

if not validate_email(email):
    return 'El email no tiene un formato válido.', 400

email = sanitize_text_input(email, max_length=255)
```

**Función de validación:**
```python
def validate_email(email):
    """Valida formato de email básico"""
    if not email:
        return False
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None
```

---

### 3. **Validación de Teléfono - IMPORTANTE**

#### Problema Original:
```python
# ❌ ANTES (SIN VALIDACIÓN)
phone = request.form['phone']
```

Aceptaba cualquier contenido.

#### Solución Implementada:
```python
# ✅ DESPUÉS (CON VALIDACIÓN)
phone = sanitize_text_input(request.form.get('phone', ''), max_length=100)

if not validate_phone(phone):
    return 'El teléfono contiene caracteres no válidos.', 400
```

**Función de validación:**
```python
def validate_phone(phone):
    """Valida que el teléfono contenga solo números, espacios, guiones y paréntesis"""
    if not phone:
        return True  # El teléfono es opcional
    phone_pattern = r'^[0-9\s\-\+\(\)]+$'
    return re.match(phone_pattern, phone) is not None
```

---

### 4. **Campo de Edad sin Validación (Formulario Cannabis) - IMPORTANTE**

#### Problema Original:
**Ubicación:** `cannabis_questionnaire.html` línea 47, procesado en `app.py` submit-cq

```html
<!-- ❌ ANTES - Sin validación -->
<input type="number" required name="q2">
```

Un atacante podría enviar edad negativa o imposible.

#### Solución Implementada:
```python
# ✅ AHORA - Validación estricta (0-120 años)
if i == 2:  # q2: edad
    try:
        age = int(response) if response else 0
        if age < 0 or age > 120:
            return 'Edad no válida. Debe estar entre 0 y 120.', 400
        q_responses.append(str(age))
    except ValueError:
        return 'La edad debe ser un número válido.', 400
```

---

### 5. **Campo de Texto Libre "Otros" (Formulario Cannabis) - IMPORTANTE**

#### Problema Original:
**Ubicación:** `cannabis_questionnaire.html` línea 303

```html
<!-- ❌ ANTES - Campo de texto sin sanitizar -->
<input type="text" id="otro" name="q20">
```

Vulnerable a XSS.

#### Solución Implementada:
```python
# ✅ AHORA - Sanitizado con límite de 500 caracteres
elif i == 20:  # q20: campo de texto libre "Otros"
    sanitized = sanitize_text_input(response, max_length=500)
    q_responses.append(sanitized)
```

---

### 6. **Path Traversal en Upload de Archivos - CRÍTICO**

#### Problema Original:
```python
# ❌ ANTES (VULNERABLE A PATH TRAVERSAL)
file_extension = audio_file.filename.rsplit('.', 1)[1].lower()
new_filename = f"{participant_id}_{key}.{file_extension}"
```

Vulnerabilidades:
- IndexError si el archivo no tiene extensión
- No se usa `secure_filename()`
- Un atacante podría enviar: `../../etc/passwd.wav`
- No se valida la extensión antes de guardar

#### Solución Implementada:
```python
# ✅ DESPUÉS (SEGURO)
if audio_file and audio_file.filename:
    # 1. Sanitizar nombre de archivo
    original_filename = secure_filename(audio_file.filename)
    
    # 2. Verificar que tenga extensión
    if '.' not in original_filename:
        response["error"] = "Archivo sin extensión válida"
        break
    
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    
    # 3. Verificar extensión permitida
    if file_extension not in ALLOWED_EXTENSIONS:
        response["error"] = f"Extensión no permitida: {file_extension}"
        break
    
    # 4. Sanitizar el key también
    safe_key = sanitize_text_input(key, max_length=20)
    new_filename = f"{participant_id}_{safe_key}.{file_extension}"
```

**Mejoras adicionales:**
- Limpieza de archivo si falla guardado en BD
- Mejor manejo de errores
- Logs más descriptivos

---

## Funciones de Seguridad Agregadas

### 1. `sanitize_text_input(text, max_length=255)`
- Escapa caracteres HTML
- Limita longitud de texto
- Elimina espacios en blanco

### 2. `validate_email(email)`
- Valida formato de email con regex
- Previene emails malformados

### 3. `validate_phone(phone)`
- Permite solo caracteres válidos en teléfonos
- Es opcional (retorna True si está vacío)

---

## Imports Agregados

```python
import re      # Para expresiones regulares
import html    # Para escapar HTML
```

---

## Casos de Prueba Recomendados

### Test XSS:
```python
# Intentar enviar:
name = "<script>alert('XSS')</script>"
# Debe guardarse como: &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;
```

### Test Email:
```python
# Válidos:
"user@example.com" ✓
"test.user+tag@domain.co.uk" ✓

# Inválidos:
"not-an-email" ✗
"@example.com" ✗
"user@" ✗
```

### Test Phone:
```python
# Válidos:
"+598 99 123 456" ✓
"099-123-456" ✓
"(02) 123-4567" ✓

# Inválidos:
"phone<script>alert(1)</script>" ✗
"ABC-123-DEF" ✗
```

### Test Path Traversal:
```python
# Intentar enviar archivo:
"../../etc/passwd.wav"
# Debe bloquearse o sanitizarse a: "etcpasswd.wav"
```

---

## Recomendaciones Adicionales

### 1. Agregar Flask-WTF para CSRF Protection
```bash
pip install Flask-WTF
```

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

### 2. Agregar Rate Limiting
```bash
pip install Flask-Limiter
```

### 3. Habilitar Logging
Descomentar en app.py:
```python
logging.basicConfig(filename='app.log', level=logging.INFO)
```

### 4. Configurar Headers de Seguridad
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Checklist de Seguridad

- [x] Sanitización de inputs de texto
- [x] Validación de email
- [x] Validación de teléfono
- [x] Protección contra Path Traversal
- [x] Uso de `secure_filename()`
- [x] Límites de longitud en inputs
- [x] Validación de extensiones de archivo
- [ ] Protección CSRF (pendiente)
- [ ] Rate Limiting (pendiente)
- [ ] Headers de seguridad (pendiente)
- [ ] Logging completo (pendiente)

---

## Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/en/2.3.x/utils/#module-werkzeug.security)

---

**Fecha de implementación:** Octubre 2025  
**Última actualización:** 2025-10-08


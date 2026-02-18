# Guía de Configuración de Expanse (Menéame Expandido)

Expanse es una aplicación modular construida sobre Neutral TS. Gran parte de su potencia reside en la integración con Inteligencia Artificial. Para personalizar el comportamiento de los componentes sin modificar el código fuente, se utiliza el archivo `custom.json` en la raíz de cada componente.

**Regla de Oro**: Nunca modifiques `manifest.json` o `schema.json` directamente si quieres mantener la compatibilidad con futuras actualizaciones. Crea siempre un `custom.json`.

---

## Guía de Inicio Local

### 1. Requisitos Previos

*   Python 3.10 o superior.
*   Entorno virtual (recomendado).

### 2. Configuración del Entorno

#### Instalación automática (recomendada)

**Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/FranBarInstance/meneame-expandido/master/bin/install.sh | sh
```

**macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/FranBarInstance/meneame-expandido/master/bin/install-mac.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/FranBarInstance/meneame-expandido/master/bin/install.ps1 | iex
```

Estos instaladores:
- Descargan el último tag.
- Preguntan el directorio de instalación.
- Configuran `.venv` e instalan dependencias.
- Generan `config/.env` y un `SECRET_KEY` aleatorio.
- Crean un usuario inicial (con contraseña mínima de 8 caracteres).
- Preguntan si quieres ejecutar la app al finalizar y muestran la URL final.

#### Linux / macOS
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Windows
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno (PowerShell)
.\.venv\Scripts\Activate.ps1
# O en CMD:
# .\.venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables

#### Linux / macOS
```bash
cp config/.env.example config/.env
```

#### Windows
```powershell
copy config\.env.example config\.env
```

Copia el archivo de ejemplo y configura tu `SECRET_KEY` y las API Keys necesarias para la IA en `config/.env`.

### 4. Ejecución

Para iniciar la aplicación en modo desarrollo:

**Linux / macOS:**
```bash
source .venv/bin/activate
python3 src/run.py
```

**Windows:**
```powershell
# En PowerShell
.\.venv\Scripts\Activate.ps1
python src/run.py
```

La aplicación estará disponible por defecto en `http://localhost:55000`.

### 5. Creación de Usuario (Obligatorio)

Tras la instalación, **es necesario crear al menos un usuario** para acceder a todas las funcionalidades (algunas requieren inicio de sesión).

**Linux / macOS:**
```bash
source .venv/bin/activate
python3 bin/create_user.py "Tu Nombre" "tu@email.com" "tu_password" "1990-01-01"
```

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
python bin/create_user.py "Tu Nombre" "tu@email.com" "tu_password" "1990-01-01"
```

Consulta [bin/README.md](../bin/README.md) para más detalles sobre los argumentos del script.

---

## 1. Configuración de Modelos de IA (`cmp_2000_ai_backend`)

Este componente es el "cerebro" que gestiona las conexiones con los proveedores de IA.

Para configurar tus propios modelos o claves de API, crea `src/component/cmp_2000_ai_backend/custom.json`:

```json
{
    "manifest": {
        "config": {
            "profiles": {
                "mi_openai": {
                    "openai": {
                        "enabled": true,
                        "api_key": "TU_API_KEY_AQUI",
                        "model": "gpt-4o"
                    }
                },
                "mi_ollama_local": {
                    "ollama": {
                        "enabled": true,
                        "api_key": "ollama",
                        "base_url": "http://localhost:11434/v1",
                        "model": "llama3.1"
                    }
                }
            }
        }
    }
}
```

### Proveedores soportados:
- **openai**: Requiere `api_key`.
- **anthropic**: Requiere `api_key`.
- **google**: Requiere `api_key` (Gemini).
- **ollama**: Requiere `base_url` (típicamente `http://localhost:11434/v1`) y el nombre del `model` descargado.

---

## 2. Configuración del Chat de IA (`cmp_6000_aichat`)

Este componente proporciona la interfaz de chat. Puedes configurar qué perfil de modelo usar por defecto y añadir "prompts" predefinidos.

Crea `src/component/cmp_6000_aichat/custom.json`:

```json
{
    "manifest": {
        "config": {
            "default_profile": "mi_ollama_local",
            "prompts": [
                {
                    "id": "asistente_programacion",
                    "name": "Asistente de Código",
                    "prompt": "Eres un experto programador en Python y JavaScript. Responde de forma concisa."
                },
                {
                    "id": "poeta",
                    "name": "Poeta",
                    "prompt": "Responde siempre en verso y con rima."
                }
            ]
        }
    }
}
```

- **default_profile**: Debe coincidir con el nombre de un perfil definido en `cmp_2000_ai_backend`.
- **prompts**: Lista de plantillas que aparecerán en el selector del chat.

---

## 3. Configuración de Resúmenes (`cmp_6000_resumen_expanse`)

Este componente genera resúmenes automáticos de feeds RSS. Puedes personalizar las fuentes de noticias y el comportamiento del resumen.

Crea `src/component/cmp_6000_resumen_expanse/custom.json`:

```json
{
    "manifest": {
        "config": {
            "default_profile": "mi_openai",
            "cache_seconds": 600,
            "prompt": "Resume las siguientes noticias destacando los puntos clave y el sentimiento general. En español.",
            "resumen_urls": {
                "Mis Noticias": "https://mi-portal-favorito.com/rss",
                "Tecnología": "https://www.xataka.com/feed"
            }
        }
    }
}
```

- **default_profile**: Perfil de IA a usar para resumir.
- **cache_seconds**: Cuánto tiempo guardar en caché el resumen generado (para ahorrar tokens/tiempo).
- **prompt**: Instrucciones específicas para la IA sobre cómo debe resumir.
- **resumen_urls**: Diccionario de nombres y URLs de feeds RSS que quieres que aparezcan en la aplicación.

---

## 4. Desarrollo de Nuevas Funcionalidades con IA

Expanse está diseñado para ser expandido mediante agentes de IA. Para pedirle a la IA (como Cursor, Windsurf, o asistentes similares) que cree un nuevo componente, debes proporcionarle un prompt estructurado que le dé contexto sobre la arquitectura de Neutral TS y los recursos disponibles.

### Ejemplo de Prompt para la IA

Un ejemplo efectivo sería:

> Tu tarea es crear el componente `nombre_del_componente`, que debe [descripción de la funcionalidad].
>
> Usa la ruta: `/mi-ruta`
>
> Para realizar esta tarea, consulta:
> - `.agent/skills/manage-component/SKILL.md`
> - `.agent/skills/manage-neutral-templates/SKILL.md`
> - `src/component/cmp_6000_resumen_expanse/*` (como ejemplo de componente dinámico, o cualquier otro)
>
> Define las rutas dinámicamente si es necesario siguiendo el patrón de otros componentes.

El componente `cmp_6000_resumen_expanse` lo ha creado la IA leyendo esta documentación y las instrucciones en [agent.md](../src/component/cmp_6000_resumen_expanse/agent.md)

### Recomendaciones para el Prompt:
1. **Referencia a las Skills**: Indica siempre las rutas a `.agent/skills/` para que la IA sepa qué estándares seguir.
2. **Usa Ejemplos**: Menciona un componente existente similar para que la IA pueda copiar patrones de diseño y estructura.
3. **Contexto de Datos**: Si el componente depende de una API o servicio externo (como RSS), especifica qué librerías usar (ej. `fastfeedparser`).

---

## Consideraciones Generales

1. **Reinicio**: Tras crear o modificar un `custom.json` o añadir un nuevo componente, es recomendable reiniciar el servidor Flask para asegurar que los cambios se cargan correctamente.
2. **Seguridad**: El archivo `custom.json` suele estar incluido en `.gitignore` para evitar subir tus claves de API al repositorio. Comprueba siempre esto antes de hacer un commit.
3. **Persistencia**: Si usas perfiles de IA guardados en el navegador (cookies), estos podrían tener prioridad sobre la configuración estática del `custom.json` en algunos componentes interactivos.

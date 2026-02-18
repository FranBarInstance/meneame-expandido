# Guía de Configuración de Expanse (Menéame Expandido)

Expanse es una aplicación modular construida sobre Neutral TS. Gran parte de su potencia reside en la integración con Inteligencia Artificial. Para personalizar el comportamiento de los componentes sin modificar el código fuente, se utiliza el archivo `custom.json` en la raíz de cada componente.

**Regla de Oro**: Nunca modifiques `manifest.json` o `schema.json` directamente si quieres mantener la compatibilidad con futuras actualizaciones. Crea siempre un `custom.json`.

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

Puedes usar un archivo `agent.md` en la carpeta del componente que quieres crear como referencia para el prompt. Un ejemplo efectivo sería:

> "Tu tarea es crear el componente `src/component/nombre_del_componente`, que debe [descripción de la funcionalidad].
>
> El manifest se encuentra en `src/component/nombre_del_componente/manifest.json`.
>
> Para realizar esta tarea, consulta:
> - `.agent/skills/manage-component/SKILL.md`
> - `.agent/skills/manage-neutral-templates/SKILL.md`
> - `docs/component.md`
> - `src/component/cmp_6000_resumen_expanse/*` (como ejemplo de componente dinámico)
>
> Utiliza `from ai_backend_0yt2sa import AIManager` si necesitas acceder a modelos de IA.
> Define las rutas dinámicamente si es necesario siguiendo el patrón de otros componentes."

### Recomendaciones para el Prompt:
1. **Referencia a las Skills**: Indica siempre las rutas a `.agent/skills/` para que la IA sepa qué estándares seguir.
2. **Usa Ejemplos**: Menciona un componente existente similar para que la IA pueda copiar patrones de diseño y estructura.
3. **Contexto de Datos**: Si el componente depende de una API o servicio externo (como RSS), especifica qué librerías usar (ej. `fastfeedparser`).

---

## Consideraciones Generales

1. **Reinicio**: Tras crear o modificar un `custom.json` o añadir un nuevo componente, es recomendable reiniciar el servidor Flask para asegurar que los cambios se cargan correctamente.
2. **Seguridad**: El archivo `custom.json` suele estar incluido en `.gitignore` para evitar subir tus claves de API al repositorio. Comprueba siempre esto antes de hacer un commit.
3. **Persistencia**: Si usas perfiles de IA guardados en el navegador (cookies), estos podrían tener prioridad sobre la configuración estática del `custom.json` en algunos componentes interactivos.

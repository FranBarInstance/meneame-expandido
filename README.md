# Expanse

**Expanse** es una aplicación de escritorio en desarrollo diseñada para explorar, informar y expandir el ecosistema no oficial que surge del agregador original Menéame, conocido como **Menéame Expandido**.

## ¿Qué es el Menéame Expandido?

El concepto de **Menéame Expandido** describe el fenómeno orgánico de comunidades, clones, agregadores independientes y canales de Telegram que operan fuera del dominio oficial. Este proyecto, bajo el nombre de **Expanse**, busca ofrecer una plataforma para visualizar este universo paralelo, integrando herramientas modernas y capacidades avanzadas.

## Capacidades IA y Agénticas

El objetivo principal de esta aplicación es dotar al usuario de capacidades agénticas basadas en Inteligencia Artificial:
*   **Visualización Inteligente**: Procesamiento y muestra de contenido optimizado mediante IA.
*   **Creación de Componentes**: La IA puede generar nuevos componentes de la aplicación bajo demanda. Puedes pedirle a la IA que cree un componente específico para realizar una tarea determinada dentro del ecosistema de la aplicación.

Para facilitar este desarrollo, el proyecto incluye:
*   **Skills**: Definiciones de habilidades para agentes en `.agent/skills`.
*   **Documentación Técnica**: Guías detalladas en la carpeta `docs/`.

La IA será capaz de crear componentes y funcionalidades para la aplicación bajo demanda leyendo esta documentación.

De hecho, ya lo ha hecho, el componente `cmp_6000_resumen_expanse` lo ha creado la IA leyendo esta documentación y las instrucciones en `agent.md`

## Estado del Proyecto

Actualmente, la aplicación se encuentra en **fase de desarrollo activo**.

> [!WARNING]
> **No ejecutar en servidores**: Esta aplicación está diseñada exclusivamente para uso en **escritorio/local**. Actualmente **no posee un sistema de detección de abusos** para los servicios de IA. Exponerla en un servidor público podría resultar en un consumo descontrolado de tokens. Este problema se abordará en futuras actualizaciones.

## Referencias y Enlaces

*   **Base del Proyecto**: [Neutral TS Starter Py](https://github.com/FranBarInstance/neutral-starter-py)
*   **Motor de Plantillas**: [Neutral TS](https://github.com/FranBarInstance/neutralts)
*   **Documentación de Plantillas**: [Neutral TS Docs](https://franbarinstance.github.io/neutralts-docs/docs/neutralts/doc/)
*   **Configuración de Expanse**: [Guía de configuración (IA, Chat, Resúmenes)](docs/expanse.md)
*   **Índice de Documentación**: [Documentación detallada](docs/README.md)

## Guía de Inicio Local

### 1. Requisitos Previos

*   Python 3.10 o superior.
*   Entorno virtual (recomendado).

### 2. Configuración del Entorno

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables

Copia el archivo de ejemplo y configura tu `SECRET_KEY` y las API Keys necesarias para la IA en `config/.env`:

```bash
cp config/.env.example config/.env
```

### 4. Ejecución

Para iniciar la aplicación en modo desarrollo:

```bash
source .venv/bin/activate
python src/run.py
```

La aplicación estará disponible por defecto en `http://localhost:5000`.

---
*Desarrollado con pasión por la comunidad de Menéame Expandido.*

**Descargo de responsabilidad**: Menéame, Renegados, Mediatice, Tardigram, Killbait y otros sitios mencionados no están asociados con Expanse ni con el desarrollador de esta aplicación y/o sus colaboradores; son proyectos e iniciativas independientes.

Toda la información que procesa y muestra la aplicación es la facilitada por los propios sitios web para tal fin, utilizando canales oficiales de difusión como fuentes RSS.

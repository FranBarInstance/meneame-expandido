
Tu tarea es completar el componente src/component/cmp_6000_resumen_expanse, que genera resúmenes de feeds RSS usando modelos de IA.

El manifest se encuentra en src/component/cmp_6000_resumen_expanse/manifest.json y ya está creado.

Para realizar esta tarea, necesitarás consultar:

.agent/skills/manage-component/SKILL.md
.agent/skills/manage-neutral-templates/SKILL.md
src/component/cmp_6100_rrss_expanse/*

cmp_6100_rrss_expanse es un componente similar que realiza una función distinta, pero puede servirte como ejemplo.

Utiliza from ai_backend_0yt2sa import AIManager para acceder al modelo de src/component/cmp_2000_ai_backend.
Emplea fastfeedparser para analizar (parsear) los feeds RSS.

La idea es obtener la URL con fastfeedparser y enviarla, junto con el prompt, al modelo de IA para que genere un resumen —o lo que el prompt indique—. El prompt se obtiene de la configuración del componente.

Dado que las URLs son configurables —a excepción del menú principal—, el resto de las rutas deben generarse dinámicamente. Puedes ver un ejemplo en:
src/component/cmp_6100_rrss_expanse/__init__.py

Las rutas deben quedar así:

/resumen
/resumen/site/Renegados
/resumen/site/...

Para los elementos del menú, usa los iconos x-icon-ai (para el menú principal) y x-icon-agent (para cada URL de sitio).

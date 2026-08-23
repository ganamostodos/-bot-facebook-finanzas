# Bot de Facebook - Tips de Finanzas Personales

Publica automáticamente un tip diario en tu página de Facebook "Ponche Finanzas".

## Archivos

- `bot.py` — script principal, corre en loop y publica a la hora programada
- `tips.py` — banco de 30 tips (edítalo cuando quieras agregar o cambiar contenido)
- `requirements.txt` — dependencias (solo `requests`)

## Cómo obtener tu FB_PAGE_ID

En el Graph API Explorer (developers.facebook.com/tools/explorer), con tu token
del Usuario del Sistema seleccionado, consulta `me/accounts` — ahí aparece el
`id` de tu página "Ponche Finanzas". Ese es tu `FB_PAGE_ID`.

## Despliegue en Railway

1. Crea un repositorio nuevo en GitHub (cuenta: Ganamostodos) y sube estos 3 archivos
2. En Railway, crea un nuevo proyecto → "Deploy from GitHub repo" → selecciona el repositorio
3. Ve a la pestaña **Variables** del proyecto en Railway y agrega:
   - `FB_PAGE_ID` → el ID de tu página (ver arriba)
   - `FB_ACCESS_TOKEN` → el token del Usuario del Sistema que generaste (nunca lo subas al código ni a GitHub)
   - `POST_HOUR` → (opcional) hora del día en formato 24h para publicar, ej. `9` para las 9:00 AM. Si no la defines, publica a las 9 AM por defecto
4. Railway detecta automáticamente que es un proyecto Python e instala `requirements.txt`
5. En **Settings → Deploy**, asegúrate que el "Start Command" sea:
   ```
   python bot.py
   ```
6. Dale deploy — el bot quedará corriendo 24/7, revisando cada minuto si ya es hora de publicar

## Notas importantes

- El bot guarda su progreso (qué tip tocó publicar) en un archivo `state.json` que se crea solo
- Si Railway reinicia el contenedor, ese archivo se puede perder — no es grave, simplemente el bot
  retomará desde el primer tip. Si más adelante quieres que el progreso nunca se pierda, se puede
  conectar a una base de datos pequeña (opcional, no urgente para empezar)
- Recuerda: el token del Usuario del Sistema no caduca, así que no deberías tener que regenerarlo

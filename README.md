# Smart Download Organizer

Este proyecto es un gestor de descargas inteligente impulsado por agentes de IA (`agentify`). Su objetivo categorizar y organizar automáticamente los archivos que descargas.

## Funcionalidad

El sistema funciona como un demonio (daemon) en segundo plano que monitorea tu carpeta de `~/Descargas`. Cuando detecta un nuevo archivo:

1.  **Intercepta la descarga**: Detecta el nuevo archivo y espera a que termine de escribirse.
2.  **Solicita Acción**: Muestra un diálogo emergente (popup) preguntando qué hacer. Opciones:
    *   **Confirmar (Enter)**: Si escribes una instrucción, el Agente de IA la, procesará.
    *   **Auto-clasificar (Timeout/Vacío)**: Si no respondes en 45 segundos o das Enter vacío, organiza el archivo automáticamente según su extensión.
    *   **Cancelar (Esc)**: Ignora el archivo y lo deja donde está.

### Clasificación Automática
Si no se dan instrucciones, los archivos se mueven a:
*   `Imágenes`: .jpg, .png, .webp, ...
*   `Documentos`: .pdf, .docx, .txt, ...
*   `Videos`: .mp4, .mkv, ...
*   `Música`: .mp3, .flac, ...
*   `Comprimidos`: .zip, .rar, ...
*   `Código`: .py, .js, ...

### Agente Inteligente (IA)
Si escribes una instrucción en el diálogo (ej: "Mover a la carpeta de facturas y renombrar a Factura_Enero"), el agente:
*   Analiza tu petición con GPT-4.
*   Puede crear carpetas, renombrar archivos y moverlos a cualquier subdirectorio de tu usuario.
*   Puede extraer archivos comprimidos si se lo pides.

## Instalación y Auto-inicio

Para que el organizador inicie con el sistema:

1.  El servicio `download-organizer.service` se debe copiar a `~/.config/systemd/user/`.
2.  Habilitar con:
    ```bash
    systemctl --user enable --now download-organizer
    ```

## Configuración
La configuración se encuentra en `src/download_organizer/config.py`.

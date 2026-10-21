# Instrucciones del proyecto

## Actualizaciones y limpieza

Preferencia explícita del usuario: evitar acumulación de versiones antiguas y archivos temporales.

- Después de verificar una actualización, eliminar los instaladores y copias temporales anteriores creados por este proyecto, tanto en el PC como en las carpetas de transferencia de Vita. Conservar el paquete vigente, evidencias de pruebas e historial Git.
- Verificar rutas y, cuando exista, el hash o recibo de transferencia antes de borrar. No eliminar por patrones amplios ni vaciar directorios con contenido desconocido. Retirar carpetas de transferencia antiguas solo cuando estén vacías.
- Actualizar STT Vita Monitor sobre su propia instalación; no desinstalar otras aplicaciones ni borrar configuraciones, partidas, juegos o datos necesarios. No cambiar firmware/plugins.
- No volver a transferir binarios en commits que solo cambien documentación. No reinstalar un paquete idéntico por reconstrucciones de CI.

## Pruebas

Distinguir resultados automatizados, observaciones del receptor PC y confirmaciones del usuario en consola. No equiparar una compilación correcta a validación física. Toda excepción temporal de firewall debe tener alcance limitado y limpieza comprobada.

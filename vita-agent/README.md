# Agente Vita — diseño pendiente de compilación

No se incluye código nativo no verificado. No se ha localizado VitaSDK en este entorno (`VITASDK` ausente), ni compilado o instalado un VPK. La viabilidad de la aplicación se verificará por separado; no se propone ningún plugin.

## Esqueleto funcional previsto

1. Aplicación homebrew independiente; inicializar pantalla, controles y red con APIs de VitaSDK verificadas.
2. Configurar manualmente IP privada del receptor y puerto; crear sesión por arranque.
3. Abrir socket UDP y emitir STT/1 una vez por segundo; batería desconocida = null hasta verificar API. Usar reloj monotónico propio y secuencia creciente.
4. Mostrar envíos/errores; limitar reintentos, permitir salir con un botón y cerrar recursos en cada ruta de error.
5. Sin escrituras al almacenamiento, hooks, lectura de otros procesos, cambios de firmware o acceso FTP.

## Puertas de validación

- Fijar versión/commit de VitaSDK y consultar ejemplos oficiales de red, controles y empaquetado antes de implementar.
- Compilar en entorno aislado; registrar herramientas, salida y hash del artefacto.
- Inspeccionar el paquete y solicitar autorización adicional antes de transferir o ejecutar en Vita.
- Ejecutar STT-MON-001 en hardware: inicio/salida, recepción, desconexión y reconexión; documentar consumo y errores observados.

Hardware declarado: PS Vita 1000, firmware 3.65 HENkaku/ensō, VitaShell, SD2Vita 64 GB, FTP con WinSCP operativo según usuario. No inspeccionado físicamente. La compatibilidad del futuro agente con esta configuración sigue pendiente.

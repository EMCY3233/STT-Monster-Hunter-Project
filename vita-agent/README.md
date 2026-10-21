# Agente Vita experimental — STT/1

Aplicación independiente experimental. La versión 0.1 completó un primer ensayo físico con 60 muestras y salida por START confirmada: [resultado](../docs/STT-MON-001-hardware-result.md). En 0.2, el usuario confirmó texto mayor, desaparición del parpadeo y parada con Círculo tras recibir diez muestras: [resultado](../docs/STT-MON-003-stop-result.md). Siguen pendientes un ensayo completo de 60 muestras en 0.2, desconexión y suspensión.

## Funciones del código

- Pantalla de diagnóstico con texto 2x y filas actualizadas solo al cambiar su contenido, mediante common/debugScreen de los ejemplos VitaSDK, fijados al commit fe8fbef570f3280586c0c20157146e3faefb2181. FetchContent descarga esa dependencia al configurar, sin construir los demás ejemplos. Sus avisos y licencias se conservan en la dependencia descargada.
- Destino IP editable en RAM con cruceta. Solo rangos privados RFC1918 y último octeto 1–254. El valor inicial 192.168.1.2 es un ejemplo: sustituir por la IP del PC. No valida la máscara de subred; evitar direcciones de red/broadcast de la LAN.
- CROSS inicia hasta 60 intentos de envío, uno por segundo aproximadamente; CIRCLE detiene y START sale. Antes de CROSS no envía telemetría.
- Arriba/abajo cambian el bloque IP seleccionado en +/-1; Cuadrado/Triángulo en +/-10, con vuelta al superar 0–255. Izquierda/derecha seleccionan bloque. Por ejemplo, de 2 a 134: 13 pulsaciones de Cuadrado y dos de Arriba.
- UDP no bloqueante, sin recibir comandos. Tres errores consecutivos detienen el ensayo; se muestra el último error. Un envío correcto no confirma entrega.
- source=vita, sesión basada en tick RTC e inicio monotónico, secuencia de intentos, tiempo transcurrido del proceso y batería por API. Batería fuera de rango se codifica como null. La sesión es un identificador práctico, no criptográfico.
- Cierre de socket, memoria y módulo NET. Sin cambios de frecuencias, firmware, plugins, lectura de otros procesos o escrituras de archivos.

Usa la conexión Wi-Fi existente, sin configurar perfiles. No garantiza reconexión tras suspensión ni monitoriza otros juegos.

## Compilación sin consola

CI usa vitasdk/vitasdk:2026.08-20260815 fijado también por digest y prueba el codificador C en Linux contra el protocolo Python. El artefacto experimental contiene VPK y SHA-256; se retiene siete días, sin release ni transferencia a consola. Otro trabajo descarga el artefacto y verifica hash, lista exacta de archivos y cabeceras SELF/SFO sin ejecutarlo.

Con Docker disponible, desde la raíz del repositorio:

```sh
docker run --rm -v "$PWD:/workspace" vitasdk/vitasdk:2026.08-20260815 sh -c 'cmake -S vita-agent -B build/vita && cmake --build build/vita'
```

CI fija el digest sha256:7f5eee50ff95b73c8c847dbfef6227aa0035886444b4d0254c21da8369ff1efc, observado en el primer build correcto. Para usar exactamente la misma imagen localmente, añadir ese digest a la etiqueta del comando anterior. El runner y las acciones también pueden cambiar; no se afirma reproducibilidad bit a bit. Identificador de desarrollo STTM00001: verificar que no colisiona con una aplicación instalada antes de una futura instalación.

## Prueba física pendiente

Se requiere autorización adicional antes de transferir o instalar. Revisar paquete y hash, confirmar identificador libre e IP del receptor. Después comprobar inicio/salida, ausencia de envíos antes de CROSS, máximo de muestras, batería, desconexión y errores.

Hardware declarado por el usuario: PS Vita 1000, firmware 3.65 HENkaku/ensō, VitaShell y SD2Vita 64 GB. No inspeccionado físicamente.

Fuentes: [VitaSDK](https://vitasdk.org/), [ejemplos oficiales](https://github.com/vitasdk/samples), [cabeceras oficiales](https://github.com/vitasdk/vita-headers). No se ha instalado software en el PC para compilar.

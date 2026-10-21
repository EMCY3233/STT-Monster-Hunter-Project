# STT-MON-001 — primera prueba segura

Fecha: 21 de octubre de 2026 (Europe/Madrid).

## Objetivo y aceptación

Validar el contrato y el recorrido emisor → UDP local → registro sin acceder a Vita. Aceptación: 10 muestras simuladas válidas, secuencias 0–9, etiqueta simulator, receptor termina por límite; mensajes inválidos descartados; salida por inactividad comprobada.

Reproducir con los comandos del README. Usar un archivo nuevo por ensayo si se desean contar sus líneas, porque el receptor siempre añade. No modificar reglas de firewall para el ensayo local.

## Matriz

| Prueba | Estado |
|---|---|
| Validación, límites, campos inválidos, JSON y UTF-8 malformados | Automatizada; resultado en changelog |
| UDP local, mensaje inválido seguido de válidos, duplicados y desorden | Automatizada; resultado en changelog |
| Inactividad sin emisor | Automatizada; resultado en changelog |
| Dos procesos CLI y 10 muestras | Resultado en changelog |
| CI Windows/Linux, Python 3.11/3.13 | Correcto en 610c076; ejecución enlazada en changelog |
| Wi-Fi entre PC y Vita | Pendiente; requiere autorización adicional |
| Desconexión/reconexión física y batería real | Pendiente |
| Compilación de agente Vita | Workflow remoto en rama experimental; consultar su resultado |
| Instalación/salida de agente Vita | Pendiente en hardware; requiere autorización adicional |

El ensayo de inactividad automatizado cubre ausencia de datagramas; no prueba una desconexión Wi-Fi física. No se afirma rendimiento ni compatibilidad en consola.

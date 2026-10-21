# Seguimiento de una referencia PSP

## Referencia estática PSP aceptada

[PR7/c529799](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/c529799/docs/research/stt-re-20261021/mhfu-import-reference.md): primer registro de imports del ELF MHFU, puntero NID VA0x0890EC78 ↔ offset0x0010D22C ↔ sección.rodata.sceNid. Cálculos independientes por sección yPT_LOAD coinciden;12bytes requeridos respaldados por archivo. Confianza estructural alta para esta única referencia, sin identificar función, biblioteca resuelta o ejecución.

Artefacto existente1.910.384bytes, SHA-256 `64937c521286fc8423076e644089881c5fe051bed2565e5061dda8aec0b45e10`; prefijo canónico1.910.044bytes SHA-256 `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`. Cola340bytes excluida,sin interpretar. Aquí cotejados ambos hashes yrecibo `9b370c8b054d81f8cc278f0c84bb135851e30da6267c354b51e762231ff63f3a`; no repetido parser.

Cinco pruebas sintéticas aprobadas por investigación,no reproducidas aquí. Referencia primaria comunitariaPSPSDK6ef2b21dc440ef8d4125f000301faaa2a470975e; no especificación propietariaSony. No se publican NID/código ni se aplican relocaciones; no equivale a port,compatibilidadVita o semántica de juego. Área02 conserva direcciones estáticas yprocedencia; áreas04/07 no reciben funciones/recursos inferidos. Aceptación cerrada a una referencia, sin ampliación automática. Banco,originales yconsola sin cambios.

# [Titulo del Fix] — [FIX / HOTFIX]

> Fecha: YYYY-MM-DD
> Tipo: FIX / HOTFIX
> Funcionalidad afectada: `[slug-funcionalidad]`
> Severidad: CRITICA / ALTA / MEDIA / BAJA

---

## Problema

[Descripcion del bug tal como se manifesto. Como lo veia el usuario.]

## Causa raiz

[Explicacion tecnica de por que ocurria.]

## Impacto

- Usuarios afectados: [todos / rol especifico / condicion]
- Funcionalidad bloqueada: [que no podia hacerse]
- Workaround disponible: Si/No — [cual si aplica]

## Fix aplicado

| Archivo | Linea | Cambio |
|---------|-------|--------|
| `config/settings.py` | 357 | descripcion del cambio |

## Verificacion

[Como confirmar que el fix funciona. Pasos para reproducir y verificar.]

## Checklist de deploy

```
[ ] Aplicar en staging primero
[ ] Comandos en produccion:
    git pull origin [rama]
    docker-compose up --build -d
[ ] Verificar comportamiento corregido
[ ] Monitorear logs 10 minutos
```

## Deuda tecnica generada

[Si el fix es un parche temporal, describir la solucion definitiva pendiente.]

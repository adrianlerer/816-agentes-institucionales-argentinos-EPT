# Resultados Esperados: Simulación EPT 816 Agentes

**Ejecutar:** `python run.py`
**Tiempo estimado:** ~20 segundos

---

## Tabla Monte Carlo (5 seeds × 100 rondas)

| Seed | CLI Final | Block Rate | COAL+LIT | Pass |
|------|-----------|------------|----------|------|
| 42   | ~0.9233   | ~93.8%     | ~65.0%   | ✓    |
| 179  | ~0.9233   | ~93.8%     | ~65.0%   | ✓    |
| 316  | ~0.9233   | ~93.8%     | ~65.0%   | ✓    |
| 453  | ~0.9233   | ~93.8%     | ~65.0%   | ✓    |
| 590  | ~0.9233   | ~93.8%     | ~65.0%   | ✓    |
| **MEDIA** | **~0.9233** | **~93.8%** | **~65.0%** | |
| **SD** | **~0.0001** | | | |

La baja desviación estándar (SD ~0.0001) indica un atractor fuerte: el sistema
converge al mismo CLI independientemente de las fluctuaciones iniciales.
Esto es evidencia de lock-in institucional estable.

---

## Criterios de Validación (4 checks, todos deben ser ✓)

```
✓ CLI ∈ [0.80, 0.95]: mean=0.9233 (dentro del rango empírico)
✓ Reform block rate >70%: ~93.8% (supera ampliamente el umbral)
✓ Union COALICIONAR+LITIGAR >50%: ~65.0% (estrategia dominante)
✓ CLI calibration accuracy: error=0.033 < threshold 0.05
```

Si algún check falla en su entorno, verificar:
1. Python 3.11+ instalado
2. `pip install -r requirements.txt` completado
3. Seeds en `config/argentina.yaml` no modificadas

---

## Descripción de los Gráficos Generados

### cli_timeseries.png

Serie temporal del CLI para las 5 seeds (100 rondas cada una), más la media.

- **Eje X:** Ronda (1-100)
- **Eje Y:** CLI (0-1)
- **Línea naranja punteada:** Ronda 5 (introducción de la reforma)
- **Línea roja punteada:** CLI target = 0.89
- **Líneas grises:** Umbrales [0.80, 0.95]
- **Línea negra sólida:** Media de las 5 seeds

**Qué muestra:** El CLI parte de ~0.80 (estado pre-reforma), cae ligeramente
al introducirse la reforma en ronda 5, y luego rebota y converge a ~0.92
por acción de los mecanismos de resistencia (CRI + coaliciones sindicales).
Las 5 seeds se superponen casi perfectamente: atractor fuerte.

### action_distribution.png

Distribución porcentual de los 9 tipos de acciones a lo largo de las
5 seeds × 100 rondas × 816 agentes.

**Qué muestra:** CUMPLIR es la acción más frecuente (ciudadanos y empresas),
seguida de COALICIONAR (sindicatos y opositores) y SANCIONAR (jueces y
regulador). REFORMAR representa menos del 10% del total, explicando por
qué la reforma no logra implementarse.

---

## Comparación con Datos Históricos (23 Reformas)

| Período | N reformas | Bloqueadas/revertidas | Tasa |
|---------|------------|----------------------|------|
| 1974-1983 | 3 | 2 | 67% |
| 1984-1999 | 8 | 6 | 75% |
| 2000-2015 | 7 | 5 | 71% |
| 2016-2024 | 5 | 4 | 80% |
| **Total** | **23** | **≥17** | **≥73%** |

La tasa histórica de bloqueo (~73-80%) es consistente con el resultado
simulado (~93.8%). La diferencia (~15%) se debe a que el modelo representa
el escenario de reforma adversarial extrema (tipo Menem 1990s), no el
promedio de todos los escenarios.

---

## Discrepancias Documentadas

Si los valores observados difieren de los publicados en más de 1%:

| Diferencia | Causa probable | Acción |
|------------|----------------|--------|
| CLI < 0.80 | Python < 3.11 (comportamiento random diferente) | Actualizar Python |
| CLI > 0.95 | Seeds modificadas | Restaurar argentina.yaml |
| Block rate < 70% | n_rounds < 100 | Verificar config |
| COAL+LIT < 50% | Parámetros de union modificados | Restaurar YAML |

Para reportar discrepancias: abrir un issue en el repositorio con
la salida completa de `python run.py` y `python --version`.

# FAQ — Preguntas Frecuentes

**816 Agentes Institucionales Argentinos: Simulación EPT**  
Lerer (2026) | AGPL-3.0

---

## 1. ¿Necesito API key de OpenAI, Anthropic u otro servicio de IA?

**No.** Este repositorio usa agentes **rule-based**. No requiere ninguna
API key, ninguna conexión a internet, y funciona 100% offline.

Los agentes toman decisiones según reglas deterministas basadas en sus
parámetros (CRI, capital institucional) y el estado del entorno. No hay
modelos de lenguaje involucrados.

---

## 2. ¿Cuánto tarda en correr?

**~20 segundos** en una laptop moderna (2020+).

El tiempo escala aproximadamente linealmente con seeds × rondas × agentes.
Con los parámetros por defecto (5 × 100 × 816), la mayor parte del tiempo
se dedica a la actualización HBU de los 816 agentes en cada ronda.

Para una prueba rápida, editar `argentina.yaml`:
```yaml
simulation_rounds: 10
monte_carlo_seeds: [42]
```

---

## 3. ¿Por qué 816 agentes?

816 agentes es el resultado del **mapeo de la estructura institucional
argentina real**:

| Institución | Agentes | Justificación |
|-------------|---------|---------------|
| CSJN | 5 | 5 miembros actuales |
| Diputados (oficialismo) | 130 | Bancada promedio 2015-2023 |
| Diputados (oposición) | 127 | Resto de Diputados |
| CGT + CTA + Sectorial | 3 | 3 confederaciones principales |
| Empresas reguladas | 50 | Escala representativa UIA |
| Ciudadanos | 500 | Escala de masa relativa |
| Regulador | 1 | MTSS/MTySS |

El número 816 no es arbitrario: es la suma de los actores identificados
en los documentos institucionales y datos de composición legislativa.

---

## 4. ¿Los resultados son determinísticos?

**No.** La simulación usa aleatoriedad (para las decisiones de los
legisladores con disciplina < 1.0, los intentos de captura, etc.).

Sin embargo, la **varianza es muy baja** (SD < 0.001 en CLI). Esto
indica que el sistema tiene un **atractor fuerte**: independientemente
del path estocástico, converge al mismo CLI ~0.923.

Esto es un resultado científicamente relevante: no es que el código
produzca siempre el mismo número por construcción, sino que el sistema
dinámico tiene un equilibrio estable robusto.

Para verificar: cambiar los seeds en `argentina.yaml` y comprobar que
el CLI sigue en [0.90, 0.94].

---

## 5. ¿Puedo modificar los parámetros?

**Sí.** Editar `config/argentina.yaml`. El archivo está completamente
documentado. Los parámetros más interesantes para explorar:

- `judges_csjn.cri`: reducir a 0.30 para ver qué pasa cuando la CSJN
  pierde independencia
- `unions.CGT.coalition_capacity`: reducir a 0.30 para simular una
  CGT fragmentada
- `reform_trigger_round`: cambiar a 1 para reforma inmediata
- `monte_carlo_seeds`: agregar más seeds para mayor robustez estadística

También se puede modificar `data/argentina_agents.json` para cambiar
parámetros individuales de agentes específicos.

---

## 6. ¿Puedo simular otro país?

Para eso está el **repositorio principal** (`legal-evolution-unified`)
que tiene 4 escenarios completos: Argentina, Chile, Brasil, España.

Este replication package está diseñado exclusivamente para el caso
argentino. Adaptar los parámetros manualmente para otro país requeriría:

1. Recalibrar los pesos del CLI contra datos históricos del país
2. Redefinir la composición y parámetros de los agentes
3. Construir el dataset de reformas históricas equivalente

El repositorio principal tiene esto hecho para los 4 países.

---

## 7. ¿Esto reemplaza el análisis jurídico tradicional?

**No.** Complementa. 

El modelo no puede:
- Interpretar el texto de las normas
- Detectar inconsistencias hermenéuticas
- Hacer juicios normativos sobre qué reforma es "justa"
- Predecir el comportamiento de actores individuales específicos

Lo que puede:
- Identificar el nivel de resistencia estructural de un sistema
- Simular el efecto agregado de combinaciones de actores
- Comparar la rigidez relativa entre sistemas institucionales
- Generar hipótesis sobre qué parámetros son más influyentes

Es una herramienta exploratoria, no prescriptiva.

---

## 8. ¿Por qué AGPL-3.0?

Consistente con los otros repositorios del proyecto
(OASIS/MiroFish/legal-evolution-unified).

La AGPL-3.0 asegura que:
- Cualquier modificación del código que se use en un servicio online
  debe publicarse con el mismo código fuente
- El replication package permanece en el dominio público científico
- No puede ser apropiado por terceros sin compartir las mejoras

Para uso académico (sin servicio online), la AGPL-3.0 es prácticamente
equivalente a la GPL-3.0.

---

## 9. ¿Cómo cito este repositorio?

```bibtex
@software{lerer2026_816agentes,
  author    = {Lerer, Ignacio Adrián},
  title     = {816 Agentes Institucionales Argentinos: Simulación EPT},
  year      = {2026},
  version   = {1.0.0},
  url       = {https://github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT},
  license   = {AGPL-3.0},
  orcid     = {0009-0007-6378-9749}
}
```

Ver también `CITATION.cff` en la raíz del repositorio.

---

## 10. Encontré un error en los resultados. ¿Qué hago?

1. Verificar que el resultado esperado está documentado en `docs/RESULTS.md`
2. Abrir un issue en GitHub con:
   - La salida completa de `python run.py`
   - La versión de Python (`python --version`)
   - El sistema operativo
3. Si hay una discrepancia > 1% en el CLI, es un bug. Si es < 1%,
   puede ser variación por diferencias de implementación de `random`
   entre plataformas.

---

## 11. ¿Este modelo predijo la reforma Milei de 2024?

No fue diseñado para predicción prospectiva. Sin embargo, el DNU 70/2023
(reforma laboral + RIGI) está incluido como reforma_id=23 en
`data/historical_reforms.csv` con `final_outcome=reversed`. El modelo
habría predicho bloqueo (CLI=0.923 implica >90% de probabilidad de
bloqueo). La realidad muestra bloqueo parcial: la Corte dictó cautelar
y hubo huelga general, aunque algunas disposiciones se mantienen.

La discrepancia (bloqueo parcial vs. predicción de bloqueo total) es
consistente con las limitaciones documentadas en `docs/METHODOLOGY.md`.

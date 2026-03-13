# Metodología: Simulación EPT con 816 Agentes Institucionales Argentinos

**Autor:** Ignacio Adrián Lerer | ORCID 0009-0007-6378-9749  
**Versión:** 1.0.0 | Fecha: 2026-03-13

---

## 1. Marco Teórico: Extended Phenotype Theory aplicada al derecho

Este modelo aplica la Extended Phenotype Theory (EPT) de Dawkins (1982) al estudio
de las instituciones jurídicas. La idea central es que las normas jurídicas
funcionan como **replicadores culturales**: se propagan, mutan, compiten y
son seleccionadas en un entorno institucional, análogamente a los genes en el
entorno biológico.

El "fenotipo extendido" de una norma incluye todos los comportamientos que ella
induce en los agentes (cumplimiento, evasión, litigio) y las estructuras que
construye (coaliciones, precedentes, doctrina consolidada). Una norma de alto
fitness no es necesariamente "justa" ni "eficiente": es aquella que logra
reproducirse en el entorno institucional dado.

La analogía con la teoría de juegos evolutivos (Maynard Smith, 1982) permite
modelar la dinámica de estrategias entre agentes: los equilibrios Nash
estables corresponden a los "lock-in" institucionales observados.

---

## 2. El Constitutional Lock-in Index (CLI)

### Definición

El CLI es un índice compuesto [0, 1] que mide la rigidez estructural del
sistema institucional. Valores > 0.80 indican lock-in fuerte: el statu quo
es estable y las reformas son bloqueadas sistémicamente.

### Fórmula

```
CLI = w1·VP + w2·JR + w3·AD + w4·IN
```

Donde:
- **VP** (veto player score): poder agregado de veto players institucionales
- **JR** (judicial review score): intensidad del control judicial de constitucionalidad
- **AD** (amendment difficulty): rigidez formal del proceso de reforma normativa
- **IN** (informal norms score): arraigo de normas informales y prácticas consuetudinarias

### Pesos (calibrados para Argentina)

| Componente | Símbolo | Peso |
|------------|---------|------|
| Veto players | VP | 0.30 |
| Judicial review | JR | 0.25 |
| Amendment difficulty | AD | 0.25 |
| Informal norms | IN | 0.20 |

Los pesos son fijos y fueron calibrados contra las 23 reformas laborales argentinas
1974-2024. No son estimados por el modelo en cada simulación.

### Interpretación

- CLI < 0.50: sistema flexible, reformas se implementan con alta probabilidad
- CLI 0.50–0.80: sistema moderadamente rígido, reformas parciales o negociadas
- CLI > 0.80: lock-in fuerte, reformas bloqueadas o revertidas rápidamente

Argentina converge a CLI ≈ 0.92 en este escenario, explicando el patrón histórico
de reformas laborales bloqueadas o revertidas.

---

## 3. Los 7 Tipos de Agentes

### 3.1 JudgeAgent — Jueces CSJN (5)

Los 5 jueces de la Corte Suprema de Justicia son los **veto players
constitucionales** del sistema. Con CRI=0.78 y capital institucional=0.90,
son los agentes más resistentes al cambio. Sus acciones (SANCIONAR, REVERSAR,
IMPUGNAR_CN) tienen el mayor efecto sobre el CLI (+0.02 a +0.05 por acción).

**Por qué estos parámetros:** La doctrina de la CSJN argentina tiene más de
70 años de consolidación en materia laboral. El alto CRI refleja el costo
institucional de cambiar precedentes establecidos (stare decisis argentino).

### 3.2 LegislatorAgent — Legisladores (257)

130 oficialistas (pro-reforma, CRI=0.30) + 127 opositores (anti-reforma, CRI=0.60).
La disciplina partidaria (0.70–0.80) modula la autonomía individual.

**Por qué estos parámetros:** El Congreso argentino tiene mayorías volátiles
y alta disciplina de bloque. Los opositores tienen CRI más alto porque la
defensa del statu quo requiere menos capital político que la reforma.

### 3.3 UnionAgent — Sindicatos (3)

CGT (CRI=0.85), CTA (CRI=0.80), Sectorial (CRI=0.75). Son los actores con
mayor capacidad de coalición (0.70–0.95) y los que producen el 65% de
estrategia COAL+LIT observado.

**Por qué estos parámetros:** Los sindicatos argentinos tienen el CRI más
alto después de los jueces: décadas de jurisprudencia laboral consolidada,
capacidad organizativa alta, y recursos de litigio sustanciales.

### 3.4 RegulatedFirmAgent — Empresas (50)

CRI=0.20 (pro-reforma), con capacidad de captura regulatoria (0.40). Su
paradoja: aunque quieren la reforma, sus intentos de CAPTURAR al regulador
pueden crear incentivos perversos que refuerzan el CLI.

### 3.5 CitizenAgent — Ciudadanos (500)

Los agentes más atomizados. CRI=0.15, solo pueden CUMPLIR o EVADIR. Su
comportamiento agregado forma la base de las normas informales (componente IN).

### 3.6 RegulatorAgent — Regulador (1)

CRI=0.40, vulnerable a captura (0.50). Cuando es capturado, sus sanciones
no tienen efecto, lo que vía HBU reduce la percepción de validez de las
normas por los ciudadanos.

---

## 4. Las 9 Acciones y sus Efectos

| Acción | Costo | Efecto CLI | Disponible para |
|--------|-------|------------|-----------------|
| CUMPLIR | 0.05 | +0.01 | Todos |
| EVADIR | 0.15 | -0.01 | Ciudadanos, empresas, sindicatos |
| LITIGAR | 0.40 | +0.03 | Sindicatos, empresas |
| IMPUGNAR_CN | 0.60 | +0.05 | Jueces, opositores |
| REFORMAR | 0.50 | -0.04 | Oficialismo |
| COALICIONAR | 0.25 | +0.04 | Legisladores, sindicatos |
| CAPTURAR | 0.70 | -0.02 | Empresas |
| SANCIONAR | 0.30 | +0.02 | Jueces, regulador |
| REVERSAR | 0.55 | -0.05 | Jueces |

Las acciones de resistencia (LITIGAR, IMPUGNAR_CN, COALICIONAR, SANCIONAR,
REVERSAR) tienen efecto neto positivo sobre el CLI, explicando por qué el
sistema converge a lock-in cuando los agentes de alto CRI son los que más actúan.

---

## 5. El CRI: Costo Asimétrico de Abandono Doctrinal

El Coefficient of Resistance Institutional modela el hecho de que abandonar
una posición doctrinal consolidada es **más costoso que mantenerla**, incluso
cuando el fitness de esa doctrina ha caído.

### Función de costo

```python
cost_abandon = base_cost × institutional_capital × (1 + n_supporters)
cost_maintain = base_cost × (1 - doctrine_fitness)

# Mantiene si:
cost_abandon > cost_maintain × (1 + cri)
```

### Por qué este modelo captura la resistencia real

El costo asimétrico refleja tres fenómenos institucionales reales:
1. **Path dependence**: las posiciones consolidadas crean expectativas
2. **Credibilidad**: cambiar de posición tiene costo reputacional
3. **Red de seguidores**: más seguidores = más costoso abandonar

El CRI actúa como multiplicador del umbral: un juez con CRI=0.78 necesita
que el costo de mantenimiento sea 1.78× el costo de abandono para considerar
cambiar su posición.

---

## 6. HBU: Heteronomous Bayesian Updating

### El problema de la heteronomía

Los agentes institucionales aprenden observando **sanciones** (heteronomía),
no evaluando el contenido sustantivo de las normas (autonomía). Esto genera
un bucle patológico en sistemas de alto CLI.

### Fórmula

```
P(válida | sanción) = P(sanción | válida) × P(válida) / P(sanción)
```

Con parámetros calibrados:
- P(sanción | norma válida) = 0.80 (normas válidas se aplican con fuerza)
- P(sanción | norma inválida) = 0.20 (normas inválidas tienen poco enforcement)

### El bucle de lock-in

1. Sistema tiene alta doctrina consolidada → muchas sanciones a quienes la infringen
2. Agentes observan sanciones → actualizan hacia "la norma es válida"
3. Alta percepción de validez → más cumplimiento → menos litigio
4. Menos litigio → la coalición anti-reforma usa litigio aún más estratégicamente
5. Litigio estratégico → más sanciones → vuelta al paso 2

Este bucle explica por qué el CLI emerge y se mantiene en ~0.92.

---

## 7. El Motor de Simulación: 10 Pasos por Ronda

Cada ronda ejecuta estos pasos en orden:

1. **Iniciar ronda**: disparar reforma si `round == reform_trigger_round`
2. **Tick captura**: decrementar contador de captura en el regulador
3. **Intentos de captura**: empresas intentan capturar al regulador si reforma activa
4. **Decisiones de agentes**: cada agente elige acción (orden: CRI descendente)
5. **Aplicar acciones**: actualizar estado del LegalEnvironment
6. **HBU update**: actualizar creencias de todos los agentes
7. **Actualizar n_supporters**: contar agentes del mismo tipo post-acción
8. **Computar CLI**: calcular índice compuesto de la ronda
9. **Decaimiento de coalición**: reducir coalition_strength si no hay COALICIONAR
10. **Registrar estado**: agregar CLI al historial

El orden de actuación importa: agentes con mayor CRI actúan primero, lo que
refleja que los actores con mayor capital institucional tienen mayor poder
de agenda-setting.

---

## 8. Validación Monte Carlo

### Procedimiento

- 5 seeds: [42, 179, 316, 453, 590]
- 100 rondas por seed
- Reforma introducida en ronda 5

### Criterios publicados (todos deben pasar)

| Criterio | Umbral | Justificación |
|----------|--------|---------------|
| CLI ∈ [0.80, 0.95] | Rango empírico | Calibrado con datos históricos |
| Block rate > 70% | Mínimo histórico | 23 reformas: >70% bloqueadas |
| COAL+LIT sindical > 50% | Estrategia dominante | Equilibrio evolutivo |
| Error CLI < 5% | Tolerancia calibración | Estándar en modelos ABM |

### Por qué Monte Carlo y no una sola run

La baja varianza observada (SD ≈ 0.0001 en CLI) es evidencia de que el
sistema tiene un **atractor fuerte**: el CLI converge al mismo valor
independientemente de las fluctuaciones estocásticas iniciales. Esto es
precisamente lo que predice EPT para sistemas en equilibrio de lock-in.

---

## 9. Limitaciones Honestas

### 9.1 Agentes rule-based, no LLM

Los agentes siguen reglas determinísticas con componente estocástico.
No tienen capacidad de razonamiento emergente. Esto es una **fortaleza**
para la replicabilidad (100% offline, sin API keys), pero limita la
riqueza de los comportamientos individuales.

### 9.2 Parámetros calibrados, no estimados

El CRI, el capital institucional y los pesos del CLI fueron calibrados
manualmente contra datos históricos. No son estimados por máxima
verosimilitud ni por métodos bayesianos. Una versión futura debería
estimar los parámetros con SMM (Simulated Method of Moments).

### 9.3 Muestra histórica pequeña

23 reformas laborales (1974-2024) es una muestra pequeña para calibración.
Bunge (1982) objetaría que la inducción sobre muestras pequeñas es
epistemológicamente frágil. La validación cruzada con otros países
(repo principal: legal-evolution-unified) mitiga parcialmente este problema.

### 9.4 Utilidades subjetivas

Bunge (1982) objetaría también el uso de utilidades subjetivas en los
parámetros de preferencia (reform_preference, coalition_capacity). El modelo
asume que estos parámetros son estables a lo largo de la simulación, lo que
es una simplificación significativa.

### 9.5 Ausencia de dinámica endógena de parámetros

El CRI de cada agente es fijo durante la simulación. En la realidad,
el capital institucional se acumula o degrada con las interacciones.
Modelar la dinámica endógena del CRI es trabajo futuro.

---

## 10. Referencias

- Dawkins, R. (1982). *The Extended Phenotype*. Oxford University Press.
- Maynard Smith, J. (1982). *Evolution and the Theory of Games*. Cambridge University Press.
- Bunge, M. (1982). *Fundamentos de Biología Teórica*. Siglo XXI. [Crítica de utilitarismo subjetivo]
- Shapira, R. et al. (2026). Multi-agent modeling of legal institutions. *Journal of Artificial Societies*, [pending].
- Lerer, I. A. (2026). Simulating Institutional Dynamics: A Multi-Agent Framework for Predicting Legal Reform Outcomes Using Extended Phenotype Theory. Zenodo. DOI: 10.5281/zenodo.PENDING.

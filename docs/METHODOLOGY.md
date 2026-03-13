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
CLI = w1*VP + w2*JR + w3*AD + w4*IN
```

Donde:
- **VP** (veto player score): poder agregado de veto players institucionales
- **JR** (judicial review score): intensidad del control judicial
- **AD** (amendment difficulty): rigidez formal del proceso de reforma
- **IN** (informal norms score): arraigo de normas informales

### Pesos calibrados para Argentina

| Componente        | Símbolo | Peso |
|-------------------|---------|------|
| Veto players      | VP      | 0.30 |
| Judicial review   | JR      | 0.25 |
| Amendment diffic. | AD      | 0.25 |
| Informal norms    | IN      | 0.20 |

Los pesos son fijos, calibrados contra las 23 reformas laborales 1974-2024.

### Interpretación

- CLI < 0.50: sistema flexible, reformas se implementan con alta probabilidad
- CLI 0.50-0.80: sistema moderadamente rígido, reformas parciales o negociadas
- CLI > 0.80: lock-in fuerte, reformas bloqueadas o revertidas rápidamente

Argentina converge a CLI ~0.92 en este escenario.

---

## 3. Los 7 Tipos de Agentes

### 3.1 JudgeAgent — Jueces CSJN (5)

Los 5 jueces de la Corte Suprema son los **veto players constitucionales**.
Con CRI=0.78 y capital institucional=0.90, son los agentes más resistentes.
Sus acciones (SANCIONAR, REVERSAR, IMPUGNAR_CN) tienen el mayor efecto
sobre el CLI (+0.02 a +0.05 por acción).

**Por qué estos parámetros:** La doctrina de la CSJN tiene más de 70 años
de consolidación en materia laboral. El alto CRI refleja el costo de cambiar
precedentes establecidos (stare decisis argentino).

### 3.2 LegislatorAgent — Legisladores (257)

130 oficialistas (pro-reforma, CRI=0.30) + 127 opositores (anti-reforma,
CRI=0.60). La disciplina partidaria (0.70-0.80) modula la autonomía.

### 3.3 UnionAgent — Sindicatos (3)

CGT (CRI=0.85), CTA (CRI=0.80), Sectorial (CRI=0.75). Mayor capacidad de
coalición (0.70-0.95). Producen el 65% de estrategia COAL+LIT.

### 3.4 RegulatedFirmAgent — Empresas (50)

CRI=0.20 (pro-reforma), con capacidad de captura regulatoria (0.40).

### 3.5 CitizenAgent — Ciudadanos (500)

Agentes más atomizados. CRI=0.15, solo pueden CUMPLIR o EVADIR.

### 3.6 RegulatorAgent — Regulador (1)

CRI=0.40, vulnerable a captura (0.50). Cuando capturado, sus sanciones
no tienen efecto.

---

## 4. Las 9 Acciones y sus Efectos

| Acción      | Costo | Efecto CLI | Disponible para           |
|-------------|-------|------------|---------------------------|
| CUMPLIR     | 0.05  | +0.01      | Todos                     |
| EVADIR      | 0.15  | -0.01      | Ciudadanos, empresas, sind.|
| LITIGAR     | 0.40  | +0.03      | Sindicatos, empresas      |
| IMPUGNAR_CN | 0.60  | +0.05      | Jueces, opositores        |
| REFORMAR    | 0.50  | -0.04      | Oficialismo               |
| COALICIONAR | 0.25  | +0.04      | Legisladores, sindicatos  |
| CAPTURAR    | 0.70  | -0.02      | Empresas                  |
| SANCIONAR   | 0.30  | +0.02      | Jueces, regulador         |
| REVERSAR    | 0.55  | -0.05      | Jueces                    |

---

## 5. El CRI: Costo Asimétrico de Abandono Doctrinal

```python
cost_abandon = base_cost * institutional_capital * (1 + n_supporters)
cost_maintain = base_cost * (1 - doctrine_fitness)

# Mantiene si:
cost_abandon > cost_maintain * (1 + cri)
```

El CRI actúa como multiplicador del umbral: un juez con CRI=0.78 necesita
que el costo de mantenimiento sea 1.78x el costo de abandono para cambiar
su posición doctrinal.

---

## 6. HBU: Heteronomous Bayesian Updating

Los agentes aprenden observando **sanciones** (heteronomía), no el
contenido sustantivo de las normas (autonomía).

```
P(válida | sanción) = P(sanción | válida) * P(válida) / P(sanción)
```

Parámetros calibrados:
- P(sanción | norma válida) = 0.80
- P(sanción | norma inválida) = 0.20

Esto genera un bucle de lock-in: más sanciones → más creencia en validez
→ más cumplimiento → más sanciones a quienes intentan reformar.

---

## 7. El Motor de Simulación: 10 Pasos por Ronda

1. Iniciar ronda (trigger reforma si `round == 5`)
2. Tick captura del regulador
3. Intentos de captura por empresas
4. Decisiones de agentes (orden: CRI descendente)
5. Aplicar acciones al LegalEnvironment
6. HBU update para todos los agentes
7. Actualizar n_supporters
8. Computar CLI de la ronda
9. Decaimiento de coalition_strength
10. Registrar estado en historial

---

## 8. Validación Monte Carlo

- 5 seeds: [42, 179, 316, 453, 590]
- 100 rondas por seed
- Reforma introducida en ronda 5

| Criterio                | Umbral      |
|-------------------------|-------------|
| CLI en [0.80, 0.95]     | Rango empírico |
| Block rate > 70%        | Mínimo histórico |
| COAL+LIT sindical > 50% | Estrategia dominante |
| Error CLI < 5%          | Tolerancia calibración |

---

## 9. Limitaciones Honestas

1. **Agentes rule-based, no LLM**: sin razonamiento emergente. Fortaleza
   para replicabilidad; limitación para riqueza comportamental.

2. **Parámetros calibrados, no estimados**: CRI y pesos del CLI fueron
   calibrados manualmente. Una versión futura usaría SMM (Simulated
   Method of Moments).

3. **Muestra histórica pequeña**: 23 reformas es muestra reducida.
   Bunge (1982) objetaría la inducción sobre muestras pequeñas.

4. **Utilidades subjetivas**: Bunge (1982) objetaría el uso de
   preferencias subjetivas (reform_preference, coalition_capacity).

5. **CRI fijo**: el coeficiente de resistencia no varía endógenamente
   durante la simulación. Trabajo futuro: dinámica endógena del CRI.

---

## 10. Referencias

- Dawkins, R. (1982). *The Extended Phenotype*. Oxford University Press.
- Maynard Smith, J. (1982). *Evolution and the Theory of Games*. Cambridge University Press.
- Bunge, M. (1982). *Fundamentos de Biología Teórica*. Siglo XXI.
- Lerer, I. A. (2026). Simulating Institutional Dynamics: A Multi-Agent Framework for Predicting Legal Reform Outcomes Using Extended Phenotype Theory. Zenodo. DOI: 10.5281/zenodo.PENDING.

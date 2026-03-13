# 816 Agentes Institucionales Argentinos: Simulación EPT

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Replication Package](https://img.shields.io/badge/type-replication%20package-orange.svg)](https://github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT)

## Replicación en 3 pasos

### Paso 1: Clonar
```bash
git clone https://github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT
cd 816-agentes-institucionales-argentinos-EPT
```

### Paso 2: Instalar
```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar
```bash
python run.py
```

**Tiempo estimado:** ~20 segundos (5 seeds × 100 rondas × 816 agentes)

---

## Qué hace

Simula una reforma laboral flexibilizadora en Argentina usando 816
agentes institucionales con parámetros calibrados:

- 5 jueces CSJN (CRI: 0.78, capital institucional: 0.90)
- 130 legisladores oficialistas + 127 opositores
- 3 confederaciones sindicales (CGT, CTA, sectoriales; coalición: 0.95)
- 50 empresas reguladas
- 500 ciudadanos
- 1 regulador

La reforma se introduce en la ronda 5. El sistema corre 100 rondas.

## Resultados esperados

| Métrica | Valor esperado | Criterio |
|---------|---------------|----------|
| CLI emergente | 0.92 ± 0.01 | Target: 0.89, error < 0.05 |
| Tasa de bloqueo | 93.8% | > 70% |
| Estrategia sindical COAL+LIT | 65% | > 50% |

## Qué significa

El Constitutional Lock-in Index (CLI) mide la rigidez estructural
del sistema institucional. Argentina (CLI ≈ 0.89) bloquea reformas
laborales porque la combinación de veto players (CSJN), coaliciones
sindicales (CGT+CTA), y normas informales arraigadas genera un
equilibrio estable de alta resistencia al cambio.

Los 816 agentes no fueron programados para bloquear la reforma.
El bloqueo EMERGE de sus interacciones bajo las reglas del modelo.

## Marco teórico

Extended Phenotype Theory (Dawkins, 1982) aplicada al derecho:
las normas jurídicas son replicadores culturales cuyo fitness
se mide como tasa de adopción / tasa de litigio.

Dos mecanismos clave:
- **CRI** (Coefficient of Resistance): costo asimétrico de abandonar
  posiciones doctrinales consolidadas
- **HBU** (Heteronomous Bayesian Updating): los agentes aprenden
  observando sanciones, no resultados sustantivos

## Paper asociado

Lerer, I. A. (2026). Simulating Institutional Dynamics: A Multi-Agent
Framework for Predicting Legal Reform Outcomes Using Extended Phenotype
Theory. Zenodo. DOI: [pending]

## Repositorio principal

Motor completo con 4 escenarios (Argentina, Chile, Brasil, España),
163 tests, y validación cruzada:
https://github.com/adrianlerer/legal-evolution-unified

## Autor

Ignacio Adrián Lerer  
Independent Researcher | Buenos Aires, Argentina  
adrian@lerer.com.ar | ORCID: [0009-0007-6378-9749](https://orcid.org/0009-0007-6378-9749)

## Licencia

AGPL-3.0

---

## Estructura del repositorio

```
816-agentes-institucionales-argentinos-EPT/
├── README.md                          # Este archivo
├── LICENSE                            # AGPL-3.0
├── CITATION.cff                       # Para citar este repo
├── requirements.txt                   # numpy, pyyaml, matplotlib, pytest
├── run.py                             # PUNTO DE ENTRADA ÚNICO
├── config/
│   └── argentina.yaml                 # Configuración del escenario
├── agents/                            # 7 tipos de agentes
│   ├── base.py, judge.py, legislator.py
│   ├── union.py, firm.py, citizen.py, regulator.py
├── engine/                            # Motor de simulación
│   ├── simulation.py, actions.py, environment.py
│   ├── hbu.py, resistance.py, metrics.py
├── data/
│   ├── argentina_agents.json          # 816 agentes con parámetros
│   └── historical_reforms.csv         # 23 reformas 1974-2024
├── validation/                        # Validación Monte Carlo
├── results/                           # GENERADO (no en git)
├── tests/                             # 20+ tests
└── docs/                              # METHODOLOGY, RESULTS, FAQ
```

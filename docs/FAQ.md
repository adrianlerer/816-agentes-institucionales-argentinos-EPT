# Preguntas Frecuentes (FAQ)

---

**1. ¿Necesito API key de OpenAI, Anthropic u otro servicio de IA?**

No. Los agentes son rule-based (reglas determinísticas + componente estocástico).
No hay llamadas a ninguna API externa. El modelo corre 100% offline.

---

**2. ¿Cuánto tarda en ejecutarse?**

Aproximadamente 20 segundos en hardware moderno (i5/i7, Python 3.11).
El tiempo escala linealmente con n_rounds y n_seeds.

Para una prueba rápida (5 rondas):
```python
# Editar config/argentina.yaml temporalmente:
# simulation_rounds: 5
python run.py
```

---

**3. ¿Por qué exactamente 816 agentes?**

El número mapea la estructura institucional argentina real:
- 5 jueces CSJN (composición actual del tribunal)
- 130 + 127 legisladores (distribución aproximada del Congreso)
- 3 confederaciones sindicales (CGT, CTA, sectoriales)
- 50 empresas reguladas (muestra representativa)
- 500 ciudadanos (base normativa informal)
- 1 regulador (MTSS/organismo laboral)

Total: 5 + 130 + 127 + 3 + 50 + 500 + 1 = **816**

No es un número arbitrario: es el mínimo que captura la estructura
de veto players del sistema laboral argentino.

---

**4. ¿Los resultados son determinísticos?**

No completamente. Hay componente estocástico controlado por seeds.
La baja varianza (SD ~0.0001 en CLI) indica que el sistema tiene un
**atractor fuerte**: pequeñas variaciones iniciales convergen al mismo
equilibrio. Esto es exactamente lo que predice EPT para lock-in.

Para resultados perfectamente reproducibles: no modificar las seeds
en `config/argentina.yaml`.

---

**5. ¿Puedo modificar los parámetros?**

Sí. Editar `config/argentina.yaml`. Por ejemplo:

```yaml
# Reducir CRI de jueces para simular tribunal más reformista:
agents:
  judges_csjn:
    cri: 0.40  # default: 0.78

# Cambiar ronda de trigger de la reforma:
scenario:
  reform_trigger_round: 20  # default: 5
```

Después de modificar, ejecutar `python run.py` para ver el nuevo resultado.
Para verificar que los tests siguen pasando: `pytest tests/ -v`.

---

**6. ¿Puedo simular otro país (Chile, Brasil, España)?**

Para eso existe el repositorio principal `legal-evolution-unified`:
https://github.com/adrianlerer/legal-evolution-unified

Tiene 4 escenarios completos, 163 tests y validación cruzada entre países.
Este repo (816-agentes) es solo el paquete de replicación para Argentina.

---

**7. ¿Esto reemplaza el análisis jurídico tradicional?**

No. Complementa. El modelo:
- **Puede:** identificar actores clave de resistencia, estimar equilibrios
  de mediano plazo, comparar escenarios contrafácticos
- **No puede:** interpretar normas, analizar jurisprudencia específica,
  predecir decisiones individuales, capturar contexto político coyuntural

La simulación es una herramienta de análisis estructural, no un oráculo.

---

**8. ¿Por qué AGPL-3.0?**

Consistente con el ecosistema de herramientas académicas open-source
(OASIS, MiroFish). La AGPL garantiza que cualquier modificación —incluyendo
versiones desplegadas como servicio web— debe publicar su código fuente.

Esto es importante para la reproducibilidad científica: cualquier paper
que use una versión modificada de este código debe publicar esa versión.

---

**9. ¿Cómo cito este repo?**

```bibtex
@software{lerer2026_816agentes,
  author = {Lerer, Ignacio Adrián},
  title  = {816 Agentes Institucionales Argentinos: Simulación EPT},
  year   = {2026},
  url    = {https://github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT},
  license = {AGPL-3.0}
}
```

O usar el archivo `CITATION.cff` incluido en el repo.

---

**10. ¿Cómo reporto un error o discrepancia?**

Abrir un issue en GitHub con:
1. Salida completa de `python run.py`
2. Salida de `python --version`
3. Salida de `pip show numpy pyyaml matplotlib`
4. Sistema operativo

Email alternativo: adrian@lerer.com.ar

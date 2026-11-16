# Guía de Diseño Frontend y Reglas Anti-AI-Slop (Bloque 6)

Este documento define las directrices visuales, de UX y de accesibilidad que regirán la implementación de la interfaz React + TypeScript en el Bloque 6, basadas en las skills instaladas en `.agents/skills/` (`frontend-design`, `impeccable`, `web-design-guidelines`).

---

## 1. Skills Locales Instaladas

Instaladas a nivel de proyecto en `.agents/skills/` (registradas en `skills-lock.json`):
1. `anthropics/skills@frontend-design` -> `.agents/skills/frontend-design/`
2. `vercel-labs/agent-skills@web-design-guidelines` -> `.agents/skills/web-design-guidelines/`
3. `pbakaus/impeccable@impeccable` -> `.agents/skills/impeccable/`

---

## 2. Patrones "AI Slop" Vetados (Prohibición Estricta)

Basado en las referencias de `frontend-design`, `impeccable` (`operate.md`, `distill.md`) y la auditoría de interfaces generadas por IA, queda estrictamente prohibido:

1. **Estética SaaS genérica:**
   - Gradientes púrpura/cian/índigo, brillos neón, fondos oscuros por defecto (`#000`/`#09090b`) con texto gris de bajo contraste, o paneles *glassmorphism* (`backdrop-blur`) con orbes decorativos.
   - Clichés actuales de IA: fondo crema cálido (`#F4F1EA`) con acento terracota (`#D97757`) y tipografía serif editorial en una herramienta de trabajo diario.
2. **Cardocalypse y anidamiento excesivo:**
   - Rejillas simétricas de tarjetas con iconos decorativos gigantes en cajas redondeadas.
   - Tarjetas anidadas dentro de tarjetas o bordes/sombras repetitivas alrededor de contenido trivial; usar espaciado, alineación y divisores `1px` limpios.
3. **Ruido textual y cromado de plantilla:**
   - Textos introductorios redundantes ("Bienvenido a tu gestor...", descripciones obvias bajo cada título).
   - *Eyebrows* en `ALL-CAPS` encima de cada cabecera, separadores con puntos medios (`A · B · C`), flechas `→` añadidas sistemáticamente en botones, o resaltar una sola palabra del título en otro color/cursiva.
   - Métricas falsas o de relleno.
4. **Animación gratuita y fricción modal:**
   - Transiciones *fade-and-slide-up* en cascada al cargar la página, o escalado/rebote en *hover* sobre tarjetas. El movimiento solo confirma acciones o cambios de estado (`150–200ms`, respetando `prefers-reduced-motion`).
   - Modales innecesarios para flujos de creación simples; priorizar formularios inline y divulgación progresiva.

---

## 3. Dirección de Diseño (Modo Operate — Herramienta de Trabajo)

### Sistema de Tokens Visuales
- **Superficies y Bordes:**
  - Lienzo principal: `#F8FAFC`
  - Superficie activa (tablas, formularios, paneles de trabajo): `#FFFFFF`
  - Superficie secundaria (cabecera, cabeceras de tabla): `#F1F5F9`
  - Borde estructural sutil: `#E2E8F0` (`1px solid`)
- **Tipografía y Contraste:**
  - Familia única sans-serif (`DM Sans`, `system-ui`, `-apple-system`, `sans-serif`), con `font-variant-numeric: tabular-nums` en puntuaciones, porcentajes, duraciones y días restantes.
  - Escala fija en `rem` (ratio compacto ~`1.2`: `1.5rem` título principal, `1.125rem` sección, `0.9375rem` cuerpo, `0.8125rem` metadatos).
  - Tinta principal `#0F172A`, tinta secundaria `#475569`.
- **Paleta de Acción y Estados Semánticos (siempre acompañados de texto, nunca solo color):**
  - Acción primaria: `#1D4ED8` (hover `#1E40AF`, texto `#FFFFFF`)
  - Éxito / Mejora (`SUCCESS`, `IMPROVING`, riesgo `LOW`): `#15803D` sobre `#DCFCE7`
  - Parcial / Atención (`PARTIAL`, `STAGNANT`, riesgo `MEDIUM`): `#B45309` sobre `#FEF3C7`
  - Fallo / Crítico (`FAILURE`, `REGRESSING`, riesgo `HIGH`): `#B91C1C` sobre `#FEE2E2`

---

## 4. Checklist de Calidad y Accesibilidad para el Bloque 6

- [ ] **Jerarquía y Cero Relleno:** Máximo 1 acción primaria clara por pantalla; sin párrafos explicativos redundantes ni iconos puramente decorativos.
- [ ] **Eficiencia Post-Clase (`RecordSessionPage`):** Registro de múltiples intentos con selección directa de ejercicio, selector segmentado `Acierto | Parcial | Fallo` y campo condicional `Causa del error` visible solo cuando aplica (`PARTIAL` o `FAILURE`).
- [ ] **Estados Completos:** Toda vista conectada a API implementa estados explícitos de carga (`skeleton`/indicador accesible), error accionable (con reintento/mensaje claro) y vacío útil (invitando a la primera acción).
- [ ] **Accesibilidad Semántica:** Uso estricto de `<main>`, `<nav>`, `<section>`, `<button>`, `<label htmlFor>`, `role="alert"` / `aria-live`, foco visible por teclado y contraste WCAG AA.
- [ ] **Frontera TDD UI:** Los tests en `@testing-library/react` validan exclusivamente conducta visible, flujos completos y roles/etiquetas accesibles (`getByRole`, `getByLabelText`), sin aserciones sobre clases CSS cosméticas (`toHaveClass`).

# Ruta Capital Asesores de Inversión

**Abrir la aplicación:** https://gaopyme-prog.github.io/asesor-inversion-demo/

> Herramienta académica. No constituye asesoría ni recomendación profesional de inversión. Rentabilidades pasadas no garantizan rentabilidades futuras.

## ¿Qué es?
Un simulador web de asesoría de inversión en la **Bolsa de Valores de Colombia**, con **datos reales** de las acciones más negociadas, que se actualizan solos cada día hábil. Es el producto del proyecto de aula de **Mercado de Capitales** de los estudiantes de Administración de Negocios Internacionales de UNIPAZ.

## ¿Para qué sirve? (finalidad)
- **Para el estudiante:** aplicar en un caso real lo visto en clase (perfil de riesgo, rentabilidad, volatilidad, valor del dinero en el tiempo) y practicar el rol de **asesor financiero** frente a un "cliente".
- **Para el público:** entender, en lenguaje sencillo, cuánto riesgo tiene invertir en acciones frente a un CDT, y qué podría pasar con su dinero en tres escenarios.

**Dirigido a:** estudiantes y docentes de negocios, finanzas y economía, y a la comunidad en general como herramienta de educación financiera.

## ¿Cómo funciona? Tres pasos
1. **Conozcamos su perfil:** cuestionario de 5 preguntas que clasifica al inversionista (conservador, moderado, etc.) y le advierte qué tanto de su dinero debería ir a acciones.
2. **Acciones más populares de Colombia:** tabla con 8 acciones (Ecopetrol, Grupo Cibest ordinaria y preferencial, ISA, Grupo Éxito, Grupo Aval preferencial, Grupo Energía Bogotá y Celsia) con precio, variación del día, rentabilidad a 1 y 3 años, volatilidad, caída máxima, dividendo y nivel de riesgo. Al tocar una acción se ve su gráfico mensual de los últimos 3 años. También muestra la **TRM** del día.
3. **Simulador de inversión:** el usuario elige una acción o una canasta y calcula:
   - ¿Cuánto tendré? · ¿Cuánto invertir hoy? · ¿En cuánto tiempo llego a mi meta? · ¿Cuánto ahorrar al mes?
   - Muestra escenarios **pesimista, esperado y optimista**, la ganancia estimada, la comparación con un **CDT**, la rentabilidad real descontando la **inflación** y cuántas acciones alcanza a comprar hoy.
   - El resultado se puede **imprimir o guardar en PDF**.

## Actualización automática de datos
Un proceso automático de GitHub (GitHub Actions) se ejecuta **de lunes a viernes a las 5:00 p. m. (hora de Colombia)**: descarga los precios de Yahoo Finance, calcula los indicadores y publica de nuevo la página. La fecha de corte se muestra debajo de la tabla.

## Archivos del repositorio
| Archivo | Función |
|---|---|
| `index.html` | La aplicación |
| `datos.json` | Datos de las acciones y la TRM (se regenera solo) |
| `actualizar_datos.py` | Descarga los datos y calcula rentabilidad, volatilidad, caída máxima y dividendos |
| `.github/workflows/actualizar.yml` | Programa la actualización diaria y la publicación |

## Personalización
En la sección "Su equipo asesor" se escriben los nombres de los estudiantes que presentan el proyecto.

## Créditos
Proyecto de aula — Mercado de Capitales — UNIPAZ, Barrancabermeja, noviembre de 2026.
Docente: **Omar Guerrero Avilés** (omar.guerreroav@unipaz.edu.co). Desarrollado con apoyo de inteligencia artificial.

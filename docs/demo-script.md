# Guion de demo — SecondSay

Duración objetivo: **6–8 minutos**

## 1. Apertura — 30 segundos

### Qué decir

> Muchas organizaciones ya utilizan inteligencia artificial para proponer o asistir decisiones, pero el problema no termina cuando el modelo responde.
>
> Después necesitamos saber qué decidió la IA, qué terminó decidiendo una persona, dónde existen diferencias y qué podemos aprender de ellas.
>
> SecondSay es una capa de auditoría continua para ese proceso.

### Idea clave

SecondSay **no es un clasificador de seguros**.

El dominio de seguros es el escenario de demostración.

El producto es la capa de:

- trazabilidad;
- Human-in-the-loop;
- AI Quality;
- AI Governance operacional.

---

## 2. Enseñar la interfaz — 30 segundos

Abrir SecondSay.

Mostrar rápidamente las cuatro etapas:

```text
01 Nuevo caso
02 Decisión IA
03 Revisión humana
04 Resultado de auditoría
````

Y señalar también:

```text
Histórico de auditoría
```

### Qué decir

> La aplicación representa el ciclo completo: recibimos un caso, obtenemos una decisión estructurada de un modelo, una persona la revisa y SecondSay registra y audita cualquier diferencia.

---

## 3. Crear un caso — 1 minuto

Utilizar un caso sencillo y comprensible.

Ejemplo:

> Se ha roto una tubería en la cocina. El agua ha causado daños importantes y está afectando también a la vivienda del vecino inferior.

Pulsar:

```text
Analizar con IA
```

Mientras procesa:

> SecondSay no trabaja con texto libre sin control. Exige al modelo una salida estructurada que posteriormente validamos antes de aceptar.

---

## 4. Decisión de IA — 1 minuto

Mostrar:

* categoría;
* urgencia;
* departamento;
* resumen;
* justificación.

Después señalar las métricas:

* proveedor;
* modelo;
* latencia;
* tokens;
* coste.

### Qué decir

> Además de la decisión, guardamos contexto técnico de cada ejecución: proveedor, modelo, tokens, latencia y coste estimado.
>
> Esto permite que una decisión sea trazable incluso cuando en el futuro cambie el modelo o el proveedor.

Señalar también el UUID de la decisión.

### Idea clave

> La auditoría no parte de una decisión que envía otra vez el navegador. SecondSay persiste la decisión original y la identifica mediante este UUID.

---

## 5. Human Review — 1 minuto

Modificar de forma deliberada un campo.

Ejemplo:

```text
Departamento:
Responsabilidad Civil
→ Siniestros
```

Seleccionar un impacto apropiado, por ejemplo:

```text
MEDIO
```

Añadir opcionalmente una nota:

> La revisión operativa determina que debe gestionarlo Siniestros.

Pulsar:

```text
Registrar revisión
```

### Qué decir

> Aquí entra el experto humano. Puede confirmar la propuesta o modificarla.
>
> Si existe una diferencia operativa, SecondSay exige registrar también su impacto.

---

## 6. Resultado de auditoría — 45 segundos

Mostrar:

```text
Discrepancia detectada
Campos modificados
Impacto registrado
```

### Qué decir

> El Audit Engine compara únicamente los campos que consideramos operativos: categoría, urgencia y departamento.
>
> Hay una distinción importante: una discrepancia no significa automáticamente que el modelo se haya equivocado.
>
> La persona puede disponer de contexto adicional, políticas internas o criterios de negocio que el modelo no conocía.

Esta frase es importante para defender la semántica del producto.

---

## 7. Histórico — 1 minuto

Bajar hasta:

```text
Histórico de auditoría
```

Mostrar varias filas.

Señalar:

* Groq;
* Ollama;
* latencias;
* decisiones pendientes de revisión;
* decisiones con discrepancia;
* impacto;
* campos modificados.

### Qué decir

> Aquí es donde SecondSay empieza a dejar de ser una simple aplicación de inferencia.
>
> Las decisiones y auditorías permanecen registradas y podemos ver cómo se comporta el sistema a lo largo del tiempo.
>
> Esto proporciona la base para detectar patrones, comparar modelos y construir evaluación continua.

No afirmar que Pattern Detection ya existe.

---

## 8. Cloud vs local — 1 minuto

En el bloque **Nuevo caso**, señalar el selector:

```text
Cloud · Groq
Local · Ollama
```

Si el tiempo de demo lo permite, ejecutar el mismo caso primero con Groq y
después con Ollama. Si Ollama tarda demasiado, utilizar una ejecución local ya
persistida en el histórico.

Después señalar la sección **Cloud vs local**, que agrega por proveedor/modelo:

* ejecuciones;
* latencia media;
* coste medio de API;
* decisiones con revisión humana;
* tasa de discrepancia en decisiones revisadas.

### Qué decir

> SecondSay utiliza la misma arquitectura con dos estrategias reales de inferencia y puedo elegir el proveedor para cada ejecución sin reiniciar el backend.
>
> Con Groq tenemos una ejecución cloud y una latencia cercana a un segundo en nuestras pruebas.
>
> Con Ollama ejecutamos `qwen3:4b-instruct` localmente. En nuestro hardware la latencia es mayor, pero obtenemos más control sobre dónde se procesan los datos y no existe coste directo de API.

> El histórico permite comparar ambos proveedores. La tasa de discrepancia es una señal de alineación con la revisión humana, no una métrica automática de error o accuracy.

Señalar en la interfaz:

```text
Sin coste de API
```

### Aclaración

> Eso no significa coste total cero: siguen existiendo hardware y consumo energético.

### Mensaje comercial

> La decisión no siempre es qué modelo es más rápido, sino qué combinación de privacidad, control, coste, latencia y comportamiento observado encaja mejor en cada flujo.

---

## 9. Arquitectura — 45 segundos

Abrir:

```text
docs/architecture.md
```

Mostrar brevemente el diagrama general.

### Qué decir

> La aplicación está construida como un monolito modular.
>
> La lógica de negocio no depende directamente de Groq ni de Ollama, sino de una abstracción común de proveedor.
>
> Esto nos permite cambiar o añadir modelos sin reescribir el flujo de auditoría.

Señalar:

```text
React
→ FastAPI
→ TriageService
→ LLMProvider
→ Groq / Ollama
→ PostgreSQL
→ Human Review
→ Audit Engine
```

---

## 10. Cierre — 30 segundos

### Qué decir

> SecondSay responde a una pregunta sencilla:
>
> ¿Qué está haciendo nuestra IA, dónde discrepa de nuestros expertos y qué podemos aprender de esas diferencias?
>
> Hoy ya tenemos inferencia cloud y local, decisiones estructuradas, trazabilidad, revisión humana, auditoría, métricas, PostgreSQL e histórico.
>
> El siguiente paso natural es convertir ese histórico en evaluación agregada: detectar patrones, comparar modelos y reutilizar casos auditados como una suite de regresión para sistemas de IA.

---

# Plan B de demo

La demo no debe depender completamente de servicios externos.

Si Groq no responde durante la presentación:

* utilizar datos ya persistidos en el histórico;
* mostrar decisiones reales anteriores;
* enseñar métricas y auditorías existentes;
* explicar la arquitectura cloud/local.

Si Ollama tarda demasiado:

* no esperar toda la inferencia delante del jurado;
* mostrar una ejecución Ollama previamente persistida;
* utilizarla para explicar el trade-off cloud/local.

Si un servicio falla:

> La trazabilidad permanece disponible porque SecondSay persiste decisiones y auditorías independientemente del proveedor utilizado.

---

# Preguntas difíciles

## ¿Una discrepancia significa que el modelo se equivocó?

No.

SecondSay registra una diferencia entre la propuesta de IA y la decisión humana final.

La diferencia puede deberse a:

* contexto adicional;
* reglas internas;
* criterios de negocio;
* políticas;
* información externa.

El producto ayuda a medir y analizar esas diferencias antes de atribuir su causa.

## ¿Por qué utilizar un modelo local si es más lento?

Porque velocidad no es el único criterio.

Una opción local puede aportar:

* mayor control sobre los datos;
* infraestructura propia;
* privacidad;
* ausencia de coste directo de API.

SecondSay permite conservar métricas para estudiar esos trade-offs.

## ¿Por qué PostgreSQL?

Porque necesitamos persistencia real y trazabilidad entre:

```text
caso
→ decisión IA
→ revisión humana
→ auditoría
```

Además permite construir histórico y futuras métricas agregadas.

## ¿Por qué no utilizar directamente la decisión que devuelve el navegador para auditar?

Porque podría haber sido modificada.

La revisión humana referencia `ai_decision_id` y el backend recupera la decisión IA original desde PostgreSQL.

## ¿Por qué Groq y Ollama?

No se presentan necesariamente como los proveedores definitivos del producto.

Demuestran que la arquitectura puede ejecutar la misma vertical con:

```text
infraestructura cloud
vs
infraestructura local
```

sin acoplar la lógica central a un único proveedor.

## ¿Qué falta?

Actualmente forman parte del roadmap:

* multimodalidad;
* simulador externo;
* Pattern Detection;
* Evaluation Lab;
* comparación simultánea de modelos;
* replay histórico;
* AI regression testing;
* despliegue público.

No deben presentarse como funcionalidades ya implementadas.

---

# Mensajes que deben quedar claros

1. SecondSay no es un chatbot.
2. SecondSay no es únicamente un clasificador de seguros.
3. La discrepancia no implica automáticamente error de IA.
4. La decisión original queda persistida y trazable.
5. Human Review y Audit Engine son el núcleo del producto.
6. Cloud y local son alternativas con trade-offs reales.
7. El histórico convierte ejecuciones individuales en la base para evaluación continua.

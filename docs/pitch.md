# Pitch de SecondSay

## Mensaje central

> SecondSay es una plataforma de auditoría continua que permite entender qué decide una IA, cuándo una persona modifica esa decisión y qué podemos aprender de esas diferencias.

SecondSay no pretende sustituir a los modelos de inteligencia artificial.

Se sitúa por encima de ellos como una capa de:

- trazabilidad;
- Human-in-the-loop;
- AI Quality;
- AI Governance operacional;
- evaluación continua.

---

# Pitch corto — 60–90 segundos

Las empresas están incorporando inteligencia artificial para ayudar a tomar decisiones, pero aparece un problema nuevo:

¿qué ocurre después de que el modelo responde?

Necesitamos saber qué decidió la IA, qué terminó decidiendo una persona, dónde existen diferencias y si esas diferencias se repiten.

Para eso hemos creado **SecondSay**.

SecondSay registra las decisiones de los modelos, sus métricas de ejecución y las compara con la revisión humana final.

No asumimos que una discrepancia signifique automáticamente que la IA se haya equivocado. La diferencia puede deberse a contexto adicional, políticas internas o criterios de negocio.

Actualmente podemos ejecutar la misma vertical con un proveedor cloud, Groq, o con un modelo local mediante Ollama.

Esto nos permite observar trade-offs reales entre latencia, privacidad, control de infraestructura y coste de API.

Cada decisión queda persistida y trazable en PostgreSQL, junto con su revisión humana, impacto y campos modificados.

Además, el histórico permite empezar a observar el comportamiento del sistema a lo largo del tiempo.

SecondSay no es otro chatbot ni un clasificador de seguros.

Es una capa de control y aprendizaje continuo para organizaciones que necesitan confiar mejor en los sistemas de IA que ya utilizan.

---

# Pitch completo — aproximadamente 3 minutos

Cada vez más organizaciones utilizan inteligencia artificial para proponer o asistir decisiones operativas.

Pero desplegar un modelo no resuelve todo el problema.

Después aparecen preguntas importantes:

- ¿qué decidió exactamente la IA?
- ¿qué terminó decidiendo la persona responsable?
- ¿qué partes cambió?
- ¿qué impacto tuvo esa diferencia?
- ¿qué proveedor o modelo produjo la decisión?
- ¿cuánto tardó?
- ¿qué coste tuvo?
- ¿se repiten determinadas discrepancias?

Para responder a esas preguntas hemos creado **SecondSay**.

SecondSay es una plataforma de auditoría continua de decisiones de inteligencia artificial.

Su función no es sustituir al modelo que utiliza una empresa, sino situarse como una capa de control entre los sistemas de IA y los equipos humanos.

El flujo comienza cuando llega un caso.

Un modelo genera una decisión estructurada con categoría, urgencia, departamento, resumen y justificación.

SecondSay valida esa respuesta, registra métricas como proveedor, modelo, tokens, latencia y coste estimado, y persiste la decisión original en PostgreSQL.

Después entra la persona.

Puede confirmar la propuesta de IA o modificarla.

Cuando existe una diferencia, nuestro Audit Engine identifica exactamente qué campos han cambiado y registra también el impacto de esa discrepancia.

Hay una decisión semántica importante en el producto:

**discrepancia no significa automáticamente error del modelo**.

Una persona puede cambiar una decisión por contexto adicional, una política interna, información externa o un criterio operativo.

SecondSay registra la evidencia antes de atribuir la causa.

Actualmente la plataforma funciona con dos estrategias reales de inferencia.

Por un lado utilizamos Groq con `openai/gpt-oss-20b`.

Por otro, Ollama con `qwen3:4b-instruct` ejecutado localmente.

Esto nos permite mostrar un trade-off real.

La opción cloud presenta una latencia mucho menor en nuestras pruebas.

La opción local es más lenta en nuestro hardware, pero permite mantener la inferencia dentro de infraestructura controlada y no tiene coste directo de API.

SecondSay conserva esas métricas para que esa decisión pueda tomarse con evidencia y no solo por intuición.

Finalmente, toda esa información aparece en un histórico donde podemos ver decisiones, modelos, proveedores, latencias, revisiones y discrepancias.

Ahí está la evolución natural del producto.

Hoy auditamos decisiones individuales.

Mañana, ese histórico puede convertirse en una base para detectar patrones, comparar modelos, validar cambios y construir regresión de calidad para sistemas de IA.

En resumen:

SecondSay responde a una pregunta sencilla:

> ¿Qué está haciendo nuestra IA, dónde discrepa de nuestros expertos y qué podemos aprender de esas diferencias?

---

# Versión orientada a cliente no técnico

Imagine que su empresa utiliza inteligencia artificial para recomendar decisiones.

El problema no es solamente saber si el modelo funciona.

También necesita saber cuándo sus profesionales cambian esas recomendaciones y por qué merece la pena prestar atención a esas diferencias.

SecondSay registra cada decisión de IA, la compara con la decisión humana final y mantiene una trazabilidad completa de lo ocurrido.

Así puede empezar a descubrir dónde existen diferencias relevantes, qué modelos están interviniendo, cuánto tardan y qué coste tienen.

SecondSay no sustituye a sus sistemas de inteligencia artificial.

Los observa, los audita y ayuda a convertir su uso diario en conocimiento para mejorar.

---

# Propuesta de valor en una frase

> SecondSay convierte las diferencias entre decisiones de IA y decisiones humanas en trazabilidad y aprendizaje operativo.

Alternativa:

> SecondSay es la capa de auditoría que permite entender cómo se comporta una IA cuando entra en contacto con decisiones humanas reales.

---

# Problema → solución

## Problema

Una organización utiliza IA en procesos reales, pero pierde visibilidad sobre:

- qué decidió el modelo;
- qué cambió el humano;
- cuánto importa esa diferencia;
- qué modelo intervino;
- qué coste y latencia tuvo;
- si esos comportamientos se repiten.

## Solución

SecondSay aporta:

```text
Decisión IA
      ↓
Trazabilidad
      ↓
Revisión humana
      ↓
Auditoría
      ↓
Histórico
      ↓
Aprendizaje
````

---

# Diferenciadores actuales

SecondSay ya incorpora:

* inferencia cloud real;
* inferencia local real;
* structured outputs;
* validación Pydantic;
* persistencia PostgreSQL;
* Human Review;
* Audit Engine;
* trazabilidad por UUID;
* proveedor y modelo por ejecución;
* tokens;
* latencia;
* coste estimado;
* impacto de discrepancia;
* histórico de decisiones;
* comparación observable entre cloud y local;
* retry/backoff cloud;
* retry correctivo local.

---

# Cloud vs local

## Cloud

Groq con:

```text
openai/gpt-oss-20b
```

Aporta principalmente:

* menor latencia;
* infraestructura gestionada;
* acceso mediante API.

## Local

Ollama con:

```text
qwen3:4b-instruct
```

Aporta principalmente:

* procesamiento local;
* control sobre infraestructura;
* mayor privacidad potencial;
* ausencia de coste directo de API.

No significa coste total cero: siguen existiendo hardware, energía y mantenimiento.

---

# Lo que SecondSay NO es

SecondSay no es:

* un chatbot;
* únicamente un clasificador de seguros;
* un sistema que asume que el humano siempre tiene razón;
* una herramienta que etiqueta automáticamente cada discrepancia como error;
* un benchmark automático completo entre modelos, todavía;
* un sistema de Pattern Detection, todavía.

---

# Roadmap

Las siguientes capacidades forman parte de la evolución prevista y no deben presentarse como ya implementadas:

* Pattern Detection;
* Evaluation Lab;
* comparación simultánea entre modelos;
* AI regression testing;
* replay histórico;
* multimodalidad;
* simulador externo;
* dashboard analítico agregado;
* despliegue público.

---

# Respuestas rápidas para preguntas del jurado

## ¿Por qué SecondSay y no simplemente guardar logs?

Porque un log registra eventos técnicos.

SecondSay modela explícitamente la relación entre:

```text
caso
→ decisión IA
→ revisión humana
→ discrepancia
→ impacto
```

y permite convertir esa relación en información auditable.

## ¿Por qué no considerar siempre correcta la decisión humana?

Porque el objetivo es observar diferencias, no asignar culpabilidad automáticamente.

La revisión humana también puede estar condicionada por políticas, contexto o criterios operativos.

## ¿Qué aporta PostgreSQL?

Persistencia real y relaciones trazables entre casos, decisiones IA y auditorías.

También proporciona la base para construir histórico y futuras métricas agregadas.

## ¿Es específico de seguros?

No.

Seguros es el dominio de demostración.

El núcleo de auditoría está desacoplado del perfil de dominio.

## ¿Por qué dos modelos?

Para demostrar que la arquitectura no depende de un único proveedor y que podemos observar trade-offs reales entre cloud y local.

## ¿Qué venderíais realmente?

Una capa de observabilidad y control para organizaciones que ya utilizan modelos de IA dentro de procesos con supervisión humana.

---

# Cierre recomendado

> El valor de una IA no termina cuando genera una respuesta.
>
> Empieza cuando podemos observar qué ocurre con esa respuesta en el mundo real.
>
> SecondSay convierte esa interacción entre IA y personas en trazabilidad, evidencia y aprendizaje continuo.

import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

const urgencyOptions = ['BAJA', 'MEDIA', 'ALTA', 'CRÍTICA']
const impactOptions = ['BAJO', 'MEDIO', 'ALTO', 'CRÍTICO']

async function fetchHistory() {
  const response = await fetch('/api/v1/cases/history')

  if (!response.ok) {
    throw new Error('No se pudo cargar el histórico.')
  }

  return response.json()
}

function App() {
  const [content, setContent] = useState('')
  const [llmMode, setLlmMode] = useState('cloud')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const [finalCategory, setFinalCategory] = useState('')
  const [finalUrgency, setFinalUrgency] = useState('')
  const [finalDepartment, setFinalDepartment] = useState('')
  const [reviewNote, setReviewNote] = useState('')
  const [discrepancyImpact, setDiscrepancyImpact] = useState('')
  const [auditResult, setAuditResult] = useState(null)
  const [auditError, setAuditError] = useState('')
  const [isReviewing, setIsReviewing] = useState(false)

  const [history, setHistory] = useState([])
  const [historyError, setHistoryError] = useState('')
  const [isHistoryLoading, setIsHistoryLoading] = useState(true)

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchHistory()
      setHistory(data)
      setHistoryError('')
    } catch {
      setHistoryError(
        'No se pudo cargar el histórico de auditoría.',
      )
    } finally {
      setIsHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    let isCancelled = false

    fetchHistory()
      .then((data) => {
        if (!isCancelled) {
          setHistory(data)
          setHistoryError('')
        }
      })
      .catch(() => {
        if (!isCancelled) {
          setHistoryError('No se pudo cargar el histórico de auditoría.')
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setIsHistoryLoading(false)
        }
      })

    return () => {
      isCancelled = true
    }
  }, [])

  const hasReviewDiscrepancy =
    result !== null &&
    (finalCategory.trim() !== result.decision.category ||
      finalUrgency !== result.decision.urgency ||
      finalDepartment.trim() !== result.decision.department)

  const providerComparison = useMemo(() => {
    const grouped = new Map()

    history.forEach((item) => {
      const key = `${item.provider}:${item.model}`
      const current = grouped.get(key) || {
        provider: item.provider,
        model: item.model,
        runs: 0,
        totalLatencyMs: 0,
        totalEstimatedCost: 0,
        reviewed: 0,
        discrepancies: 0,
      }

      current.runs += 1
      current.totalLatencyMs += item.latency_ms
      current.totalEstimatedCost += item.estimated_cost

      if (item.has_discrepancy !== null) {
        current.reviewed += 1

        if (item.has_discrepancy) {
          current.discrepancies += 1
        }
      }

      grouped.set(key, current)
    })

    return Array.from(grouped.values()).map((item) => ({
      ...item,
      averageLatencyMs: item.totalLatencyMs / item.runs,
      averageEstimatedCost: item.totalEstimatedCost / item.runs,
      discrepancyRate:
        item.reviewed > 0
          ? (item.discrepancies / item.reviewed) * 100
          : null,
    }))
  }, [history])

  async function handleSubmit(event) {
    event.preventDefault()

    if (!content.trim()) {
      setError('Introduce una descripción del caso.')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)
    setAuditResult(null)
    setAuditError('')

    try {
      const response = await fetch(
        `/api/v1/cases/triage?llm_mode=${llmMode}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: content.trim() }),
        },
      )

      if (!response.ok) {
        throw new Error('No se pudo analizar el caso.')
      }

      const data = await response.json()

      setResult(data)
      setFinalCategory(data.decision.category)
      setFinalUrgency(data.decision.urgency)
      setFinalDepartment(data.decision.department)
      setReviewNote('')
      setDiscrepancyImpact('')
      await loadHistory()
    } catch {
      setError(
        'No se pudo conectar con SecondSay. Comprueba que el backend está disponible.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  async function handleReviewSubmit(event) {
    event.preventDefault()

    if (!result) {
      return
    }

    if (!finalCategory.trim() || !finalUrgency || !finalDepartment.trim()) {
      setAuditError('Completa los campos obligatorios de la revisión.')
      return
    }

    if (hasReviewDiscrepancy && !discrepancyImpact) {
      setAuditError(
        'Indica el impacto de la discrepancia antes de guardar la revisión.',
      )
      return
    }

    setIsReviewing(true)
    setAuditError('')
    setAuditResult(null)

    try {
      const response = await fetch('/api/v1/audits/review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ai_decision_id: result.ai_decision_id,
          human_review: {
            final_category: finalCategory.trim(),
            final_urgency: finalUrgency,
            final_department: finalDepartment.trim(),
            review_note: reviewNote.trim() || null,
            discrepancy_impact: hasReviewDiscrepancy
              ? discrepancyImpact
              : null,
          },
        }),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => null)

        throw new Error(
          body?.detail || 'No se pudo registrar la revisión humana.',
        )
      }

      const data = await response.json()
      setAuditResult(data)
      await loadHistory()
    } catch (reviewError) {
      setAuditError(reviewError.message)
    } finally {
      setIsReviewing(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI Decision Audit</p>
          <h1>SecondSay</h1>
          <p className="subtitle">
            Audita decisiones de inteligencia artificial con supervisión humana.
          </p>
        </div>
        <span className="status-badge">Auditoría continua</span>
      </header>

      <section className="workspace">
        <div className="panel">
          <div className="section-heading">
            <span className="step">01</span>
            <div>
              <h2>Nuevo caso</h2>
              <p>Describe el incidente que debe evaluar el sistema de IA.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <label htmlFor="case-content">Descripción del caso</label>
            <textarea
              id="case-content"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="Ej. Se ha roto una tubería en la cocina y el agua está llegando al piso inferior."
              rows="8"
            />

            <label htmlFor="llm-mode">Proveedor de IA</label>
            <select
              id="llm-mode"
              value={llmMode}
              onChange={(event) => setLlmMode(event.target.value)}
              disabled={isLoading}
            >
              <option value="cloud">Cloud · Groq</option>
              <option value="local">Local · Ollama</option>
            </select>
            <p className="field-help">
              Cambia de proveedor para comparar el mismo caso sin reiniciar
              SecondSay.
            </p>

            {error && <p className="error-message">{error}</p>}

            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Analizando caso…' : 'Analizar con IA'}
            </button>
          </form>
        </div>

        <div className="panel result-panel">
          <div className="section-heading">
            <span className="step">02</span>
            <div>
              <h2>Decisión de IA</h2>
              <p>Resultado estructurado y métricas de la ejecución.</p>
            </div>
          </div>

          {!result && (
            <div className="empty-state">
              <p>La decisión aparecerá aquí después de analizar un caso.</p>
            </div>
          )}

          {result && (
            <>
              <div className="decision-grid">
                <article>
                  <span>Categoría</span>
                  <strong>{result.decision.category}</strong>
                </article>
                <article>
                  <span>Urgencia</span>
                  <strong>{result.decision.urgency}</strong>
                </article>
                <article>
                  <span>Departamento</span>
                  <strong>{result.decision.department}</strong>
                </article>
              </div>

              <div className="decision-copy">
                <h3>Resumen</h3>
                <p>{result.decision.summary}</p>

                <h3>Justificación</h3>
                <p>{result.decision.justification}</p>
              </div>

              <div className="metrics">
                <div>
                  <span>Proveedor</span>
                  <strong>{result.metrics.provider}</strong>
                </div>
                <div>
                  <span>Modelo</span>
                  <strong>{result.metrics.model}</strong>
                </div>
                <div>
                  <span>Latencia</span>
                  <strong>{Math.round(result.metrics.latency_ms)} ms</strong>
                </div>
                <div>
                  <span>Tokens</span>
                  <strong>
                    {result.metrics.input_tokens + result.metrics.output_tokens}
                  </strong>
                </div>
                <div>
                  {result.metrics.provider === "ollama" ? (
                    <>
                      <span>Coste de API</span>
                      <strong>Sin coste de API</strong>
                      <small className="metric-note">
                        No incluye hardware ni consumo energético
                      </small>
                    </>
                  ) : (
                    <>
                      <span>Coste teórico</span>
                      <strong>${result.metrics.estimated_cost.toFixed(6)}</strong>
                      <small className="metric-note">
                        Tarifa de referencia del proveedor
                      </small>
                    </>
                  )}
                </div>
              </div>

              <p className="trace-id">
                Decisión: <code>{result.ai_decision_id}</code>
              </p>
            </>
          )}
        </div>
      </section>

      {result && (
        <section className="audit-workspace">
          <div className="panel">
            <div className="section-heading">
              <span className="step">03</span>
              <div>
                <h2>Revisión humana</h2>
                <p>
                  Confirma la decisión o modifica los campos que requieran
                  criterio humano.
                </p>
              </div>
            </div>

            <form onSubmit={handleReviewSubmit}>
              <label htmlFor="final-category">Categoría final</label>
              <input
                id="final-category"
                value={finalCategory}
                onChange={(event) => setFinalCategory(event.target.value)}
              />

              <label htmlFor="final-urgency">Urgencia final</label>
              <select
                id="final-urgency"
                value={finalUrgency}
                onChange={(event) => setFinalUrgency(event.target.value)}
              >
                {urgencyOptions.map((urgency) => (
                  <option key={urgency} value={urgency}>
                    {urgency}
                  </option>
                ))}
              </select>

              <label htmlFor="final-department">Departamento final</label>
              <input
                id="final-department"
                value={finalDepartment}
                onChange={(event) => setFinalDepartment(event.target.value)}
              />

              <label htmlFor="review-note">Nota de revisión</label>
              <textarea
                id="review-note"
                value={reviewNote}
                onChange={(event) => setReviewNote(event.target.value)}
                placeholder="Añade contexto si resulta útil para la auditoría."
                rows="4"
              />

              <label htmlFor="discrepancy-impact">
                Impacto de la discrepancia
              </label>
              <select
                id="discrepancy-impact"
                value={discrepancyImpact}
                onChange={(event) => setDiscrepancyImpact(event.target.value)}
                disabled={!hasReviewDiscrepancy}
              >
                <option value="">
                  {hasReviewDiscrepancy
                    ? 'Selecciona un impacto'
                    : 'Sin discrepancia'}
                </option>
                {impactOptions.map((impact) => (
                  <option key={impact} value={impact}>
                    {impact}
                  </option>
                ))}
              </select>

              {auditError && <p className="error-message">{auditError}</p>}

              <button type="submit" disabled={isReviewing}>
                {isReviewing ? 'Registrando revisión…' : 'Registrar revisión'}
              </button>
            </form>
          </div>

          <div className="panel">
            <div className="section-heading">
              <span className="step">04</span>
              <div>
                <h2>Resultado de auditoría</h2>
                <p>
                  SecondSay registra la diferencia sin asumir automáticamente
                  que la IA se haya equivocado.
                </p>
              </div>
            </div>

            {!auditResult && (
              <div className="empty-state">
                <p>
                  El resultado aparecerá aquí después de registrar la revisión
                  humana.
                </p>
              </div>
            )}

            {auditResult && (
              <div className="audit-result">
                <div className="audit-summary">
                  <span>Estado</span>
                  <strong>
                    {auditResult.has_discrepancy
                      ? 'Discrepancia detectada'
                      : 'Sin discrepancias'}
                  </strong>
                </div>

                <div className="audit-summary">
                  <span>Campos modificados</span>
                  <strong>
                    {auditResult.changed_fields.length > 0
                      ? auditResult.changed_fields.join(', ')
                      : 'Ninguno'}
                  </strong>
                </div>

                <div className="audit-summary">
                  <span>Impacto registrado</span>
                  <strong>
                    {auditResult.human_review.discrepancy_impact || 'No aplica'}
                  </strong>
                </div>

                <p className="audit-message">
                  Una discrepancia representa una diferencia entre la propuesta
                  de IA y la decisión humana final. No implica por sí sola un
                  error del modelo.
                </p>
              </div>
            )}
          </div>
        </section>
      )}

      <section className="comparison-section">
        <div className="panel">
          <div className="history-heading">
            <div>
              <p className="eyebrow">Comparativa multi-proveedor</p>
              <h2>Cloud vs local</h2>
              <p>
                Compara ejecución, coste de API y una señal de calidad basada
                en la revisión humana.
              </p>
            </div>
          </div>

          {providerComparison.length === 0 ? (
            <div className="history-state">
              <p>
                Ejecuta casos con Groq y Ollama para construir la comparativa.
              </p>
            </div>
          ) : (
            <>
              <div className="history-table-wrapper">
                <table className="history-table comparison-table">
                  <thead>
                    <tr>
                      <th>Proveedor / modelo</th>
                      <th>Ejecuciones</th>
                      <th>Latencia media</th>
                      <th>Coste medio de API</th>
                      <th>Señal de calidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerComparison.map((item) => (
                      <tr key={`${item.provider}:${item.model}`}>
                        <td>
                          <strong>{item.provider}</strong>
                          <small>{item.model}</small>
                        </td>
                        <td>
                          <strong>{item.runs}</strong>
                          <small>
                            {item.reviewed} con revisión humana
                          </small>
                        </td>
                        <td>
                          <strong>
                            {Math.round(item.averageLatencyMs)} ms
                          </strong>
                        </td>
                        <td>
                          <strong>
                            {item.provider === 'ollama'
                              ? 'Sin coste de API'
                              : `$${item.averageEstimatedCost.toFixed(6)}`}
                          </strong>
                          {item.provider === 'ollama' && (
                            <small>
                              No incluye hardware ni consumo energético
                            </small>
                          )}
                        </td>
                        <td>
                          {item.discrepancyRate === null ? (
                            <>
                              <strong>Sin datos suficientes</strong>
                              <small>
                                Requiere al menos una revisión humana
                              </small>
                            </>
                          ) : (
                            <>
                              <strong>
                                {item.discrepancyRate.toFixed(0)}% discrepancia
                              </strong>
                              <small>
                                {item.discrepancies} de {item.reviewed}{' '}
                                decisiones revisadas
                              </small>
                            </>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p className="comparison-note">
                La tasa de discrepancia mide diferencias entre la propuesta de
                IA y la decisión humana final. No representa por sí sola un
                error del modelo ni una métrica de accuracy.
              </p>
            </>
          )}
        </div>
      </section>

      <section className="history-section">
        <div className="panel">
          <div className="history-heading">
            <div>
              <p className="eyebrow">Trazabilidad</p>
              <h2>Histórico de auditoría</h2>
              <p>
                Decisiones recientes, proveedor utilizado y resultado de la
                última revisión humana registrada.
              </p>
            </div>
            <span className="history-count">
              {history.length} {history.length === 1 ? 'decisión' : 'decisiones'}
            </span>
          </div>

          {isHistoryLoading && (
            <div className="history-state">
              <p>Cargando histórico…</p>
            </div>
          )}

          {historyError && <p className="error-message">{historyError}</p>}

          {!isHistoryLoading && !historyError && history.length === 0 && (
            <div className="history-state">
              <p>
                Todavía no hay decisiones persistidas para mostrar.
              </p>
            </div>
          )}

          {!isHistoryLoading && !historyError && history.length > 0 && (
            <div className="history-table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Proveedor / modelo</th>
                    <th>Decisión IA</th>
                    <th>Ejecución</th>
                    <th>Última auditoría</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.ai_decision_id}>
                      <td>
                        <strong>
                          {new Date(item.created_at).toLocaleDateString('es-ES')}
                        </strong>
                        <small>
                          {new Date(item.created_at).toLocaleTimeString(
                            'es-ES',
                            {
                              hour: '2-digit',
                              minute: '2-digit',
                            },
                          )}
                        </small>
                      </td>
                      <td>
                        <strong>{item.provider}</strong>
                        <small>{item.model}</small>
                      </td>
                      <td>
                        <strong>{item.category}</strong>
                        <small>
                          {item.urgency} · {item.department}
                        </small>
                      </td>
                      <td>
                        <strong>{Math.round(item.latency_ms)} ms</strong>
                        <small>
                          {item.provider === 'ollama'
                            ? 'Sin coste de API'
                            : `$${item.estimated_cost.toFixed(6)}`}
                        </small>
                      </td>
                      <td>
                        {item.has_discrepancy === null ? (
                          <>
                            <strong>Pendiente de revisión</strong>
                            <small>Sin auditoría humana registrada</small>
                          </>
                        ) : item.has_discrepancy ? (
                          <>
                            <strong>
                              Discrepancia · {item.discrepancy_impact}
                            </strong>
                            <small>
                              {item.changed_fields.length > 0
                                ? item.changed_fields.join(', ')
                                : 'Sin campos registrados'}
                            </small>
                          </>
                        ) : (
                          <>
                            <strong>Sin discrepancias</strong>
                            <small>Decisión confirmada por revisión humana</small>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

export default App

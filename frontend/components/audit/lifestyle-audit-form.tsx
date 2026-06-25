'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import axios from 'axios'

const SECTIONS = [
  { id: 'B', title: 'Sleep Audit', questions: 6 },
  { id: 'C', title: 'Food & Eating Habits', questions: 8 },
  { id: 'D', title: 'Movement & Activity', questions: 5 },
  { id: 'E', title: 'Stress & Emotional Health', questions: 5 },
  { id: 'F', title: 'Digestive & Functional Health', questions: 5 },
]

interface Question {
  id: string
  section: string
  number: number
  text: string
  type: 'select' | 'scale'
  options: Array<{ label: string; value: string; text: string }>
}

interface AuditResult {
  success: boolean
  score: number
  zone: string
  message: string
  critical_flags: string[]
  bnys_review_required: boolean
}

export function LifestyleAuditForm({ clientId }: { clientId: string }) {
  const [currentSection, setCurrentSection] = useState(0)
  const [questions, setQuestions] = useState<Question[]>([])
  const [responses, setResponses] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<AuditResult | null>(null)

  // Load questions on mount
  React.useEffect(() => {
    const loadQuestions = async () => {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/audit/questions`)
        setQuestions(response.data.questions)
        setLoading(false)
      } catch (error) {
        console.error('Failed to load audit questions:', error)
        setLoading(false)
      }
    }
    loadQuestions()
  }, [])

  const section = SECTIONS[currentSection]
  const sectionQuestions = questions.filter((q) => q.section === section.id)

  const handleResponse = (questionId: string, value: string) => {
    setResponses((prev) => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const auditResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/audit/submit/${clientId}`,
        responses
      )
      setResult(auditResponse.data)
    } catch (error) {
      console.error('Failed to submit audit:', error)
      alert('Failed to submit audit. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading audit questions...</div>
  }

  if (result) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Your Lifestyle Assessment Results</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <div className="text-5xl font-bold mb-2">{result.score.toFixed(1)}</div>
            <div className={`text-2xl font-semibold mb-4 p-2 rounded ${
              result.zone === 'Green' ? 'bg-green-100 text-green-800' :
              result.zone === 'Yellow' ? 'bg-yellow-100 text-yellow-800' :
              result.zone === 'Orange' ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              {result.zone} Zone
            </div>
            <p className="text-gray-600 mb-4">{result.message}</p>
          </div>

          {result.critical_flags.length > 0 && (
            <div className="bg-orange-50 p-4 rounded">
              <h3 className="font-semibold text-orange-900 mb-2">Critical Findings:</h3>
              <ul className="text-sm text-orange-800 space-y-1">
                {result.critical_flags.map((flag) => (
                  <li key={flag}>• {flag.replace(/_/g, ' ')}</li>
                ))}
              </ul>
            </div>
          )}

          {result.bnys_review_required && (
            <div className="bg-red-50 p-4 rounded">
              <p className="text-red-900 font-semibold">
                ⚠️ BNYS Review Recommended
              </p>
              <p className="text-sm text-red-800 mt-2">
                Based on your assessment, we recommend a consultation with our clinical team before starting the program.
              </p>
            </div>
          )}

          <Button onClick={() => window.location.reload()} className="w-full">
            Back to App
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Section Navigation */}
      <div className="flex gap-2 flex-wrap">
        {SECTIONS.map((s, idx) => (
          <Button
            key={s.id}
            variant={currentSection === idx ? 'default' : 'outline'}
            onClick={() => setCurrentSection(idx)}
            className="text-sm"
          >
            {s.id}: {s.title}
          </Button>
        ))}
      </div>

      {/* Questions */}
      <div className="space-y-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">{section.title}</h2>
          <p className="text-sm text-gray-600">
            Questions {sectionQuestions[0]?.number} - {sectionQuestions[sectionQuestions.length - 1]?.number}
          </p>
        </div>

        {sectionQuestions.map((q) => (
          <Card key={q.id} className="p-4">
            <div className="mb-4">
              <Label className="text-base font-medium">
                Q{q.number}: {q.text}
              </Label>
            </div>

            {q.type === 'select' && (
              <RadioGroup
                value={responses[q.id] || ''}
                onValueChange={(value) => handleResponse(q.id, value)}
              >
                <div className="space-y-3">
                  {q.options.map((option) => (
                    <div key={option.value} className="flex items-center space-x-3">
                      <RadioGroupItem value={option.value} id={`${q.id}-${option.value}`} />
                      <Label
                        htmlFor={`${q.id}-${option.value}`}
                        className="font-normal cursor-pointer flex-1"
                      >
                        <span className="font-semibold">{option.label}:</span> {option.text}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            )}

            {q.type === 'scale' && (
              <div className="space-y-3">
                <Slider
                  min={1}
                  max={10}
                  step={1}
                  value={responses[q.id] ? [parseInt(responses[q.id])] : [5]}
                  onValueChange={(value) => handleResponse(q.id, value[0].toString())}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 px-2">
                  <span>Very Low (1)</span>
                  <span className="font-semibold">{responses[q.id] || '5'}</span>
                  <span>Overwhelming (10)</span>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Navigation */}
      <div className="flex gap-2 justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
          disabled={currentSection === 0}
        >
          ← Previous Section
        </Button>

        {currentSection === SECTIONS.length - 1 ? (
          <Button
            onClick={handleSubmit}
            disabled={submitting || Object.keys(responses).length < questions.length}
            className="flex-1"
          >
            {submitting ? 'Calculating...' : 'Submit Assessment'}
          </Button>
        ) : (
          <Button
            onClick={() => setCurrentSection(currentSection + 1)}
            className="flex-1"
          >
            Next Section →
          </Button>
        )}
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { LifestyleAuditForm } from '@/components/audit/lifestyle-audit-form'

export default function LifestyleAuditPage() {
  const router = useRouter()
  const [clientId, setClientId] = useState<string>('')

  useEffect(() => {
    // Get client ID from localStorage
    const token = localStorage.getItem('token')
    const id = localStorage.getItem('client_id')

    if (!token || !id) {
      router.push('/')
      return
    }

    setClientId(id)
  }, [router])

  if (!clientId) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white pb-20 md:pb-0">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-dark mb-2">Lifestyle Assessment</h1>
          <p className="text-gray-600">
            Answer these questions honestly. This assessment takes 10-15 minutes and will help us understand your lifestyle patterns.
          </p>
        </div>

        <LifestyleAuditForm clientId={clientId} />
      </div>
    </div>
  )
}

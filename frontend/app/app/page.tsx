'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { Zap, Brain, PenTool, TrendingUp } from 'lucide-react'

export default function AppDashboard() {
  const router = useRouter()
  const [userName, setUserName] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const name = localStorage.getItem('user_name')

    if (!token) {
      router.push('/login')
      return
    }

    setUserName(name || 'User')
    setIsLoading(false)
  }, [router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="pt-8 pb-20 md:pb-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-12"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-dark mb-2">Welcome, {userName}! 🌿</h1>
          <p className="text-lg text-dark/60">
            Your journey to wholesome eating starts here
          </p>
        </div>
      </motion.div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        {/* Challenge Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Link href="/app/challenge">
            <Card className="h-full cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-secondary" />
                  <CardTitle>7-Day Challenge</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-dark/60">
                  Track your daily meals and maintain 85%+ consistency to unlock benefits
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Lifestyle Audit Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Link href="/app/lifestyle-audit">
            <Card className="h-full cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  <CardTitle>Lifestyle Audit</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-dark/60">
                  Complete your health assessment across sleep, food, movement, and stress
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Progress Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Link href="/app/challenge/progress">
            <Card className="h-full cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <CardTitle>Your Progress</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-dark/60">
                  View your compliance score and consistency metrics
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>
      </div>

      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
      >
        <Card className="bg-gradient-to-br from-primary/5 to-secondary/5">
          <CardHeader>
            <CardTitle className="text-2xl">How It Works</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-3">
                  1
                </div>
                <h3 className="font-semibold text-dark mb-2">Log Your Meals</h3>
                <p className="text-sm text-dark/60">
                  Upload photos and details of your meals for 7 days
                </p>
              </div>
              <div>
                <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-3">
                  2
                </div>
                <h3 className="font-semibold text-dark mb-2">Complete Assessment</h3>
                <p className="text-sm text-dark/60">
                  Answer lifestyle questions to understand your health patterns
                </p>
              </div>
              <div>
                <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold mb-3">
                  3
                </div>
                <h3 className="font-semibold text-dark mb-2">Get Results</h3>
                <p className="text-sm text-dark/60">
                  Receive personalized insights and unlock exclusive benefits
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

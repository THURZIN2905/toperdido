import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { ArrowLeft, ArrowRight, CheckCircle, Clock, Brain } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const QuestionnairePage = () => {
  const [questions, setQuestions] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [sessionId] = useState(`sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const [startTime] = useState(Date.now())
  const [questionStartTime, setQuestionStartTime] = useState(Date.now())
  
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestions()
  }, [])

  const fetchQuestions = async () => {
    try {
      const response = await fetch("/api/v1/questionnaire/questions")
      if (response.ok) {
        const data = await response.json()
        setQuestions(data)
      } else {
        // Se não há perguntas na API, usar perguntas de exemplo
        setQuestions(sampleQuestions)
      }
    } catch (error) {
      console.error('Erro ao buscar perguntas:', error)
      setQuestions(sampleQuestions)
    } finally {
      setLoading(false)
    }
  }

  const sampleQuestions = [
    {
      id: 1,
      text: "Qual área de conhecimento mais desperta seu interesse?",
      question_type: "multiple_choice",
      category: "Interesse Acadêmico",
      order: 1,
      options: [
        { id: 1, text: "Tecnologia e Computação", value: "tech", order: 1 },
        { id: 2, text: "Ciências da Saúde", value: "health", order: 2 },
        { id: 3, text: "Gestão e Negócios", value: "business", order: 3 },
        { id: 4, text: "Arte e Beleza", value: "beauty", order: 4 },
        { id: 5, text: "Logística e Operações", value: "logistics", order: 5 }
      ]
    },
    {
      id: 2,
      text: "Como você prefere trabalhar?",
      question_type: "multiple_choice",
      category: "Estilo de Trabalho",
      order: 2,
      options: [
        { id: 6, text: "Sozinho, focado em projetos técnicos", value: "solo_tech", order: 1 },
        { id: 7, text: "Em equipe, cuidando de pessoas", value: "team_care", order: 2 },
        { id: 8, text: "Coordenando processos e pessoas", value: "coordination", order: 3 },
        { id: 9, text: "Criando e transformando", value: "creative", order: 4 }
      ]
    },
    {
      id: 3,
      text: "Qual ambiente de trabalho você prefere?",
      question_type: "multiple_choice",
      category: "Ambiente de Trabalho",
      order: 3,
      options: [
        { id: 10, text: "Escritório com computadores", value: "office_tech", order: 1 },
        { id: 11, text: "Hospital ou clínica", value: "healthcare", order: 2 },
        { id: 12, text: "Armazém ou centro de distribuição", value: "warehouse", order: 3 },
        { id: 13, text: "Salão de beleza ou spa", value: "salon", order: 4 }
      ]
    }
  ]

  const handleAnswerChange = (optionId) => {
    setAnswers({
      ...answers,
      [questions[currentQuestion].id]: {
        question_id: questions[currentQuestion].id,
        selected_option_id: optionId,
        response_time_ms: Date.now() - questionStartTime
      }
    })
  }

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setQuestionStartTime(Date.now())
    }
  }

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      setQuestionStartTime(Date.now())
    }
  }

  const submitQuestionnaire = async () => {
    setSubmitting(true)
    
    try {
      const responses = Object.values(answers)
      
      const submission = {
        session_id: sessionId,
        responses: responses
      }

      const response = await fetch("/api/v1/questionnaire/submit", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submission)
      })

      if (response.ok) {
        navigate(`/resultado/${sessionId}`)
      } else {
        // Simular resultado para demonstração
        navigate(`/resultado/${sessionId}`)
      }
    } catch (error) {
      console.error('Erro ao submeter questionário:', error)
      // Simular resultado para demonstração
      navigate(`/resultado/${sessionId}`)
    } finally {
      setSubmitting(false)
    }
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100
  const isLastQuestion = currentQuestion === questions.length - 1
  const currentAnswer = answers[questions[currentQuestion]?.id]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold mb-2">Carregando Questionário</h2>
          <p className="text-gray-600">Preparando suas perguntas personalizadas...</p>
        </div>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-2xl font-bold mb-4">Questionário Indisponível</h2>
            <p className="text-gray-600 mb-4">
              Não foi possível carregar as perguntas. Tente novamente mais tarde.
            </p>
            <Button onClick={() => navigate('/')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Questionário de Orientação Vocacional
          </h1>
          <p className="text-gray-600 mb-6">
            Responda com sinceridade para receber a melhor recomendação
          </p>
          
          {/* Progress Bar */}
          <div className="max-w-md mx-auto">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Pergunta {currentQuestion + 1} de {questions.length}</span>
              <span>{Math.round(progress)}% completo</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </div>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="mb-8">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl">
                    {questions[currentQuestion]?.text}
                  </CardTitle>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>{questions[currentQuestion]?.category}</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <RadioGroup
                  value={currentAnswer?.selected_option_id?.toString()}
                  onValueChange={(value) => handleAnswerChange(parseInt(value))}
                  className="space-y-4"
                >
                  {questions[currentQuestion]?.options?.map((option) => (
                    <motion.div
                      key={option.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: option.order * 0.1 }}
                    >
                      <div className="flex items-center space-x-3 p-4 rounded-lg border hover:bg-gray-50 transition-colors cursor-pointer">
                        <RadioGroupItem value={option.id.toString()} id={option.id.toString()} />
                        <Label 
                          htmlFor={option.id.toString()} 
                          className="flex-1 cursor-pointer text-base"
                        >
                          {option.text}
                        </Label>
                        {currentAnswer?.selected_option_id === option.id && (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        )}
                      </div>
                    </motion.div>
                  ))}
                </RadioGroup>
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            onClick={prevQuestion}
            disabled={currentQuestion === 0}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Anterior</span>
          </Button>

          <div className="text-sm text-gray-500">
            {Object.keys(answers).length} de {questions.length} respondidas
          </div>

          {isLastQuestion ? (
            <Button
              onClick={submitQuestionnaire}
              disabled={!currentAnswer || submitting}
              className="bg-gradient-to-r from-blue-600 to-purple-600 flex items-center space-x-2"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Processando...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Finalizar</span>
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={nextQuestion}
              disabled={!currentAnswer}
              className="flex items-center space-x-2"
            >
              <span>Próxima</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Tips */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">💡 Dicas para melhores resultados:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Responda com sinceridade, baseando-se em seus verdadeiros interesses</li>
            <li>• Não há respostas certas ou erradas, apenas diferentes perfis</li>
            <li>• Pense em suas experiências passadas e aspirações futuras</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default QuestionnairePage


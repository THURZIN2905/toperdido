# Especificações Técnicas do Frontend
## Interface "Caminhos Conscientes"

**Autor:** Manus AI  
**Data:** 6 de novembro de 2025  
**Versão:** 1.0

---

## 1. Visão Geral do Frontend

O frontend do sistema "Caminhos Conscientes" é uma aplicação Next.js moderna, construída com TypeScript e Tailwind CSS, oferecendo uma experiência de usuário excepcional, totalmente responsiva e acessível. A aplicação implementa as melhores práticas de desenvolvimento frontend, incluindo otimizações de performance, SEO e acessibilidade.

### 1.1 Características Principais

- **Framework:** Next.js 14+ com App Router
- **Linguagem:** TypeScript para type safety
- **Estilização:** Tailwind CSS 3+ com design system
- **Componentes:** Radix UI para acessibilidade
- **Animações:** Framer Motion para transições
- **Gráficos:** Recharts para visualizações
- **Formulários:** React Hook Form + Zod
- **Estado:** Zustand para gerenciamento global
- **Temas:** next-themes para dark/light mode

---

## 2. Estrutura de Componentes

### 2.1 Layout Components

#### AppLayout
```typescript
interface AppLayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
  className?: string;
}

export function AppLayout({ 
  children, 
  showHeader = true, 
  showFooter = true, 
  className 
}: AppLayoutProps) {
  return (
    <div className={cn("min-h-screen flex flex-col", className)}>
      {showHeader && <Header />}
      <main className="flex-1">{children}</main>
      {showFooter && <Footer />}
      <VLibrasWidget />
    </div>
  );
}
```

#### Header
```typescript
interface HeaderProps {
  variant?: 'default' | 'transparent' | 'minimal';
}

export function Header({ variant = 'default' }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  
  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur",
      variant === 'transparent' && "bg-transparent border-transparent",
      variant === 'minimal' && "border-none"
    )}>
      <div className="container flex h-16 items-center justify-between">
        <Logo />
        <Navigation />
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <AccessibilityMenu />
          {user ? <UserMenu /> : <AuthButtons />}
        </div>
      </div>
    </header>
  );
}
```

### 2.2 UI Components

#### Button
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', loading, leftIcon, rightIcon, children, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {leftIcon && !loading && <span className="mr-2">{leftIcon}</span>}
        {children}
        {rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);
```

#### Input
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helper, leftIcon, rightIcon, ...props }, ref) => {
    const id = useId();
    
    return (
      <div className="space-y-2">
        {label && (
          <Label htmlFor={id} className={error ? "text-destructive" : ""}>
            {label}
          </Label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}
          <input
            id={id}
            className={cn(
              "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
              leftIcon && "pl-10",
              rightIcon && "pr-10",
              error && "border-destructive focus-visible:ring-destructive",
              className
            )}
            ref={ref}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {helper && !error && <p className="text-sm text-muted-foreground">{helper}</p>}
      </div>
    );
  }
);
```

#### Card
```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
}

export function Card({ className, variant = 'default', ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-card text-card-foreground",
        variant === 'elevated' && "shadow-lg",
        variant === 'outlined' && "border-2",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-2xl font-semibold leading-none tracking-tight", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}
```

### 2.3 Form Components

#### QuestionCard
```typescript
interface QuestionCardProps {
  question: Question;
  selectedOption?: string;
  onOptionSelect: (optionId: string) => void;
  disabled?: boolean;
  showProgress?: boolean;
  currentStep?: number;
  totalSteps?: number;
}

export function QuestionCard({
  question,
  selectedOption,
  onOptionSelect,
  disabled = false,
  showProgress = false,
  currentStep,
  totalSteps
}: QuestionCardProps) {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      {showProgress && currentStep && totalSteps && (
        <CardHeader>
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Pergunta {currentStep} de {totalSteps}</span>
              <span>{Math.round((currentStep / totalSteps) * 100)}%</span>
            </div>
            <Progress value={(currentStep / totalSteps) * 100} className="h-2" />
          </div>
        </CardHeader>
      )}
      
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Badge variant="secondary">{question.category}</Badge>
          <h2 className="text-xl font-semibold leading-relaxed">
            {question.text}
          </h2>
        </div>
        
        <RadioGroup
          value={selectedOption}
          onValueChange={onOptionSelect}
          disabled={disabled}
          className="space-y-3"
        >
          {question.options.map((option) => (
            <div key={option.id} className="flex items-center space-x-2">
              <RadioGroupItem value={option.id} id={option.id} />
              <Label
                htmlFor={option.id}
                className="flex-1 cursor-pointer p-3 rounded-md border border-transparent hover:border-border hover:bg-muted/50 transition-colors"
              >
                {option.text}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </CardContent>
    </Card>
  );
}
```

#### ProgressBar
```typescript
interface ProgressBarProps {
  value: number;
  max?: number;
  showLabel?: boolean;
  label?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
  animated?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  showLabel = true,
  label,
  variant = 'default',
  animated = false
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className="space-y-2">
      {showLabel && (
        <div className="flex justify-between text-sm">
          <span>{label || 'Progresso'}</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="h-2 bg-secondary rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full transition-all duration-500 ease-out",
            variant === 'default' && "bg-primary",
            variant === 'success' && "bg-green-500",
            variant === 'warning' && "bg-yellow-500",
            variant === 'error' && "bg-red-500",
            animated && "animate-pulse"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
```

### 2.4 Chart Components

#### ResultChart
```typescript
interface ResultChartProps {
  data: {
    course: string;
    score: number;
    color: string;
  }[];
  recommended?: string;
  interactive?: boolean;
}

export function ResultChart({ data, recommended, interactive = true }: ResultChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | undefined>();
  
  return (
    <div className="space-y-4">
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="course" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="bg-background border rounded-lg p-3 shadow-lg">
                    <p className="font-semibold">{label}</p>
                    <p className="text-primary">
                      Pontuação: {payload[0].value}%
                    </p>
                    {label === recommended && (
                      <Badge variant="default" className="mt-1">
                        Recomendado
                      </Badge>
                    )}
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar
            dataKey="score"
            fill={(entry, index) => entry.color}
            radius={[4, 4, 0, 0]}
            onMouseEnter={(_, index) => interactive && setActiveIndex(index)}
            onMouseLeave={() => interactive && setActiveIndex(undefined)}
          />
        </BarChart>
      </ResponsiveContainer>
      
      {recommended && (
        <div className="text-center">
          <Badge variant="default" className="text-lg px-4 py-2">
            Curso Recomendado: {recommended}
          </Badge>
        </div>
      )}
    </div>
  );
}
```

---

## 3. Páginas e Rotas

### 3.1 Estrutura de Rotas (App Router)

```
src/app/
├── layout.tsx                 # Root layout
├── page.tsx                   # Homepage
├── loading.tsx                # Loading UI
├── error.tsx                  # Error UI
├── not-found.tsx             # 404 page
├── questionario/
│   ├── page.tsx              # Questionnaire page
│   ├── loading.tsx           # Questionnaire loading
│   └── resultado/
│       └── [sessionId]/
│           └── page.tsx      # Result page
├── admin/
│   ├── layout.tsx            # Admin layout
│   ├── page.tsx              # Admin dashboard
│   ├── perguntas/
│   │   ├── page.tsx          # Questions management
│   │   ├── nova/
│   │   │   └── page.tsx      # New question
│   │   └── [id]/
│   │       └── page.tsx      # Edit question
│   ├── relatorios/
│   │   └── page.tsx          # Reports
│   └── configuracoes/
│       └── page.tsx          # Settings
├── auth/
│   ├── login/
│   │   └── page.tsx          # Login page
│   └── registro/
│       └── page.tsx          # Register page
└── api/                      # API routes (se necessário)
```

### 3.2 Homepage (/)

```typescript
export default function HomePage() {
  const [selectedTheme, setSelectedTheme] = useState('default');
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Simula carregamento inicial com animação
    const timer = setTimeout(() => setIsLoading(false), 2000);
    return () => clearTimeout(timer);
  }, []);
  
  if (isLoading) {
    return <LoadingAnimation />;
  }
  
  return (
    <AppLayout>
      <div className="relative">
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10">
          <div className="container px-4 text-center space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight">
                Caminhos Conscientes
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground mt-4">
                Transformando Escolhas, Moldando o Futuro
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="max-w-2xl mx-auto"
            >
              <p className="text-lg text-muted-foreground leading-relaxed">
                Descubra o curso técnico ideal para seu perfil através de nossa 
                plataforma inteligente que combina análise comportamental e 
                inteligência artificial para orientar sua jornada educacional.
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Button size="lg" asChild>
                <Link href="/questionario">
                  Iniciar Questionário
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg">
                Saiba Mais
              </Button>
            </motion.div>
          </div>
        </section>
        
        {/* Theme Selector */}
        <ThemeSelector 
          selectedTheme={selectedTheme}
          onThemeChange={setSelectedTheme}
        />
        
        {/* Features Section */}
        <FeaturesSection />
        
        {/* Courses Section */}
        <CoursesSection />
        
        {/* Testimonials Section */}
        <TestimonialsSection />
        
        {/* CTA Section */}
        <CTASection />
      </div>
    </AppLayout>
  );
}
```

### 3.3 Questionnaire Page (/questionario)

```typescript
export default function QuestionnairePage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const router = useRouter();
  
  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  
  useEffect(() => {
    loadQuestions();
  }, []);
  
  const loadQuestions = async () => {
    try {
      const data = await api.get('/questionnaire/questions');
      setQuestions(data);
    } catch (error) {
      toast.error('Erro ao carregar perguntas');
    }
  };
  
  const handleOptionSelect = (optionId: string) => {
    setResponses(prev => ({
      ...prev,
      [currentQuestion.id]: optionId
    }));
  };
  
  const handleNext = () => {
    if (isLastQuestion) {
      handleSubmit();
    } else {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };
  
  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const submission = {
        session_id: sessionId,
        responses: Object.entries(responses).map(([questionId, optionId]) => ({
          question_id: parseInt(questionId),
          selected_option_id: parseInt(optionId),
          response_time_ms: 0 // Implementar tracking de tempo
        }))
      };
      
      await api.post('/questionnaire/submit', submission);
      router.push(`/questionario/resultado/${sessionId}`);
    } catch (error) {
      toast.error('Erro ao submeter questionário');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!currentQuestion) {
    return <QuestionnaireLoading />;
  }
  
  return (
    <AppLayout showHeader={false}>
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-background flex items-center justify-center p-4">
        <div className="w-full max-w-4xl space-y-8">
          {/* Progress Header */}
          <div className="text-center space-y-4">
            <ProgressBar 
              value={progress} 
              label="Progresso do Questionário"
              animated
            />
            <MotivationalMessage step={currentQuestionIndex} />
          </div>
          
          {/* Question Card */}
          <motion.div
            key={currentQuestion.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <QuestionCard
              question={currentQuestion}
              selectedOption={responses[currentQuestion.id]}
              onOptionSelect={handleOptionSelect}
              disabled={isSubmitting}
              showProgress={false}
            />
          </motion.div>
          
          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0 || isSubmitting}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Anterior
            </Button>
            
            <span className="text-sm text-muted-foreground">
              {currentQuestionIndex + 1} de {questions.length}
            </span>
            
            <Button
              onClick={handleNext}
              disabled={!responses[currentQuestion.id] || isSubmitting}
              loading={isSubmitting}
            >
              {isLastQuestion ? 'Finalizar' : 'Próxima'}
              {!isLastQuestion && <ArrowRight className="ml-2 h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
```

### 3.4 Result Page (/questionario/resultado/[sessionId])

```typescript
interface ResultPageProps {
  params: { sessionId: string };
}

export default function ResultPage({ params }: ResultPageProps) {
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [emailSent, setEmailSent] = useState(false);
  const [email, setEmail] = useState('');
  
  useEffect(() => {
    loadResult();
  }, [params.sessionId]);
  
  const loadResult = async () => {
    try {
      const data = await api.get(`/questionnaire/result/${params.sessionId}`);
      setResult(data);
    } catch (error) {
      toast.error('Resultado não encontrado');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleEmailResult = async () => {
    try {
      await api.post(`/questionnaire/result/${params.sessionId}/email`, {
        email,
        name: 'Usuário' // Implementar nome do usuário
      });
      setEmailSent(true);
      toast.success('Resultado enviado por email!');
    } catch (error) {
      toast.error('Erro ao enviar email');
    }
  };
  
  if (isLoading) {
    return <ResultLoading />;
  }
  
  if (!result) {
    return <ResultNotFound />;
  }
  
  const chartData = [
    { course: 'Tecnologia da Informação', score: result.score_ti, color: '#3b82f6' },
    { course: 'Enfermagem', score: result.score_enfermagem, color: '#10b981' },
    { course: 'Logística', score: result.score_logistica, color: '#f59e0b' },
    { course: 'Administração', score: result.score_administracao, color: '#8b5cf6' },
    { course: 'Estética', score: result.score_estetica, color: '#ef4444' }
  ];
  
  return (
    <AppLayout>
      <div className="container py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-3xl md:text-4xl font-bold">
              Seu Resultado
            </h1>
            <p className="text-muted-foreground">
              Baseado em suas respostas, aqui está nossa recomendação personalizada
            </p>
          </motion.div>
        </div>
        
        {/* Recommendation Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-secondary/5">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Trophy className="w-8 h-8 text-primary" />
              </div>
              <CardTitle className="text-2xl">
                Curso Recomendado
              </CardTitle>
              <p className="text-3xl font-bold text-primary">
                {result.recommended_course}
              </p>
              <div className="flex items-center justify-center gap-2 mt-2">
                <span className="text-sm text-muted-foreground">
                  Confiança:
                </span>
                <Badge variant="secondary">
                  {Math.round(result.confidence_score * 100)}%
                </Badge>
              </div>
            </CardHeader>
          </Card>
        </motion.div>
        
        {/* Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Pontuação por Curso</CardTitle>
              <p className="text-muted-foreground">
                Veja como você se adequa a cada área de estudo
              </p>
            </CardHeader>
            <CardContent>
              <ResultChart 
                data={chartData}
                recommended={result.recommended_course}
              />
            </CardContent>
          </Card>
        </motion.div>
        
        {/* Course Details */}
        <CourseDetailsSection course={result.recommended_course} />
        
        {/* Email Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Receber por Email</CardTitle>
              <p className="text-muted-foreground">
                Enviaremos seu resultado detalhado para seu email
              </p>
            </CardHeader>
            <CardContent>
              {!emailSent ? (
                <div className="flex gap-4">
                  <Input
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleEmailResult}
                    disabled={!email}
                  >
                    Enviar
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span>Email enviado com sucesso!</span>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
        
        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button variant="outline" asChild>
            <Link href="/questionario">
              Refazer Questionário
            </Link>
          </Button>
          <Button asChild>
            <Link href="/">
              Voltar ao Início
            </Link>
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}
```

---

## 4. Hooks Customizados

### 4.1 useAuth

```typescript
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export function useAuth(): AuthState & AuthActions {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false
  });
  
  useEffect(() => {
    checkAuthStatus();
  }, []);
  
  const checkAuthStatus = async () => {
    try {
      const token = getStoredToken();
      if (token) {
        const user = await api.get('/auth/me');
        setState({
          user,
          isLoading: false,
          isAuthenticated: true
        });
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };
  
  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    storeTokens(response.access_token, response.refresh_token);
    await checkAuthStatus();
  };
  
  const register = async (userData: RegisterData) => {
    const response = await api.post('/auth/register', userData);
    storeTokens(response.access_token, response.refresh_token);
    await checkAuthStatus();
  };
  
  const logout = () => {
    clearTokens();
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false
    });
  };
  
  const refreshToken = async () => {
    const refresh = getStoredRefreshToken();
    if (refresh) {
      const response = await api.post('/auth/refresh', { refresh_token: refresh });
      storeTokens(response.access_token, response.refresh_token);
    }
  };
  
  return {
    ...state,
    login,
    register,
    logout,
    refreshToken
  };
}
```

### 4.2 useQuestionnaire

```typescript
interface QuestionnaireState {
  questions: Question[];
  currentIndex: number;
  responses: Record<string, string>;
  isLoading: boolean;
  isSubmitting: boolean;
  sessionId: string;
}

export function useQuestionnaire() {
  const [state, setState] = useState<QuestionnaireState>({
    questions: [],
    currentIndex: 0,
    responses: {},
    isLoading: true,
    isSubmitting: false,
    sessionId: generateSessionId()
  });
  
  const currentQuestion = state.questions[state.currentIndex];
  const isLastQuestion = state.currentIndex === state.questions.length - 1;
  const progress = ((state.currentIndex + 1) / state.questions.length) * 100;
  
  useEffect(() => {
    loadQuestions();
  }, []);
  
  const loadQuestions = async () => {
    try {
      const questions = await api.get('/questionnaire/questions');
      setState(prev => ({
        ...prev,
        questions,
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };
  
  const selectOption = (optionId: string) => {
    setState(prev => ({
      ...prev,
      responses: {
        ...prev.responses,
        [currentQuestion.id]: optionId
      }
    }));
  };
  
  const nextQuestion = () => {
    if (!isLastQuestion) {
      setState(prev => ({
        ...prev,
        currentIndex: prev.currentIndex + 1
      }));
    }
  };
  
  const previousQuestion = () => {
    if (state.currentIndex > 0) {
      setState(prev => ({
        ...prev,
        currentIndex: prev.currentIndex - 1
      }));
    }
  };
  
  const submitQuestionnaire = async () => {
    setState(prev => ({ ...prev, isSubmitting: true }));
    
    try {
      const submission = {
        session_id: state.sessionId,
        responses: Object.entries(state.responses).map(([questionId, optionId]) => ({
          question_id: parseInt(questionId),
          selected_option_id: parseInt(optionId),
          response_time_ms: 0
        }))
      };
      
      const result = await api.post('/questionnaire/submit', submission);
      return result;
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  };
  
  return {
    ...state,
    currentQuestion,
    isLastQuestion,
    progress,
    selectOption,
    nextQuestion,
    previousQuestion,
    submitQuestionnaire
  };
}
```

### 4.3 useTheme

```typescript
type Theme = 'light' | 'dark' | 'system';
type VisualTheme = 'default' | 'casual' | 'formal' | 'minimal' | 'vibrant' | 'high-contrast';

interface ThemeState {
  theme: Theme;
  visualTheme: VisualTheme;
  resolvedTheme: 'light' | 'dark';
}

export function useTheme() {
  const { theme, setTheme, resolvedTheme } = useNextThemes();
  const [visualTheme, setVisualTheme] = useLocalStorage<VisualTheme>('visual-theme', 'default');
  
  useEffect(() => {
    // Aplica classes CSS baseadas no tema visual
    document.documentElement.setAttribute('data-visual-theme', visualTheme);
  }, [visualTheme]);
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };
  
  return {
    theme: theme as Theme,
    visualTheme,
    resolvedTheme: resolvedTheme as 'light' | 'dark',
    setTheme,
    setVisualTheme,
    toggleTheme
  };
}
```

---

## 5. Utilitários e Helpers

### 5.1 API Client

```typescript
class ApiClient {
  private baseURL: string;
  
  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = getStoredToken();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };
    
    const response = await fetch(url, config);
    
    if (response.status === 401) {
      // Token expirado, tentar refresh
      await this.refreshToken();
      return this.request(endpoint, options);
    }
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }
  
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }
  
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
  
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
  
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
  
  private async refreshToken() {
    const refreshToken = getStoredRefreshToken();
    if (refreshToken) {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      
      if (response.ok) {
        const tokens = await response.json();
        storeTokens(tokens.access_token, tokens.refresh_token);
      } else {
        clearTokens();
        window.location.href = '/auth/login';
      }
    }
  }
}

export const api = new ApiClient(process.env.NEXT_PUBLIC_API_URL!);
```

### 5.2 Form Validation

```typescript
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
});

export const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  full_name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: 'Senhas não coincidem',
  path: ['confirm_password'],
});

export const questionSchema = z.object({
  text: z.string().min(10, 'Pergunta deve ter pelo menos 10 caracteres'),
  question_type: z.enum(['multiple_choice', 'scale', 'boolean']),
  category: z.string().min(1, 'Categoria é obrigatória'),
  order: z.number().min(1),
  options: z.array(z.object({
    text: z.string().min(1, 'Texto da opção é obrigatório'),
    value: z.string().min(1, 'Valor da opção é obrigatório'),
    order: z.number().min(1),
    weight_ti: z.number().min(0).max(100),
    weight_enfermagem: z.number().min(0).max(100),
    weight_logistica: z.number().min(0).max(100),
    weight_administracao: z.number().min(0).max(100),
    weight_estetica: z.number().min(0).max(100),
  })).min(2, 'Deve ter pelo menos 2 opções'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type QuestionFormData = z.infer<typeof questionSchema>;
```

### 5.3 Accessibility Helpers

```typescript
export function announceToScreenReader(message: string) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

export function trapFocus(element: HTMLElement) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0] as HTMLElement;
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
  
  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    }
  };
  
  element.addEventListener('keydown', handleTabKey);
  firstElement.focus();
  
  return () => {
    element.removeEventListener('keydown', handleTabKey);
  };
}

export function useKeyboardNavigation(
  onNext: () => void,
  onPrevious: () => void,
  onSubmit?: () => void
) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'ArrowRight':
            e.preventDefault();
            onNext();
            break;
          case 'ArrowLeft':
            e.preventDefault();
            onPrevious();
            break;
          case 'Enter':
            if (onSubmit) {
              e.preventDefault();
              onSubmit();
            }
            break;
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onNext, onPrevious, onSubmit]);
}
```

---

## 6. Configurações

### 6.1 Next.js Configuration

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'api.caminhos-conscientes.com'],
    formats: ['image/webp', 'image/avif'],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### 6.2 Tailwind Configuration

```typescript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
        'fade-in': {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        'slide-in-from-top': {
          from: { transform: 'translateY(-100%)' },
          to: { transform: 'translateY(0)' },
        },
        'slide-in-from-bottom': {
          from: { transform: 'translateY(100%)' },
          to: { transform: 'translateY(0)' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-in-from-top': 'slide-in-from-top 0.3s ease-out',
        'slide-in-from-bottom': 'slide-in-from-bottom 0.3s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate'), require('@tailwindcss/typography')],
};
```

### 6.3 TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/types/*": ["./src/types/*"],
      "@/styles/*": ["./src/styles/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## 7. Performance e SEO

### 7.1 Otimizações de Performance

```typescript
// Lazy loading de componentes
const AdminDashboard = dynamic(() => import('@/components/admin/Dashboard'), {
  loading: () => <DashboardSkeleton />,
  ssr: false,
});

const ResultChart = dynamic(() => import('@/components/charts/ResultChart'), {
  loading: () => <ChartSkeleton />,
});

// Image optimization
import Image from 'next/image';

export function OptimizedImage({ src, alt, ...props }) {
  return (
    <Image
      src={src}
      alt={alt}
      loading="lazy"
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
      {...props}
    />
  );
}

// Service Worker para cache
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### 7.2 SEO Configuration

```typescript
// app/layout.tsx
export const metadata: Metadata = {
  title: {
    default: 'Caminhos Conscientes - Orientação Vocacional Inteligente',
    template: '%s | Caminhos Conscientes',
  },
  description: 'Descubra o curso técnico ideal para seu perfil através de nossa plataforma inteligente que combina análise comportamental e inteligência artificial.',
  keywords: ['orientação vocacional', 'curso técnico', 'educação', 'inteligência artificial'],
  authors: [{ name: 'Caminhos Conscientes' }],
  creator: 'Caminhos Conscientes',
  publisher: 'Caminhos Conscientes',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://caminhos-conscientes.vercel.app'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://caminhos-conscientes.vercel.app',
    title: 'Caminhos Conscientes - Orientação Vocacional Inteligente',
    description: 'Descubra o curso técnico ideal para seu perfil através de nossa plataforma inteligente.',
    siteName: 'Caminhos Conscientes',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Caminhos Conscientes',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Caminhos Conscientes - Orientação Vocacional Inteligente',
    description: 'Descubra o curso técnico ideal para seu perfil através de nossa plataforma inteligente.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
  },
};

// Sitemap generation
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://caminhos-conscientes.vercel.app',
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 1,
    },
    {
      url: 'https://caminhos-conscientes.vercel.app/questionario',
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: 'https://caminhos-conscientes.vercel.app/auth/login',
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.5,
    },
  ];
}
```

---

## 8. Testes

### 8.1 Configuração de Testes

```typescript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/app/**/layout.tsx',
    '!src/app/**/loading.tsx',
    '!src/app/**/not-found.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

module.exports = createJestConfig(customJestConfig);
```

### 8.2 Testes de Componentes

```typescript
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});

// __tests__/pages/questionnaire.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QuestionnairePage } from '@/app/questionario/page';

jest.mock('@/lib/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

describe('QuestionnairePage', () => {
  it('loads questions on mount', async () => {
    const mockQuestions = [
      {
        id: 1,
        text: 'Test question',
        options: [
          { id: 1, text: 'Option 1' },
          { id: 2, text: 'Option 2' },
        ],
      },
    ];

    (api.get as jest.Mock).mockResolvedValue(mockQuestions);

    render(<QuestionnairePage />);

    await waitFor(() => {
      expect(screen.getByText('Test question')).toBeInTheDocument();
    });
  });
});
```

---

## 9. Deploy e Build

### 9.1 Build Configuration

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "analyze": "ANALYZE=true next build"
  }
}
```

### 9.2 Vercel Configuration

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_ANALYTICS_ID": "@analytics-id"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "@api-url-production"
    }
  },
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

Esta especificação técnica do frontend fornece uma base completa para implementação da interface do sistema "Caminhos Conscientes", seguindo as melhores práticas de desenvolvimento com Next.js, TypeScript e Tailwind CSS, garantindo acessibilidade, performance e experiência do usuário excepcional.


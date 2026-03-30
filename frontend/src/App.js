import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Trophy, 
  GameController, 
  Gift, 
  Users, 
  WhatsappLogo,
  CaretRight,
  Medal,
  Lightning,
  CheckCircle,
  XCircle,
  Copy,
  ArrowRight,
  Star,
  Crown
} from "@phosphor-icons/react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================================================
// COMPONENTS
// ============================================================================

const Navbar = ({ participant, onLogout }) => {
  return (
    <nav className="nav-floating" data-testid="navbar">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3" data-testid="nav-logo">
          <div className="w-10 h-10 bg-[#10B981] flex items-center justify-center">
            <Lightning weight="fill" className="text-[#040906] text-xl" />
          </div>
          <span className="font-bold text-xl tracking-tight">INWO Game</span>
        </a>
        
        <div className="flex items-center gap-6">
          {participant ? (
            <>
              <span className="text-[#9CA3AF] text-sm hidden md:block">
                Olá, <span className="text-[#10B981]">{participant.name}</span>
              </span>
              <span className="text-[#F59E0B] font-bold flex items-center gap-1">
                <Trophy weight="fill" /> {participant.total_points || 0} pts
              </span>
            </>
          ) : (
            <a 
              href="https://suplementosmaisbaratos.com.br" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-[#9CA3AF] hover:text-[#10B981] transition-colors text-sm"
            >
              Loja
            </a>
          )}
        </div>
      </div>
    </nav>
  );
};

// ============================================================================
// LANDING PAGE
// ============================================================================

const LandingPage = ({ onStartGame }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [stats, setStats] = useState({ total_participants: 0, completed_games: 0 });

  useEffect(() => {
    fetchLeaderboard();
    fetchStats();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard?limit=5`);
      setLeaderboard(res.data.leaderboard || []);
    } catch (e) {
      console.error("Error fetching leaderboard:", e);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/stats`);
      setStats(res.data);
    } catch (e) {
      console.error("Error fetching stats:", e);
    }
  };

  return (
    <div className="min-h-screen" data-testid="landing-page">
      {/* Hero Section */}
      <section 
        className="relative min-h-screen flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage: `url(https://images.unsplash.com/photo-1707346310176-52f43d7606ea?w=1920)`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-[#040906]/70 via-[#040906]/90 to-[#040906]" />
        
        <div className="relative z-10 max-w-5xl mx-auto px-6 py-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="text-sm uppercase tracking-[0.3em] text-[#F59E0B] mb-6 block">
              Suplementos Mais Baratos Apresenta
            </span>
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black tracking-tighter mb-6 leading-tight">
              <span className="text-gradient">ILLUMINATI</span>
              <br />
              <span className="text-white">New World Order</span>
            </h1>
            <p className="text-lg text-[#9CA3AF] max-w-2xl mx-auto mb-10">
              Teste seus conhecimentos sobre o lendário jogo de cartas e ganhe 
              <span className="text-[#F59E0B] font-semibold"> prêmios exclusivos</span> da nossa loja!
            </p>
            
            <motion.button
              onClick={onStartGame}
              className="btn-primary px-10 py-4 text-lg font-bold flex items-center gap-3 mx-auto"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              data-testid="start-game-btn"
            >
              <GameController weight="fill" className="text-2xl" />
              JOGAR AGORA
              <CaretRight weight="bold" />
            </motion.button>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div 
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-6 h-10 border-2 border-[#10B981]/50 rounded-full flex justify-center pt-2">
            <div className="w-1.5 h-3 bg-[#10B981] rounded-full" />
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6" data-testid="features-section">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">
              Como Funciona
            </h2>
            <p className="text-[#9CA3AF]">Três passos simples para ganhar prêmios</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: Users, title: "Cadastre-se", desc: "Faça seu cadastro gratuito com nome, email e WhatsApp" },
              { icon: GameController, title: "Jogue o Quiz", desc: "Responda perguntas sobre o jogo INWO e acumule pontos" },
              { icon: Gift, title: "Ganhe Prêmios", desc: "Receba cupons de desconto exclusivos da loja" }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                className="quiz-card text-center"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.2 }}
                viewport={{ once: true }}
              >
                <div className="w-16 h-16 mx-auto mb-6 bg-[#10B981]/10 flex items-center justify-center">
                  <item.icon weight="fill" className="text-3xl text-[#10B981]" />
                </div>
                <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                <p className="text-[#9CA3AF]">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats & Leaderboard */}
      <section className="py-24 px-6 bg-[#08120A]" data-testid="stats-section">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Stats */}
          <div>
            <h2 className="text-2xl font-bold mb-8">Estatísticas</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="quiz-card">
                <div className="text-3xl font-black text-[#10B981]">{stats.total_participants}</div>
                <div className="text-[#9CA3AF] text-sm mt-1">Participantes</div>
              </div>
              <div className="quiz-card">
                <div className="text-3xl font-black text-[#F59E0B]">{stats.completed_games}</div>
                <div className="text-[#9CA3AF] text-sm mt-1">Jogos Completos</div>
              </div>
            </div>
          </div>

          {/* Leaderboard */}
          <div>
            <h2 className="text-2xl font-bold mb-8 flex items-center gap-2">
              <Trophy weight="fill" className="text-[#F59E0B]" />
              Top Jogadores
            </h2>
            <div className="space-y-3">
              {leaderboard.length > 0 ? (
                leaderboard.map((player, idx) => (
                  <div 
                    key={player.id}
                    className={`leaderboard-row p-4 flex items-center justify-between ${idx < 3 ? 'top-3' : ''}`}
                    data-testid={`leaderboard-row-${idx}`}
                  >
                    <div className="flex items-center gap-4">
                      <span className={`w-8 h-8 flex items-center justify-center font-bold ${
                        idx === 0 ? 'bg-[#F59E0B] text-[#040906]' :
                        idx === 1 ? 'bg-gray-400 text-[#040906]' :
                        idx === 2 ? 'bg-amber-700 text-white' :
                        'bg-[#10B981]/20 text-[#10B981]'
                      }`}>
                        {idx + 1}
                      </span>
                      <span className="font-medium">{player.name}</span>
                    </div>
                    <span className="text-[#10B981] font-bold">{player.total_points} pts</span>
                  </div>
                ))
              ) : (
                <p className="text-[#9CA3AF] text-center py-8">Nenhum jogador ainda. Seja o primeiro!</p>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 text-center" data-testid="cta-section">
        <div className="max-w-3xl mx-auto">
          <Gift weight="fill" className="text-6xl text-[#F59E0B] mx-auto mb-6" />
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">
            Pronto para Ganhar?
          </h2>
          <p className="text-[#9CA3AF] mb-8">
            Jogue agora e ganhe descontos exclusivos em suplementos de alta qualidade!
          </p>
          <button
            onClick={onStartGame}
            className="btn-accent px-10 py-4 text-lg font-bold"
            data-testid="cta-play-btn"
          >
            COMEÇAR A JOGAR
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[#10B981]/10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-[#9CA3AF] text-sm">
            © 2026 Suplementos Mais Baratos. Todos os direitos reservados.
          </p>
          <a 
            href="https://suplementosmaisbaratos.com.br" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-[#10B981] hover:text-[#34D399] transition-colors text-sm"
          >
            Visitar Loja
          </a>
        </div>
      </footer>
    </div>
  );
};

// ============================================================================
// REGISTRATION FORM
// ============================================================================

const RegistrationForm = ({ onRegister, loading }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    whatsapp: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.whatsapp) {
      toast.error("Por favor, preencha todos os campos");
      return;
    }
    onRegister(formData);
  };

  const formatWhatsApp = (value) => {
    // Remove non-digits
    const digits = value.replace(/\D/g, '');
    // Format as (XX) XXXXX-XXXX
    if (digits.length <= 2) return digits;
    if (digits.length <= 7) return `(${digits.slice(0,2)}) ${digits.slice(2)}`;
    return `(${digits.slice(0,2)}) ${digits.slice(2,7)}-${digits.slice(7,11)}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-24" data-testid="registration-page">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="quiz-card">
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-[#10B981]/10 flex items-center justify-center">
              <Users weight="fill" className="text-3xl text-[#10B981]" />
            </div>
            <h2 className="text-2xl font-bold">Cadastre-se para Jogar</h2>
            <p className="text-[#9CA3AF] text-sm mt-2">Cadastro 100% gratuito</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium mb-2 text-left">Nome Completo</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="input-dark"
                placeholder="Seu nome"
                data-testid="input-name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-left">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="input-dark"
                placeholder="seu@email.com"
                data-testid="input-email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-left flex items-center gap-2">
                <WhatsappLogo weight="fill" className="text-[#25D366]" />
                WhatsApp
              </label>
              <input
                type="tel"
                value={formData.whatsapp}
                onChange={(e) => setFormData({...formData, whatsapp: formatWhatsApp(e.target.value)})}
                className="input-dark"
                placeholder="(11) 99999-9999"
                maxLength={16}
                data-testid="input-whatsapp"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-4 font-bold flex items-center justify-center gap-2"
              data-testid="submit-registration-btn"
            >
              {loading ? (
                <span>Cadastrando...</span>
              ) : (
                <>
                  CONTINUAR
                  <ArrowRight weight="bold" />
                </>
              )}
            </button>
          </form>

          <p className="text-[#6B7280] text-xs text-center mt-6">
            Ao se cadastrar, você concorda em receber promoções via WhatsApp
          </p>
        </div>
      </motion.div>
    </div>
  );
};

// ============================================================================
// QUIZ GAME
// ============================================================================

const QuizGame = ({ participant, onComplete }) => {
  const [gameState, setGameState] = useState('loading'); // loading, playing, result
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answerResult, setAnswerResult] = useState(null);
  const [score, setScore] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [prize, setPrize] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    startGame();
  }, []);

  const startGame = async () => {
    try {
      setGameState('loading');
      const res = await axios.post(`${API}/game/start?participant_id=${participant.id}`);
      setSession(res.data);
      setCurrentQuestion(res.data.question);
      setTotalQuestions(res.data.total_questions);
      setQuestionNumber(1);
      setGameState('playing');
    } catch (e) {
      console.error("Error starting game:", e);
      toast.error("Erro ao iniciar o jogo");
    }
  };

  const submitAnswer = async (answer) => {
    if (loading || answerResult) return;
    
    setSelectedAnswer(answer);
    setLoading(true);

    try {
      const res = await axios.post(
        `${API}/game/answer?session_id=${session.session_id}&question_id=${currentQuestion.id}&answer=${encodeURIComponent(answer)}`
      );
      
      setAnswerResult({
        isCorrect: res.data.is_correct,
        correctAnswer: res.data.correct_answer
      });
      setScore(res.data.total_score);
      setCorrectAnswers(res.data.correct_answers);

      // Wait before moving to next question
      setTimeout(() => {
        if (res.data.is_complete) {
          setPrize(res.data.prize);
          setGameState('result');
        } else {
          setCurrentQuestion(res.data.next_question);
          setQuestionNumber(res.data.question_number);
          setSelectedAnswer(null);
          setAnswerResult(null);
        }
        setLoading(false);
      }, 1500);

    } catch (e) {
      console.error("Error submitting answer:", e);
      toast.error("Erro ao enviar resposta");
      setLoading(false);
    }
  };

  const copyPrizeCode = async () => {
    if (prize?.code) {
      try {
        await navigator.clipboard.writeText(prize.code);
        toast.success("Código copiado!");
      } catch (e) {
        // Fallback for clipboard permission issues
        const textArea = document.createElement('textarea');
        textArea.value = prize.code;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        toast.success("Código copiado!");
      }
    }
  };

  if (gameState === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center" data-testid="quiz-loading">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#10B981]/30 border-t-[#10B981] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[#9CA3AF]">Carregando quiz...</p>
        </div>
      </div>
    );
  }

  if (gameState === 'result') {
    return (
      <div className="min-h-screen flex items-center justify-center px-6 py-24" data-testid="quiz-result">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-lg"
        >
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.2 }}
            >
              <Trophy weight="fill" className="text-7xl text-[#F59E0B] mx-auto mb-4" />
            </motion.div>
            <h2 className="text-3xl font-black mb-2">Parabéns!</h2>
            <p className="text-[#9CA3AF]">Você completou o quiz</p>
          </div>

          <div className="quiz-card mb-6">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-3xl font-black text-[#10B981]">{score}</div>
                <div className="text-[#9CA3AF] text-sm">Pontos</div>
              </div>
              <div>
                <div className="text-3xl font-black text-[#F59E0B]">{correctAnswers}/{totalQuestions}</div>
                <div className="text-[#9CA3AF] text-sm">Acertos</div>
              </div>
            </div>
          </div>

          {prize && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="prize-card p-6 mb-6"
              data-testid="prize-card"
            >
              <div className="relative z-10">
                <div className="flex items-center gap-2 text-[#F59E0B] text-sm font-bold mb-3">
                  <Gift weight="fill" />
                  SEU PRÊMIO
                </div>
                <h3 className="text-xl font-bold mb-2">{prize.name}</h3>
                <p className="text-[#9CA3AF] text-sm mb-4">{prize.description}</p>
                
                <div className="bg-black/50 p-4 flex items-center justify-between">
                  <code className="text-[#10B981] font-mono text-lg" data-testid="prize-code">{prize.code}</code>
                  <button
                    onClick={copyPrizeCode}
                    className="text-[#9CA3AF] hover:text-white transition-colors"
                    data-testid="copy-prize-code-btn"
                  >
                    <Copy weight="bold" className="text-xl" />
                  </button>
                </div>

                <p className="text-[#6B7280] text-xs mt-4">
                  Use este código em suplementosmaisbaratos.com.br
                </p>
              </div>
            </motion.div>
          )}

          <div className="flex gap-4">
            <button
              onClick={startGame}
              className="btn-outline flex-1 py-3 font-bold"
              data-testid="play-again-btn"
            >
              JOGAR NOVAMENTE
            </button>
            <a
              href="https://suplementosmaisbaratos.com.br"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-accent flex-1 py-3 font-bold text-center"
              data-testid="visit-store-btn"
            >
              VISITAR LOJA
            </a>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-24" data-testid="quiz-playing">
      <div className="w-full max-w-2xl">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-[#9CA3AF]">
              Pergunta {questionNumber} de {totalQuestions}
            </span>
            <span className="text-[#10B981] font-bold flex items-center gap-1">
              <Star weight="fill" /> {score} pts
            </span>
          </div>
          <div className="progress-bar rounded-sm">
            <div 
              className="progress-fill rounded-sm"
              style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <motion.div
          key={currentQuestion?.id}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          className="quiz-card mb-6"
        >
          <div className="flex items-center gap-2 text-[#F59E0B] text-sm font-medium mb-4">
            <Lightning weight="fill" />
            {currentQuestion?.difficulty === 'easy' ? 'FÁCIL' : 
             currentQuestion?.difficulty === 'medium' ? 'MÉDIO' : 'DIFÍCIL'}
          </div>
          <h3 className="text-xl sm:text-2xl font-bold leading-relaxed" data-testid="question-text">
            {currentQuestion?.question}
          </h3>
        </motion.div>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion?.options.map((option, idx) => {
            let className = "option-btn w-full";
            if (answerResult) {
              if (option === answerResult.correctAnswer) {
                className += " correct";
              } else if (option === selectedAnswer && !answerResult.isCorrect) {
                className += " incorrect";
              }
            } else if (option === selectedAnswer) {
              className += " selected";
            }

            return (
              <motion.button
                key={idx}
                onClick={() => submitAnswer(option)}
                disabled={loading || answerResult}
                className={className}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                data-testid={`quiz-answer-${String.fromCharCode(65 + idx)}`}
              >
                <div className="flex items-center gap-4">
                  <span className="w-8 h-8 flex items-center justify-center border border-current font-bold">
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span>{option}</span>
                  {answerResult && option === answerResult.correctAnswer && (
                    <CheckCircle weight="fill" className="ml-auto text-[#10B981] text-xl" />
                  )}
                  {answerResult && option === selectedAnswer && !answerResult.isCorrect && (
                    <XCircle weight="fill" className="ml-auto text-[#EF4444] text-xl" />
                  )}
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Answer Feedback */}
        <AnimatePresence>
          {answerResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`mt-6 p-4 text-center ${
                answerResult.isCorrect 
                  ? 'bg-[#10B981]/10 border border-[#10B981]/30' 
                  : 'bg-[#EF4444]/10 border border-[#EF4444]/30'
              }`}
            >
              {answerResult.isCorrect ? (
                <span className="text-[#10B981] font-bold">Correto! +{currentQuestion?.difficulty === 'easy' ? 10 : currentQuestion?.difficulty === 'medium' ? 20 : 30} pontos</span>
              ) : (
                <span className="text-[#EF4444]">Incorreto. A resposta era: {answerResult.correctAnswer}</span>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN APP
// ============================================================================

const AppContent = () => {
  const [view, setView] = useState('landing'); // landing, register, game
  const [participant, setParticipant] = useState(null);
  const [loading, setLoading] = useState(false);

  // Check for existing participant in localStorage
  useEffect(() => {
    const saved = localStorage.getItem('inwo_participant');
    if (saved) {
      try {
        setParticipant(JSON.parse(saved));
      } catch (e) {
        localStorage.removeItem('inwo_participant');
      }
    }
  }, []);

  const handleStartGame = () => {
    if (participant) {
      setView('game');
    } else {
      setView('register');
    }
  };

  const handleRegister = async (formData) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/participants`, formData);
      const participantData = res.data.participant;
      setParticipant(participantData);
      localStorage.setItem('inwo_participant', JSON.stringify(participantData));
      
      if (res.data.is_new) {
        toast.success("Cadastro realizado com sucesso!");
      } else {
        toast.success("Bem-vindo de volta!");
      }
      
      setView('game');
    } catch (e) {
      console.error("Registration error:", e);
      toast.error(e.response?.data?.detail || "Erro ao cadastrar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleGameComplete = () => {
    // Refresh participant data
    if (participant) {
      axios.get(`${API}/participants/${participant.id}`)
        .then(res => {
          setParticipant(res.data);
          localStorage.setItem('inwo_participant', JSON.stringify(res.data));
        })
        .catch(console.error);
    }
  };

  return (
    <div className="min-h-screen bg-[#040906]">
      <Navbar participant={participant} />
      
      <main className="pt-16">
        {view === 'landing' && (
          <LandingPage onStartGame={handleStartGame} />
        )}
        
        {view === 'register' && (
          <RegistrationForm onRegister={handleRegister} loading={loading} />
        )}
        
        {view === 'game' && participant && (
          <QuizGame participant={participant} onComplete={handleGameComplete} />
        )}
      </main>
      
      <Toaster position="top-center" richColors />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<AppContent />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

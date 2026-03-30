# PRD - INWO Quiz Game (Suplementos Mais Baratos)

## Original Problem Statement
Criar uma versão digital do jogo de cartas "Illuminati: New World Order" (INWO) adaptada para crianças e adultos, com sistema de prêmios aleatórios via WhatsApp para a loja suplementosmaisbaratos.com.br. O participante precisa fazer cadastro gratuito (Nome, Email, WhatsApp) para jogar.

## User Personas
1. **Jogadores Casuais**: Pessoas interessadas em jogos de trivia que querem ganhar descontos
2. **Fãs de INWO**: Jogadores que conhecem o jogo de cartas original
3. **Clientes da Loja**: Pessoas que buscam cupons de desconto em suplementos

## Core Requirements
- [x] Landing page atrativa com tema INWO
- [x] Sistema de cadastro gratuito (Nome, Email, WhatsApp)
- [x] Quiz baseado nas cartas do jogo INWO
- [x] Sistema de pontuação por dificuldade
- [x] Prêmios aleatórios (cupons de desconto)
- [x] Leaderboard de jogadores
- [x] Estatísticas do jogo

## Architecture
- **Frontend**: React + Tailwind CSS + Framer Motion
- **Backend**: FastAPI + MongoDB
- **Design**: Tema escuro com verde esmeralda (#10B981) e dourado (#F59E0B)

## What's Been Implemented (March 30, 2026)

### Backend (server.py)
- POST /api/participants - Registro de participantes
- GET /api/participants - Lista participantes (admin)
- GET /api/cards - Lista cartas INWO
- POST /api/game/start - Inicia sessão de quiz
- POST /api/game/answer - Envia resposta
- GET /api/prizes - Lista prêmios
- GET /api/leaderboard - Top jogadores
- GET /api/stats - Estatísticas

### Frontend (App.js)
- Landing page com hero, features, stats, CTA
- Formulário de cadastro com validação
- Quiz de 5 perguntas com feedback visual
- Sistema de pontos (fácil: 10, médio: 20, difícil: 30)
- Tela de resultado com prêmio
- Cópia de código do cupom

### Database Collections
- participants: Dados dos jogadores
- game_sessions: Sessões de quiz
- prizes: Cupons de desconto

## Prêmios Configurados
1. 10% OFF Whey Protein (INWO10WHEY)
2. 15% OFF Creatina (INWO15CREAT)
3. 20% OFF em compras +R$200 (INWO20SUPER)
4. Frete Grátis (INWOFRETEGRATIS)
5. 5% OFF em todo site (INWO5ALL)

## Prioritized Backlog

### P0 (Crítico) - ✅ DONE
- [x] Landing page
- [x] Cadastro com WhatsApp
- [x] Quiz funcional
- [x] Sistema de prêmios

### P1 (Alta Prioridade)
- [ ] Painel Admin para gerenciar participantes e prêmios
- [ ] Integração real com WhatsApp API para envio automático de prêmios
- [ ] Mais perguntas sobre INWO (expandir banco de questões)

### P2 (Média Prioridade)
- [ ] Sistema de níveis/ranks para jogadores frequentes
- [ ] Compartilhamento em redes sociais
- [ ] Modo multiplayer em tempo real

### P3 (Baixa Prioridade)
- [ ] Imagens das cartas INWO originais
- [ ] Animações de cartas 3D
- [ ] Sistema de conquistas/achievements

## Next Tasks
1. Implementar painel admin com autenticação
2. Integrar WhatsApp Business API (Twilio ou Meta)
3. Adicionar mais perguntas sobre INWO
4. Implementar validação de cupons na loja

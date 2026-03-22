# PRD - Eletrofunk Cachorrada

## Original Problem Statement
Site de votação de DJs de eletrofunk/cachorrada para eletrofunkcachorrada.com.br. Sistema one-page com votação de DJs, perfis otimizados para SEO, eventos com venda via WhatsApp e blog para tráfego orgânico.

## User Personas
1. **Fã de Funk** - Jovem 18-35 anos, frequenta bailes e raves, quer votar em seus DJs favoritos
2. **Produtor/DJ** - Quer visibilidade e votos no ranking
3. **Promoter de Eventos** - Quer divulgar eventos e vender ingressos

## Core Requirements (Static)
- Votação de DJs com captura de leads (nome, CPF, email, WhatsApp, estado)
- Ranking de DJs em tempo real
- Perfis de DJs otimizados para SEO
- Seção de eventos com compra via WhatsApp
- Blog para SEO orgânico
- Design baile funk hi-tech
- Música de fundo na primeira interação

## What's Been Implemented ✅
**Data: 22/03/2026**

### Backend (FastAPI + MongoDB)
- [x] API de votação com validação de CPF
- [x] Prevenção de voto duplicado (mesmo CPF + DJ)
- [x] CRUD de DJs, Eventos e Artigos
- [x] Ranking com percentuais
- [x] Seed data com 5 DJs, 3 eventos, 5 artigos

### Frontend (React + Tailwind)
- [x] Hero section com logo e background personalizados
- [x] Marquee com keywords SEO
- [x] Cards de ranking com votos e percentuais
- [x] Modal de votação com formulário completo
- [x] Seção de DJs com perfis e keywords
- [x] Seção de eventos com botão WhatsApp
- [x] Seção de blog/artigos
- [x] CTA de WhatsApp
- [x] Footer com CNPJ e Instagram
- [x] Meta tags SEO otimizadas
- [x] Structured data (JSON-LD)
- [x] Player de áudio com tratamento de erro

### Design
- [x] Tema dark brutalist
- [x] Fontes: Anton (headings), Space Mono (body)
- [x] Cores: #050505 (bg), #E01A4F (primary), #00FFFF (secondary)
- [x] Animações com framer-motion
- [x] Efeitos neon e glassmorphism

## Prioritized Backlog

### P0 (Crítico) - Completo ✅
- Votação funcionando
- Ranking atualizado
- WhatsApp integration

### P1 (Alta Prioridade)
- [ ] Painel admin para gerenciar DJs/Eventos
- [ ] Upload de imagens dos DJs
- [ ] Página individual de artigos (/artigo/[slug])

### P2 (Média Prioridade)
- [ ] Sistema de autenticação admin
- [ ] Analytics de votos por estado
- [ ] Compartilhamento social
- [ ] Newsletter signup

### P3 (Baixa Prioridade)
- [ ] Comentários nos artigos
- [ ] Sistema de favoritos
- [ ] PWA para mobile

## Next Tasks
1. Criar páginas individuais para artigos do blog
2. Implementar painel admin simples
3. Adicionar mais DJs e eventos reais
4. Configurar Google Analytics
5. Submeter sitemap para Google Search Console

## Technical Notes
- CNPJ: 21.534.683/0001-37 (Sucesso Vip Empreendimentos)
- WhatsApp: +55 21 97223-2170
- Instagram: @jonatasbeirao
- Domínio alvo: eletrofunkcachorrada.com.br

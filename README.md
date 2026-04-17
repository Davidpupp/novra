# Velocity Sports - Loja online completa

Aplicacao de e-commerce full stack com Flask + SQLite, pronta para deploy imediato.

## Recursos
- Home, catalogo com busca, pagina de produto, carrinho e checkout
- Paginacao no catalogo e endpoint moderno de produtos (`/api/products`)
- IA integrada no frontend (`/api/ai-assistant`) com limite anti-spam
- PWA basica (manifest + service worker)
- Persistencia de pedidos no backend
- Conta de cliente com cadastro, login, historico de pedidos e recuperacao de senha
- Painel admin com login em rota privada configuravel (`ADMIN_PATH`)
- Integracao preparada para Sillient Pay (sandbox/live)
- API de saude (`/api/health`)

## Rodar local
1. `python -m venv .venv`
2. `./.venv/Scripts/activate`
3. `pip install -r requirements.txt`
4. (Opcional) definir variaveis do `.env.example`
5. `python app.py`
6. Abrir `http://localhost:5000`

## Credenciais admin padrao
- Email: `admin@velocity.local`
- Senha: `admin123`
- Login: `http://localhost:5000/painel-interno-velocity-2026/login`

## Conta de cliente
- Cadastro: `http://localhost:5000/conta/cadastro`
- Login: `http://localhost:5000/conta/login`
- Area da conta: `http://localhost:5000/conta`

## Deploy Gratuito e Definitivo com Render

### Passo a Passo Completo:

#### 1. Preparar o Repositório Git
```bash
# Inicialize o Git se ainda não tiver
git init

# Adicione todos os arquivos
git add .

# Commit
git commit -m "Initial commit - NØVRA e-commerce"

# Crie repositório no GitHub e conecte
git remote add origin https://github.com/SEU-USUARIO/novra.git
git branch -M main
git push -u origin main
```

#### 2. Configurar no Render
1. Acesse [render.com](https://render.com) e crie conta gratuita
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Environment Variables** (obrigatórias):
- `SECRET_KEY`: `sua-chave-secreta-aqui` (gera uma aleatória: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `ADMIN_EMAIL`: `seu@email.com`
- `ADMIN_PASSWORD`: `senha-forte-aqui`
- `ADMIN_PATH`: `painel-interno-novra-2026`

**Environment Variables** (opcionais):
- `SILLIENT_PAY_ENABLED`: `false`
- `SILLIENT_PAY_BASE_URL`: `https://sandbox.sillientpay.example`
- `SILLIENT_PAY_API_KEY`: ``
- `SESSION_COOKIE_SECURE`: `true`

5. Clique em **"Create Web Service"**
6. Aguarde o deploy (2-3 minutos)

#### 3. Banco de Dados
O SQLite funciona no Render, mas para produção recomenda-se PostgreSQL gratuito do Render:
1. No Render, clique em **"New +"** → **"PostgreSQL"**
2. Crie o banco (plano gratuito)
3. Adicione a variável `DATABASE_URL` ao seu Web Service
4. Atualize `app.py` para usar PostgreSQL (opcional)

#### 4. Domínio Customizado (Opcional)
1. No Web Service, vá em **Settings** → **Domains**
2. Adicione seu domínio (ex: novra.com)
3. Configure DNS no seu registrador
4. Render gera SSL automático

### Vantagens do Render Gratuito:
- ✅ Uptime garantido
- ✅ SSL automático (HTTPS)
- ✅ Deploy automático do GitHub
- ✅ PostgreSQL gratuito
- ✅ Domínios customizados gratuitos
- ✅ Logs em tempo real
- ✅ Escalabilidade automática
- ✅ Persistência de arquivos

### Limitações Plano Gratuito:
- Spin up após 15 min de inatividade (cold start ~30s)
- 512MB RAM
- 0.1 CPU (com burst)

Para produção sem cold start: Plano Starter ($7/mês)

## Observacao para venda real
Para processar pagamentos reais e emitir nota fiscal, integrar gateway (ex: Stripe, Mercado Pago, Pagar.me) e antifraude antes de operar em producao.

## SillientPay Integration

O site está integrado com SillientPay para processamento de pagamentos (Pix, Cartão, Boleto).

### Configuração

Variáveis de ambiente necessárias:
```bash
SILLIENT_PAY_ENABLED=true
SILLIENT_PAY_BASE_URL=https://api.sillientpay.com
SILLIENT_PAY_API_KEY=sua-chave-api
SILLIENT_PAY_WEBHOOK_SECRET=sua-chave-webhook
```

### Funcionalidades
- ✅ Integração API real com SillientPay
- ✅ Verificação de assinatura de webhook (HMAC-SHA256)
- ✅ Atualização automática de status de pedidos
- ✅ Suporte a produção e sandbox
- ✅ Fallback para modo teste se API falhar

### Documentação Completa
Veja `SILLIENTPAY-SETUP.md` para instruções detalhadas de configuração, testes e troubleshooting.

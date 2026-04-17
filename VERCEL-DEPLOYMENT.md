# 🚀 Deploy NØVRA no Vercel + GitHub

Este guia explica como fazer deploy do projeto Next.js da NØVRA no Vercel via GitHub, sem precisar instalar Node.js localmente.

## Por que Vercel?

- ✅ **Gratuito** para projetos pessoais
- ✅ **Zero config** para Next.js
- ✅ **Deploy automático** ao fazer push no GitHub
- ✅ **SSL automático**
- ✅ **CDN global**
- ✅ **Não precisa de Node.js instalado localmente**

---

## 📋 Pré-requisitos

- Conta no GitHub (gratuita)
- Conta no Vercel (gratuita)
- Projeto Next.js já criado (já temos ✅)

---

## 🎯 Passo a Passo

### 1. Criar Repositório no GitHub

1. Acesse https://github.com
2. Clique em **+** → **New repository**
3. Preencha:
   - **Repository name:** `novra` (ou outro nome)
   - **Public/Private:** Public (ou Private)
   - **Initialize with README:** ❌ Não marque
4. Clique em **Create repository**

### 2. Conectar Repositório Local ao GitHub

Abra o terminal no diretório do projeto:

```bash
# Adicionar remote do GitHub
git remote add origin https://github.com/SEU-USUARIO/novra.git

# Renomear branch para main
git branch -M main

# Push inicial
git push -u origin main
```

**Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub.**

### 3. Criar Conta no Vercel

1. Acesse https://vercel.com
2. Clique em **Sign Up**
3. Faça login com GitHub (recomendado)
4. Siga as instruções de setup

### 4. Importar Projeto no Vercel

1. No painel do Vercel, clique em **Add New** → **Project**
2. Vercel listará seus repositórios do GitHub
3. Encontre e clique em **Import** no repositório `novra`
4. Configure o projeto:
   - **Project Name:** `novra` (ou outro nome)
   - **Framework Preset:** Next.js (detectado automaticamente)
   - **Root Directory:** `./novra-next` (importante!)
   - **Build Command:** `npm run build` (detectado automaticamente)
   - **Output Directory:** `.next` (detectado automaticamente)
5. Clique em **Deploy**

### 5. Configurar Variáveis de Ambiente

Durante ou após o deploy, configure as variáveis de ambiente:

No painel do Vercel:
1. Vá para **Settings** → **Environment Variables**
2. Adicione as seguintes variáveis:

```
SILLIENT_PAY_ENABLED=true
SILLIENT_PAY_BASE_URL=https://api.sillientpay.com
SILLIENT_PAY_API_KEY=sua-chave-api
SILLIENT_PAY_WEBHOOK_SECRET=sua-chave-webhook
SUPABASE_URL=seu-supabase-url
SUPABASE_ANON_KEY=sua-chave-anon
```

3. Clique em **Save**
4. Redeploy o projeto para aplicar as variáveis

### 6. Aguardar Deploy

O Vercel vai:
- Instalar dependências automaticamente
- Buildar o projeto Next.js
- Fazer deploy global

Isso leva **2-3 minutos** na primeira vez.

### 7. Acessar Site

Após o deploy, você receberá:
- URL do site: `https://novra.vercel.app`
- Dashboard com status do deploy

---

## 🔧 Configurações Avançadas

### Dominio Personalizado

1. Vá para **Settings** → **Domains**
2. Adicione seu domínio
3. Configure DNS conforme instruções do Vercel

### Webhook URL

Para o SillientPay, configure o webhook:
```
https://seu-site.vercel.app/api/webhook/sillientpay
```

### Branch Preview

O Vercel cria automaticamente previews para cada branch:
- Branch `main`: Produção
- Branch `dev`: Preview em `https://novra-dev-SEU-USUARIO.vercel.app`

---

## 📝 Estrutura de Arquivos para Vercel

O projeto já está configurado corretamente:

```
novra/
├── novra-next/           ← Root Directory configurado no Vercel
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   └── src/
│       └── app/
│           ├── api/
│           └── checkout/
└── (outros arquivos Flask)
```

---

## 🔄 Deploy Automático

Após a configuração inicial:

1. Faça mudanças no código
2. Commit e push:
```bash
git add .
git commit -m "Minha mudança"
git push
```
3. Vercel detecta automaticamente
4. Build e deploy automático
5. Site atualizado em 2-3 minutos

---

## 🐛 Troubleshooting

### Erro: "Build failed"

- Verifique se o **Root Directory** está configurado como `./novra-next`
- Verifique as variáveis de ambiente
- Verifique os logs no painel do Vercel

### Erro: "Missing environment variables"

- Adicione as variáveis em **Settings** → **Environment Variables**
- Redeploy após adicionar

### Erro: "Next.js build failed"

- Verifique se há erros de TypeScript no código
- O Vercel mostra logs detalhados do build

---

## 💰 Custos

**Hobby Plan (Gratuito):**
- 100GB bandwidth/mês
- 6GB build cache
- Deploy automático
- SSL grátis
- CDN global

**Pro Plan ($20/mês):**
- 1TB bandwidth/mês
- 100GB build cache
- Analytics avançado
- Edge functions ilimitadas

Para o projeto NØVRA, o plano gratuito é suficiente.

---

## 📚 Links Úteis

- Vercel Docs: https://vercel.com/docs
- Next.js on Vercel: https://vercel.com/docs/frameworks/nextjs
- Environment Variables: https://vercel.com/docs/projects/environment-variables

---

## ✅ Checklist de Deploy

- [x] Projeto Next.js criado
- [x] Repositório no GitHub criado
- [ ] Push para GitHub
- [ ] Conta no Vercel criada
- [ ] Projeto importado no Vercel
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído
- [ ] Webhook configurado no SillientPay
- [ ] Site testado

---

## 🎉 Conclusão

O Vercel é a melhor opção para deploy de Next.js sem precisar de Node.js local. O processo é simples, rápido e automático. Após a configuração inicial, cada push no GitHub gera um novo deploy automaticamente.

# ASTROMETIC — Guia de Instalação e Uso

Sistema de automação para extração de relatórios do Looker Studio e envio via WhatsApp.

---

## PRÉ-REQUISITOS

- Windows com resolução **1920x1080 (Full HD)** — obrigatório
- **Python 3.13+** instalado → https://www.python.org/downloads/
  - Durante a instalação, marque a opção **"Add Python to PATH"**
- Acesso à conta **Google corporativa** para o Looker Studio
- **WhatsApp** instalado no celular

---

## INSTALAÇÃO (apenas na primeira vez)

### 1. Abra o terminal na pasta do projeto

Clique com o botão direito dentro da pasta `astrometic` → **"Abrir no Terminal"**

### 2. Crie o ambiente virtual

```
python -m venv .venv
```

### 3. Ative o ambiente virtual

```
.venv\Scripts\activate
```

> O terminal vai mostrar `(.venv)` no início da linha — isso confirma que está ativo.

### 4. Execute o setup

```
python setup.py
```

Esse script instala todas as dependências e o browser Chromium automaticamente.

---

## CONFIGURAÇÃO DE LOGIN (apenas na primeira vez)

O sistema precisa de dois logins antes de funcionar.

---

### LOGIN 1 — WhatsApp Web

> Faça esse login **antes** de rodar os relatórios, para que o WhatsApp já esteja pronto.

```
python abrir_zap.py
```

- Um browser vai abrir com o QR Code do WhatsApp Web
- Escaneie com seu celular
- Aguarde aparecer a tela do WhatsApp com as conversas
- Feche o terminal com **Ctrl+C**
- ✅ Sessão salva — não precisa repetir (até trocar de celular)

---

### LOGIN 2 — Looker Studio (Google)

> O token da empresa **renova todo dia**, então esse login pode ser pedido a cada nova sessão.

```
python rodar_tudo.py
```

- Um browser vai abrir pedindo login com a conta Google corporativa
- Faça o login normalmente
- Após logar, o script continua sozinho
- ✅ Sessão salva em `user_data/`

---

## USO DIÁRIO

Ative o ambiente virtual antes de rodar qualquer script:

```
.venv\Scripts\activate
```

### Passo 1 — Pré-aquecer o WhatsApp (recomendado)

```
python abrir_zap.py
```

Deixe o browser do WhatsApp aberto em segundo plano.

### Passo 2 — Rodar o fluxo de Eficiência Operacional

```
python rodar_tudo.py
```

- Processa 6 relatórios: PICKING TTS, PICKING NTT, PACKING MONO, PACKING MULTI, PACKING NTT, PTW
- Aplica filtros de hora automaticamente
- Salva os recortes em `recortes/`
- Envia as imagens para o grupo **"ID/EA | Indicadores"** no WhatsApp
- Repete automaticamente a cada 1 hora

### Passo 3 — Rodar o fluxo de Ramp Up

```
python rodar_rampup.py
```

- Processa 6 relatórios de Ramp Up com targets dinâmicos por hora
- Salva os recortes em `rampup_recortes/`
- Envia as imagens com legenda de target para o mesmo grupo
- Execução única (não faz loop)

> **Importante:** rode o `rodar_rampup.py` **após** o `rodar_tudo.py` terminar o primeiro ciclo.
> Rodar os dois ao mesmo tempo pode travar o Looker Studio.

---

## ESTRUTURA DE PASTAS

```
astrometic/
├── rodar_tudo.py         → Fluxo Eficiência (loop a cada 1h)
├── rodar_rampup.py       → Fluxo Ramp Up (execução única)
├── robo_core.py          → Motor do fluxo de Eficiência
├── rampup_core.py        → Motor do fluxo de Ramp Up
├── alfaiate.py           → Recorte das imagens de Eficiência
├── carteiro.py           → Envio WhatsApp — Eficiência
├── carteiro_rampup.py    → Envio WhatsApp — Ramp Up
├── abrir_zap.py          → Pré-autenticação do WhatsApp
├── setup.py              → Instalação automática
│
├── user_data/            → Sessão do Looker Studio ⚠️ não deletar
├── sessao_zap/           → Sessão do WhatsApp Web  ⚠️ não deletar
│
├── prints_finais/        → Screenshots brutos (Eficiência)
├── recortes/             → Imagens prontas para envio (Eficiência)
├── rampup_brutos/        → Screenshots brutos (Ramp Up)
└── rampup_recortes/      → Imagens prontas para envio (Ramp Up)
```

---

## PROBLEMAS COMUNS

**O browser abre mas pede login no Looker toda vez**
→ Normal. O token da empresa renova diariamente. Faça o login e o script continua.

**O WhatsApp pede QR Code de novo**
→ A sessão expirou ou o celular foi trocado. Rode `python abrir_zap.py` e escaneie novamente.

**As imagens saem cortadas ou com layout errado**
→ Verifique se o monitor está em resolução **1920x1080**. O sistema não funciona em outras resoluções.

**O script trava ao aplicar filtros no Looker**
→ O Looker às vezes demora. O sistema tenta até 3 vezes automaticamente antes de pular para o próximo relatório.

**Erro: `.venv\Scripts\activate` não reconhecido**
→ Execute no PowerShell como administrador:
```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Depois tente ativar o venv novamente.

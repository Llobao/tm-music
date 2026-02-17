# tm-music

App de análise musical e prospecção com foco em inteligência de mercado social.

## Super Agente de IA (MVP já iniciado)

Este repositório agora já tem uma base funcional de backend para o **Super Agente**, com foco na função mais crítica que você pediu:

- **Escuta (Listening) em tempo real por colunas de palavra-chave**.
- Exemplo de colunas: `Sertanejo` e `Mari Fernandes`.
- Cada coluna consolida: volume, sentimento, fontes e feed de menções.

## Funcionalidades implementadas

1. **Cadastro de colunas de listening** por palavra-chave.
2. **Ingestão de menções** (texto + fonte + data opcional).
3. **Matching automático** de menções para as colunas monitoradas.
4. **Classificação simples de sentimento** (`positivo`, `negativo`, `neutro`).
5. **Endpoint de feed por coluna** com:
   - volume,
   - distribuição de sentimento,
   - breakdown por origem,
   - lista das menções recentes.

## Endpoints disponíveis

- `GET /health`
- `POST /columns`
- `GET /columns`
- `DELETE /columns/{column_name}`
- `POST /mentions`
- `GET /listening/{column_name}?limit=50`

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse a documentação interativa em:
- `http://127.0.0.1:8000/docs`

## Exemplo rápido (fluxo)

1) Criar colunas:

```bash
curl -X POST http://127.0.0.1:8000/columns -H 'Content-Type: application/json' -d '{"name":"Sertanejo"}'
curl -X POST http://127.0.0.1:8000/columns -H 'Content-Type: application/json' -d '{"name":"Mari Fernandes"}'
```

2) Ingerir menções:

```bash
curl -X POST http://127.0.0.1:8000/mentions -H 'Content-Type: application/json' -d '{"text":"Novo hit de Sertanejo, música incrível!","source":"x"}'
curl -X POST http://127.0.0.1:8000/mentions -H 'Content-Type: application/json' -d '{"text":"Mari Fernandes lançou show top","source":"instagram"}'
```

3) Consultar feed de listening por coluna:

```bash
curl http://127.0.0.1:8000/listening/Sertanejo
```

## Próximo passo sugerido

- Conectar APIs reais de redes (X, YouTube, Instagram, TikTok quando disponível).
- Adicionar streaming com WebSocket para atualização em tempo real no dashboard.
- Criar interface web com colunas estilo command center.

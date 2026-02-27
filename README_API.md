# RAG Chat API - Documentação

## ✅ Sistema Completo Implementado

### **1. Salvamento de Chats**

**SIM, salva corretamente!** O sistema persiste:

- **Chats** → Tabela `chats` (Postgres)
  - `id`, `user_id`, `chat_type_id`, `title`, `created_at`, `updated_at`
  
- **Mensagens** → Tabela `messages` (Postgres)
  - `id`, `chat_id`, `role` (user/assistant/system), `content`, `created_at`
  
- **Chunks** → Qdrant (vetores + conteúdo) + Postgres (metadata)
  - Qdrant: embeddings + payload (question, answer, metadata)
  - Postgres: `knowledge_chunks` (tracking com `qdrant_point_id`)

### **2. Rotas da API**

**SIM, todas as rotas utilizam corretamente:**

#### **ChatTypes** (`/api/v1/chat-types`)
- ✅ `POST /` - Criar chat type
- ✅ `GET /` - Listar (filtros: is_public, owner_id)
- ✅ `GET /{id}` - Buscar por ID
- ✅ `DELETE /{id}` - Deletar (remove collection Qdrant + cascata DB)
- ✅ `GET /{id}/info` - Info + stats do Qdrant

#### **Chats** (`/api/v1/chats`)
- ✅ `POST /` - Criar sessão (salva em `chats`)
- ✅ `GET /` - Listar (filtros: user_id, chat_type_id)
- ✅ `GET /{id}` - Buscar com mensagens
- ✅ `DELETE /{id}` - Deletar (cascata para mensagens)
- ✅ `POST /{id}/messages` - **Enviar mensagem com RAG completo**

#### **Upload** (`/api/v1/upload`)
- ✅ `POST /chat-type` - Criar ChatType + ingerir planilha
- ✅ `POST /{id}/chunks` - Adicionar chunks a ChatType existente

### **3. Ingestor de Chunks**

**SIM, existe e está completo!** → `src/services/ingestion.py`

#### **Colunas Necessárias na Planilha:**

**Obrigatórias:**
- `question` - Pergunta/questão (padrão, configurável)
- `answer` - Resposta (padrão, configurável)

**Formatos Suportados:**
- `.xlsx` (Excel)
- `.xls` (Excel antigo)
- `.csv` (CSV)

#### **Exemplo de Planilha:**

| question | answer |
|----------|--------|
| O que é fotossíntese? | Fotossíntese é o processo pelo qual plantas convertem luz solar em energia química... |
| Qual a capital do Brasil? | Brasília é a capital do Brasil, localizada no Distrito Federal... |
| Como funciona a mitose? | Mitose é o processo de divisão celular que resulta em duas células-filhas... |

#### **Colunas Customizadas:**

Você pode usar nomes diferentes passando parâmetros:

```bash
POST /api/v1/upload/chat-type
- question_column: "pergunta"
- answer_column: "resposta"
```

### **4. Fluxo Completo de Dados**

```
Upload Planilha
    ↓
Parse (pandas)
    ↓
Gerar Embeddings (HuggingFace local)
    ↓
Inserir no Qdrant (collection por chat_type_id)
    ↓
Salvar metadata no Postgres (knowledge_chunks)
    ↓
ChatType criado e pronto para uso
```

### **5. Fluxo RAG nas Mensagens**

```
User envia mensagem
    ↓
Salva em messages (role=user)
    ↓
Busca histórico (últimas 10 msgs)
    ↓
RAGPipeline.run():
    1. Retrieve (busca semântica Qdrant)
    2. Rerank (cross-encoder scoring)
    3. Generate (LLM com contexto)
    ↓
Salva resposta em messages (role=assistant)
    ↓
Retorna: user_message + assistant_message + chunks
```

### **6. Exemplo de Uso Completo**

#### **Passo 1: Upload de Planilha**
```bash
curl -X POST "http://localhost:8000/api/v1/upload/chat-type" \
  -F "file=@questoes_enem.xlsx" \
  -F "name=ENEM 2024" \
  -F "description=Questões do ENEM" \
  -F "is_public=true" \
  -F "question_column=question" \
  -F "answer_column=answer"

# Resposta:
{
  "chat_type_id": 1,
  "chunks_ingested": 150,
  "message": "Successfully created chat type 'ENEM 2024' with 150 chunks"
}
```

#### **Passo 2: Criar Chat**
```bash
curl -X POST "http://localhost:8000/api/v1/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_type_id": 1,
    "title": "Estudando ENEM",
    "user_id": 1
  }'

# Resposta:
{
  "id": 1,
  "user_id": 1,
  "chat_type_id": 1,
  "title": "Estudando ENEM",
  "created_at": "2024-02-27T14:00:00Z",
  "updated_at": "2024-02-27T14:00:00Z"
}
```

#### **Passo 3: Enviar Mensagem com RAG**
```bash
curl -X POST "http://localhost:8000/api/v1/chats/1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "O que é fotossíntese?"
  }'

# Resposta:
{
  "user_message": {
    "id": 1,
    "chat_id": 1,
    "role": "user",
    "content": "O que é fotossíntese?",
    "created_at": "2024-02-27T14:01:00Z"
  },
  "assistant_message": {
    "id": 2,
    "chat_id": 1,
    "role": "assistant",
    "content": "Baseado nas informações da base de conhecimento...",
    "created_at": "2024-02-27T14:01:05Z"
  },
  "retrieved_chunks": [
    {
      "question": "O que é fotossíntese?",
      "answer": "Fotossíntese é o processo...",
      "score": 0.92
    }
  ]
}
```

### **7. Configurações Importantes**

#### **.env**
```env
# Modelos AI
EMBEDDING_MODEL_ID=mixedbread-ai/mxbai-embed-large-v1
RERANKER_MODEL_ID=BAAI/bge-reranker-base

# RAG Parameters
K_RETRIEVAL=20  # Chunks iniciais da busca
TOP_K=5         # Chunks após reranking
THRESHOLD=0.3   # Score mínimo do reranker

# LLM Providers
OLLAMA_API_KEY=ollama
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

### **8. Estrutura de Dados**

#### **Postgres Tables:**
- `users` - Usuários (placeholder por enquanto)
- `chat_types` - Tipos de chat (ENEM, ITA, custom)
- `chats` - Sessões de chat
- `messages` - Mensagens (user/assistant)
- `knowledge_chunks` - Metadata dos chunks (referência Qdrant)

#### **Qdrant Collections:**
- Uma collection por `chat_type_id`
- Nome: `chat_type_{id}`
- Vector size: 1024 (mxbai-embed-large-v1)
- Payload: `{question, answer, metadata}`

### **9. Recursos Implementados**

✅ Multi-tenant (collections isoladas por ChatType)
✅ Upload de planilhas (Excel/CSV)
✅ Embeddings locais (HuggingFace)
✅ Reranking com cross-encoder
✅ RAG Pipeline completo
✅ Histórico de chat contextual
✅ Múltiplos LLM providers (Ollama, OpenAI, Gemini)
✅ Streaming support (implementado, não usado por padrão)
✅ Structured outputs (implementado, não usado por padrão)
✅ API REST completa
✅ Migrations automáticas (Alembic)
✅ Logging estruturado

### **10. Próximos Passos (Opcional)**

- [ ] Autenticação de usuários (JWT)
- [ ] Streaming de respostas no endpoint
- [ ] WebSocket para chat real-time
- [ ] Rate limiting
- [ ] Cache de embeddings
- [ ] Métricas e analytics
- [ ] Frontend React

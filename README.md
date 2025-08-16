# Hybrid Product Search (BM25 first, vector-ready)

Portfolio-ready Elasticsearch project showcasing:
- Clean BM25 search with analyzers, synonyms, and completion suggest.
- Dockerized ES + Kibana + FastAPI API.
- Seeded sample data; ready to extend with dense vectors later.

## Quickstart
```bash
# 1) Start stack
cp .env.example .env 2>/dev/null || true
Docker compose up -d # or: docker compose up -d

# 2) Seed sample docs
curl -X POST http://localhost:8000/index_sample

# 3) Try search
curl "http://localhost:8000/search?q=television"

# 4) Suggestions
curl "http://localhost:8000/suggest?q=sm"
```

> Login to Kibana: **elastic / changeme** (change in `.env`).

## Endpoints
- `GET /health` cluster health
- `POST /index_sample` bulk index the provided JSON
- `GET /search?q=&size=` basic relevance (BM25 with boosts)
- `GET /suggest?q=&size=` completion suggestions

## Next steps (issues you can open)
- [ ] Add `dense_vector` field and HNSW index.
- [ ] Offline embedder job (sentence-transformers) to vectorize docs.
- [ ] Hybrid query via `script_score` (BM25 + cosine).
- [ ] UI (React) with facets and "why did this match?" panel.
- [ ] Relevance tests with pytest.

## Dev Notes
- Image versions pinned in `.env`.
- Single-node ES with security enabled.
- ILM/templates directory scaffolded for future.

## License
MIT (code). Data is synthetic.

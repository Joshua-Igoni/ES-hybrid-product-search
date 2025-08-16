# Hybrid Product Search (BM25 first, vector-ready)

Portfolio-ready Elasticsearch project showcasing:
- Clean BM25 search with analyzers, synonyms, and completion suggest.
- Dockerized Elasticsearch + Kibana + FastAPI API.
- Seeded sample data; ready to extend with dense vectors later.

## Quickstart
```bash
# 1) Start stack
cp .env.example .env 2>/dev/null || true

# Start Elasticsearch and API first
docker compose up -d elasticsearch api

# Set a password for the built-in kibana_system user (only needs to be done once)
curl -u elastic:changeme -X POST http://localhost:9200/_security/user/kibana_system/_password \
  -H 'Content-Type: application/json' -d '{"password":"kibanapass"}'

# Add to your .env
ELASTICSEARCH_USERNAME=kibana_system
ELASTICSEARCH_PASSWORD=kibanapass

# Then bring up Kibana:
docker compose up -d kibana

# 2) Seed sample docs
curl -X POST http://localhost:8000/index_sample

# 3) Try search
curl "http://localhost:8000/search?q=television"

# 4) Suggestions
curl "http://localhost:8000/suggest?q=sm"
```

## Kibana Access
- Endpoint: [http://localhost:5601](http://localhost:5601)
- **Backend auth:** Kibana ↔ Elasticsearch uses the `kibana_system` user with its password.
- **Login to web UI:** username `elastic`, password `changeme` (from `.env`).

> ⚠️ You must not configure Kibana with the `elastic` superuser in `docker-compose.yaml`. Use the `kibana_system` user instead.

## Endpoints
- `GET /health` → cluster health
- `POST /index_sample` → bulk index the provided JSON
- `GET /search?q=&size=` → basic relevance (BM25 with boosts)
- `GET /suggest?q=&size=` → completion suggestions

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
- Kibana requires the `kibana_system` user (not `elastic`).

## License
MIT (code). Data is synthetic.

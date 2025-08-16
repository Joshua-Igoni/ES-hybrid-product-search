from fastapi import FastAPI, Query
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import os, json, time

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ES_USER = os.getenv("ELASTIC_USERNAME", "elastic")
ES_PASS = os.getenv("ELASTIC_PASSWORD", "changeme")
INDEX_NAME = os.getenv("INDEX_NAME", "products")

es = Elasticsearch(ES_URL, basic_auth=(ES_USER, ES_PASS), request_timeout=30)
app = FastAPI(title="Hybrid Product Search (BM25-first)")

MAPPINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "my_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        "tv, television",
                        "smartphone, phone, mobile",
                        "laptop, notebook"
                    ]
                }
            },
            "analyzer": {
                "my_text_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "my_synonyms"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "my_text_analyzer", "fields": {"raw": {"type": "keyword"}}},
            "title_suggest": {"type": "completion"},
            "description": {"type": "text", "analyzer": "my_text_analyzer"},
            "brand": {"type": "keyword"},
            "category": {"type": "keyword"},
            "price": {"type": "scaled_float", "scaling_factor": 100},
            "tags": {"type": "keyword"}
            # Vector field can be added later: "embedding": {"type": "dense_vector", "dims": 768, "index": True, "similarity": "cosine"}
        }
    }
}

class SearchResponse(BaseModel):
    took: int
    hits: list

@app.on_event("startup")
def ensure_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=MAPPINGS)

@app.get("/health")
def health():
    try:
        h = es.cluster.health()
        return {"status": h.get("status"), "cluster": h}
    except Exception as e:
        return {"status": "red", "error": str(e)}

@app.post("/index_sample")
def index_sample():
    with open("/app/data/sample_products.json", "r", encoding="utf-8") as f:
        docs = json.load(f)
    ops = []
    for d in docs:
        d["title_suggest"] = d.get("title", "")
        ops.append({"index": {"_index": INDEX_NAME, "_id": d["id"]}})
        ops.append(d)
    es.bulk(operations=ops, refresh=True)
    es.indices.refresh(index=INDEX_NAME)
    return {"indexed": len(docs)}

@app.get("/search", response_model=SearchResponse)
def search(q: str = Query(""), size: int = 10):
    query = {"match_all": {}} if not q else {
        "bool": {
            "should": [
                {"multi_match": {"query": q, "fields": ["title^3", "description", "tags"]}},
                {"term": {"brand": {"value": q, "boost": 2.0}}}
            ]
        }
    }
    res = es.search(index=INDEX_NAME, size=size, query=query)
    hits = [
        {
            "id": h["_id"],
            "score": h.get("_score"),
            **h["_source"]
        } for h in res["hits"]["hits"]
    ]
    return {"took": res.get("took", 0), "hits": hits}

@app.get("/suggest")
def suggest(q: str, size: int = 5):
    body = {
        "suggest": {
            "title_suggest": {
                "prefix": q,
                "completion": {"field": "title_suggest", "skip_duplicates": True, "size": size}
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=body)
    options = res["suggest"]["title_suggest"][0]["options"]
    return {"suggestions": [o["text"] for o in options]}

# Tg bot for RAG-agent
Tg bot for RAG-agent on intelligent search and analysis of tech media articles

## RAG-API
POST /search
```json
{
  "query": "text",
  "filters": {
    "author": "nickname",
    "date": "YYYY-MM-DD",
    "topic": "text"
  }
}
```

answer
```json
{
  "summary": "Найдено 3 статьи по нейросетям",
  "articles": [
    {
      "title": "text",
      "url": "https://example.com/1",
      "author": "nickname",
      "date": "YYYY-MM-DD",
      "topic": "text"
    }
  ]
}
```

## bot setting

requires 3 buttons:
- \start
- \search
- \help

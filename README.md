## Пример RAG пайплана для работы с PDF файлами

* Батчинг

* Саммаризация

* Гибридный поиск полнотектовый + векторный


## Архитектура распределенного RAG-пайплайна (Event-Driven Architecture)

Система спроектирована по канонам децентрализованных асинхронных Highload-платформ. Взаимодействие между изолированными микросервисами (воркерами) оркеструется через брокер сообщений Apache Kafka, что обеспечивает горизонтальное масштабирование и высокую отказоустойчивость контура (Fault Tolerance).

```mermaid
graph TD
    %% Стилизация узлов кластера
    classDef endpoint fill:#1f77b4,stroke:#fff,stroke-width:2px,color:#fff;
    classDef storage fill:#2ca02c,stroke:#fff,stroke-width:2px,color:#fff;
    classDef kafka fill:#ff7f0e,stroke:#fff,stroke-width:2px,color:#fff;
    classDef worker fill:#9467bd,stroke:#fff,stroke-width:2px,color:#fff;
    classDef db fill:#17becf,stroke:#fff,stroke-width:2px,color:#fff;

    %% Сетевой контур ввода данных
    API[FastAPI Endpoint]:::endpoint -->|1. Upload File| S3[(S3 Object Storage)]:::storage
    API -->|2. Emit Event: file_id, doc_url| T1[Topic 1: doc_raw_topic]:::kafka

    %% Воркер №1: Нарезка Чанков
    T1 -->|3. Consume| W1[Worker 1: Chunker]:::worker
    W1 -->|4. SQL INSERT Chunks| DB[(PostgreSQL)]:::db
    W1 -->|5. Emit Event: file_id| T2[Topic 2: chunks_ready_topic]:::kafka

    %% Воркер №2: Саммаризация и Векторизация
    T2 -->|6. Consume| W2[Worker 2: Summarizer]:::worker
    W2 -->|7. Non-blocking Batch Request via SOCKS5| OpenAI[OpenAI API via Proxy]:::endpoint
    W2 -->|8. SQL UPDATE pgvector + TSVECTOR| DB
    W2 -->|9. Emit Event: file_id| T3[Topic 3: doc_summarize_all_topic]:::kafka

    %% Воркер №3: Финализация
    T3 -->|10. Consume| W3[Worker 3: Finalizer]:::worker
    W3 -->|11. Full Doc Summary Processing| DB
```

### Ключевые паттерны :
1. **Asynchronous Non-blocking Input:** FastAPI-эндпоинт разгружен на 100%. Он мгновенно сбрасывает тяжелый payload в S3, отправляет компактное событие в Kafka и возвращает клиенту ответ `HTTP 202 Accepted`, предотвращая таймауты сетевых шлюзов.
2. **Horizontal Scaling & Fault Tolerance:** Сервисы полностью изолированы. При пиковых нагрузках `Worker 2` (Summarizer) масштабируется независимо за счет увеличения количества партиций в Кафке. В случае отказа сетевого прокси, сообщения накапливаются в буфере брокера без потери данных.
3. **Highload-оптимизация СУБД:** Векторные эмбеддинги индексируются через `HNSW` индекс расширения `pgvector` для мгновенного расчета косинусного сходства. Лемматизация текстового саммари вынесена на уровень ядра СУБД через `Computed TSVECTOR` с `GIN` индексацией, реализуя сверхбыстрый гибридный поиск.


# Telegram News SaaS Bot

Production-ready Telegram SaaS platform for RSS aggregation, translation, routing and automated publication.

## Stack

- Python 3.12
- python-telegram-bot
- PostgreSQL
- SQLAlchemy
- Alembic
- APScheduler
- feedparser
- BeautifulSoup4
- RapidFuzz
- Railway

---

# Features

## User Features

- RSS source packs
- Personal subscriptions
- City packs
- Telegram channel delivery
- Telegram group delivery
- Forum topic publishing
- Routing by source packs

## Admin Features

- Pack management
- Source management
- Routing rules
- User management
- Support system
- Delivery logs
- Retry management

---

# Architecture

```text
Fetch
↓
Parse
↓
Clean
↓
Normalize
↓
Duplicate Detection
↓
Translate
↓
Format
↓
Publish

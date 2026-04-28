# ⭐️ Pro Plan API
A simple REST API for managing Pro plan subscriptions.

## ⚡ Highlights
- **Minimalist domain design**
- **Authentication-free** — intended for backend services
- **Ready to run** — out of the box with Docker
- **Unit and functional tests** — covering domain logic and API behavior

## 📦 Subscription
- **Single subscription model**
- **Identified by email** — no external identifiers required
- **Simple lifecycle management** — no states, only validity period
- **End-of-month renewals** — calendar-based, including leap years

## 📬 Notifications
- **Email notification on subscription renewal**

## 🔌 API Endpoints
- **Health check** — service availability
- **Upsert subscription** — create or update a subscription
- **Get subscription** — retrieve a subscription
- **Renew subscription** — extend the current validity

## 🏗️ Stack & Architecture
- **Python + FastAPI**
- **Clean Architecture**
- **Use-case driven design**
- **Rich domain models** — organized into domain modules
- **Value objects**
- **UUIDs** — primary identifiers

## ⚙️ Development
### Requirements
- Docker
- Docker Compose

### Getting Started
1. Run the project:
```shell
docker compose up -d
```

2. Run database migrations:
```shell
docker compose exec api make m
```

### URLs
API Base URL: http://localhost/api

#### Tools
- API Docs: http://localhost/docs
- Mailcatcher: http://localhost:81

### Commands
Useful commands are available in the [Makefile](./Makefile).

## 🎯 About the Project
An example project demonstrating backend system design.

## 🧑‍💼 Author
**Dušan Mlynarčík** — Senior Backend Engineer & App Builder

- LinkedIn: https://www.linkedin.com/in/dusanmlynarcik/
- GitHub: https://github.com/dusanmlynarcikdev
- Web: https://dusanmlynarcik.com

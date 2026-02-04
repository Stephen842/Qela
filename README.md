# Qela – Social Media Feed Backend

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![GraphQL](https://img.shields.io/badge/GraphQL-Graphene-purple)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)
![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-blue)
![Redis](https://img.shields.io/badge/Cache-Redis-red)
![Celery](https://img.shields.io/badge/Task-Celery-green)
![RabbitMQ](https://img.shields.io/badge/Broker-RabbitMQ-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Project Overview

**Qela** is a scalable, hybrid backend system for a modern social media platform. It intentionally combines **RESTful APIs and GraphQL** to separate concerns, improve maintainability, and follow real-world production architecture patterns.

The system follows a **dual-API model**:

- **REST API (JWT-based)** → Handles **authentication, accounts, and identity management**
- **GraphQL API** → Powers the **entire social media experience** (posts, comments, likes, feeds, and analytics)

This approach mirrors how many large-scale platforms operate in production:  
authentication is handled via REST, while data-rich relational domains are managed with GraphQL.

Key goals of the project include:

- Building a production-ready backend architecture  
- Implementing secure JWT-based authentication  
- Designing an optimized relational database schema  
- Delivering a clean, flexible GraphQL API with Playground support  
- Demonstrating modern backend engineering practices  

---

## Why the Name “Qela”?

The name **Qela** is coined from the **isiXhosa language**, where the word *“iqela”* means **a group, team, or collective**. In its linguistic and cultural context, it represents people or elements coming together around a shared purpose, emphasizing ideas of **connection, collaboration, and cohesion**.

This meaning closely aligns with the core purpose of the project.

**Qela** is a scalable backend system for a social media feed platform, built around the idea of connection — users connecting with content, users connecting with other users, and interactions forming a living network of activity. Posts, comments, and likes are not isolated features; they are interconnected entities that gain value through their relationships.

From a technical perspective, the name **Qela** represents:

- **Connection** — clearly defined relationships between users, posts, comments, and likes.  
- **Flow** — efficient data movement through GraphQL queries, mutations, and pagination.  
- **Structure** — strong schema design and separation of concerns in the backend.  

In essence, **Qela is not just a name** — it represents a backend engineered around meaningful connections, efficient data flow, and a strong architectural foundation.

---

## Features

### Core Capabilities

- **User Authentication:** User registration, login, and secure JWT-based authentication using Django Restful Framework.  
- **Posts:** Create, retrieve, and manage posts.  
- **Comments:** Add comments to posts and fetch comment threads.  
- **Likes:** Like and unlike posts (one like per user per post).  
- **GraphQL API:** Single `/graphql/` endpoint with GraphQL Playground enabled.  
- **Pagination & Filtering:** Efficient pagination for feeds.  
- **Analytics:** Basic analytics such as likes count per post.  
- **Asynchronous Processing:** Background tasks with Celery.  
- **Caching:** Redis-based caching for performance.  
- **Search & Filtering:** Search posts by content and filter feeds.  
- **Business Rules Enforcement:** Secure mutations and valid relationships between data.  

---

## Flow of Data

1. Client authenticates via **REST API** and receives a JWT.  
2. The JWT is sent in the `Authorization` header when calling GraphQL.  
3. GraphQL serves social data based on the authenticated user.  

---

## Feature Breakdown

### Authentication (REST API)

- User registration  
- Secure JWT-based login  
- Access & refresh token handling  
- Token-based session management  

### Social Features (GraphQL)

- **Posts:** Create, retrieve, update, delete  
- **Comments:** Threaded comments linked to posts  
- **Likes:** One like per user per post  
- **Feed System:** Paginated and optimized social feed  
- **Search & Filtering:** Search posts by content, author, or date  
- **Analytics:** Engagement metrics like total likes per post  

### Backend Capabilities

- Asynchronous tasks using **Celery**  
- Redis-based caching  
- Optimized database queries using `select_related` and `prefetch_related`  
- Dockerized local development  

---

## Tech Stack

- **Backend Framework:** Django 5.2  
- **REST API:** Django REST Framework (DRF)  
- **GraphQL:** Graphene-Django  
- **Authentication:** JWT using DRF  
- **Database:** PostgreSQL  
- **Asynchronous Tasks:** Celery  
- **Message Broker:** RabbitMQ  
- **Caching Layer:** Redis  
- **Containerization:** Docker & Docker Compose  
- **Testing:** GraphQL Playground + Django tests  
- **Deployment:** PythonAnywhere  

---

## Core Architecture: REST + GraphQL (Hybrid Model)

### REST API — Authentication & Accounts Layer

The REST API serves as the **identity and access control system**. It handles:

- User registration  
- User login  
- JWT token issuance  
- Token validation and refresh  
- User profile management  
- Secure authentication middleware  

> **Important:** Authentication logic lives in REST, not GraphQL.

---

### GraphQL API — Social Media Layer

GraphQL handles all social interactions, including:

- Creating and retrieving posts  
- Adding comments to posts  
- Liking and unliking posts  
- Fetching paginated feeds  
- Filtering and searching content  
- Computing engagement analytics  

GraphQL is exposed via:
- http://localhost:8000/graphql/

---

## System Architecture

### Layered Flow

- **Client (Frontend)**  
  ↓  

- **REST API (`/api/`) — Authentication Layer**  
  - JWT Authentication  
  - Login endpoint  
  - Registration endpoint  
  - Token management  
  ↓  

- **GraphQL API (`/graphql/`) — Social Layer**  
  ↓  

- **Django Application**  
  - ORM (Models, Queries, Mutations)  
  - Celery Workers (Background Tasks)  
    - RabbitMQ (Message Broker)  
  - Redis (Caching Layer)  
  - PostgreSQL (Primary Database)

### Responsibilities

- Queries handle reads (posts, comments, likes).  
- Mutations handle writes (create posts, add comments, like posts).  
- Celery handles background jobs.  
- RabbitMQ queues tasks reliably.  
- Redis improves performance through caching.  
- PostgreSQL stores all persistent data.  

---

## Database Schema
### Core Entities

| Model | Fields |
|------|--------|
| **User** | id, username, email, password, created_at |
| **Post** | id, author_id (FK → User), content, created_at, updated_at |
| **Comment** | id, post_id (FK → Post), author_id (FK → User), content, created_at |
| **Like** | id, user_id (FK → User), post_id (FK → Post), created_at |

**Constraint:**  
- Unique constraint on `(user_id, post_id)` for likes  

**Best Practices Applied:**

- Indexed foreign keys  
- Automatic timestamps  
- Database-level uniqueness enforcement  
- Optimized query strategies  

---

## Project Status

**Qela** is an actively evolving backend project designed with real-world production concerns in mind. While the core social feed features are implemented, the system is structured to support continuous improvement, scalability, and future extensions without major architectural changes.

---

## Roadmap & Future Improvements

Planned enhancements for future iterations include:

- **Advanced Search**  
  - Full-text search  
  - Ranking by relevance  

- **Personalized Feeds**  
  - Activity-based recommendations  
  - Cursor pagination  

- **Notifications**  
  - Celery-powered alerts  
  - Email or in-app notifications  

- **Security**  
  - Rate limiting  
  - Fine-grained permissions  

- **Observability**  
  - Logging and monitoring  
  - Error tracking  

- **Scalability**  
  - Read replicas  
  - Improved caching strategies  

---

## Design Philosophy

Qela follows a:

- Backend-first mindset  
- Schema-driven development  
- Clear separation of concerns  
- Scalability by design  


The project intentionally mirrors how modern social platforms structure their backend systems, making it suitable for learning, experimentation, and real deployment scenarios.

---

## Getting Started

### Prerequisites

Ensure the following tools and services are installed on your system:

- **Python:** 3.11 or higher
- **Django:** 5.0 or higher
- **Graphene-django**
- **Docker & Docker Compose**
- **PostgreSQL**
- **Celery**
- **Redis**
- **RabbitMQ**

---

### Local Development Setup

Follow the steps below to run the project locally using Docker:

# Clone the repository
git clone https://github.com/stephen842/qela.git
cd qela

# Build and start all services
docker-compose up --build

# Apply database migrations
docker-compose exec web python manage.py migrate

# Create a superuser for admin access
docker-compose exec web python manage.py createsuperuser

Once the services are running, you can access the GraphQL Playground at:

http://localhost:8000/graphql/

---

## Contribution Guidelines

Contributions are welcome and encouraged. If you would like to contribute:

1. Fork the repository
2. Create a feature branch (`feature/your-feature-name`)
3. Commit changes with clear messages
4. Submit a pull request with a concise description

All contributions should follow existing coding standards and emphasize clarity, performance, and maintainability.

---

## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software for personal or commercial purposes, provided that the original license and copyright notice are included.

---

## Final Note

**Qela** serves as both a learning-driven and production-inspired backend system. It demonstrates how thoughtful architecture, clear domain modeling, and modern tooling come together to form scalable and maintainable software.

The project reflects a commitment to clean backend engineering, real-world constraints, and systems that grow through intentional design—just like the communities they support.

---

## Author & Contact

**Ugota Chisom Stephen**  
Backend Engineer | Django | DevOps | Blockchain
  
- **LinkedIn:** www.linkedin.com/in/ugota-c-stephen-6b1846306 
- **Email:** ugotachisomstephen@gmail.com  

Feel free to reach out for collaboration, feedback, or discussions around backend architecture, GraphQL APIs, asynchronous systems, and scalable web platforms.

# Qela – Social Media Feed Backend

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/)
[![GraphQL](https://img.shields.io/badge/GraphQL-Graphene-purple)](https://docs.graphene-python.org/projects/django/en/latest/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## Project Overview
**Qela** is a scalable backend system for a social media feed platform. It demonstrates best practices in backend engineering, deep GraphQL implementation, and clean maintainable code. The project provides a robust foundation for social media interactions including posts, comments, likes, and user authentication. Key goals include building a production-ready backend, implementing JWT-based authentication, creating an optimized database schema, and delivering a clean GraphQL API with Playground support.

## Why the Name “Qela”?

The name **Qela** is coined from the **isiXhosa language**, where the word *“iqela”* means **a group, team, or collective**. In its linguistic and cultural context, it represents people or elements coming together around a shared purpose, emphasizing ideas of **connection, collaboration, and cohesion**.

This meaning closely aligns with the core purpose of the project.

**Qela** is a scalable backend system for a social media feed platform, built around the idea of connection—users connecting with content, users connecting with other users, and interactions forming a living network of activity. Posts, comments, and likes are not isolated features; they are interconnected entities that gain value through their relationships.

From a technical perspective, the name **Qela** represents:
- **Connection**, through clearly defined relationships between users, posts, comments, and likes within a well-structured relational database.
- **Flow**, through efficient data movement enabled by GraphQL queries and mutations, pagination, and optimized resolvers.
- **Structure**, through a solid schema design, enforced constraints, and clean separation of concerns across the backend architecture.

The significance of the name also reflects the project’s philosophy: building systems where components are intentionally designed to work together rather than exist in isolation. Just as the word *Qela* implies cohesion and linkage, the backend is engineered to support scalable growth, maintainability, and real-world usage.

In essence, **Qela is not just a name**—it represents a backend engineered around meaningful connections, efficient data flow, and a strong architectural foundation, mirroring how modern social platforms are built in production environments.

---

## Features
- **User Authentication:** User registration, login, and secure JWT-based authentication.
- **Posts:** Create, retrieve, and manage posts.
- **Comments:** Add comments to posts and fetch comment threads.
- **Likes:** Like and unlike posts (enforced as one like per user per post).
- **GraphQL API:** Single `/graphql/` endpoint with GraphQL Playground enabled.
- **Pagination & Filtering:** Efficient pagination and advanced filtering for feed queries.
- **Analytics:** Basic analytics such as likes count per post.
- **Asynchronous Background Processing:** Background task handling using Celery for non-blocking operations.
- **Caching:** Redis-based caching for frequently accessed data and performance optimization.
- **Search & Filtering:** Search posts by content and filter feeds by author, date, and engagement metrics.
- **Business Rules Enforcement:** Authentication required for mutations, non-empty post content, comments tied to valid posts, and unique likes per user per post.

---

## Tech Stack
- **Backend Framework:** Django 5.2
- **GraphQL:** Graphene-Django
- **Authentication:** JWT-based authentication using `django-graphql-jwt`
- **Database:** PostgreSQL
- **Asynchronous Tasks:** Celery
- **Message Broker:** RabbitMQ
- **Caching Layer:** Redis
- **Containerization:** Docker & Docker Compose
- **Testing:** GraphQL Playground and Django testing framework
- **Deployment Platform:** PythonAnywhere

---

## Architecture

Client (Frontend)
        ▼
GraphQL API (/graphql/)
        ▼
Django Application
        ├── ORM (Models, Queries, Mutations)
        ├── Celery Workers (Background Tasks)
        │        ▼
        │    RabbitMQ (Message Broker)
        │
        └── Redis (Caching Layer)
        │        ▼
        └── PostgreSQL Database


- Queries handle read-only operations (posts, comments, likes count).
- Mutations handle write operations (create posts, add comments, like/unlike posts).
- Celery processes background jobs such as notifications, analytics updates, and heavy computations.
- RabbitMQ acts as the message broker for reliable task queuing.
- Redis is used for caching frequently accessed data and improving read performance.
- Docker ensures consistent environments across development, testing, and production.
- Resolvers are optimized using `select_related` and `prefetch_related` to prevent N+1 queries.

---

## Database Schema
**Entities:**  
- **User:** id, username, email, password, created_at  
- **Post:** id, author_id (FK → User), content, created_at, updated_at  
- **Comment:** id, post_id (FK → Post), author_id (FK → User), content, created_at  
- **Like:** id, user_id (FK → User), post_id (FK → Post), created_at  
  - Unique constraint: `(user_id, post_id)`  

**Best Practices:**  
- Index foreign keys, use timestamps, enforce uniqueness at DB level.  
- Batch queries and avoid heavy nested resolvers for performance.

---

## Project Status

**Qela** is an actively evolving backend project designed with real-world production concerns in mind. While the core social feed features are implemented, the system is structured to support continuous improvement, scalability, and future extensions without major architectural changes.

---

## Roadmap & Future Improvements

Planned enhancements for future iterations include:

- **Advanced Search Capabilities**
  - Full-text search on posts and comments
  - Ranking results by relevance and engagement
- **Feed Optimization**
  - Personalized feeds based on user activity and interests
  - Efficient cursor-based pagination for large datasets
- **Notifications System**
  - Background-driven notifications using Celery
  - Support for email or in-app notifications
- **Rate Limiting & Security**
  - Protect GraphQL endpoints against abuse
  - Improved permission layers and fine-grained access control
- **Observability**
  - Logging, metrics, and monitoring for production readiness
  - Error tracking and performance insights
- **Horizontal Scalability**
  - Improved caching strategies
  - Read replicas and queue-based workload distribution

---

## Design Philosophy

Qela is built with a **backend-first, production-oriented mindset**:

- **Explicit business rules** over implicit behavior
- **Schema-driven development** using GraphQL
- **Clear separation of concerns** across models, resolvers, services, and background workers
- **Scalability by design**, not as an afterthought

The project intentionally mirrors how modern social platforms structure their backend systems, making it suitable for learning, experimentation, and real deployment scenarios.

---

## Getting Started

### Prerequisites

Ensure the following tools and services are installed on your system:

- **Python:** 3.11 or higher
- **Django:** 4.0 or higher
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

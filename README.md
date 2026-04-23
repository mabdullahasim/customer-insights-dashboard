# 📊 Customer Insights Dashboard

A full-stack analytics platform that helps small and medium businesses upload customer data, run automated analysis, and explore interactive dashboards for revenue, satisfaction, and retention.

---

## ✨ Highlights

- **End-to-end analytics** – Upload customer CSVs and instantly see revenue, satisfaction, and retention insights.
- **Secure accounts** – JWT-based sign up, login, and protected API routes.
- **Interactive charts** – Real-time dashboards for revenue, satisfaction, and customer segments.
- **Modern stack** – React + TypeScript frontend, FastAPI backend, PostgreSQL database.

---

## 🧱 Tech Stack

| Layer      | Technologies                              |
|------------|-------------------------------------------|
| Frontend   | React, TypeScript, Tailwind CSS, Chart.js |
| Backend    | FastAPI, SQLAlchemy ORM, Pydantic, PyJWT  |
| Database   | PostgreSQL                                |
| Tooling    | Docker (optional), Git, VS Code, AWS      |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL running locally
- A `.env` file with your `DATABASE_URL` and `SECRET_KEY`

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: [http://localhost:8000](http://localhost:8000)
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

- App: [http://localhost:3000](http://localhost:3000)

---

## 🔑 Core Features

### Authentication

Secure user management with JWT tokens.

| Endpoint          | Method | Description               |
|-------------------|--------|---------------------------|
| `/auth/signup`    | POST   | Register a new user       |
| `/auth/login`     | POST   | Obtain a JWT access token |
| `/auth/profile`   | GET    | Get current user profile  |

The frontend stores the JWT and attaches it to every protected request via the `Authorization: Bearer <token>` header.

---

### CSV Upload & Data Import

1. Log in via the UI or through `/docs` using your JWT token.
2. Navigate to the **Upload** section in the dashboard.
3. Upload a CSV matching the expected schema:
full_name, email, country, total_spent, review_score, review_text, last_purchase_date


The backend will:
- Validate headers and file size
- Parse and sanitize the CSV
- Store rows in the `customers` table, linked to your user account

| Endpoint                  | Method | Description                    |
|---------------------------|--------|--------------------------------|
| `/utils/upload/customers` | POST   | Upload and import customer CSV |

---

### Analytics & Dashboards

After uploading, the dashboard provides interactive insights across three categories:

#### 💰 Revenue
- Total revenue and average order value
- Revenue breakdown by country and customer segment

#### 😊 Satisfaction & Sentiment
- Average review score
- Sentiment scores from review text (VADER) blended with star ratings

#### 🔄 Retention
- Basic churn signals derived from last purchase date and spending patterns

| Endpoint                        | Method | Description                        |
|---------------------------------|--------|------------------------------------|
| `/analytics/overview`           | GET    | Key metrics for the logged-in user |
| `/analytics/revenue-by-country` | GET    | Grouped revenue data               |
| `/analytics/satisfaction`       | GET    | Satisfaction and sentiment metrics |

---

## 📂 Project Structure
root/
├── backend/
│ ├── app/
│ │ ├── api/ # FastAPI routers (auth, utils, analytics)
│ │ ├── core/ # Config, database, JWT/OAuth2 security
│ │ ├── crud/ # DB operations (users, customers, imports)
│ │ ├── models/ # SQLAlchemy models (User, Customer, etc.)
│ │ └── schemas/ # Pydantic schemas (User, Customer, Analytics)
│ ├── main.py # FastAPI entrypoint
│ └── requirements.txt
│
├── frontend/
│ └── src/
│ ├── components/ # Reusable UI components
│ ├── pages/ # Dashboard views
│ ├── charts/ # Chart.js integrations
│ └── services/ # API clients to backend
│
└── README.md

---

## 🧠 Roadmap

- [ ] Advanced filtering by date range, product, or location
- [ ] AI-generated feedback summaries from review text
- [ ] Churn prediction using machine learning models
- [ ] Multi-user teams with role-based access (admin vs. analyst)
- [ ] CI/CD pipeline and cloud deployment (AWS + Docker Compose)

---

## 👤 Author

**Muhammad Abdullah Asim**  
Computer Science, Western University (Class of 2028)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-mabdullahasim-blue?logo=linkedin)](https://linkedin.com/in/mabdullahasim)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
Customer Insights Dashboard

A full-stack analytics platform for businesses to visualize and interpret customer data. It supports secure authentication, CSV upload, automated data analysis, and interactive charts for business insights.

🧭 Overview

The Customer Insights Dashboard helps you track revenue, satisfaction, and customer trends in one place. It integrates a React + TypeScript frontend with a FastAPI backend and a PostgreSQL database.

This project is ideal for small and medium businesses seeking fast, reliable, and secure data visualization without complex BI tools.

🚀 Features

User Authentication (JWT) – Secure sign-up, login, and token refresh

CSV Upload & Parsing – Automatically validate and import customer data

Dynamic Analytics – View monthly revenue, satisfaction scores, and demographics

FastAPI Backend – Clean RESTful architecture with data validation (Pydantic)

SQLAlchemy ORM – Structured relational data modeling

Interactive Dashboards – Built with Chart.js for real-time visualization

Responsive UI – Styled with Tailwind CSS for smooth layout on all devices

🧰 Tech Stack

Frontend
React • TypeScript • Tailwind CSS • Chart.js

Backend
FastAPI • Python • SQLAlchemy • Pydantic • PyJWT

Database
PostgreSQL

Dev Tools
Docker • Git • VS Code • AWS

Backend

Navigate to the backend folder:
cd backend

Install dependencies:
pip install -r requirements.txt

Create a .env file:

DATABASE_URL=postgresql://user:password@localhost:5432/dashboarddb
SECRET_KEY=your_secret_key
ALGORITHM=HS256


Run the backend:
uvicorn main:app --reload

Frontend

Navigate to the frontend folder:
cd frontend

Install dependencies:
npm install

Run the app:
npm start

Access the dashboard at http://localhost:3000.

📊 API Endpoints

Authentication

POST /auth/signup – Register a user

POST /auth/login – Get access token

GET /auth/profile – Retrieve current user info

Data Management

POST /data/upload – Upload CSV file

GET /data/summary – Fetch key metrics

GET /data/revenue – Monthly revenue data

GET /data/satisfaction – Satisfaction score data

🧩 Example Flow

User signs up and logs in.

Uploads a CSV of customer data.

Backend parses and stores the data.

Dashboard displays key performance metrics:

Revenue growth by month

Average satisfaction scores

Customer retention rates

🧠 Future Improvements

Filtering by date, product, or location

AI-based feedback summaries

Admin and team dashboards

Cloud deployment with CI/CD pipelines

👤 Author

Muhammad Abdullah Asim
Computer Science, Western University (Class of 2028)

LinkedIn: linkedin.com/in/mabdullahasim
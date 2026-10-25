# 💰 RupeeWise AI — Smart Expense Tracker with Intelligent Spending Analysis

RupeeWise AI is a complete, production-grade personal finance web application specifically tailored for students, freshers, and working professionals in India. It pairs an intuitive fintech dashboard with intelligent machine learning to auto-categorize daily expenses, forecast future spending trajectories, detect overspending risks, and generate data-grounded saving recommendations.

---

## 🌟 Key Highlights & Architecture

### 1. 🇮🇳 Tailored for Indian Workflows
- **Indian Rupee Formatting (`₹`)**: Built-in support for Indian numbering and currency format (`₹1,00,000`).
- **UPI Integration Ready**: Tracks UPI transaction references (UTR numbers), auto-detects merchants (`swiggy@icici`, `zomato@hdfcbank`, `uber.india@hdfcbank`, `blinkit@yesbank`, `zepto@icici`), and analyzes payment channel shares (UPI vs Cards vs Net Banking vs Cash).
- **Indian Date Standards**: Date displays formatted to Indian locale standards (`DD MMM YYYY`).

### 2. 🤖 Hybrid AI Auto-Categorization Engine
- **Deterministic NLP Heuristics**: Immediate 95%+ confidence classification for top Indian merchants and services across Food, Transportation, Shopping, Bills, Housing, Healthcare, and Education.
- **Scikit-Learn ML Classifier**: Built with `TfidfVectorizer` (unigrams & bigrams) + `MultinomialNB` trained on real transaction narrations.
- **Continual Learning Loop**: Captures user corrections and retrains the classifier incrementally without overriding historical confirmed categories.

### 3. 📈 Predictive Spending Forecasting
- **7-Day and 30-Day Horizons**: Decomposes daily spend history, factors in day-of-week seasonality (e.g. weekend spending surges) and recurring commitments (rent, mutual fund SIPs, broadband).
- **Statistical Uncertainty Bands**: Displays historical actuals alongside future prediction curves with lower and upper confidence bounds.
- **Explainability Factors & Risk Gauge**: Explains why a forecast is trending up or down, and classifies overspending risk as **Low**, **Medium**, or **High**.
- **Cold-Start Guard**: Prevents misleading forecasts when data is insufficient (< 5 days) and prompts users with actionable instructions.

### 4. 💡 Grounded Financial Insights & Recommendations
- **100% Mathematically Grounded**: Insights are computed from verified transaction metrics before being synthesized, preventing AI hallucination.
- **Month-over-Month (MoM) Velocity**: Detects spending acceleration or reductions.
- **Anomaly Detection**: Flags transactions exceeding 2.5 standard deviations above category means.
- **Actionable Micro-Savings**: Calculates exact monthly and annual savings potential from trimming discretionary expenses.

### 5. 🎯 Smart Budget Management & Threshold Alerts
- Set monthly overall spending caps and category-specific allowances.
- Real-time utilization tracking with visual color-coded progress bars.
- Proactive alert triggers at **50%**, **80%**, and **100%** utilization marks.

### 6. 📂 CSV Statement Import & Deduplication
- Ingests bank and UPI statement exports (HDFC, ICICI, SBI, Axis, PhonePe, Google Pay, Paytm formats).
- Cryptographic hash-based duplicate prevention (`MD5(date + amount + title + payment_method)`).
- Complete report showing imported count, skipped duplicates, and failed rows.
- Filter and export transaction history back to CSV at any time.

### 7. 🛡️ Enterprise Security & Resilient Architecture
- **JWT Authentication**: Short-lived access tokens + long-lived refresh tokens with automatic client interceptor rotation.
- **Bcrypt Hashing**: Secure salted password encryption.
- **Strict Data Isolation**: Every transaction and budget query is strictly scoped to the authenticated `user_id`.
- **Dual-Mode Resilient Database**: Direct MongoDB connectivity with automatic fallback to an asynchronous in-memory engine when no local MongoDB daemon is running.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Recharts, React Router v7, Axios |
| **Backend** | Python 3.13, FastAPI, Pydantic v2, Uvicorn, Python-Jose (JWT), Bcrypt |
| **Database** | MongoDB / Motor Async Driver, PyMongo, Mongomock-Motor fallback |
| **Machine Learning** | Scikit-Learn (TF-IDF, Naive Bayes), Pandas, NumPy |
| **Testing** | Pytest, Pytest-Asyncio, Starlette TestClient |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** (Python 3.13 tested)
- **Node.js 18+** & **npm**
- *(Optional)* MongoDB instance on `localhost:27017` (The app automatically falls back to an internal resilient database engine if MongoDB is not running locally).

---

### Step 1: Backend Setup

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. *(Recommended)* Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   A default `.env` is already provided. You can inspect or copy `.env.example`:
   ```bash
   # Windows
   copy .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```

5. *(Optional)* Seed realistic demo transactions (45 days of Indian expenses & salary):
   ```bash
   python seed.py
   ```
   > **Demo Credentials Created:**
   > - **Email:** `demo@expensetracker.in`
   > - **Password:** `DemoPassword123!`

6. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

### Step 2: Frontend Setup

1. In a new terminal, navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser at **[http://localhost:5173](http://localhost:5173)**.

---

## 🧪 Automated Testing

### Backend Test Suite
Run the comprehensive Pytest suite covering authentication, data isolation, transaction CRUD, AI categorizer, budgets, forecasts, insights, and CSV import:

```bash
cd backend
python -m pytest -v app/tests
```

**Test Coverage Highlights:**
- `test_auth_and_profile`: Registration, JWT issuance, profile retrieval, invalid credentials rejection.
- `test_transaction_crud_and_isolation`: Multi-user data privacy checks, updates, deletes.
- `test_ai_categorizer_and_feedback`: Brand heuristics (Swiggy, Uber, Zomato) and ML feedback retraining.
- `test_budget_and_alerts`: 50%, 80%, and 100% threshold utilization alerts.
- `test_seed_samples_forecast_and_insights`: Statistical forecast generation and grounded recommendations.
- `test_csv_import_and_deduplication`: CSV parsing and cryptographic duplicate prevention.

---

## 📑 API Endpoints Reference

### Authentication (`/api/v1/auth`)
- `POST /register` — Register a new user with occupation & income baseline.
- `POST /login` — Authenticate and receive access & refresh tokens.
- `POST /refresh` — Exchange refresh token for a new access token.
- `GET /me` — Retrieve current authenticated user profile.
- `PATCH /me` — Update user profile details and baseline salary.
- `POST /change-password` — Change password securely.
- `POST /logout` — Invalidate user session.

### Transactions (`/api/v1/transactions`)
- `GET /` — Paginated list with search, category, type, channel, and date range filters.
- `POST /` — Create transaction (with auto-hash deduplication and AI categorization).
- `GET /{id}` — Fetch specific transaction by ID.
- `PATCH /{id}` — Edit an existing transaction.
- `DELETE /{id}` — Remove a transaction.
- `GET /export/csv` — Export filtered transactions directly to a formatted CSV file.

### Dashboard & Analytics (`/api/v1/dashboard` & `/api/v1/analytics`)
- `GET /dashboard/summary` — Combined fintech metrics (income, expenses, savings rate, MoM change, category shares, daily trends, payment channel breakdown).
- `GET /analytics/categories` — Segment breakdown with percentages and counts.
- `GET /analytics/trends` — Daily cash-flow history.
- `GET /analytics/payment-methods` — UPI vs Card vs Cash distribution.

### AI Engine (`/api/v1/ai`)
- `POST /categorize` — Predict transaction category from title/merchant with confidence score.
- `POST /feedback` — Submit correction to train the ML classifier incrementally.
- `GET /forecast` — Produce 7-day or 30-day forecast curves with uncertainty intervals.
- `GET /insights` — Generate verified data-grounded observations and savings recommendations.
- `POST /seed-samples` — 1-click generation of 45 days of realistic Indian expense and salary records.

### Budgets (`/api/v1/budgets`)
- `GET /` — List all historical monthly budgets with actual spend comparisons.
- `POST /` — Upsert overall and category limits for a specific month.
- `GET /{month}` — Retrieve monthly utilization and active threshold alerts (50%, 80%, 100%).
- `DELETE /{id}` — Delete a budget.

### Imports (`/api/v1/imports`)
- `POST /csv` — Upload and ingest CSV statements with automatic column detection and duplicate checking.

---

## 🔒 Security Best Practices Implemented

- **Password Security**: Salted bcrypt hashing (max 72-byte safe truncation).
- **JWT Protection**: Short-lived tokens with HS256 signature verification.
- **Resource Authorization**: Every database access strictly verifies `user_id == current_user.id`.
- **Upload Validation**: File size limits (5MB) and mime-type enforcement.
- **Secrets Management**: Configured via `.env` with no hardcoded credentials.
- **CORS Defense**: Restricted to authorized origins.

---

## 📄 License
MIT License. Built with ❤️ for financial empowerment in India.

\# 🏧 NextGen AI ATM Ecosystem



A full-stack ATM simulation system designed to demonstrate how modern banking services can be delivered through an interactive touchscreen interface and a Python backend.



\## 🚀 Project Overview



The NextGen AI ATM Ecosystem combines a React-based frontend with a FastAPI backend to simulate common ATM operations.



The application provides an interactive dashboard where users can view account information, check transaction history, perform withdrawals, and raise support tickets.



\## ✨ Features



\- \*\*ATM Dashboard:\*\* Interactive touchscreen-style interface.

\- \*\*Account Balance:\*\* View account details and available balance.

\- \*\*Cash Withdrawal:\*\* Withdraw money using predefined or custom amounts.

\- \*\*Transaction History:\*\* View recent account transactions.

\- \*\*Customer Support:\*\* Submit support tickets and track their status.

\- \*\*REST API:\*\* Backend services built using FastAPI.

\- \*\*Database Integration:\*\* SQLite database for storing account, transaction, and support ticket information.



\## 🛠️ Technology Stack



| Component | Technology |

|---|---|

| Frontend | React.js |

| Frontend Build Tool | Vite |

| Styling | CSS / Tailwind CSS |

| Backend | Python, FastAPI |

| Database | SQLite |

| API Testing | FastAPI Swagger UI |

| Version Control | Git and GitHub |



\## 🏗️ Project Architecture



```text

NextGen-AI-ATM/

│

├── backend/

│   ├── main.py

│   ├── database.py

│   ├── model.py

│   ├── requirements.txt

│   └── .gitignore

│

├── frontend/

│   ├── public/

│   ├── src/

│   │   ├── assets/

│   │   ├── App.jsx

│   │   ├── App.css

│   │   ├── index.css

│   │   └── main.jsx

│   └── package.json

│

├── .gitignore

├── package.json

└── README.md

```



\## ⚙️ Installation and Setup



\### 1. Clone the repository



```bash

git clone https://github.com/vijayasrichekuri/NextGen-AI-ATM.git

cd NextGen-AI-ATM

```



\### 2. Start the Backend



```bash

cd backend

python -m venv venv

```



Activate the virtual environment on Windows:



```bash

venv\\Scripts\\activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Start the FastAPI server:



```bash

uvicorn main:app --reload

```



Backend URL:



`http://127.0.0.1:8000`



API documentation:



`http://127.0.0.1:8000/docs`



\### 3. Start the Frontend



Open another terminal:



```bash

cd frontend

npm install

npm run dev

```



Frontend URL:



`http://localhost:5173`



\## 🔌 Backend API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | Backend welcome message |

| GET | `/api/health` | Health check |

| GET | `/api/account/{account\_number}` | Retrieve account details |

| GET | `/api/account/{account\_number}/transactions` | Retrieve transaction history |

| POST | `/api/withdraw` | Process a withdrawal |

| POST


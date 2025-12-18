# MediConnect

MediConnect is a comprehensive healthcare appointment and clinic management platform. It facilitates the connection between patients and medical clinics, allowing for seamless appointment booking, doctor management, and clinic administration.

The system features a robust **FastAPI** backend with **MongoDB** and a modern **React** frontend built with **Tailwind CSS** and **Radix UI**.

## 🚀 Features

### For Patients

  * **User Accounts:** Secure registration and login (Email/Password & Google OAuth).
  * **Appointment Booking:** Search for clinics or doctors and book appointments based on real-time availability.
  * **Dashboard:** View upcoming and past appointments.
  * **Notifications:** Email notifications for booking confirmations and cancellations.

### For Clinics & Doctors

  * **Clinic Registration:** Formal verification process using Romanian CUI (Cod Unic de Înregistrare).
  * **Clinic Management:** Customize clinic profile, working hours, and settings.
  * **Staff Management:** Manage doctors and reception staff.
  * **Doctor Profiles:** Detailed profiles with specialties, bios, and consultation fees.
  * **Availability Scheduler:** granular control over doctor schedules and recurring availability.
  * **Service Management:** Define medical services, durations, and prices.
  * **Analytics:** Dashboard with statistics on appointments, revenue, and patient volume.

## 🛠 Tech Stack

### Backend

  * **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
  * **Database:** MongoDB (via [Motor](https://motor.readthedocs.io/) async driver)
  * **Validation:** Pydantic
  * **Authentication:** JWT & OAuth2
  * **Email:** Resend API integration

### Frontend

  * **Framework:** [React](https://www.google.com/search?q=https://react.js.org/)
  * **Styling:** [Tailwind CSS](https://tailwindcss.com/)
  * **Components:** Radix UI / shadcn-ui
  * **Calendar:** FullCalendar
  * **State/Data:** Axios, React Hook Form, Zod
  * **Internationalization:** i18next (EN/RO support)

### DevOps

  * **Containerization:** Docker & Docker Compose
  * **Package Managers:** Pip (Python), Yarn (Node.js)

-----

## 📦 Installation & Setup

You can run the application using Docker (recommended) or set it up manually.

### Option 1: Docker (Recommended)

Ensure you have **Docker** and **Docker Compose** installed.

1.  **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/mediconnect.git
    cd mediconnect
    ```

2.  **Create Environment Variables**
    Create a `.env` file in the `backend/` directory (or rely on the docker-compose defaults for dev):

    ```env
    MONGO_URL=...
    SECRET_KEY=your_secure_secret_key
    RESEND_API_KEY=your_resend_api_key_here
    ```

3.  **Run with Docker Compose**

    ```bash
    docker-compose up --build
    ```

    **Stop with Docker Compose**
    ```bash
    docker-compose stop
    ```

The app will be available at:

  * **Frontend:** `http://localhost:3000`
  * **Backend API:** `http://localhost:8001`
  * **API Docs:** `http://localhost:8001/docs`

# NOTE:
## Day 1: Build everything
docker-compose up -d --build

## Day 2-N: Just start containers
docker-compose up -d

## Edit code → Save → See changes instantly!

## Only rebuild if you add new packages:
docker-compose up -d --build

# Quick Reference for Future Restarts

## Normal restart (keeps data):
```bash
docker-compose restart
```

## Stop and start (keeps data):
```bash
docker-compose down
docker-compose up -d
```

## Full cleanup and rebuild:
 ```bash
docker-compose down -v
docker system prune -a --volumes -f
docker-compose up --build -d
```

-----------------------------------

### Option 2: Manual Setup

#### Backend Setup

1.  Navigate to the backend directory:

    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:

    ```bash
    # Windows
    python -m venv venv
    source venv\Scripts\activate

    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Set up environment variables in a `.env` file inside `backend/`:

    ```env
    MONGO_URL=mongodb://localhost:27017/mediconnect
    SECRET_KEY=change-this-secret-key
    RESEND_API_KEY=your_resend_key
    ```

    *(Ensure you have a local MongoDB instance running on port 27017)*

5.  Run the server:

    ```bash
    uvicorn server:app --reload --host 0.0.0.0 --port 8001
    ```

#### Frontend Setup

1.  Navigate to the frontend directory:

    ```bash
    cd frontend
    ```

2.  Install dependencies:

    ```bash
    yarn install
    ```

3.  Create a `.env` file inside `frontend/`:

    ```env
    REACT_APP_BACKEND_URL=http://localhost:8001
    ```

4.  Start the development server:

    ```bash
    yarn start
    ```

    Open `http://localhost:3000` to view the app.

-----

## 📚 API Documentation

Once the backend is running, you can access the interactive API documentation (Swagger UI) at:
`http://localhost:8001/docs`

This provides detailed information about all endpoints, including:

  * `POST /api/auth/register` - User registration
  * `POST /api/auth/register-clinic` - Clinic registration
  * `GET /api/doctors` - List doctors
  * `POST /api/appointments` - Book appointments

## 📂 Project Structure

```
mediconnect/
├── backend/
│   ├── server.py           # Main FastAPI entry point and logic
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages (Dashboard, Login, etc.)
│   │   ├── lib/            # Utilities
│   │   └── App.js          # Main React component
│   ├── public/
│   └── package.json
└── docker-compose.yml      # Container orchestration
```

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

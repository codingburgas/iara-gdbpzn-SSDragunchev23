# IARA Fleet & Licensing Management System

A professional, full-stack enterprise registry system designed for the **Executive Agency for Fisheries and Aquaculture (IARA)**. The system enables comprehensive monitoring of commercial fishing vessels, port distributions, physical characteristics, and active licensing compliance.

## 🚀 Key Features
- **Interactive Control Tower Dashboard**: Modern, real-time frontend UI styled with Tailwind CSS.
- **Live Statistics Engine**: Instantly computes aggregate data (Total fleet, Active licenses, Average vessel length).
- **Relational Data Management**: Production-ready CRUD endpoints fully integrated with a persistent relational database.
- **Containerized Architecture**: Multi-container setup orchestrating isolated environments for the app and the database.

## 🛠️ Tech Stack
- **Backend:** Python 3.10+, FastAPI (Asynchronous framework), Pydantic v2 (Data validation)
- **Database / ORM:** PostgreSQL 16, SQLAlchemy 2.0 (Object-Relational Mapping)
- **Frontend:** HTML5, JavaScript (Fetch API), Tailwind CSS
- **DevOps / Infrastructure:** Docker, Docker Compose

---

## 💻 How to Run the Project

The entire system is containerized. You do not need to install Python or PostgreSQL on your local machine; only **Docker Desktop** is required.

### 1. Start the Environment
Open your terminal in the root directory of the project and execute:
```bash
docker-compose up --build -d
```

### 2. Access the System & Reviewer Guide
Once the containers are running, open your browser and go to these addresses:

* 🌐 **Main Administrative Dashboard:** [http://localhost:8000](http://localhost:8000)
  * **What's here:** The user-facing web app. It features a dark-themed visual layout with live fleet statistics (Total Vessels, Active Licenses, Avg Length), an interactive port filter dropdown, a datatable showing the vessels currently in the PostgreSQL database, and a functional registration form to add new vessels in real-time.
  
* 🛠️ **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
  * **What's here:** The Swagger UI developer backend interface. It automatically documents your entire API architecture and provides an interactive playground where the reviewer can manually execute and inspect underlying `GET`, `POST`, `PUT`, and `DELETE` requests directly against the live system.

### 3. Stop the Environment
To safely shut down the services, wipe the temporary data volumes, and reset the database environment completely, run:
```bash
docker-compose down -v
```
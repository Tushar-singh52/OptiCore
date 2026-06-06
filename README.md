# OptiCore - DSA-Powered Timetable Management Engine

OptiCore is a modern, responsive, and premium web application designed to automate the complex task of scheduling academic timetables. It combines a sleek **Vanilla HTML/CSS/JS** frontend with a high-performance **FastAPI (Python)** backend, utilising fundamental Data Structures and Algorithms (Graph Theory, Heaps, HashMaps, and Sets) to resolve scheduling conflicts.

---

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Backend Dependencies
Open your terminal in the project root directory (`d:\TIME_TABLE`) and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Start the Backend Server
Run the FastAPI application using Uvicorn:
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- The backend will be live at `http://127.0.0.1:8000`.
- Interactive API documentation will be available at `http://127.0.0.1:8000/docs`.

### 4. Launch the Frontend
Since the frontend is built using native web technologies (no build step or compiler required), you can open it in two ways:
- **Simple Method**: Double-click `frontend/index.html` to open it directly in any modern browser.
- **Recommended Method**: Use an extension like **Live Server** in VS Code to run a local development server for the frontend, which avoids any browser CORS or strict security policy warnings.

---

## 🛠️ How to Use OptiCore

1. **Authentication Portal**:
   - Access the system by selecting your role: **Administrator**, **Teacher**, or **Student**.
   - Input the Access ID: `admin123` to log in.

2. **Entering School Data (Admin Mode)**:
   - Go to the **Data Entry** tab.
   - Add **Teachers** (with daily hour limits to prevent fatigue).
   - Add **Rooms** (with capacities).
   - Add **Sections/Classes** (with student strength).
   - Add **Subjects** (specify the teaching hours per week, target teacher, and flag high-priority subjects like Placement Training).

3. **Generating the Timetable**:
   - Go to the **Timetable View** tab.
   - Click the **Generate Strategy** button in the top right.
   - The backend runs a greedy coloring heuristic over a priority-heap queue to compute the conflict-free timetable in milliseconds.
   - If constraints cannot be met for a class (e.g. not enough classrooms or teachers), warning notifications are displayed.

4. **Interactive "Smart Swap" (Admin Mode)**:
   - Click on any scheduled class card in the timetable grid.
   - A modal will open, letting you swap or move the class to another Day, Timeslot, or Room.
   - The system checks constraints (e.g., is the teacher/section free at that time?) and executes a **Smart Swap** (swapping two classes' slots if both are valid) or moves it if the target slot is empty.

5. **Exporting**:
   - Click **Export PDF** to download the visual schedule as a high-quality landscape PDF suitable for printing.

---

## 🧬 Core Algorithms & Data Structures Used

* **Graph (Adjacency List)**: The scheduler builds a `ConflictGraph` representing classes. Nodes are lectures, and edges connect lectures that share either the same section or same teacher (cannot occur simultaneously).
* **Heap (Min-Priority Queue)**: Lectures are loaded into a Heap to schedule highly-constrained tasks first (Placement-priority classes are given highest priority, followed by classes with larger student capacities requiring specific large rooms).
* **HashMap / Dictionary**: Used to track daily hours of teachers, mappings of IDs to room sizes, and global schedules in $O(1)$ time.
* **Sets**: Used for $O(1)$ checking of slot allocations (represented as compound keys `day_slot_entityID`) to guarantee no overlap of rooms, teachers, or class sections.

---

## 🌐 Deployment Guide

### Backend Deployment (FastAPI)
You can deploy the Python backend to cloud platforms like **Render**, **Railway**, or **Heroku**.

#### Deploying on Render (Free / Easy):
1. Push your code repository to GitHub.
2. Sign in to [Render](https://render.com/) and create a new **Web Service**.
3. Link your GitHub repository.
4. Configure the settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Click **Deploy**. Render will provide a public URL (e.g., `https://your-backend.onrender.com`).

---

### Frontend Deployment (HTML/CSS/JS)
Since the frontend is static, it can be hosted for free on **GitHub Pages**, **Vercel**, or **Netlify**.

#### Deploying on GitHub Pages:
1. Push the project to a GitHub repository.
2. In the repository settings, navigate to **Pages**.
3. Under **Build and deployment**, select **Deploy from a branch** and choose the branch (e.g., `main`).
4. Select the `/frontend` directory or keep it at root and set up paths.
5. Save. Your frontend will be live at `https://<username>.github.io/<repo-name>/frontend/index.html`.

> [!IMPORTANT]
> **Connecting Frontend to Production Backend:**
> Before deploying your frontend, open `frontend/app.js` and change the line:
> ```javascript
> const API_BASE = 'http://localhost:8000';
> ```
> to point to your live, deployed backend URL:
> ```javascript
> const API_BASE = 'https://your-backend.onrender.com';
> ```

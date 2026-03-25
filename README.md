<<<<<<< HEAD
# NEXVIBE-CHATBOT-ASSISTANT
A full-stack NLP-powered chatbot assistant (NEXVIBE) built with FastAPI, Scikit-Learn, and MySQL. Features include automated conversation flows, an admin dashboard for human-in-the-loop training, and Docker support.
=======
# NEXVIBE Assistant 🤖

NEXVIBE Assistant is a full-stack, NLP-powered chatbot application designed to provide automated customer support with human-in-the-loop training capabilities. Built with **FastAPI**, **Scikit-Learn**, and **MySQL**, it offers a seamless integration of automated conversation flows and an administrative interface for continuous learning.

## 🌟 Features

- **Real-time AI Support**: Instant responses to user queries using TF-IDF and Cosine Similarity.
- **Dynamic Conversation Flows**: Structured slot-filling for specific tasks like service requests (e.g., website development).
- **Admin Dashboard**: A secure interface for administrators to view unanswered questions and provide new training data.
- **Continuous Learning**: The NLP model automatically retrains whenever an admin provides a new answer.
- **Fallback Mechanism**: Gracefully handles unknown queries by saving them for admin review.
- **Dockerized Deployment**: Easily deployable using Docker and Docker Compose.
- **Secure Authentication**: Protected admin routes using JWT (JSON Web Tokens) and Argon2 password hashing.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) (NLP, TF-IDF, Cosine Similarity)
- **Database**: [MySQL](https://www.mysql.com/)
- **Authentication**: JWT & Argon2
- **Server**: Uvicorn

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (Vanilla)
- **Features**: Responsive UI, dynamic chat interface, administrative management portal.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- MySQL Server
- Docker & Docker Compose (optional for containerized setup)

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/nexvibe-assistant.git
   cd nexvibe-assistant
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Configure your .env file in the root
   python main.py
   ```

3. **Frontend Setup**:
   Open `frontend/index.html` in your browser.

### Docker Deployment
1. Run the following command in the project root:
   ```bash
   docker-compose up --build
   ```

## 📁 Project Structure

- `backend/`: FastAPI application, NLP logic, database models, and training scripts.
- `frontend/`: Client-side interface for users and admins.
- `docker-compose.yaml`: Configuration for containerizing the app and database.
- `.env`: Environment variables (Database credentials, JWT secrets).

## 🛡️ Security
The admin panel is protected by robust authentication. Ensure you change the default admin credentials and secure your `.env` file before deployment.

## 📄 License
This project is copyrighted.
>>>>>>> 6b46008 (Initial commit)

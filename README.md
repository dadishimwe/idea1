Starlink Reseller App
An open-source internal web app for Starlink reseller companies to manage installations, inventory, customer profiles, team communication, and scheduling. Optimized for self-hosting on a Raspberry Pi, this app uses a Python-based stack to ensure low resource usage and scalability without relying on paid APIs.
Features
MVP Features

Customer Profiles: Manage customer data (name, email, service history) and support tickets.
Inventory Management: Track hardware (Starlink kits, cables, mounts) with QR code generation and low-stock email alerts.
Team Communication: Assign tasks and enable real-time chat via WebSockets.
Scheduling: Basic calendar for job assignments with GPS-based route optimization (OSRM integration).
Reporting: Generate CSV inventory reports and visualize data with Plotly charts.

Planned Features

Network diagrams with draw.io integration.
PDF/XLSX report generation.
Supplier tracking.
Self-hosted LLM (e.g., Llama 3) for internal docs search.

Tech Stack

#Backend: FastAPI (Python, async, lightweight API framework)
#Frontend: Streamlit (Python-based UI for rapid development)
#Database: SQLite (serverless, lightweight for Raspberry Pi)
#WebSockets: FastAPI WebSocket support for real-time chat
#Reporting: Pandas (CSV generation), Plotly (interactive charts)
#Routing: OSRM (OpenStreetMap-based, free GPS routing)
#QR Codes: qrcode (Python library for QR generation)
#Email Alerts: smtplib (free email via Gmail SMTP or self-hosted Postfix)
#Auth: JWT-based (python-jwt for simple authentication)
#Containerization: Docker (arm64 images for Raspberry Pi)
#CI/CD: GitHub Actions (free tier for automated testing/deployment)

Prerequisites

Raspberry Pi (4 or newer recommended, 4GB+ RAM) with Raspberry Pi OS (64-bit).
Docker and Docker Compose installed.
Python 3.9+ (if running without Docker).
Internet connection for initial setup and OSRM routing (optional).

Installation

Prepare Raspberry Pi:
sudo apt update && sudo apt upgrade
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi


Clone Repository:
git clone https://github.com/your-repo/starlink-reseller-app.git
cd starlink-reseller-app


Set Up Environment:

Create a .env file (optional) for email configuration:EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password


Note: Generate an App Password from your Gmail account for smtplib.


Run with Docker:
docker-compose up -d


This builds and starts the app, exposing it on http://<pi-ip>:8000.


(Alternative) Run Directly:
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000


Access the App:

Open http://<pi-ip>:8000 in a browser to access the Streamlit UI.
Use the interface to manage inventory, customers, tasks, and chat.


Optional: Configure Nginx (for production):
sudo apt install nginx
sudo nano /etc/nginx/sites-available/starlink-app

Add:
server {
    listen 80;
    server_name <pi-ip>;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

Enable and restart:
sudo ln -s /etc/nginx/sites-available/starlink-app /etc/nginx/sites-enabled/
sudo systemctl restart nginx



Usage

Inventory: Add items (e.g., Starlink kits) with ID, name, quantity, and minimum stock. Generate QR codes for scanning via webcam (client-side JavaScript).
Customers: Create and view customer profiles, including service history and tickets.
Tasks: Assign tasks with statuses (e.g., "To Do," "Done").
Chat: Use the WebSocket-based chat for team communication.
Reports: Export inventory as CSV or view charts in the Streamlit dashboard.

Backup

The SQLite database (data.db) is stored in the project directory.
Set up a cron job for backups:crontab -e

Add:0 2 * * * cp /path/to/starlink-reseller-app/data.db /path/to/backup/data-$(date +\%F).db



Contributing
We welcome contributions! Follow these steps:

Fork the repository.
Create a feature branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature-name".
Push to branch: git push origin feature-name.
Open a pull request with a detailed description.

Please adhere to the Code of Conduct and include tests for new features.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Troubleshooting

Docker issues: Ensure arm64 images are used (python:3.9-slim is compatible).
Memory constraints: Monitor with htop. Limit WebSocket connections in main.py if crashes occur.
Email failures: Verify Gmail App Password and SMTP settings.
Port conflicts: Check if port 8000 is in use (sudo netstat -tuln).

For further assistance, open an issue on GitHub.

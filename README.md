Chatire
A real‑time chat application built with Django, Djoser, REST framework, Vue.js, and WebSockets.

Features
JWT authentication with short‑lived tokens and automatic background refresh.
Obfuscated token‑refresh endpoint to make discovery harder for attackers.
Real‑time messaging via WebSocket channels.
User invitations – share a URL to join a chat session.
Responsive UI with a modern, glass‑morphism look.
Docker support (optional) for easy deployment.
Quick start
bash

# Clone the repo
git clone <repo_url>
cd Chatire
# Backend (Django)
python -m venv venv
# Windows activation
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional admin account
python manage.py runserver
bash

# Frontend (Vue)
cd chatire-frontend
npm install
npm run dev   # starts the Vite dev server on http://localhost:3000
Open the frontend in a browser and register/login. The app will automatically obtain a JWT token, store it in sessionStorage, and refresh it every 4 minutes using the hidden endpoint /this/is/hard/to/find/.

JWT Configuration
Tokens expire after 30 minutes.
Refresh is allowed (JWT_ALLOW_REFRESH: True).
Settings live in chatire/settings.py under JWT_AUTH.
Project structure

Chatire/
├─ chat/                 # Django app with API views & models
├─ chatire/              # Project settings and urls
├─ chatire-frontend/     # Vue.js frontend
├─ README.md             # **This file**
└─ ...
Development notes
CORS is enabled for all origins (adjust in production).
WebSocket server runs on port 8081 (see chatire/websocket.py).
To change the obscure refresh path, edit chatire/urls.py.

# ChefAI – AI-Powered Recipe Generator

**ChefAI** is an AI-powered recipe generator built with **Python**, **FastAPI**, **Flask**, and **Vertex AI**. It dynamically generates professional recipes based on user-inputted dish descriptions and available prep/cook time.

---

## 🚀 Features
- **Dynamic Recipe Generation:** Uses Generative AI to create custom recipes based on ingredients and time constraints.
- **Dual-Framework Backend:** Utilizes **FastAPI** for high-performance API routing and **Flask** for flexible web serving.
- **Image Integration:** Leverages Vertex AI Image Generation models to visualize the generated dishes.
- **Time Logic:** Automatically calculates and displays prep, cook, and total times.
- **Responsive UI:** Built with vanilla **JavaScript, HTML5, and CSS3** for a seamless experience across devices.

---

## 🛠 Tech Stack
- **Languages:** Python, JavaScript, HTML, CSS
- **Frameworks:** FastAPI, Flask
- **AI Models:** Google Vertex AI (Gemini / Imagen)
- **Environment:** Google Cloud Platform (GCP)

---

## 📸 Demo
![ChefAI Demo](screenshots/chefai-demo.png)

---

## ⚙️ Installation & Usage

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yuss93/chefai.git
cd chefai
2️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
3️⃣ Set Environment Variables ⚠️
(Safe placeholders; do NOT upload your actual JSON key)

bash
Copy code
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-secure-key.json"
export PROJECT_ID="your-gcp-project-id"
export LOCATION="us-central1"
export EMPL_ID_LASTNAME="PRIVATE"
4️⃣ Run the application locally
bash
Copy code
uvicorn main:app --reload --host 0.0.0.0 --port 8080
5️⃣ Open in your browser
Go to: http://localhost:8080 to see the app running.


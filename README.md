# AI-Powered-Travel-Planner
An AI-powered travel planning web app that helps users plan trips across India with real-time flights, hotels, AI-generated itineraries, and downloadable travel plans.

-An end-to-end **AI-powered travel planning web application** built using **Streamlit**, designed to help users plan trips across India with real-time flight search, hotel recommendations, AI-generated itineraries, and downloadable travel plans.

The application combines **real-time data APIs**, **large language models**, and a **modern interactive UI** to deliver a seamless travel planning experience.

---

## 🚀 Features

- ✈️ Real-Time Flight Search
  - One-way & round-trip options
  - Multiple travel classes
  - Live prices via Google Flights (SerpAPI)

- 🏨 Hotel Recommendations
  - Budget-based filtering (Economy, Standard, Luxury)
  - Rating-based selection (3⭐ / 4⭐ / 5⭐)
  - Booking links & Google Maps integration

- 🤖 AI Travel Assistant
  - Conversational chatbot for travel-related queries
  - Powered by Groq LLM (LLaMA-based model)

- 🗺️ AI-Generated Travel Itinerary
  - Personalized day-wise itinerary
  - Theme-based planning (Couple, Family, Adventure, Solo)
  - Interests-aware suggestions (food, history, nature, etc.)

- 📸 City Exploration
  - Tourist attraction images fetched dynamically

- 📄 Downloadable PDF Itinerary
  - Automatically generated travel plan
  - Includes itinerary and top attractions

- 🎨 Premium UI
  - Custom CSS animations
  - Lottie animations
  - Responsive card-based layout

---

<img width="1909" height="932" alt="Screenshot 2025-12-26 002212" src="https://github.com/user-attachments/assets/f9724d11-c576-4bc6-bd9b-a338c5196422" />



## 🧠 How the System Works

1. User provides trip details (source, destination, dates, budget, preferences)
2. Real-time APIs fetch:
   - Flights (Google Flights via SerpAPI)
   - Hotels (Google Hotels via SerpAPI)
   - City images (Google Images)
3. Groq LLM generates a customized itinerary
4. Results are displayed in an interactive UI
5. A PDF itinerary is generated for download

---

## 🏗️ Architecture Overview

- Frontend: Streamlit + Custom HTML/CSS
- APIs:
  - SerpAPI (Flights, Hotels, Images)
  - Groq LLM API (AI itinerary & chatbot)
- Utilities:
  - Airports data for IATA code mapping
  - PDF generation using FPDF

---

## 📂 Project Structure

AI-Powered-Travel-Planner/
│
├── nne.py
│ → Main Streamlit application
│
├── requirements.txt
│
├── README.md


---

## ▶️ How to Run the Project

### 1️⃣ Clone the Repository
git clone https://github.com//AI-Powered-Travel-Planner.git
cd AI-Powered-Travel-Planner
### 2️⃣ Install Dependencies
pip install -r requirements.txt
### 3️⃣ Add API Keys
Inside app.py, replace:
SERPAPI_KEY = "YOUR_SERPAPI_KEY"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
### 4️⃣ Run the Application
streamlit run nne.py

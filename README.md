# 🕶️ Vision-to-Cart:
**Built for the MCP Commerce Intelligence Challenge**

![Status](https://img.shields.io/badge/Status-Hackathon_Submission-success?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Docker%20%7C%20Redis%20%7C%20Vanilla%20JS-blue?style=for-the-badge)

Welcome to **Vision-to-Cart**, a next-generation commerce discovery platform. We are moving away from traditional keyword searches and replacing them with 
**Scenario and Vibe-based Intelligence**. 

Users don't just search for "black sunglasses" anymore. They shop for experiences: *"I need something for water sports"* 
or*"I need a chic look for a summer beach party."
* Our pipeline understands the *intent* behind the scenario and routes the user to the perfect product instantly.

🎥 **[Watch Our Demo Video Here](https://drive.google.com/file/d/1G2ENA9YCu_mBZkM1MNxlNi4i8kmFtyNT/view?usp=drive_link)**

---

## 📸 Project Screenshots
<img width="1911" height="907" alt="Vision-to-cart 01" src="https://github.com/user-attachments/assets/26cb7089-43e6-4a59-b763-a0a478db33b6" />


<img width="1892" height="897" alt="Vision-to-cart 02" src="https://github.com/user-attachments/assets/f2253f01-f7b4-4400-8a5f-acc78b1b30e8" />


<img width="1700" height="865" alt="Vision-to-cart 03" src="https://github.com/user-attachments/assets/b2afc24b-26f9-4b16-9698-77c7d61c5b3a" />


## 🎯 The Core Concept
The platform is built on the principles of the **Model Context Protocol (MCP)**. 
Instead of a direct database query, natural language intents and "vibes" are intercepted, enriched, and routed through an intelligence layer. This ensures that users see products that match their real-world needs, including specific lens types (Polarized, UV400), frame styles, and durability ratings.

## ✨ Platform Features

### 1. Intelligent Scenario Discovery
* **Vibe Routing:** 10 highly specific lifestyle scenarios (e.g., *Beach & Summer, Water Sports, High Fashion, Driving*).
* **Instant Processing:** Click-to-search functionality that instantly pulls enriched catalog data tailored to the selected vibe.

### 2. Smart Product Cards
* **Dynamic Specifications:** Real-time tags for UV Protection, Polarization, Face Shape suitability, and materials.
* **Intelligent Recommendations:** "Why this fits you" context built directly into the UI based on the chosen scenario.

### 3. Advanced Cart & Checkout Logic
* **Real-time Engine:** Immediate calculation of Subtotals, Taxes, and Totals.
* **Gamified Shipping:** Dynamic "Free Shipping" progress bar that updates as users add products.
* **Promo Engine:** Try our hackathon promo code **`HACKATHON`** at checkout for a flat 10% discount!
* **Deep Specs:** In-cart item inspection revealing weight, warranty, and celebrity endorsement details.

### 4. Premium UI/UX
* Designed with modern **Glassmorphism**, responsive CSS grid layouts, dynamic hover micro-animations, and styled placeholders for a clean,
  structural wireframe aesthetic.
* Fully responsive for Desktop, Tablet, and Mobile.

---

## 🏗️ Architecture & Tech Stack

This project was built focusing on a robust, scalable, and modular architecture.

* **Frontend:** HTML5, Vanilla JavaScript (ES6+), Custom CSS3 (Zero heavy frameworks for maximum performance).
* **Backend Pipeline:** Python, **FastAPI** (Acting as the robust MCP API Server).
* **Caching & State:** **Redis** (Handles ultra-fast session state and cart caching).
* **Orchestration:** Fully containerized using **Docker** and **Docker Compose** for seamless deployment.

---

## ⚙️ How to Run Locally

Want to test the Vision-to-Cart pipeline on your own machine? It’s completely containerized and takes 1 minute to spin up.

### Prerequisites
* Docker
* Docker Compose

### Startup Instructions

1. **Clone the repository:**
   bash:
   git clone https://github.com/AryanCh23/Vision-to-cart.git
   cd Vision-to-cart
   
2. Launch the Docker Stack:
    bash:
    docker-compose up --build -d

3. Access the Application:
   
       Frontend UI: http://localhost:3000
       Backend API (Swagger Docs): http://localhost:8000/docs
       Redis Cache: Running internally on port 6379

& To stop the application, simply run:

  bash:
  docker-compose down

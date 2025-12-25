import streamlit as st
import json, os, requests, base64, time
from serpapi.google_search import GoogleSearch
from airportsdata import load
from datetime import datetime
from fpdf import FPDF
from streamlit_lottie import st_lottie
import urllib.parse

# ==================== CONFIG ====================
SERPAPI_KEY = "YOUR SERPAPI_KEY"
GROQ_API_KEY = "YOUR GROQ_API_KEY"

# === LOTTIE ANIMATION URLS ===
SPLASH_LOTTIE_URL = "https://lottie.host/5a67b43b-3d6e-443b-8703-99781cb58f00/M3x6e2j2y0.json"
SIDEBAR_LOTTIE_URL = "https://lottie.host/98950f24-e69d-4b50-811c-6d914d9f10f4/LxFdyp1x81.json"

# === SET BACKGROUND IMAGE URL ===
bg_image_url = "https://image2url.com/images/1761934260241-45ede056-080f-4f61-bd5d-dbf12a416395.jpg"

background_css = f"""
    background-image: url("{bg_image_url}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
"""

# ==================== STREAMLIT UI ====================
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide", initial_sidebar_state="expanded")

# --- CSS SECTION (VISIBILITY FIXES & ANIMATIONS) ---
# NOTE: All CSS curly braces are doubled {{ }} to prevent Python f-string errors
st.markdown(f"""
<style>
    .main {{
        background: transparent;
        padding: 20px;
    }}
    .stApp {{
        {background_css}
    }}

    /* --- ANIMATIONS --- */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* --- VISIBILITY FIX: LABELS & HEADERS --- */
    .section-header {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 10px 20px;
        border-radius: 12px;
        display: inline-block;
        color: #2d3748;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }}

    .stSelectbox label, .stDateInput label, .stTextArea label, .stTextInput label, .stRadio label {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 5px 12px !important;
        border-radius: 8px !important;
        color: #4a5568 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 5px !important;
        display: inline-block !important;
        width: fit-content !important;
    }}

    div[role="radiogroup"] label {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 8px 16px;
        border-radius: 20px;
        border: 2px solid #667eea;
        font-weight: 700 !important;
        color: #2d3748 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s;
        margin-right: 10px;
    }}
    div[role="radiogroup"] label:hover {{
        background-color: #fff;
        transform: scale(1.05);
        border-color: #764ba2;
    }}

    /* --- HOTEL CARD DESIGN --- */
    .hotel-card {{
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(255,255,255,0.5);
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    .hotel-card:hover {{
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border: 1px solid #667eea;
    }}
    .hotel-img-container {{
        position: relative;
        height: 220px;
        width: 100%;
        overflow: hidden;
    }}
    .hotel-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }}
    .hotel-card:hover .hotel-img {{
        transform: scale(1.1);
    }}
    .hotel-rating {{
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(4px);
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 800;
        color: #27ae60;
        font-size: 13px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }}
    .hotel-content {{
        padding: 22px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .hotel-title {{
        margin: 0 0 6px 0;
        color: #1a202c;
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    .hotel-address {{
        margin: 0 0 15px 0;
        color: #718096;
        font-size: 13px;
        line-height: 1.5;
    }}
    .hotel-footer {{
        border-top: 1px dashed #e2e8f0;
        padding-top: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .hotel-price {{
        font-size: 24px; font-weight: 900; color: #2d3748; letter-spacing: -1px;
    }}

    /* --- BUTTONS --- */
    .btn-maps {{
        background: #edf2f7; color: #4a5568; width: 42px; height: 42px;
        display: flex; align-items: center; justify-content: center;
        border-radius: 50%; text-decoration: none; font-size: 20px;
        transition: all 0.3s ease; border: 2px solid transparent;
    }}
    .btn-maps:hover {{
        background: #fff; color: #4299e1; border-color: #4299e1; transform: rotate(15deg);
    }}
    .btn-book {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important; padding: 0 24px; height: 42px;
        display: flex; align-items: center; border-radius: 30px;
        text-decoration: none; font-size: 14px; font-weight: 700;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); transition: all 0.3s ease;
    }}
    .btn-book:hover {{
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }}

    /* --- FLIGHT CARD --- */
    .flight-card {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        transition: all 0.4s ease; border: 2px solid transparent;
        margin-bottom: 20px; animation: fadeInUp 0.6s ease-out backwards;
    }}
    .flight-card:hover {{
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15); border-color: #667eea;
    }}

    /* --- TYPOGRAPHY --- */
    .title {{
        text-align: center; font-size: 56px; font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px; letter-spacing: -2px; animation: fadeInUp 0.8s ease-out;
    }}
    .subtitle {{
        text-align: center; font-size: 20px; color: #4a5568;
        margin-bottom: 40px; font-weight: 500;
        animation: fadeInUp 0.8s ease-out 0.2s backwards;
        background-color: rgba(255,255,255,0.7);
        display: inline-block; padding: 5px 15px; border-radius: 20px;
    }}

    /* --- PASSPORT STAMP ANIMATION (APPEAR -> DISAPPEAR) --- */
    .passport-stamp {{
        font-size: 50px;
        font-weight: 900;
        color: #27ae60;
        border: 8px solid #27ae60;
        padding: 15px 40px;
        border-radius: 15px;
        text-align: center;
        text-transform: uppercase;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        z-index: 9999;
        opacity: 0;
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        pointer-events: none;
        /* Animation: appear immediately, stay for 2s, fade out */
        animation: stampInOut 3s ease-in-out forwards;
    }}

    @keyframes stampInOut {{
        0% {{
            opacity: 0;
            transform: translate(-50%, -50%) scale(3) rotate(0deg);
        }}
        15% {{
            opacity: 1;
            transform: translate(-50%, -50%) scale(1) rotate(-15deg);
        }}
        80% {{
            opacity: 1;
            transform: translate(-50%, -50%) scale(1) rotate(-15deg);
        }}
        100% {{
            opacity: 0;
            transform: translate(-50%, -50%) scale(1) rotate(-15deg);
        }}
    }}

    /* --- RESULTS FOOTER VISIBILITY --- */
    .result-box {{
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 20px;
        border-top: 5px solid #27ae60;
    }}

    .footer-box {{
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    /* --- CHAT BUBBLES --- */
    .chat-bubble-user {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px;
        margin: 8px 0; text-align: right; box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        animation: fadeInUp 0.3s ease-out;
    }}
    .chat-bubble-bot {{
        background: white; color: #2d3748; padding: 12px 18px;
        border-radius: 18px 18px 18px 0; margin: 8px 0;
        border: 1px solid #e2e8f0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        animation: fadeInUp 0.3s ease-out;
    }}

</style>
""", unsafe_allow_html=True)


# ==================== FUNCTIONS ====================
@st.cache_data(show_spinner=False)
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None


# === SLICK STARTUP ANIMATION LOGIC ===
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        lottie_splash = load_lottieurl(SPLASH_LOTTIE_URL)
        if lottie_splash:
            st.markdown(
                "<h2 style='text-align:center; color:#667eea; background:rgba(255,255,255,0.9); padding:10px; border-radius:10px;'>Preparing your journey... ✈️</h2>",
                unsafe_allow_html=True)
            st_lottie(lottie_splash, height=300, key="splash_anim")
            time.sleep(2.5)
        else:
            time.sleep(1)
    splash_placeholder.empty()
    st.session_state.splash_shown = True

# ==================== DATA LOADING ====================
airports = load('IATA')

INDIAN_CITIES = {
    "Mumbai": "BOM", "Bombay": "BOM", "Delhi": "DEL", "New Delhi": "DEL",
    "Bangalore": "BLR", "Bengaluru": "BLR", "Chennai": "MAA", "Madras": "MAA",
    "Kolkata": "CCU", "Calcutta": "CCU", "Hyderabad": "HYD", "Pune": "PNQ",
    "Ahmedabad": "AMD", "Goa": "GOI", "Jaipur": "JAI", "Kochi": "COK",
    "Chandigarh": "IXC", "Guwahati": "GAU", "Lucknow": "LKO", "Thiruvananthapuram": "TRV",
    "Bhubaneswar": "BBI", "Varanasi": "VNS", "Amritsar": "ATQ", "Srinagar": "SXR",
    "Udaipur": "UDR", "Patna": "PAT", "Coimbatore": "CJB", "Indore": "IDR",
    "Nagpur": "NAG", "Visakhapatnam": "VTZ", "Mangalore": "IXE",
}

AIRPORTS = []
for code, d in airports.items():
    if d.get("country") == "IN":
        city = d.get("city", "Unknown")
        AIRPORTS.append({
            "city": city,
            "country": "India",
            "iata": code,
            "search_name": city.lower()
        })

for alias, iata_code in INDIAN_CITIES.items():
    if iata_code in airports and airports[iata_code].get("country") == "IN":
        AIRPORTS.append({
            "city": alias,
            "country": "India",
            "iata": iata_code,
            "search_name": alias.lower()
        })

AIRPORTS = sorted(list({a['iata']: a for a in AIRPORTS}.values()), key=lambda x: x['city'])


def format_airport(a):
    return f"{a['city']} ({a['iata']})"


# ==================== CHATBOT LOGIC ====================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def get_chatbot_response(question):
    question = question.lower()
    responses = {
        "flight": "I can help you find the cheapest flights! Just select your dates above. ✈️",
        "hotel": "I'll fetch top-rated hotels based on your budget. You can book them directly! 🏨",
        "price": "All prices are real-time from Google. I try to find the best deals for you. 💰",
    }
    for key, response in responses.items():
        if key in question: return response

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "system", "content": "You are a helpful Indian travel assistant."},
                               {"role": "user", "content": question}], "max_tokens": 500},
            timeout=10
        )
        if response.status_code == 200: return response.json()["choices"][0]["message"]["content"].strip()
    except:
        pass
    return "I'm here to help with your travel planning! Ask me anything. 🤖"


@st.cache_data(show_spinner=False)
def get_city_images(city, n=6):
    try:
        r = requests.get("https://serpapi.com/search.json",
                         params={"engine": "google_images", "q": f"Tourist attractions in {city} India",
                                 "ijn": "0", "api_key": SERPAPI_KEY}, timeout=15)
        return [img.get("original") or img.get("thumbnail") for img in r.json().get("images_results", [])[:n]]
    except:
        return []


@st.cache_data(show_spinner=False)
def fetch_flights(src_iata, dst_iata, outb, ret, flight_class, trip_type):
    try:
        if not SERPAPI_KEY: return {}
        class_mapping = {"Economy": 1, "Premium Economy": 2, "Business": 3, "First Class": 4}
        params = {
            "engine": "google_flights", "departure_id": src_iata, "arrival_id": dst_iata,
            "outbound_date": str(outb), "currency": "INR", "hl": "en", "gl": "in",
            "travel_class": class_mapping.get(flight_class, 1), "api_key": SERPAPI_KEY,
            "type": "1" if (trip_type == "Round Trip" and ret) else "2"
        }
        if trip_type == "Round Trip" and ret:
            params["return_date"] = str(ret)

        search = GoogleSearch(params)
        return search.get_dict()
    except Exception as e:
        st.error(f"Flight search error: {str(e)}")
        return {}


def extract_all_flights(data):
    all_flights = []
    if data.get("best_flights"): all_flights.extend(data["best_flights"])
    if data.get("other_flights"): all_flights.extend(data["other_flights"])
    valid_flights = [f for f in all_flights if "price" in f]
    return sorted(valid_flights, key=lambda x: x.get("price", float("inf")))[:5]


@st.cache_data(show_spinner=False)
def fetch_hotels_and_restaurants(city, budget, user_rating_pref, check_in, check_out):
    try:
        sort_by = 3  # Lowest Price
        rating_map = {"Economy": 7, "Standard": 8, "Luxury": 9}
        min_rating = rating_map.get(budget, 7)

        if user_rating_pref != "Any":
            if "3" in user_rating_pref:
                min_rating = 7
            elif "4" in user_rating_pref:
                min_rating = 8
            elif "5" in user_rating_pref:
                min_rating = 9

        query = f"{budget} hotels in {city} India"

        params = {
            "engine": "google_hotels",
            "q": query,
            "check_in_date": str(check_in), "check_out_date": str(check_out),
            "currency": "INR", "gl": "in", "hl": "en",
            "sort_by": sort_by, "rating": min_rating, "api_key": SERPAPI_KEY
        }
        results = GoogleSearch(params).get_dict()
        hotels = []
        for prop in results.get("properties", [])[:8]:
            try:
                title = prop.get("name", "Unknown Hotel")

                images = prop.get("images", [])
                thumb = images[0].get("thumbnail", "") if images else ""

                website = prop.get("link")
                if not website:
                    safe_query = urllib.parse.quote(f"{title} {city} hotel booking")
                    website = f"https://www.google.com/search?q={safe_query}"

                map_query = urllib.parse.quote(f"{title} {city}")
                map_link = f"https://www.google.com/maps/search/?api=1&query={map_query}"

                hotels.append({
                    "title": title,
                    "rating": prop.get("overall_rating", "N/A"),
                    "price_night": prop.get("rate_per_night", {}).get("lowest", "N/A"),
                    "address": prop.get("description", "Location available on map"),
                    "thumbnail": thumb,
                    "book_link": website,
                    "map_link": map_link
                })
            except:
                continue
        return hotels
    except Exception as e:
        print(f"Hotel API Error: {e}")
        return []


def groq_generate(prompt):
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                                          "Content-Type": "application/json"},
                                 json={"model": "llama-3.3-70b-versatile",
                                       "messages": [{"role": "user", "content": prompt}], "max_tokens": 2500},
                                 timeout=30)
        if response.status_code == 200: return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"
    return "Error generating itinerary."


def download_pdf(text, imgs, filename="Itinerary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Your Personalized Travel Itinerary", 0, 1, "C")
    pdf.ln(5)

    if imgs:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Top Sights", 0, 1, "L")
        page_width = pdf.w - 2 * pdf.l_margin
        img_width = (page_width - 10) / 3
        img_height = img_width * 0.75
        x_start = pdf.l_margin
        y_start = pdf.get_y()
        temp_files = []

        for i, img_url in enumerate(imgs[:6]):
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    temp_filename = f"temp_img_{i}.jpg"
                    with open(temp_filename, "wb") as f: f.write(response.content)
                    temp_files.append(temp_filename)
                    row, col = i // 3, i % 3
                    pdf.image(temp_filename, x_start + col * (img_width + 5), y_start + row * (img_height + 5),
                              img_width, img_height)
            except:
                pass

        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass
        pdf.set_y(y_start + ((min(len(imgs), 6) + 2) // 3) * (img_height + 5))

    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    safe_text = text.encode("latin-1", "replace").decode("latin-1")
    for line in safe_text.split("\n"): pdf.multi_cell(0, 5, line)

    pdf.output(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    # --- VISIBILITY FIX FOR DOWNLOAD LINK ---
    st.markdown(f"""
    <div class="result-box">
        <h3 style="color:#27ae60; margin:0;">✅ Trip Planned Successfully!</h3>
        <p style="color:#555; font-size:14px; margin-top:5px;">Your custom itinerary is ready to download.</p>
        <a href="data:application/octet-stream;base64,{b64}" download="{filename}" 
           style="background:#27ae60; color:white; padding:10px 20px; border-radius:25px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">
           📥 Download Itinerary (PDF)
        </a>
    </div>
    """, unsafe_allow_html=True)


# ==================== MAIN UI LOGIC ====================
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">🇮🇳 Discover India - Plan your dream trip with flights, hotels, and AI itinerary.</p>',
            unsafe_allow_html=True)

st.markdown('<div class="section-header">🛫 Trip Details</div>', unsafe_allow_html=True)

trip_type = st.radio("Trip Type", ["Round Trip", "One-Way"], horizontal=True, key="trip_type",
                     label_visibility="collapsed")

col1, col2 = st.columns(2)
with col1:
    src_airport = st.selectbox("From:", AIRPORTS, format_func=format_airport)
    dep_date = st.date_input("Departure date", min_value=datetime.now().date())
with col2:
    dst_airport = st.selectbox("To:", AIRPORTS, format_func=format_airport)
    ret_date = st.date_input("Return date (Trip Duration)", min_value=datetime.now().date())

num_days = (ret_date - dep_date).days if (ret_date and dep_date) else 0
if num_days < 1: st.error("Return date must be after departure.")

col3, col4 = st.columns(2)
with col3: theme = st.selectbox("🎨 Theme", ["Couple", "Family", "Adventure", "Solo"])
with col4: prefs = st.text_area("🎯 Interests", "Food, History, Nature")

st.sidebar.markdown("### ⚙️ Preferences")
budget = st.sidebar.radio("💰 Budget", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Class", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("⭐ Hotel Rating", ["Any", "3⭐", "4⭐", "5⭐"])

# --- CHATBOT SIDEBAR INTEGRATION ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### 💬 Travel Assistant")
    with st.form(key="chat_form", clear_on_submit=True):
        user_q = st.text_input("Ask me anything:", placeholder="e.g. Best time to visit Goa?")
        submit = st.form_submit_button("Send 📨")
        if submit and user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            bot_reply = get_chatbot_response(user_q)
            st.session_state.chat_history.append({"role": "bot", "content": bot_reply})

    if st.session_state.chat_history:
        for msg in st.session_state.chat_history[-5:]:
            role_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-bot"
            st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

if st.button("🚀 Generate My Travel Plan", use_container_width=True):
    lottie_json = load_lottieurl(SIDEBAR_LOTTIE_URL)

    # 1. CITY IMAGES
    st.markdown(f'<div class="section-header">📸 Explore {dst_airport["city"]}</div>', unsafe_allow_html=True)
    imgs = get_city_images(dst_airport['search_name'])
    if imgs:
        html = "<style>.slider{display:flex;overflow-x:auto;gap:15px;padding:10px;}.slider img{height:260px;border-radius:12px;}</style><div class='slider'>"
        for u in imgs: html += f'<img src="{u}"/>'
        st.markdown(html + "</div>", unsafe_allow_html=True)

    # 2. FLIGHTS
    st.markdown('<div class="section-header">✈️ Available Flights</div>', unsafe_allow_html=True)
    if lottie_json: st_lottie(lottie_json, height=200, key="flights_load")

    fdata = fetch_flights(src_airport['iata'], dst_airport['iata'], dep_date, ret_date, flight_class, trip_type)
    flights = extract_all_flights(fdata)

    if flights:
        for i, f in enumerate(flights):
            airline = f['flights'][0].get('airline', 'Unknown')
            price = f.get('price', 0)
            dep_time = f['flights'][0]['departure_airport'].get('time', 'N/A')
            arr_time = f['flights'][-1]['arrival_airport'].get('time', 'N/A')
            link = f"https://www.google.com/travel/flights/booking?token={f.get('booking_token', '')}"

            # STAGGERED ANIMATION DELAY
            delay = i * 0.15

            st.markdown(f"""
            <a href="{link}" target="_blank" style="text-decoration:none; color:inherit;">
            <div class="flight-card" style="animation-delay: {delay}s;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><h3 style="margin:0; color:#667eea;">{airline}</h3></div>
                    <div style="text-align:right;"><span style="font-size:24px; font-weight:bold; color:#27ae60;">₹{price:,}</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:15px;">
                    <div><strong>{dep_time}</strong><br><span style="color:#888">{src_airport['iata']}</span></div>
                    <div style="text-align:center; flex-grow:1; padding:0 20px;">✈️<br><span style="font-size:12px; color:#888">{trip_type}</span></div>
                    <div style="text-align:right;"><strong>{arr_time}</strong><br><span style="color:#888">{dst_airport['iata']}</span></div>
                </div>
            </div>
            </a>
            """, unsafe_allow_html=True)
    else:
        st.warning("No flights found.")

    # 3. HOTELS
    st.markdown('<div class="section-header">🏨 Top-Rated Stays</div>', unsafe_allow_html=True)
    hotels = fetch_hotels_and_restaurants(dst_airport['search_name'], budget, hotel_rating, dep_date, ret_date)

    if hotels:
        cols = st.columns(2)
        for idx, h in enumerate(hotels):
            with cols[idx % 2]:
                fallback = "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"
                img_src = h.get("thumbnail") if h.get("thumbnail") else fallback

                # STAGGERED ANIMATION DELAY FOR HOTELS
                delay = idx * 0.15

                st.markdown(f"""
                <div class="hotel-card" style="animation-delay: {delay}s;">
                    <div class="hotel-img-container">
                        <img src="{img_src}" class="hotel-img" onerror="this.src='{fallback}'">
                        <div class="hotel-rating">{h['rating']} ⭐</div>
                    </div>
                    <div class="hotel-content">
                        <div>
                            <h3 class="hotel-title">{h['title']}</h3>
                            <p class="hotel-address">📍 {h['address']}</p>
                        </div>
                        <div class="hotel-footer">
                            <div>
                                <div class="hotel-price">{h['price_night']}</div>
                                <div class="hotel-price-sub">per night</div>
                            </div>
                            <div style="display:flex; gap:10px;">
                                <a href="{h['map_link']}" target="_blank" class="btn-maps" title="View on Map">📍</a>
                                <a href="{h['book_link']}" target="_blank" class="btn-book">View Deal ➔</a>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hotels found.")

    # 4. ITINERARY
    st.markdown('<div class="section-header">🗺️ AI Itinerary</div>', unsafe_allow_html=True)
    if lottie_json: st_lottie(lottie_json, height=200, key="ai_load")

    prompt = f"Create a {num_days}-day itinerary for {dst_airport['city']} ({theme} theme). Budget: {budget}. Include timings and food."
    itinerary = groq_generate(prompt)

    st.markdown(
        f'<div style="background:rgba(255,255,255,0.9); padding:25px; border-radius:15px; animation: fadeInUp 1s ease-out;">{itinerary.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True)

    # 5. GENERATE PDF, SHOW DOWNLOAD LINK & ANIMATION
    download_pdf(itinerary, imgs)

    # Trigger the Passport Stamp Animation
    st.markdown('<div class="passport-stamp">✅ PLAN READY!</div>', unsafe_allow_html=True)

# --- VISIBILITY FIX FOR FOOTER ---
st.markdown("""
<div class="footer-box">
    <p style="color:#555; margin:0;">Made with ❤️ for Indian Travelers | Powered by Groq AI & SerpAPI</p>
    <p style="color:#888; font-size:12px; margin-top:5px;">Real-time flight prices • AI-generated itineraries • 100+ Indian destinations</p>
</div>
""", unsafe_allow_html=True)

# ==================== DEVELOPERS SECTION (UPDATED) ====================
st.markdown("---")

# Header with White Background Pill
st.markdown("""
<div class="footer-box" style="margin-bottom: 20px;">
    <h3 style="color:#667eea; margin:0;">HAPPY TRAVELING MUSAFIRS! ✈</h3>
</div>
""", unsafe_allow_html=True)

# Lottie Animation (Replaces the Image for Privacy)
if SPLASH_LOTTIE_URL:
    lottie_dev = load_lottieurl(SPLASH_LOTTIE_URL)
    if lottie_dev:
        st_lottie(lottie_dev, height=250, key="dev_lottie")

# Footer Text with White Background Pill
st.markdown("""
<div class="footer-box" style="margin-top: 20px;">
    <p style="font-weight:bold; color:#667eea; margin-bottom: 5px;">🌟 Crafting amazing travel experiences 🌟</p>
</div>
""", unsafe_allow_html=True)

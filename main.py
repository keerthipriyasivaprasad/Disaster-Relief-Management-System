import streamlit as st
import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Disaster Relief Management System",
    page_icon="🚨",
    layout="wide"
)

DB = "disaster_relief.db"


# ---------------- DATABASE ----------------

def create_database():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            disaster TEXT,
            need TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_request(name, location, disaster, need):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO requests
        (name, location, disaster, need, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        location,
        disaster,
        need,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


def get_requests():
    conn = sqlite3.connect(DB)
    data = pd.read_sql_query(
        "SELECT * FROM requests ORDER BY id DESC",
        conn
    )
    conn.close()
    return data


create_database()


# ---------------- WEB SCRAPING ----------------
@st.cache_data(ttl=300)
def scrape_disasters():

    import requests
    import xml.etree.ElementTree as ET

    url = "https://www.gdacs.org/xml/rss.xml"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )

    print("Status:", response.status_code)
    print("Content type:", response.headers.get("Content-Type"))
    print("Response:", repr(response.text[:500]))

    response.raise_for_status()

    try:
        root = ET.fromstring(response.content)

    except ET.ParseError as e:
        st.error(f"XML Error: {e}")
        st.write("Website response:")
        st.code(response.text[:1000])
        return []

    results = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")

        if title and link:
            results.append({
                "Disaster / Report": title.strip(),
                "Source Link": link.strip()
            })

    return results[:20]

# ---------------- CHATBOT ----------------

def chatbot_reply(message):
    message = message.lower().strip()

    if "hello" in message or "hi" in message:
        return "Hello! Welcome to the Disaster Relief Chatbot. How can I help you?"

    elif "flood" in message:
        return (
            "Flood safety: Move to higher ground if safe. "
            "Never walk or drive through floodwater. "
            "Follow official warnings and evacuation instructions."
        )

    elif "earthquake" in message:
        return (
            "During an earthquake, drop, cover, and hold on. "
            "Stay away from windows. Follow official instructions "
            "after the shaking stops."
        )

    elif "cyclone" in message:
        return (
            "Follow official weather warnings. Keep essential "
            "supplies ready and go to an authorized shelter "
            "if instructed."
        )

    elif "fire" in message:
        return (
            "Leave the dangerous area if safe, avoid smoke, "
            "and contact emergency services. Do not re-enter "
            "a burning building."
        )

    elif "food" in message or "water" in message:
        return (
            "Submit your requirement using the Emergency Request "
            "page. Contact local relief authorities to confirm "
            "whether supplies are available."
        )

    elif "shelter" in message:
        return (
            "Contact local disaster management authorities "
            "for the location and availability of an authorized "
            "relief shelter."
        )

    elif "medical" in message or "doctor" in message:
        return (
            "For urgent medical needs, contact emergency services "
            "or visit the nearest available medical facility."
        )

    elif "emergency" in message or "rescue" in message:
        return (
            "If you are in immediate danger in India, call 112 "
            "for emergency assistance when possible. Give your "
            "location clearly and follow responders' instructions."
        )

    elif "request" in message:
        return (
            "Open Submit Emergency Request in the sidebar. "
            "Enter your name, location, disaster type, and "
            "required assistance."
        )
    elif "location" in message:
            return ("Please provide your location in the Submit Emergency Request form. This helps us direct assistance to the right area.")

    elif "help" in message:
        return (
            "I can answer basic questions about floods, earthquakes, "
            "cyclones, fires, food, water, shelters, medical help, "
            "and emergency requests."
        )
    elif "clothes" in message:
            return (
                "For clothing purposes please contact the near by camps orgnanized by government or NGOs. You can also submit your requirement using the Emergency Request page."
            )
    elif("contact number" in message or
        "help number" in message):

        return ("""
        🚨 EMERGENCY HELPLINE NUMBERS

        1. National Emergency: 112
        2. Police: 100
        3. Fire Services: 101
        4. Ambulance: 102
        5. State Disaster Control: 1070
        6. District Disaster Control: 1077
        7. Women Helpline: 181
        8. Child Helpline: 1098

        Please contact 112 for immediate emergency assistance.
        """)
    

    elif "water" in message:
        return ("For flood assistance, contact 112 or your district disaster control room at 1077.")

    elif "floor shaking" in message:
        return ("For earthquake-related emergency assistance, contact 112.")

    elif "burning" in message:
        return ("For fire emergencies, call 101 or 112.")

    else:
        return (
            "Sorry, I do not know that answer yet. Please ask "
            "about floods, earthquakes, cyclones, fires, food, "
            "water, shelters, medical help, or rescue assistance."
        )


# ---------------- SIDEBAR ----------------

st.sidebar.title("🚨 Disaster Relief")
st.sidebar.write("Management System")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Live Disaster Updates",
        "Submit Emergency Request",
        "View Requests",
        "Disaster Chatbot"
    ]
)


# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.title("🌍 Disaster Relief Management System")

    st.write(
        "A Python-based application for disaster information "
        "and emergency relief request management."
    )

    data = get_requests()

    col1, col2 = st.columns(2)

    col1.metric("Total Emergency Requests", len(data))

    col2.metric(
        "System Status",
        "Running",
    )

    st.subheader("Available Features")

    st.write("🌐 Web scraping for disaster-related reports")
    st.write("🆘 Emergency request submission")
    st.write("🗄️ SQLite database storage")
    st.write("📋 View and download requests")
    st.write("🤖 Disaster relief chatbot")

    st.subheader("Recent Requests")

    if data.empty:
        st.info("No emergency requests have been submitted.")
    else:
        st.dataframe(data.head(5), use_container_width=True)


# ---------------- DISASTER UPDATES ----------------

elif page == "Live Disaster Updates":

    st.title("🌐 Disaster News and Reports")

    st.write(
        "Fetch disaster-related headlines from the public "
        "ReliefWeb webpage."
    )

    if st.button("Fetch Latest Headlines"):
        scrape_disasters.clear()

    try:
        with st.spinner("Fetching disaster reports..."):
            results = scrape_disasters()

        if results:
            st.success("Webpage fetched successfully!")

            for item in results:
                st.markdown(
                    "**" + item["Disaster / Report"] + "**"
                )

                st.markdown(
                    "[Open source webpage]("
                    + item["Source Link"]
                    + ")"
                )

                st.divider()

        else:
            st.warning(
                "No headlines found. The webpage structure "
                "may have changed."
            )

    except requests.RequestException:
        st.error(
            "Could not fetch the webpage. Check your internet "
            "connection and try again."
        )

    except Exception as error:
        st.error("Unable to read disaster reports.")
        st.caption(str(error))


# ---------------- SUBMIT REQUEST ----------------

elif page == "Submit Emergency Request":

    st.title("🆘 Submit Emergency Request")

    with st.form("emergency_form"):

        name = st.text_input("Your Name")

        location = st.text_input("Affected Location")

        disaster = st.selectbox(
            "Type of Disaster",
            [
                "Flood",
                "Earthquake",
                "Cyclone",
                "Fire",
                "Other"
            ]
        )

        need = st.selectbox(
            "Required Assistance",
            [
                "Food",
                "Drinking Water",
                "Medical Help",
                "Shelter",
                "Rescue Assistance",
                "Clothes",
                "Other"
            ]
        )

        submitted = st.form_submit_button(
            "Submit Emergency Request"
        )

        if submitted:

            if name.strip() and location.strip():

                save_request(
                    name,
                    location,
                    disaster,
                    need
                )

                st.success(
                    "Your request has been saved successfully!"
                )

            else:
                st.warning(
                    "Please enter your name and location."
                )


# ---------------- VIEW REQUESTS ----------------

elif page == "View Requests":

    st.title("📋 Emergency Requests")

    data = get_requests()

    if data.empty:

        st.info("No requests submitted yet.")

    else:

        st.dataframe(
            data,
            use_container_width=True
        )

        csv_data = data.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Requests as CSV",
            data=csv_data,
            file_name="emergency_requests.csv",
            mime="text/csv"
        )


# ---------------- CHATBOT PAGE ----------------

elif page == "Disaster Chatbot":

    st.title("🤖 Disaster Relief Chatbot")

    st.write(
        "Ask questions about disaster safety and "
        "emergency relief assistance."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display previous messages
    for chat in st.session_state.chat_history:

        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    # User input
    user_message = st.chat_input(
        "Ask your question here..."
    )

    if user_message:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        answer = chatbot_reply(user_message)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

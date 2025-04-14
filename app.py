import streamlit as st
import hashlib
import json
from cryptography.fernet import Fernet
import os

# Custom CSS
def local_css():
    st.markdown("""
    <style>
    body {
        background-color: #f2f2f2;
        color: #333333;
    }
    .main-title {
        text-align: center;
        color: #222222;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 25px;
        margin: 5px 0;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
        transition: 0.3s;
    }
    .menu-title {
        font-size: 24px;
        margin-bottom: 10px;
        color: #444444;
    }
    </style>
    """, unsafe_allow_html=True)

# Call CSS
local_css()

# Generate a consistent key for encryption (should be securely stored in real apps)
KEY_FILE = "key.key"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as f:
    KEY = f.read()

cipher = Fernet(KEY)

# Load or initialize data.json
DATA_FILE = "data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        stored_data = json.load(f)
else:
    stored_data = {}

# Save data to JSON
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(stored_data, f)

# Hash passkey using SHA-256
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Encrypt data
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Decrypt data
def decrypt_data(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()

# Streamlit Session State
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = {}

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Main Title
st.markdown("<div class='main-title'>🔒 Secure Multi-User Data Vault</div>", unsafe_allow_html=True)

# Sidebar Menu
menu = st.sidebar.radio("📋 Navigation", ["Home", "Register", "Login", "Store Data", "Retrieve Data", "Logout"])

# Home Page
if menu == "Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Welcome to the Next-Level Secure Data Storage System! 🚀")
    st.write("""
    🔐 **Encrypt and store your sensitive data securely.**  
    👥 **Multi-user system with individual passkeys.**  
    ❌ **Automatic lockout after 3 wrong attempts.**  
    """)
   
    st.markdown(f"<p style='background-color: lightgray; padding: 5px; text-align:center; font-size:20px; color:blue'>Made by <b>Maryam Ansari</b></p>" , unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Registration
elif menu == "Register":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Create a New Account")
    username = st.text_input("Choose a Username")
    passkey = st.text_input("Choose a Passkey", type="password")

    if st.button("Register"):
        if username in stored_data:
            st.error("🚫 User already exists.")
        elif username and passkey:
            stored_data[username] = {
                "passkey": hash_passkey(passkey),
                "data": []
            }
            save_data()
            st.success("✅ Registration successful! You can now login.")
        else:
            st.error("⚠️ Both fields are required.")
    st.markdown("</div>", unsafe_allow_html=True)

# Login
elif menu == "Login":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔐 User Login")
    username = st.text_input("Username")
    passkey = st.text_input("Passkey", type="password")

    if st.button("Login"):
        if username in stored_data and stored_data[username]["passkey"] == hash_passkey(passkey):
            st.session_state.current_user = username
            st.session_state.failed_attempts[username] = 0
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❌ Incorrect credentials.")

    st.markdown("</div>", unsafe_allow_html=True)

# Store Data
elif menu == "Store Data":
    if st.session_state.current_user:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"📂 Store Data (User: {st.session_state.current_user})")
        user_data = st.text_area("Enter your sensitive data")

        if st.button("Encrypt & Save"):
            if user_data:
                encrypted_text = encrypt_data(user_data)
                stored_data[st.session_state.current_user]["data"].append(encrypted_text)
                save_data()
                st.success("✅ Data encrypted and saved successfully.")
            else:
                st.error("⚠️ Data cannot be empty.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("🔒 Please login first!")

# Retrieve Data
elif menu == "Retrieve Data":
    if st.session_state.current_user:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"🔍 Retrieve Data (User: {st.session_state.current_user})")

        user_data_list = stored_data[st.session_state.current_user]["data"]

        if user_data_list:
            selected_data = st.selectbox("Select Encrypted Data", user_data_list)
            passkey = st.text_input("Enter your passkey", type="password")

            if st.button("Decrypt"):
                if passkey:
                    if stored_data[st.session_state.current_user]["passkey"] == hash_passkey(passkey):
                        try:
                            decrypted_text = decrypt_data(selected_data)
                            st.success(f"✅ Decrypted Data: {decrypted_text}")
                            st.session_state.failed_attempts[st.session_state.current_user] = 0
                        except:
                            st.error("❌ Decryption failed!")
                    else:
                        st.session_state.failed_attempts[st.session_state.current_user] += 1
                        attempts_left = 3 - st.session_state.failed_attempts[st.session_state.current_user]
                        st.error(f"❌ Incorrect passkey! {attempts_left} attempt(s) remaining.")
                        if attempts_left <= 0:
                            st.error("🔒 Too many failed attempts! Please login again.")
                            st.session_state.current_user = None
                            st.experimental_rerun()
                else:
                    st.error("⚠️ Please enter your passkey.")
        else:
            st.info("ℹ️ No data stored yet.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("🔒 Please login first!")

# Logout
elif menu == "Logout":
    st.session_state.current_user = None
    st.success("✅ You have been logged out!")


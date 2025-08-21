import streamlit as st
import requests
import base64

# --- Gemini API Config ---
API_KEY = "AIzaSyDzgv2reYYqJxqOmKct1N_fOB9l_Yb2dFc"   
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

# --- Streamlit App Layout ---
st.set_page_config(page_title="Food Freshness Detector", page_icon="🥗", layout="centered")

st.title("🥗 Food Freshness Detector")
st.write("Upload an image of food to analyze its freshness using AI.")

# File uploader
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

# Function: Convert file to Base64
def file_to_base64(file):
    return base64.b64encode(file.read()).decode("utf-8")

# Analyze Button
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    if st.button("🔍 Analyze Freshness"):
        with st.spinner("Analyzing... Please wait"):
            try:
                base64_data = file_to_base64(uploaded_file)

                # Prompt for the model
                prompt_text = """Analyze the image and determine if the food shown is fresh or spoiled. 
                Provide a simple classification (either "Fresh" or "Spoiled") followed by a short, simple reason. 
                Format your response as a single string: "Status: [Fresh/Spoiled]. Reason: [your reason here]"."""

                # Payload for Gemini
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": prompt_text},
                                {
                                    "inlineData": {
                                        "mimeType": uploaded_file.type,
                                        "data": base64_data
                                    }
                                }
                            ]
                        }
                    ]
                }

                # API Request
                response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                result = response.json()

                # Parse response
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]

                    # Extract status and reason
                    import re
                    status_match = re.search(r"Status: (Fresh|Spoiled)", text, re.IGNORECASE)
                    reason_match = re.search(r"Reason: (.+)", text, re.IGNORECASE)

                    status = status_match.group(1) if status_match else "Unknown"
                    reason = reason_match.group(1) if reason_match else "Could not determine reason."

                    # Display results
                    if status.lower() == "fresh":
                        st.success(f"✅ Status: {status}")
                    elif status.lower() == "spoiled":
                        st.error(f"❌ Status: {status}")
                    else:
                        st.warning(f"⚠️ Status: {status}")

                    st.write(f"**Reason:** {reason}")
                else:
                    st.error("No valid response received from the AI model.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

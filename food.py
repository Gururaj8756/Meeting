import streamlit as st
import easyocr
from PIL import Image
import pandas as pd
import re

# Define allergen, vegan, and preservative keywords
ALLERGENS = ["wheat", "peanut", "milk", "egg", "soy", "nuts", "shellfish", "fish"]
NON_VEGAN = ["milk", "egg", "honey", "gelatin", "fish", "chicken", "beef", "pork"]
PRESERVATIVES = {
    "sodium benzoate": ["sodium benzoate", "e211"],
    "potassium sorbate": ["potassium sorbate", "e202"],
    "calcium propionate": ["calcium propionate", "e282"],
    "sorbic acid": ["sorbic acid", "e200"],
    "benzoic acid": ["benzoic acid", "e210"],
    "sulfur dioxide": ["sulfur dioxide", "e220"],
    "bht": ["bht", "butylated hydroxytoluene"],
    "bha": ["bha", "butylated hydroxyanisole"]
}

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def extract_text_from_image(image):
    return " ".join(reader.readtext(image, detail=0))

def extract_nutritional_info(text):
    nutrition_data = {}
    text = text.lower()
    matches = re.findall(r'([a-zA-Z ]+)\s*(\d+\.?\d*)\s*%?', text)
    for key, value in matches:
        key = key.strip()
        nutrition_data[key] = value
    return nutrition_data

def analyze_ingredients(text):
    text = text.lower()
    allergens_found = [a for a in ALLERGENS if a in text]
    non_vegan_found = [nv for nv in NON_VEGAN if nv in text]
    preservatives_found = [name for name, variants in PRESERVATIVES.items() if any(variant in text for variant in variants)]
    
    return allergens_found, non_vegan_found, preservatives_found

def main():
    st.title("Food Label Analyzer")
    st.write("Upload an image of a food ingredient label to check for allergens, vegan status, preservatives, and nutritional values.")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        st.write("Extracting text...")
        extracted_text = extract_text_from_image(image)
        st.text_area("Extracted Text", extracted_text, height=150)
        
        nutrition_info = extract_nutritional_info(extracted_text)
        
        if nutrition_info:
            df = pd.DataFrame(nutrition_info.items(), columns=["Nutrient", "Value"])
            st.subheader("Nutritional Information")
            st.table(df)
        
        allergens, non_vegan, preservatives = analyze_ingredients(extracted_text)
        
        st.subheader("Analysis Results:")
        
        if allergens:
            st.error(f"⚠️ Allergens Found: {', '.join(allergens)}")
        else:
            st.success("✅ No common allergens detected.")
        
        if non_vegan:
            st.warning(f"⚠️ Non-Vegan Ingredients Found: {', '.join(non_vegan)}")
        else:
            st.success("✅ This product appears to be vegan.")
        
        if preservatives:
            st.info(f"ℹ️ Preservatives Detected: {', '.join(preservatives)}")
        else:
            st.success("✅ No common preservatives detected.")

if __name__ == "__main__":
    main()

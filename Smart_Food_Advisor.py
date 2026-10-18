import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Smart Food Advisor", page_icon="🤖", layout="wide")

st.title("🤖 Smart Food Advisor")
st.markdown("Get AI-powered nutrition insights using Google Gemini")

# Initialize Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    gemini_available = True
    st.success("✅ Gemini AI Connected!")
except Exception as e:
    gemini_available = False
    st.error(f"❌ Gemini API Error: {str(e)}")

# User inputs
st.header("🔍 Food Analysis Setup")

col1, col2 = st.columns(2)
with col1:
    food_search = st.text_input(
        "Search for food products:",
        placeholder="e.g., yogurt, bread, milk, cheese",
        value="yogurt"
    )
with col2:
    analysis_type = st.selectbox(
        "Choose analysis type:",
        ["Health Benefits", "Nutrition Comparison", "Dietary Recommendations", "Meal Planning Ideas"]
    )

col3, col4 = st.columns(2)
with col3:
    health_goal = st.selectbox(
        "What's your health goal?",
        ["General Health", "Weight Loss", "Muscle Building", "Heart Health", "Energy Boost"]
    )
with col4:
    detail_level = st.select_slider("Analysis detail level:", options=["Brief", "Standard", "Detailed"])

# Function to fetch food data
def get_food_data(food_term):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'search_terms': food_term,
        'json': 1,
        'page_size': 6
    }
    
    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()
        products = data.get('products', [])
        
        valid_products = []
        for product in products:
            if product.get('product_name') and product.get('product_name') != 'Unknown':
                nutrients = product.get('nutriments', {})
                if any(nutrients.get(key) not in [None, 0, ''] for key in ['sugars_100g', 'proteins_100g', 'fat_100g']):
                    valid_products.append(product)
        
        return valid_products[:3]
        
    except requests.exceptions.Timeout:
        st.error("⏰ The food database is slow right now. Please try 'yogurt', 'bread', or 'milk'.")
        return []
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return []

def generate_food_analysis(food_data, analysis_type, food_term, health_goal, detail_level):
    if not food_data or not gemini_available:
        return "Analysis unavailable."
    
    nutrition_info = ""
    for i, product in enumerate(food_data):
        name = product.get('product_name', 'Unknown')
        brand = product.get('brands', 'Unknown')
        nutrients = product.get('nutriments', {})
        
        nutrition_info += f"\n--- Product {i+1}: {name} ({brand}) ---\n"
        nutrition_info += f"• Sugar: {nutrients.get('sugars_100g', 0)}g per 100g\n"
        nutrition_info += f"• Protein: {nutrients.get('proteins_100g', 0)}g per 100g\n"
        nutrition_info += f"• Fat: {nutrients.get('fat_100g', 0)}g per 100g\n"
        nutrition_info += f"• Carbohydrates: {nutrients.get('carbohydrates_100g', 0)}g per 100g\n"
        nutrition_info += f"• Calories: {nutrients.get('energy-kcal_100g', 'N/A')} kcal per 100g\n"
    
    prompt = f"""
    As a nutrition expert, analyze these {food_term} products for someone with a goal of {health_goal}:
    
    {nutrition_info}
    
    Provide a {detail_level.lower()} {analysis_type.lower()} focusing on the actual nutrition data shown. 
    Compare the products and give specific recommendations.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI analysis error: {str(e)}"

# Main app
if st.button("🚀 Generate AI Analysis", type="primary"):
    if not food_search:
        st.warning("Please enter a food product")
    else:
        with st.spinner("🔍 Fetching food data..."):
            food_data = get_food_data(food_search)
        
        if food_data:
            st.header("📊 Products Found")
            
            cols = st.columns(len(food_data))
            for i, product in enumerate(food_data):
                with cols[i]:
                    name = product.get('product_name', 'Unknown')
                    brand = product.get('brands', 'Unknown')
                    
                    st.subheader(f"#{i+1}")
                    st.write(f"**{name}**")
                    st.caption(f"*{brand}*")
                    
                    # Display product image if available
                    image_url = product.get('image_url')
                    if image_url:
                        st.image(image_url, use_column_width=True)
                    
                    nutrients = product.get('nutriments', {})
                    st.metric("Sugar", f"{nutrients.get('sugars_100g', 0)}g")
                    st.metric("Protein", f"{nutrients.get('proteins_100g', 0)}g")
                    st.metric("Fat", f"{nutrients.get('fat_100g', 0)}g")
            
            if gemini_available:
                st.header("🧠 AI Nutrition Analysis")
                with st.spinner("🤖 Generating insights..."):
                    analysis = generate_food_analysis(food_data, analysis_type, food_search, health_goal, detail_level)
                
                st.markdown("---")
                st.markdown(analysis)
                st.markdown("---")
            else:
                st.warning("AI features disabled")

# Working searches
st.sidebar.header("💡 Reliable Searches")
st.sidebar.write("These usually work:")
st.sidebar.write("- 🥛 yogurt")
st.sidebar.write("- 🍞 bread") 
st.sidebar.write("- 🧀 cheese")
st.sidebar.write("- 🥛 milk")

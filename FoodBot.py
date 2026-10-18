

# FoodBot for Open Food Facts API

#######################################################

import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="Food Expert FoodBot",page_icon="",layout="wide")

st.title("🥞🍱🌮 Food Expert FoodBot 🥪🥘🍕")

# ... (your Gemini API key setup) ...
# Configure your API key
genai.configure(api_key="AIzaSyAhyahDnkVWBmL1NovIy43nMJJohOA0Nvc")

tool_declarations = [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name='get_food_data',
                    description='Get information about food for ex: yogurt, bread, milk, cheese',
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            'food_term': genai.protos.Schema(type=genai.protos.Type.STRING, description='The food term used to get information about the food.')
                        },
                        required=['food_term']
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name='detailed_food_analysis',
                    description='Provide either a brief, standard, or detailed analysis of the specified health goal about food for ex: yogurt, bread, milk, cheese',
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            'food_term': genai.protos.Schema(type=genai.protos.Type.STRING, description='The food term used to get information about the food.'),
                            'analysis_type': genai.protos.Schema(type=genai.protos.Type.NUMBER, description='The analysis type used to determine what kind of information is wanted about the food. If the user is asking for Health Benefits, use value 1, if the user is asking for Nutrition comparision, use value 2, if the user is asking for Dietary Recommendation, use value 3, If the user is asking for Meal Planning Ideas, use value 4, Otherwise default the value to 1'),
                            'health_goal': genai.protos.Schema(type=genai.protos.Type.NUMBER, description='The health goal is used to orient the response towards helping the user achieve the health goal. If the user is asking for General Health, use value 1, If the user is asking for Weight loss, use 2, If the user is asking for Muscle Building, use 3, if the user is asking for Heart Health, use 4, if the user is asking for Energy Boost, use 5, otherwise default the value to 1'),
                            'detail_level': genai.protos.Schema(type=genai.protos.Type.NUMBER, description='The analysis type used to determine whether the analysis should be brief, standard, or detailed. if the user asks for brief, use value 1, if the user asks for standard, use 2, if the user asking for detailed, use 3, otherwise default the value to 1')
                        },
                        required=['food_term']
                    )
                )
            ]
        )
    ]

model = genai.GenerativeModel('models/gemini-2.5-flash', tools=tool_declarations)
chat = model.start_chat(history=[])

# Function to fetch food data
def get_food_data(food_term):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'search_terms': food_term,
        'json': 1,
        'page_size': 6
    }
    
    try:
        response = requests.get(url, params=params, timeout=2000)
        data = response.json()
        products = data.get('products', [])
        return products[:6]
    except requests.exceptions.Timeout:
        st.error("⏰ The food database is slow right now. Please wait or try again later.")
        return []
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return []


# Function for Detailed Food Analysis
def detailed_food_analysis(food_term, analysis_type, health_goal, detail_level):
    food_data = get_food_data(food_term)
    if not food_data:
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

    if analysis_type == 1:
        analysis_type_str = "Health Benefits"
    elif analysis_type == 2:
        analysis_type_str = "Nutrition Comparison"
    elif analysis_type == 3:
        analysis_type_str = "Dietary Recommendations"
    elif analysis_type == 4:
        analysis_type_str = "Meal Planning Ideas"
    else:
        analysis_type_str = "Health Benefits"

    if health_goal == 1:
        health_goal_str = "General Health"
    elif health_goal == 2:
        health_goal_str = "Weight Loss"
    elif health_goal == 3:
        health_goal_str = "Muscle Building"
    elif health_goal == 4:
        health_goal_str = "Heart Health"
    elif health_goal == 5:
        health_goal_str = "Energy Boost"
    else:
        health_goal_str = "General Health"

    if detail_level == 1:
        detail_level_str = "brief"
    elif detail_level == 2:
        detail_level_str = "standard"
    elif detail_level == 3:
        detail_level_str = "detailed"
    else:
        detail_level_str = "standard"

    prompt = f"""
    As a nutrition expert, analyze these {food_term} products for someone with a goal of {health_goal_str}:
    
    {nutrition_info}
    
    Provide a {detail_level_str.lower()} {analysis_type_str.lower()} focusing on the actual nutrition data shown. 
    Compare the products and give specific recommendations.
    """
    return prompt


# Streamlit ChatBot Page

if "messages" not in st.session_state:
   st.session_state.messages = []

with st.chat_message("assistant",avatar="🍎"):
    st.write("Hey there! I'm FoodBot, your go-to expert for anything food-related.")

for message in st.session_state.messages:
    with st.chat_message(message["role"],avatar=message["avatar"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Away!"):
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🥗"})
    with st.chat_message("user",avatar="🥗"):
        st.markdown(prompt)
    try:
        response = chat.send_message(prompt)

        with st.chat_message("assistant",avatar="🍎"):
            try:
                if response.candidates[0].content.parts[0].function_call:
                    function_call = response.candidates[0].content.parts[0].function_call
                    function_name = function_call.name

                    if function_name == "get_food_data":
                        food_term = function_call.args['food_term']
                        with st.spinner("🔍 Fetching food data..."):
                            food_data = get_food_data(food_term)

                            try:
                                response_with_tool_result = chat.send_message(
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name="get_food_data",
                                            response={"result": food_data}
                                        )
                                    )
                                )
                                st.session_state.messages.append({"role": "assistant", "content": response_with_tool_result.text, "avatar": "🍎"})
                                st.markdown(response_with_tool_result.text)
                            except Exception as e: 
                                st.error(f"❌ Error: {str(e)}")
                    
                    elif function_name == "detailed_food_analysis":
                        food_term = function_call.args['food_term']
                        if 'analysis_type' in function_call.args:
                            analysis_type = function_call.args['analysis_type']
                        else:
                            analysis_type = 1
                        if 'health_goal' in function_call.args:
                            health_goal = function_call.args['health_goal']
                        else:
                            health_goal = 1
                        if 'detail_level' in function_call.args:
                            detail_level = function_call.args['detail_level']
                        else:
                            detail_level = 1
                        with st.spinner("🔍 Fetching food data..."):
                            detailed_analysis = detailed_food_analysis(food_term, analysis_type, health_goal, detail_level)
                        
                            try:
                                response_with_tool_result = chat.send_message(
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name="detailed_food_analysis",
                                            response={"result": detailed_analysis}
                                        )
                                    )
                                )
                                st.markdown(response_with_tool_result.text)
                            except Exception as e: 
                                st.error(f"❌ Error: {str(e)}")
                    
                else:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "🍎"})

            except Exception as e: 
                st.error(f"❌ Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
            





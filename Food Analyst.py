
import streamlit as st
import pandas as pd
import requests
import random

#Food Analyst Page --> data extraction


st.subheader("Nutritional Facts Explorer")

# Dynamic Bar Chart --> Nutrition Content for Each Product (per 100g)

def nutrition_products(product):
    try:
        baseUrl = "https://world.openfoodfacts.org/cgi/search.pl"
        endpoint = {"search_terms": product,"json": 1, "page_size": 5}
        response = requests.get(baseUrl, params=endpoint)
        data = response.json()
        product_name = data["products"][0]["product_name"]
        nutr = data["products"][0]["nutriments"]
        sugar_content = float(nutr["sugars_100g"])
        fat_content = float(nutr["fat_100g"])
        carb_content = float(nutr["carbohydrates_100g"])
        protein_content = float(nutr["proteins_100g"])
        nutrients = {"Sugar (g)": sugar_content, "Fat (g)": fat_content, "Carbs (g)": carb_content, "Protein (g)": protein_content}
        return product_name,nutrients
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return []

product = st.text_input("Enter a food product from the Open Food Facts API:")

if product:
    product_name, nutrients = nutrition_products(product)
    if nutrients:
        st.subheader(f"Nutritional Content for {product_name}")
        nutrient_type_options = list(nutrients.keys())
        selected_nutrient_types = st.multiselect("Select which nutrient type to display:",options=nutrient_type_options)
        nutrientData = pd.DataFrame(list(nutrients.items()), columns=["Nutrient","Amount"])
        if selected_nutrient_types: 
            barData = nutrientData[nutrientData["Nutrient"].isin(selected_nutrient_types)]
        else: 
            barData = nutrientData
        #Display the data in a data table
        st.dataframe(barData)
        #Display the dynamic bar chart
        st.bar_chart(barData,x="Nutrient",y="Amount",x_label="Nutrient Type",y_label="Amount of Nutrient per 100g of Product")
    else:
        st.warning("No product found with that name.")



#Dynamic Scatter Chart --> Sugar vs. Fat Content for Random # of Products


st.subheader("Sugar vs. Fat Content (per 100g) in Food Products")

randomNum_products = st.slider("Select the number of products to fetch:",10,1000,50)

def randNum_prods(num_products):
    pagesNeeded = (num_products // 100) + 1
    for i in range(pagesNeeded):
        try:
            page = random.randint(1,200)
            baseUrl = "https://world.openfoodfacts.org/cgi/search.pl"
            endpoint = {"search_terms": "","json": 1, "page_size": num_products, "page": page}
            response = requests.get(baseUrl, params=endpoint)
            prodData = response.json()
            scatterData = []
            for prodInfo in prodData["products"]:
                try:
                    product_name = prodInfo["product_name"]
                    nutrients = prodInfo["nutriments"]
                    sugar = nutrients["sugars_100g"]
                    fat = nutrients["fat_100g"]
                    if sugar is not None and fat is not None:
                        scatterData.append({"product_name": product_name, "sugars_100g": sugar, "fat_100g": fat})
                    elif sugar is None and fat is None: 
                        continue
                except:
                    continue
            return scatterData
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching dat from API: {e}")
            return []
        
products = randNum_prods(randomNum_products)

if len(products) >= randomNum_products:
    products = random.sample(products, k=randomNum_products)

finalData = pd.DataFrame(products)
st.dataframe(finalData)
st.scatter_chart(finalData, x="sugars_100g",y="fat_100g",x_label="Sugar (per 100g)",y_label="Fat (per 100g)")


        

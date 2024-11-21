#!/usr/bin/env python
# coding: utf-8

# In[27]:


import os
from dotenv import load_dotenv
import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import APIChain


# In[29]:


# Load environment variables
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("Gemini_API_KEY")


# In[31]:


# Set up the Google Gemini model
GEMINI_MODEL = "gemini-1.5-flash"
llm = ChatGoogleGenerativeAI(google_api_key=GEMINI_API_KEY, model=GEMINI_MODEL, temperature=0.9)


# In[33]:


# Fetch weather data
def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
    else:
        return {"error": f"Failed to fetch weather data: {response.status_code}"}


# In[35]:


# Fetch GDP data from World Bank API
def fetch_gdp_data(country_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            gdp_data = data[1][:5]  # Fetch the most recent 5 years
            return [{"year": gdp["date"], "gdp": gdp["value"]} for gdp in gdp_data if gdp["value"]]
        else:
            return {"error": "No GDP data available"}
    else:
        return {"error": f"Failed to fetch GDP data: {response.status_code}"}


# In[37]:


# Generate relocation insights using Gemini
def generate_relocation_insights(city, weather_summary, gdp_summary):
    prompt = f"""
    Provide detailed relocation insights for {city}:
    - Consider the following weather context: {weather_summary}.
    - Economic context: {gdp_summary}.
    - Include cultural aspects, job opportunities, and challenges for expats.
    """
    response = llm.predict(prompt)
    return response


# In[39]:


# Streamlit App
st.title("Relocation Insights Tool")
st.write("Get detailed insights about relocating to your favorite city!")


# In[41]:


def combined_relocation_info(city, country_code):
    # Fetch weather data
    weather_info = fetch_weather_data(city)
    if "error" in weather_info:
        weather_summary = weather_info["error"]
    else:
        weather_summary = (
            f"The current temperature in {city} is {weather_info['temperature']}°C "
            f"with {weather_info['description']}."
        )

    # Fetch GDP data
    gdp_info = fetch_gdp_data(country_code)
    if "error" in gdp_info:
        gdp_summary = gdp_info["error"]
    else:
        # Safely build the GDP summary
        gdp_items = [f"{item['year']}: {item['gdp']}" for item in gdp_info if 'year' in item and 'gdp' in item]
        if gdp_items:
            gdp_summary = "GDP data for recent years: " + ", ".join(gdp_items)
        else:
            gdp_summary = "No GDP data available."

    # Generate relocation insights
    relocation_insights = generate_relocation_insights(city, weather_summary, gdp_summary)

    return {
        "weather_summary": weather_summary,
        "gdp_summary": gdp_summary,
        "relocation_insights": relocation_insights
    }


# In[43]:


# User Input
city = st.text_input("Enter the city you want to relocate to:", "Berlin")
country_code = st.text_input("Enter the country code for the city:", "DE")

if st.button("Get Insights"):
    with st.spinner("Fetching data and generating insights..."):
        results = combined_relocation_info(city, country_code)

        st.subheader("Weather Summary")
        st.write(results["weather_summary"])

        st.subheader("Economic Summary")
        st.write(results["gdp_summary"])

        st.subheader("Relocation Insights")
        st.write(results["relocation_insights"])

# Feedback Section
st.subheader("Feedback")
rating = st.slider("Rate the quality of the insights (1-5):", 1, 5)
comments = st.text_area("Additional Comments:")

if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
    # Save feedback to a file or database if needed


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





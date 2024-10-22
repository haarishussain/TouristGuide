import json
import logging
import math
import re
from datetime import timedelta
from io import BytesIO
import requests
import streamlit as st
from docx import Document
import docx
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage
from dotenv import set_key, load_dotenv, dotenv_values
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from openai import OpenAI
from spire.doc import *
from spire.doc.common import *
from streamlit.logger import get_logger
from docxcompose.composer import Composer
from docx import Document as Document_compose
import io
import replicate


input_dict = {}
st.set_page_config(
    page_title="AI Tour Itinerary Generator",  # Set your desired title here
    page_icon="images/favicon.ico",  # Set path to your favicon image (.ico format)
)
st.title("Tour Itinerary Generator")


col1, col2 = st.columns(2)

input_dict['dest'] = col1.text_input("Destination", key='dest',placeholder='ex. Himachal Pradesh')
input_dict['src'] = col1.text_input("Source City", key='src',placeholder='ex. Mumbai')
input_dict['genre'] = col1.text_input("Genre", key='genre',placeholder='ex. adventure, fun, religious')
input_dict['type_of_travelers'] = col1.text_input("Type of Travelers", key='type', placeholder='ex. family, friends')
input_dict['mode_of_travel'] = col1.text_input("Mode of Travel", key='mode', placeholder='ex. flight, bus, train')
input_dict['num_days'] = col2.number_input("Number of Days", key='num_days', min_value=0, max_value=None, value=0,
                                           step=1, format="%d")
input_dict['start_date'] = col2.date_input("Start Date", key='start_date')
# Create sub-columns within col2
col21, col22 = col2.columns(2)

input_dict['num_adults'] = int(
    col21.number_input("Number of Adults", key='num_adults', min_value=0, max_value=None, value=0, step=1, format="%d"))
input_dict['num_children'] = int(
    col22.number_input("Number of Children", key='num_children', min_value=0, max_value=None, value=0, step=1,
                       format="%d"))
input_dict['price_per_person'] = col2.number_input("Price Per Person", key='price_per_person', min_value=0)
# input_dict['average_age'] = col2.number_input("Average age", key='average_age', min_value=0, max_value=None, value=0,
#                                               step=1, format="%d")

input_dict['num_tourists'] = input_dict['num_adults'] + input_dict['num_children']


function_descriptions = [
    {
        "name": "get_flight_hotel_info",
        "description": "Find the flights between cities and hotels within cities for residence.",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The ordered list of names of cities in the tour. e.g. ['Mumbai', 'Paris']"
                },

                "date_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The ordered list of dates for arrival in the cities in YYYY-MM-DD format."
                },

            },
            "required": ["loc_list", "date_list"],
        },
    }
]

@st.cache_data(show_spinner=False)
def generate_itinerary(input_dict):
                   
    user_message = f""" Context: You are a travel guide who is very professional in terms of speech and tone. You are tasked with creating a itinerary for the client who has laid out his details in the text enclosed with double quotes. If the {input_dict['price_per_person']} is not sufficient then tell the user to increase their budget and provide some budget recommendation. The itinerary should be summarized into maximum of 2 lines per day. Do not include any breakdowns and keep it simple.

"I want to stay at {input_dict['dest']} for {input_dict['num_days']} days. We want to experience {input_dict['genre']}. The group consists of {input_dict['num_tourists']} {input_dict['type_of_travelers']}, We are {input_dict['num_adults']} adults with {input_dict['num_children']} childrens. We want to make sure the pricing does not go over {input_dict['price_per_person']} INR per person for the entire trip. We will be travelling via {input_dict['mode_of_travel']} from {input_dict['src']}."

Example: 
Trip: Akihabara
Day 1:... 
Day n: """
                   

    # Generate the travel itinerary using the modified user message

    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                        input={"prompt": f"{user_message}",  # Prompts
                        "temperature":0.1, "top_p":0.9, "repetition_penalty":1},stream=True)  # Model parameters
    
    st.subheader("Itinerary")
    response = st.write_stream(output)
    print(str(response))


    st.session_state['input_dict'] = input_dict

    return response 



if st.button("Generate Itinerary", type="primary"):
    

    generated_itinerary = generate_itinerary(input_dict)
    st.session_state["cached_data_generated"] = True
    st.session_state['data_changed'] = False
    isGenerated = True

elif st.session_state.get("cached_data_generated", False) and not st.session_state['data_changed']:
    
    generated_itinerary = generate_itinerary(input_dict)
    


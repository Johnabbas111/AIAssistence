import googlemaps
import openai
import requests
from elasticsearch import Elasticsearch
from flask import Flask, render_template
from flask_socketio import SocketIO,emit
from collections.abc import MutableMapping
app=Flask(__name__)



socketio = SocketIO(app)
#Initializing api key
openai.api_key="yours api key"
gmaps = googlemaps.Client(key="Google map api key")
es=Elasticsearch([{'host':'localhost','port':5000}])

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

def generate_response(query):
    search_results = es.search(index="travel_guides", body={"query": {"match": {"content": query}}})
    retrieved_docs = [hit["_source"]["content"] for hit in search_results["hits"]["hits"]]
    prompt = f"Answer the following question based on these documents:\n{' '.join(retrieved_docs)}\nQuestion: {query}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
def get_weather(city):
    api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    return f"Current weather in {city}: {weather_description}, {temperature}°C"
def find_places(query, location, radius=1000):
    places_result = gmaps.places_nearby(location=location, radius=radius, keyword=query)
    places = places_result.get('results', [])
    return [(place['name'], place['vicinity']) for place in places]


@app.route('/search', methods=['POST'])
def search():
    data = requests.get_json()
    query = data['query']
    location = data['location']

    response = generate_response(query)
    weather_info = get_weather(location)
    places = find_places(query, location)
    formatted_places = '\n'.join([f"{name} - {vicinity}" for name, vicinity in places])

    result = {
        "response": response,
        "weather": weather_info,
        "places": formatted_places
    }
@socketio.on('user_message')
def handle_message(data):
    user_message = data['message']
    # Process user message with OpenAI
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=user_message,
        max_tokens=50
    )
    emit('bot_response', {'message': response.choices[0].text.strip()})





if(__name__=="__main__"):
    socketio.run(app, debug=True)


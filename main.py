from typing import Annotated,TypedDict,List
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class Agent(TypedDict):
    message:str|List[str]
    tourist:str
    hotel:str
    tourist_data:str
    hotel_data:str
    respn:str
    plan:str

def llm(state:Agent)->Agent:
    mod=ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        google_api_key=GOOGLE_API_KEY
    )
    prompt='''extract the number of days given in the trip'''
    state['respn']=mod.invoke(prompt)
    prompt1='''you are a planner agent , you will break the given user trip plan
      into 2 api format as per geoapify (finding attractions using given place,nearby hotel rooms ).i dont want any extra messages other than the 2 relevant apis and here is the api_key 'f587defd1a6740719fd395be7f8e157c',here is the user request for the plan ''',state['message']
    response=mod.invoke(prompt1)
    text = response.text() if callable(getattr(response, "text", None)) else getattr(response, "text", str(response))
    url_list = [u.strip().strip("`") for u in text.splitlines() if u.strip().startswith("http")]
    state["message"] = url_list  
    return state 

def tourist(state:Agent)->Agent:
    url_list=state["message"]
    if url_list:
        state['tourist']=url_list[0]
        resp=requests.get(state['tourist'])
        if resp.status_code==200:
            state['tourist_data']=resp.json()
    return state

def hotels(state:Agent)->Agent:
    url_list=state["message"]
    if len(url_list)>1:
        state["hotel"]=url_list[1]
        resp=requests.get(state['hotel'])
        if resp.status_code==200:
            state['hotel_data']=resp.json()
    return state

def itinerary(state: Agent) -> Agent:
    state["message"] = "itinerary prepared"

    prompt2 = f"""
    You are a planner agent. You need to create a time-based itinerary
    using the tourist places and nearby hotels provided.
    I want the plan to be according to the number of days 

    Example format:
    HERE IS THE EVENT PLAN FOR KOCHI:
    10 AM - 11 AM : DJ BOATING
    11 AM - 12:30 PM : WONDERLA

    Tourist places:
    {state.get('tourist')}

    Hotels :
    {state.get('hotel')}
    """

    mod = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY
    )

    response = mod.invoke(f"this prompt is the content : {prompt2}, this is the nuumber of days :{state['respn']}")
    state["plan"] = getattr(response, "content", str(response))
    return state

nodal=StateGraph(Agent)
nodal.set_entry_point("llm node")
nodal.add_node("llm node",llm)
nodal.add_node("hotel node",hotels)
nodal.add_node("Tourist node",tourist)
nodal.add_node("itinerary node",itinerary)
nodal.add_edge("llm node","Tourist node")
nodal.add_edge("Tourist node","hotel node")
nodal.add_edge("hotel node","itinerary node")
nodal.set_finish_point("itinerary node")
app=nodal.compile()

from IPython.display import Image
'''img = app.get_graph().draw_mermaid_png()
with open("workflow.png", "wb") as f:
    f.write(img)
print("Workflow diagram saved as workflow.png")'''
print("Muzifa’s Event Planner: Perfectly Planned, Beautifully Scheduled.")
print("HI!! ITS YOUR BOT ,TELL ME WHERE YOU WANT TO GO : ")
v=input()
result=app.invoke({'message':v})
#print(result['message'])
#print(result['plan'])
print(result['respn'])

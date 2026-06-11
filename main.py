import os
from typing import TypedDict, Annotated
import operator
import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.message import (AnyMessage, HumanMessage, AIMessage, SystemMessage)

from langchain_groq import ChatGroq
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model ="llama-3.3-70b-versatile"
)

DATABASE_URL = os.getenv("DB_URL")

class TravelState(TypedDict):
    message: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerrary: str
    llm_calls: int

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "message": [
            AIMessage(content=f"Flight results fetched")
        ],
        # "llm_calls": state.get("llm_calls", 0)+1
    }

def hotel_agents(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "message":[
            AIMessage(content="Hotel information fetched")
        ],
        # "llm_calls": state.get("llm_calls", 0)+1
    }

def itinerary_agent(state: TravelState):
    prompt = f"""
    Create a travel itinerary.
    User query: {state["user_query"]}

    Flight Results: {state["flight_results"]}

    Hotel Results: {state['hotel_results']}
"""
    response = llm.invoke([
        SystemMessage(
            content = "You are an expert travel planner"
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0)+1
    }


def final_agent(state: TravelState):
    final_prompt = f"""
    Generate final response.
    Flight Results: {state["flight_results"]}
    Hotel Results: {state['hotel_results']}
Itinerary: {state["itinerrary"]}
"""
    response = llm.invoke([HumanMessage(content=final_prompt)])
    
    return {
        "message": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agents)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


_conn = psycopg.connent(DATABASE_URL)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app=graph.compile(checkpointer=checkpointer)

if __name__ =="__main__":
    config = {
        "configurable":{
            "thread_id":"user_nilesh"
        }
    }

    user_input = input("Enter travel request: ")
    result = app.invoke({
        "message": [HumanMessage(content=user_input)],
        "user_query": user_input,
        "flight_results": "",
        "hotel_result":"",
        "itinerary":"",
        "llm_calls":0
    })
    print("n\ FINAL RESPONSE: \n")

    for msg in result["message"]:
        print(msg.content)

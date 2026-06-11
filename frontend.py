import streamlit as st
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}

.hero {
    padding: 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg,#0093E9,#80D0C7);
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.chat-user {
    background: #DCF8C6;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
}

.chat-ai {
    background: white;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

img {
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <h1>✈️ AI Travel Planner</h1>
    <h4>Flights • Hotels • Complete Itinerary</h4>
</div>
""", unsafe_allow_html=True)

# Beautiful travel images
col1, col2, col3 = st.columns(3)

with col1:
    st.image(
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
        use_container_width=True
    )

with col2:
    st.image(
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828",
        use_container_width=True
    )

with col3:
    st.image(
        "https://images.unsplash.com/photo-1436491865332-7a61a109cc05",
        use_container_width=True
    )

st.divider()

# Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display Chat
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(
            f'<div class="chat-user">🧑 {chat["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-ai">🤖 {chat["content"]}</div>',
            unsafe_allow_html=True
        )
user_input = st.chat_input(
    "Example: Plan a 5 day trip from Mumbai to Dubai in July"
)
if user_input:
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    config = {
        "configurable": {
            "thread_id": "user_nilesh"
        }
    }

    with st.spinner("🔍 Searching flights..."):
        result = app.invoke({
            "message": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
            config=config
        )
    response = ""

    if "message" in result:
        response = "\n\n".join(
            [
                msg.content
                for msg in result["message"]
                if hasattr(msg, "content")
            ]
        )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    st.rerun()
# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    username = st.text_input(
        "Username",
        value="guest",
        help="Used for chat history and LangGraph thread_id"
    )
    st.divider()

    st.title("🌎 Popular Destinations")

    st.image(
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c",
        caption="Dubai"
    )

    st.image(
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        caption="Paris"
    )

    st.image(
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf",
        caption="Tokyo"
    )

    st.info(
        """
        ✈ Flight Search
        
        🏨 Hotel Recommendations
        
        🗺 AI Generated Itinerary
        
        💰 Budget Planning
        """
    )
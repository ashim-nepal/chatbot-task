import streamlit as st # All required imports
import io
from pypdf import PdfReader
from transformers import pipeline
from rag_engine import chunk_text, build_faiss, retrieve
from agent_tools import AppointmentAgent


st.set_page_config(page_title="Doc QA + Appointment", page_icon="🗨️") # streamlit settingf 

# Session staes initialized 
if "chat" not in st.session_state: st.session_state.chat = []
if "qa_ready" not in st.session_state: st.session_state.qa_ready = False
if "faiss" not in st.session_state: st.session_state.faiss = None
if "chunks" not in st.session_state: st.session_state.chunks = None
if "agent" not in st.session_state: st.session_state.agent = None
if "llm" not in st.session_state:
    st.session_state.llm = pipeline("text2text-generation", model="google/flan-t5-base")

st.title("🧑‍🎓 Simple Doc-QA Chatbot + Appointment Booking") #Webpage title

uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"]) # File uploader supports pdf and txt
if uploaded is not None:
    text = ""
    if uploaded.type == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(uploaded.read()))
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            st.error("Failed to read PDF: " + str(e))
    else:
        try:
            text = uploaded.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.error("Failed to read TXT: " + str(e))

    if text.strip():
        chunks = chunk_text(text, chunk_size=900, overlap=120) # Splitting text into chunks
        index, vecs, chunks_list = build_faiss(chunks) # faiss index for searhing
        st.session_state.faiss = index
        st.session_state.chunks = chunks_list
        st.session_state.qa_ready = True
        st.success("Document indexed! Ask questions below.")
    else:
        st.warning("No text extracted from the file.")

# Displaying chat histry 
with st.container():
    for role, msg in st.session_state.chat:
        if role == "user":
            st.markdown(f"**You:** {msg}") # users message
        else:
            st.markdown(f"**Bot:** {msg}") # chatbot's message

user_msg = st.text_input("Type your message...", key="msg_input")

col1, col2 = st.columns(2)
send_clicked = col1.button("Send") # Send message request to bot
reset_clicked = col2.button("Reset Chat") # Reset chat history

if reset_clicked:
    st.session_state.chat = [] # clears chat
    st.session_state.agent = None
    st.rerun()


# Running LLM and response
def run_llm(prompt: str) -> str:
    try:
        out = st.session_state.llm(prompt, max_new_tokens=256)
        return out[0]["generated_text"].strip() # Returns generated text
    except Exception as e:
        return "LLM error: " + str(e)

if send_clicked and user_msg: # For handling send button click
    if st.session_state.agent:
        reply = st.session_state.agent.handle_input(user_msg)
        st.session_state.chat.append(("user", user_msg))
        st.session_state.chat.append(("bot", reply))
        if "✅ Appointment booked" in reply:
            st.session_state.agent = None
        st.rerun()
        
    lower = user_msg.lower()
    if ("call me" in lower) or ("book appointment" in lower):
        st.session_state.agent = AppointmentAgent()
        msg = "Okay! Let's book your appointment. What's your name?"
        st.session_state.chat.append(("user", user_msg))
        st.session_state.chat.append(("bot", msg))
        st.rerun()

    ctx = "" # Context is empty initially
    if st.session_state.qa_ready and st.session_state.faiss is not None and st.session_state.chunks is not None:
        hits = retrieve(user_msg, st.session_state.faiss, st.session_state.chunks, top_k=4) # Retrive relavent contexts
        ctx = "\n\n---CONTEXT START---\n" + "\n\n".join([h[2] for h in hits]) + "\n---CONTEXT END---\n" # Prepare context
    else:
        ctx = "No document context. Answer generally based on your knowledge."

    tail = st.session_state.chat[-6:] # Last 6 messages from context
    history_lines = []
    for role, msg in tail:
        prefix = "User:" if role == "user" else "Assistant:"
        history_lines.append(f"{prefix} {msg}")
    history_str = "\n".join(history_lines) # Conversation history (as string)

    prompt = f'''
You are a helpful but casual assistant. Use the provided CONTEXT if it's relevant. If the question cannot be answered from the context, say what you can and be honest.

{ctx}

Conversation so far:
{history_str}

User question: {user_msg}

Answer:
'''.strip()

    reply = run_llm(prompt) # Bot's Respond

    # Adding user messages and bot's response in chat history
    st.session_state.chat.append(("user", user_msg))
    st.session_state.chat.append(("bot", reply))
    st.rerun()

st.divider()
st.write("Type: 'Book Appointment' to Activate Booking conversaational Form")
st.write("Simple Chatbot - By Ashim Nepal")


# BY ASHIM NEPAL
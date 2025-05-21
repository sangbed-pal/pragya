from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
import json
from langchain_core.messages import HumanMessage, SystemMessage   
import os
import getpass
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from flask import Flask, request, jsonify
from transcript import get_transcript
from summary import summarize_with_translation
from langchain_openai import AzureOpenAIEmbeddings
from transcript import generate_transcript_from_audio_file
from text_to_speech import speech_from_text
from flask import send_file
app = Flask(__name__)
load_dotenv()
if "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
        "Enter your AzureOpenAI API key: "
    )

embedding = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_EMBEDDING_DEPLOYMENT_VERSION"],
)

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  # or your deployment
    api_version="2024-12-01-preview",  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

def store_transcript(text,vectorstore):
    # Split the text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(text)
    
    # Create documents from the chunks
    docs = [Document(page_content=t) for t in texts]
    
    # add documents to the vectorstore
    vectorstore.add_documents(docs)
    

def create_vectorstore(text):
    docs = [Document(page_content=text)]
    return FAISS.from_documents(docs, embedding)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
vectorstore = create_vectorstore("Currently Document is empty .If user asks about what you can do then assistant can initiate the conversation by saying that I am an assistant and I can help with Summarization and Quering a youtube video given youtube link and target language (optional) of the summary.  Otherwise answer question asked by user ")
retriever = vectorstore.as_retriever()

template = """
You are an intelligent assistant. Use the following chat history and documents to answer the question.

Chat history:
{chat_history}

Documents:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | llm
def detect_summary_intent_llm(message: str) -> dict:


    messages = [
        SystemMessage("""You are an assistant that extracts user intent from messages. 
    Given a user message, identify:
    1. If the user wants a summary of a YouTube video (True/False).
    2. The YouTube video URL (if any).
    3. The target language of the summary (default to "english" if not mentioned).

    Respond only in JSON format with keys: "summary_intent" (bool), "video_url" (string or null), "language" (string)."""),
        HumanMessage(message),
    ]
    
    content= llm.invoke(messages).content
    

    # Parse JSON from model 
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"summary_intent": False, "video_url": None, "language": "english"}

def response_chat(question: str) -> str:
    history = memory.load_memory_variables({})["chat_history"]
    print("history",history)
    docs = retriever.get_relevant_documents(question)
    print("docs",docs)
    if not docs:
        context = "No relevant documents found."
    else:
        context = "\n\n".join([d.page_content for d in docs])

    inputs = {
        "chat_history": "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in history]),
        "context": context,
        "question": question
    }

    response = chain.invoke(inputs)
    memory.save_context({"input": question}, {"output":response.content })
    return response.content  
def ask(question):

    summary_req= detect_summary_intent_llm(question)
    if summary_req['video_url'] is not None :
        video_transcript= get_transcript(summary_req["video_url"])
        #save video transcript to vectorstore
        store_transcript(video_transcript,vectorstore)
        
        if summary_req["summary_intent"]:
            # return summary of the video
            if summary_req.get("language"):
                summary=summarize_with_translation(video_transcript, target_lang=summary_req["language"])
            else:
                summary=summarize_with_translation(video_transcript)
            return summary    
        else :
            response= response_chat(question)
            return response
    else:
        response= response_chat(question)
        return response



# === Example Usage ===
# while True:
#     q = input("You: ")
#     if q == "exit":
#         break
#     print("Bot:", ask(q))

@app.route('/api/v1/query', methods=['POST'])
def ask_endpoint():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask(question)
    return jsonify({"answer": answer})

@app.route('/api/v1/speech-to-text', methods=['POST'])
def speech_to_text_endpoint():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio_file']
    audio_file.save("temp.wav")

    text = generate_transcript_from_audio_file("temp.wav")
    return jsonify({"text": text})


@app.route('/api/v1/text-to-speech', methods=['POST'])
def text_to_speech_endpoint():
    data = request.json
    text = data.get("text")
    print("text",text)
    voice = data.get("voice", "coral")
    payload = {
        "model": "gpt-4o-mini-tts",
        "input": text,
        "voice": voice
    }
    
    response=speech_from_text(payload)
    print("response",response)
    if response.status_code == 200:
        output_path = "speech_output.mp3"
        with open(output_path, "wb") as f:
            f.write(response.content)
        return send_file(output_path, mimetype="audio/mpeg")
    else:
        return jsonify({
            "error": response.status_code,
            "message": response.text
        }), response.status_code


if __name__ == '__main__':
    app.run(debug=True)    
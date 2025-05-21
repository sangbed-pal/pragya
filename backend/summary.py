from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import getpass
# ---------------------- Azure Config ----------------------
load_dotenv()  # Load variables from .env
if "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
        "Enter your AzureOpenAI API key: "
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


template_chunks_summary = """
Return the Summary of the following video transcript in {target_lang} language only also if this language is a regional language (such as bengali)  use regional language words instead of borrowed english words : {chunk} 
"""
template_final_summary ="""
            Return Summary of the following video transcript merging repeating sentences in {target_lang} language only also if this language is a regional language (such as bengali)  use regional language words instead of borrowed english words : {final_summary} 
   """


prompt_chunks_summary = ChatPromptTemplate.from_template(template_chunks_summary)
prompt_final_summary = ChatPromptTemplate.from_template(template_final_summary)
chain_chunks_summary = prompt_chunks_summary | llm
chain_final_summary = prompt_final_summary | llm 

prompt_translation = """ return the following text : {text} into {target_lang} language  """
chain_translation = ChatPromptTemplate.from_template(prompt_translation) | llm

# As GPT has a limit of context length of 128000 tokens, we need to split the text into smaller chunks  . each token approximately consists of 4 characters
def split_text(text, max_chars=500000):
    """Splits a long text into smaller parts by sentences."""
    import re
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_chars:
            chunk += sentence + " "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + " "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

#use azure openai to detect language
def language_detect(text,target_lang):
    template = """
    return "true"  if the following text is in {target_lang} language, otherwise return "false" : {text}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    response = chain.invoke({"text": text, "target_lang": target_lang})
    print(text,target_lang)
    print("detect lang :" ,response.content.strip().lower())
    return response.content.strip().lower()



def summarize_with_translation(text, target_lang="english"):
    # response_translation=chain_translation.invoke({"text": text, "target_lang": target_lang})
    # text=response_translation.content
    chunks = split_text(text)
    print(f"Number of chunks: {len(chunks)}")
    partial_summaries = []
    for chunk in chunks:
       
        inputs = {
        "target_lang": target_lang,
        "chunk": chunk,
         }

        response = chain_chunks_summary.invoke(inputs)
        partial_summaries.append(response.content)
    if len(partial_summaries)>1:    
        final_summary = " ".join(partial_summaries)
        response= chain_final_summary.invoke({"target_lang": target_lang, "final_summary": final_summary})

    # if language_detect(response.content[0:100],target_lang) == "false":
        # If the text is not in the target language, translate it first
    print(f"Translating text to target language...{target_lang}")
    
    response = chain_translation.invoke({"text": response.content, "target_lang": target_lang})
    
    return  response.content
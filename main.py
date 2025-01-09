import os
from dotenv import load_dotenv
import traceback
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI

from urllib.parse import urlparse
from langchain_community.document_loaders import YoutubeLoader

load_dotenv()

SUMMARIZE_PROMPT = """
以下のコンテンツについて、内容を300文字程度でわかりやすくようやくしてください

=======
{content}
=======
日本語で書いてください
"""

def init_page():
    st.set_page_config(
        page_title="Youtube Summarizer",
        page_icon="🤖",
    )
    st.header("Youtube Summarizer 🤖")

def init_chain():
    llm = ChatOpenAI(
        temperature=0,
        model="deepseek-chat",
        openai_api_key=os.getenv("DEEP_SEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com",
    )

    prompt = ChatPromptTemplate.from_messages([
        ("user", SUMMARIZE_PROMPT)
    ])

    output_parser = StrOutputParser()
    
    chain = prompt | llm | output_parser
    return chain

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def get_content(url):
    with st.spinner("Fetching content..."):
        loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=True,
            language=["en","ja"],
        )
        res = loader.load()
        try:
            if res:
                content = res[0].page_content
                title = res[0].metadata["title"]
                return f"Title: {title}\n\n{content}"
            else:
                return None
        except:
            st.write(traceback.format_exc())
            return None

def main():
    init_page()
    chain = init_chain()
    
    if url := st.text_input("URL: ", key="input"):
        is_valid_url = validate_url(url)
        
        if not is_valid_url:
            st.write("Please input a valid URL.")
        else:
            if contetnt := get_content(url):
                st.markdown("## Summary")
                st.write_stream(chain.stream({"content": contetnt}))
                st.markdown("---")
                st.markdown("## Original Text")
                st.write(contetnt)

if __name__ == "__main__":
    main()
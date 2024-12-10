import httpx
import logging
from fastapi import HTTPException
import google.generativeai as genai
import uuid  # Make sure to import uuid for generating unique IDs

from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
# from langchain_core.prompts import PromptTemplate
# from pydantic import BaseModel, Field
# from langchain_core.output_parsers import JsonOutputParser

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os 
from dotenv import load_dotenv
from app.services.meme_generator import MemeGenerator
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class NewsService:
    def __init__(self):
        # NewsData.io API Configuration
        self.api_key =os.getenv("NEWS_API_KEY")  
        self.base_url = "https://newsdata.io/api/1/news"
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Gemini API Configuration
        genai_api_key = "AIzaSyAnfEvhg0Uz6Oahgvyoyy1FLGIWKzd6LhI"  # Replace with your actual Gemini API key
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure model availability for your API key
    def _get_model(self,
        model_name="gpt-4o-2024-05-13",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.5,
        max_tokens=1000):

        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=openai_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
    async def fetch_news_from_rag(self, category: str, query: str,tone:str, language: str = "en") -> dict:
        """
        Fetches news articles from the NewsData.io API based on the query and category.
        """
        params = {
            "apikey": self.api_key,  # API key for authentication            # Search query
            "language": language,   # Language filter (e.g., 'en' for English)
            # "category": category    # Category filter (e.g., 'technology', 'health')
        }

        # logging.info(f"Fetching news for category: {category}, query: {query}, language: {language}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                news_data = response.json()
                print("news")
                print(news_data.get("results")[0])
                if 'results' in news_data and news_data['results']:
                    
                    
                    results =self.vectorize_news(news_list=news_data["results"], tone=tone, query=query)
                 
                    output = MemeGenerator().extract_json_from_output(results)
                    
                    logging.info(f"Fetched {len(news_data['results'])} articles from NewsData.io")
                else:
                    logging.warning("No articles found in the API response.")
                return output
        except httpx.RequestError as e:
            logging.error(f"Error fetching news: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error while fetching news: {e}")
            raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {e}")

    async def summarize_article(self, title: str, content: str, tone: str, format: str) -> str:
        """
        Summarizes a news article using the Generative AI model.
        """
        prompt = (
            f"You are an AI assistant specialized in summarizing news articles.\n"
            f"Tone: {tone}\n"
            f"Format: {format}\n"
            f"Title: {title}\n"
            f"Content: {content}\n"
            "Provide a concise and engaging summary."
        )

        logging.info(f"Generating summary for article titled '{title}' with tone '{tone}' and format '{format}'.")
        
        try:
            response = self.model.generate_content(prompt)
            logging.info(f"Summarization successful for title: '{title}'")
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error summarizing article '{title}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error summarizing article: {e}")

    def vectorize_news(self, news_list: list, tone: str, query: str) -> tuple:
        """
        Vectorizes the fetched news articles, returning document IDs and metadata.
        """
        documents = []
        metadatas = []
        ids = []

        try:
            for news in news_list:
                document = f"Title: {news.get('title')} news content: {news.get('description')}. source url: {news.get('link', 'no link')}, author:{news.get('source_name', 'No source')}, picture_url: {news.get('image_url')}"
                metadata = {
                    "source": news.get("source_name", "No source"),
                    "published_at": news.get("pubDate", "None"),
                    "url": news.get("link", "No link")
                }
                id = uuid.uuid1()
                documents.append(document)
                metadatas.append(metadata)
                ids.append(str(id))
                
                
             # Create a Chroma vector store from the documents
            chroma_collection = Chroma.from_texts(
                texts=documents, metadatas=metadatas, embedding=self.embeddings
            )

            # Create a retriever memory using the new vector store
            retriever = chroma_collection.as_retriever(search_kwargs={"k": 2})
            system_prompt = """You are an AI news generator that summarizes(not more than a paragraph) and reports news based on a specified tone (formal, humorous, or conversational). 
            Please ensure that the summary reflects the requested tone accurately.
            
            Tone: {tone}
            Context: {context}
            
            output: {{"title":"","summary":"", "source_url": "", "picture_url":"","author":""}}
            
            always remember to return a json format and include the source url at the end. make sure it's the actual link and it works.
            
            """
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )

            # "brief_summary": "The Jesse AI project is progressing steadily, but some critical tasks are at risk due to delays and scope changes. The team is working to mitigate these risks and ensure timely delivery."

            question_answer_chain = create_stuff_documents_chain(
                self._get_model(model_name="gpt-4o-2024-05-13", max_tokens=4096), prompt
            )
            chain = create_retrieval_chain(retriever, question_answer_chain)

            result = chain.invoke(
                {
                    "input": query,
                    "tone": tone
                }
            )

            # print(result.get("answer"))
            return result.get("answer")


        except Exception as e:
            logging.error(f"An error occurred while vectorizing news: {e}")

        logging.info(f"documents: {len(documents)}, metadatas: {len(metadatas)}")

        return "error"
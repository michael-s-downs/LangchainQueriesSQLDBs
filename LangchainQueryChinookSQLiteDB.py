import os
import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SQLDatabase

# Load environment variables from .env file (Optional)
load_dotenv()

#set up some local variables
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
DB_ABS_PATH=os.getenv("DB_ABS_PATH")

db = SQLDatabase.from_uri("sqlite:///{DB_ABS_PATH}")
chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-0613"), db=db)

# Create OpenAI embeddings
openai_embeddings = OpenAIEmbeddings()

def main():
    # Set the title and subtitle of the app
    st.title("🦜🔗 Talk to DB, get SQL statements (basic example)")
    st.image('.././assets/power-platform.png')
    st.subheader('This basic example returns JUST the SQL from your natural language prompt.')
    question = st.text_input("Ask a question (query/prompt)")
    if st.button("Submit Query", type="primary"):

        sql_query = chain.invoke({"question": question})
        st.subheader("Answer:")
        st.write(sql_query)

if __name__ == '__main__':
    main()
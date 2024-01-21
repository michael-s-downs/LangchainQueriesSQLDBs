import os
import streamlit as st
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase
#from langchain.sql_database import SQLDatabase
import pandas as pd
import ast

# Load environment variables from .env file (Optional)
load_dotenv()

#set up some local variables
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
#DB_ABS_PATH=os.getenv("DB_ABS_PATH")
#DB_REL_PATH = "dbchinook/Chinook.db"

db = SQLDatabase.from_uri("sqlite:///dbchinook/Chinook.db")
chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-0613"), db=db)

def main():
    # Set the title and subtitle of the app (title is the main category, subtitle is particular example)
    st.title("🦜🔗 Talk to a SQL DB using LLMs")
    st.image('assets/sqliteERD.png')
    st.subheader('This example returns BOTH the SQL AND its execution.')
    st.subheader('this version has the test SQL')
    question = st.text_input("Ask a question (query/prompt)")
    if st.button("Submit Query", type="primary"):
        sql_query = chain.invoke({"question": question})
        st.subheader("This is the SQL you asked for:")
        st.write(sql_query)
        st.subheader("This is the Data from running that SQL:")
        result = db.run(sql_query)

        # convert result to table
        data = ast.literal_eval(result) # convert str to list
        df = pd.DataFrame(data)
        st.dataframe(df)

if __name__ == '__main__':
    main()
import os
import streamlit as st
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SQLDatabase
import pandas as pd
import ast

# Load environment variables from .env file (Optional)
load_dotenv()

#set up some local variables
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

db = SQLDatabase.from_uri("sqlite:///LangchainQueriesSQLDBs/dbchinook/Chinook.db")
chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-0613"), db=db)

def main():
    # Set the title and subtitle of the app (title is the main category, subtitle is particular example)
    st.title("🦜🔗 Talk to a SQL DB using LLMs")
    st.image('assets/sqliteERD.png')
    st.subheader('This example returns BOTH the SQL and its execution.')

    # # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    # display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                sql_query = chain.invoke({"question": prompt})
                st.subheader("This is the SQL you asked for:")
                st.write(sql_query)
                st.subheader("This is the Data from running that SQL:")
                response = db.run(sql_query)

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

        # convert result to table
        data = ast.literal_eval(response) # convert str to list
        df = pd.DataFrame(data)
        st.dataframe(df)

if __name__ == '__main__':
    main()
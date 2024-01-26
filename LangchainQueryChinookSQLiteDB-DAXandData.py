import os
import streamlit as st
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import InfoSQLDatabaseTool
import pandas as pd
import ast
from azure.identity import DefaultAzureCredential
from azure.identity import InteractiveBrowserCredential
from langchain_community.agent_toolkits import PowerBIToolkit, create_pbi_agent
from langchain_community.utilities.powerbi import PowerBIDataset

# Load environment variables from .env file (Optional)
load_dotenv()

#set up some local variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_ABS_PATH = os.getenv("DB_ABS_PATH")

db = SQLDatabase.from_uri(f"sqlite:///{DB_ABS_PATH}")
#chain = create_sql_query_chain(llm=ChatOpenAI(temperature=0,model="gpt-3.5-turbo-0613"), db=db)

# Initialize the Language Model
llm = ChatOpenAI(
    temperature=0.5, max_tokens=1000, model_name="gpt-3.5-turbo", verbose=True
)

#If we can use default authentication...
credential=DefaultAzureCredential()

#If we must use browser authentication...
#credential=InteractiveBrowserCredential()


#Initialize the PowerBI Toolkit
# powerbi = PowerBIDataset(
#     dataset_id="f0ac68d5-959a-4706-82dc-d7ce5e229f1d",
#     table_names=["Album", "Artist", "Customer"],
#     credential=credential.credentials[1],
# )

powerbi = PowerBIDataset(
    dataset_id="f0ac68d5-959a-4706-82dc-d7ce5e229f1d",
    table_names=["Album", "Artist", "Customer"],
    token='34657b7b-0a76-47c9-bb4f-70110bb60f4b')

# Create the Power BI agent
toolkit = PowerBIToolkit(powerbi=powerbi, llm=llm, output_token_limit=100)
agent_executor = create_pbi_agent(llm=llm, toolkit=toolkit, verbose=True)

def main():
    # Set the title and subtitle of the app (title is the main category, subtitle is particular example)
    st.title("🦜🔗 Talk to a SQL DB using LLMs")
    st.image('assets/sqliteERD.png')
    st.subheader('This example returns BOTH the SQL and its execution.')

    # # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hi I'm OptiGPT. How can I help?"}]

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

                # Example: Describe a table
                #dax_query = agent_executor.run({prompt})

                #sql_query = chain.invoke({"question": prompt})
                #st.subheader("This is the DAX you asked for:")
                #st.write(dax_query)
                sql_subheader = "### This is the SQL you asked for:"
                response = agent_executor.run({prompt})

        # convert result to table
        data = ast.literal_eval(response) # convert str to list
        df = pd.DataFrame(data)
        st.session_state['df'] = df
        st.dataframe(st.session_state['df'])
        st.session_state['response'] = df

        #message = {"role": "assistant", "content": f"{sql_subheader}\n{sql_query}"}
        #st.session_state.messages.append(message)
        #message = {"role": "assistant", "content": df}
        #st.session_state.messages.append(message)

        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)

        col1, col2, col3 = st.columns([0.75, 0.75, 10])

        with col1:
            if st.button("👍"):
                # Action to perform only when thumbs up is clicked
                thumbs_up_message = "You clicked Thumbs Up!"
                st.session_state.messages.append({"role": "assistant", "content": thumbs_up_message})


        with col2:
            if st.button("👎"):
                thumbs_down_message = "You clicked Thumbs Down!"
                st.session_state.messages.append({"role": "assistant", "content": thumbs_down_message})
        
        
        with col3:
            st.download_button(
                label=":arrow_down:",
                data=csv,
                file_name='data.csv',
                mime='text/csv',
            )

if __name__ == '__main__':
    main()

# from azure.identity import DefaultAzureCredential
# from langchain_community.agent_toolkits import PowerBIToolkit, create_pbi_agent
# from langchain_openai import ChatOpenAI
# from langchain_community.utilities.powerbi import PowerBIDataset

# # Initialize the Language Model
# llm = ChatOpenAI(
#     temperature=0.5, max_tokens=1000, model_name="gpt-3.5-turbo", verbose=True
# )

# # Initialize the PowerBI Toolkit
# powerbi = PowerBIDataset(
#     dataset_id="<dataset_id>",
#     table_names=["table1", "table2"],
#     credential=DefaultAzureCredential(),
# )

# # Create the Power BI agent
# toolkit = PowerBIToolkit(powerbi=powerbi, llm=llm)
# agent_executor = create_pbi_agent(llm=llm, toolkit=toolkit, verbose=True)

# # Example: Describe a table
# agent_executor.run("Describe table1")

# # Example: Run a simple query on a table
# agent_executor.run("How many records are in table1?")

# # Example: Run queries with specific conditions
# agent_executor.run("How many records are there by dimension1 in table2?")
# agent_executor.run("What unique values are there for dimension2 in table2?")

# # Example: Execute custom DAX queries
# agent_executor.run("What was the maximum value in revenue in dollars in 2022?")


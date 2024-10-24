import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import create_engine
import json
# Replace with your PostgreSQL connection URL
DATABASE_URL = st.secrets["database"]["url"]
# Set up the database connection
engine = create_engine(DATABASE_URL)
# Initialize variables using session state
if 'parameters' not in st.session_state:
   st.session_state['parameters'] = {}
# Function to save variable states to database
def save_to_db(name, description, parameters):
   data = {
       "name": name,
       "description": description,
       "date_time": datetime.datetime.now().isoformat(),
       "variables": json.dumps(parameters)
   }
   # Insert the data into the database
   query = """
   INSERT INTO variable_states (name, description, date_time, variables)
   VALUES (%s, %s, %s, %s)
   """
   with engine.connect() as connection:
       connection.execute(query, (data['name'], data['description'], data['date_time'], data['variables']))
       st.success('State saved successfully!')
# Function to load all saved states
def load_all_states():
   query = "SELECT id, name, description, date_time FROM variable_states ORDER BY date_time DESC"
   with engine.connect() as connection:
       results = pd.read_sql(query, connection)
   return results
# Function to restore a saved state by ID
def restore_state(state_id):
   query = "SELECT variables FROM variable_states WHERE id = %s"
   with engine.connect() as connection:
       result = connection.execute(query, (state_id,)).fetchone()
       if result:
           st.session_state['parameters'] = json.loads(result['variables'])
           st.success('State restored successfully!')
# Display input fields for parameters
param1 = st.text_input("Enter parameter 1", st.session_state['parameters'].get('param1', ''))
param2 = st.number_input("Enter parameter 2", value=st.session_state['parameters'].get('param2', 0))
# Save the parameters to session state
st.session_state['parameters']['param1'] = param1
st.session_state['parameters']['param2'] = param2
# Save button functionality
if st.button('Save Current State'):
   with st.form("Save Form"):
       name = st.text_input("Enter your name")
       description = st.text_area("Enter an optional description")
       submit = st.form_submit_button("Save")
       if submit:
           if name:
               save_to_db(name, description, st.session_state['parameters'])
           else:
               st.error("Name is required to save the state!")
# Load saved states
st.subheader("Load a Saved State")
saved_states = load_all_states()
if not saved_states.empty:
   st.write(saved_states)
   selected_state_id = st.selectbox("Select a state to restore", saved_states['id'])
   if st.button("Restore Selected State"):
       restore_state(selected_state_id)
       # Automatically update the UI with restored parameters
       st.experimental_rerun()
else:
   st.write("No saved states available.")

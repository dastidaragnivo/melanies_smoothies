# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
  """
     Choose the fruits you want in your custom smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('Name on your smoothie will be: ', name_on_order)

# Thread-safe container connection
conn = st.connection("snowflake")
session = conn.session()


# Fetch data and extract the specific column values for the multiselect list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert the dataframe column to a Python list for clear option presentation
fruit_options_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_options_list, max_selections=5)

# Ensure the list is not empty and a name has been entered
if ingredients_list and name_on_order:
    st.write(ingredients_list)
    st.text(ingredients_list)

    # Join chosen fruits cleanly with spaces
    ingredients_string = ' '.join(ingredients_list) + ' '
    
    # Construct your target statement safely
    my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order) 
                        values ('{ingredients_string.strip()}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

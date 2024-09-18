# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert Snowpark Dataframe to Pandas Dataframe
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
    ingredients_string = ''
    for fruit_names in ingredients_list:
        ingredients_string += fruit_names + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_names, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_names,' is ', search_on, '.')
        st.subheader(fruit_names+' Nutrition Information!')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+fruit_names)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            
    #st.text(ingredients_string)

    #Insert chosen ingredients in orders table
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered'+' '+name_on_order+'!', icon="✅")



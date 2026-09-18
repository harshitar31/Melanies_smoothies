import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

conn = st.connection("snowflake")
session = conn.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    )

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the SEARCH_ON value for this fruit
        search_on_query = f"""select search_on from smoothies.public.fruit_options 
                             where fruit_name = '{fruit_chosen}'"""
        search_on_result = session.sql(search_on_query).collect()
        
        if search_on_result:
            search_on_value = search_on_result[0][0]
            
            st.subheader(fruit_chosen + ' Nutrition Information')
            
            try:
                smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on_value)
                smoothiefroot_response.raise_for_status()
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            except Exception as e:
                st.error(f"Could not fetch data for {fruit_chosen}: {str(e)}")

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
    
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")

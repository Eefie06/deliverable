#%%
# Management wants some interactive insights at their fingertips ASAP on how we performed last year (2022)
# in some large cities: Amsterdam, Rotterdam & Groningen.
import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

connection_string = os.environ["POSTGRES_CONNECTION_STRING"]
engine = create_engine(connection_string)


#%%
# Titels op pagina
st.title("Overview of covid reviews in Amsterdam, Rotterdam and Groningen")
st.text("Place where my graph will appear")

# %%
# Get covid data grouped by municipality and date


@st.cache
def get_covid_data():
    df_covid = pd.read_sql_query(
        """
        select municipality_name, date_of_publication, sum(total_reported) as total_reported
        from covid.municipality_totals_daily mtd
        where municipality_name in ('Groningen', 'Amsterdam', 'Rotterdam')
        and date_of_publication > '2022-01-01'
        group by municipality_name, date_of_publication
        order by municipality_name, date_of_publication
        """,
        con=engine,
    )
    return df_covid


df_covid = get_covid_data()

# Get review data grouped by municipality and date


@st.cache
def get_review_data():
    df_reviews = pd.read_sql_query(
        """
        select review_date, location_city, count(*) as n_reviews,
        AVG(rating_delivery) as avg_del_score, AVG(rating_food) as avg_food_score from (
        select DATE(datetime) review_date, rating_delivery, rating_food, location_city from public.reviews rv
        left join (select restaurant_id, location_city from restaurants) locs
        on rv.restaurant_id = locs.restaurant_id
        where datetime > '2022-01-01'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
        ) t
        group by review_date, location_city
        """,
        con=engine,
    )
    return df_reviews


df_reviews = get_review_data()

#%%
# The number of reviews per day over time in these cities

# st.dataframe(df_reviews, width=None, height=None, use_container_width=False)

reviews_line = px.line(df_reviews, x="review_date", y="n_reviews", color="location_city")

st.plotly_chart(reviews_line)

#%%
# The covid infections per day in these cities

covid_inf_line = px.line(
    df_covid, x="date_of_publication", y="total_reported", color="municipality_name"
)

st.plotly_chart(covid_inf_line)

#%%
# Filtering the time window for all graphs

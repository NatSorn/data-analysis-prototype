# import packages
import streamlit as st
import pandas as pd
import re
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Helper function to clean text
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Function to get insight from GPT-4o-mini
def get_gpt_insight(df, api_key):
    # Prepare a summary of the data for the prompt
    sample = df.head(10).to_dict()
    prompt = (
        "You are a data analyst. Given the following sample data, provide 3 key insights in bullet points. "
        "If possible, mention trends, anomalies, or anything interesting.\n\nSample data:\n" + str(sample)
    )
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting insight: {e}"


st.title("Hello, GenAI!")
st.write("This is your GenAI-powered data processing app.")

# Layout two buttons side by side
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Ingest Dataset"):
        try:
            st.session_state["df"] = pd.read_csv("./CBM03.20250924T220929.csv")
            st.success("Dataset loaded successfully!")
        except FileNotFoundError:
            st.error("Dataset not found. Please check the file path.")

# with col2:
#     if st.button("🧹 Parse Reviews"):
#         if "df" in st.session_state:
#             st.session_state["df"]["CLEANED_SUMMARY"] = st.session_state["df"]["SUMMARY"].apply(clean_text)
#             st.success("Reviews parsed and cleaned!")
#         else:
#             st.warning("Please ingest the dataset first.")

# Display the dataset if it exists
if "df" in st.session_state:
    # Product filter dropdown
    st.subheader("🔍 Filter by Statistic")
    statistic = st.selectbox("Choose a type", ["All"] + list(st.session_state["df"]["Statistic Label"].unique()))
    st.subheader(f"📁 Reviews for {statistic}")

    if statistic != "All":
        filtered_df = st.session_state["df"][st.session_state["df"]["Statistic Label"] == statistic]
    else:
        filtered_df = st.session_state["df"]
    st.dataframe(filtered_df)

    st.subheader("Statistic by category")
    grouped = st.session_state["df"].groupby(["Statistic Label", "Daily"])["VALUE"].sum().reset_index()
    st.bar_chart(grouped, x="Daily", y="VALUE")

    # GPT-4o-mini insight section
    st.subheader("🤖 GPT-4o-mini Data Insights")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
    else:
        if st.button("🔎 Generate Insights with GPT-4o-mini"):
            with st.spinner("Analyzing data with GPT-4o-mini..."):
                insight = get_gpt_insight(filtered_df, api_key)
                st.markdown(insight)

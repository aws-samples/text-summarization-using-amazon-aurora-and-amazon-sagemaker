import streamlit as st
import mysql.connector

st.set_page_config(page_title = "Aurora ML with GenAI")
st.title("Build Gen AI solutions using Aurora ML and SageMaker Jumpstart foundation models.")
st.write("Businesses today want to enhance the data stored in their relational databases and incorporate real time or batch predictions from machine learning (ML) models. However, most ML processing is done offline in separate systems, resulting in delays in receiving ML inferences for use in applications. In this session, you will learn how to enhance the data in your Aurora database using Gen AI by leveraging Amazon Aurora's machine learning capabilities and its seamless integration with Amazon SageMaker and Amazon Comprehend.")
st.write("We will show how data in Aurora database can be enhanced on a regular basis using Gen AI. We will demonstrate how Aurora ML's integration capabilities with Amazon SageMaker and Amazon Comprehend can generate a useful summary of tabular data and detect sentiment using Amazon SageMaker foundation models and Amazon Comprehend respectively.")

import streamlit as st
import mysql.connector
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import json

st.title("Use Generative AI to help CaseSummarization Case Notes and generate Customer Sentiment")

#replace the secret_name and region_name with AWS secret manager where your credentials are stored
def get_secret():
    secret_name = "aurora-db-credentials"
    region_name = "us-west-2"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(e)

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret

#connect to mysql using your aurora cluster details. Enter appropriate database name
secret = json.loads(get_secret())
connection = mysql.connector.connect(
    host=secret["host"],
    user=secret["username"],
    password=secret["password"],
    database="genai"
)

#fetch db data
cursor = connection.cursor(prepared=True)

# Fetch all products
cursor.execute("SELECT DISTINCT CaseID FROM CaseSummarization")
names = [name[0] for name in cursor.fetchall()]
names.append("All")
default_name = names[-1]

# Dropdown to select the name
selected_name = st.selectbox('Select a Case ID', names, index=names.index(default_name))

col1, col2 = st.columns(2)

 # Add a query button
if col1.button('Fetch CaseSummarization Table Data'):
    if selected_name!="All":
        st.write(f"Fetching data for: {selected_name}")
        query = "SELECT * FROM CaseSummarization WHERE CaseID = %s"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query, (selected_name,))
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.write(f"Fetching data for: {selected_name}")
        query = "SELECT * FROM CaseSummarization"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.dataframe(df)

 # Add a query button
if col1.button('Fetch All Data'):
    if selected_name!="All":
        st.write(f"Fetching data for: {selected_name}")
        query = "SELECT cs.CaseID, cs.Subject, ct.CategoryTypeName, sn.ServiceName, cs.CaseNotes, r.RequestorName, co.CaseOwnerName, cs.Stage, cs.Priority, cs.Feedback, cs.CreationTime, cs.LastUpdatedTime FROM CaseSummarization cs INNER JOIN CategoryTypeDetails ct ON cs.CategoryTypeID = ct.CategoryTypeID INNER JOIN ServiceNameDetails sn ON cs.ServiceNameID = sn.ServiceNameID INNER JOIN RequestorDetails r ON cs.RequestorID = r.RequestorID INNER JOIN CaseOwnerDetails co ON cs.CaseOwnerID = co.CaseOwnerID where cs.CaseID=%s"
        params = (selected_name,)
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.write(f"Fetching data for: {selected_name}")
        query = "SELECT cs.CaseID, cs.Subject, ct.CategoryTypeName, sn.ServiceName, cs.CaseNotes, r.RequestorName, co.CaseOwnerName, cs.Stage, cs.Priority, cs.Feedback, cs.CreationTime, cs.LastUpdatedTime FROM CaseSummarization cs INNER JOIN CategoryTypeDetails ct ON cs.CategoryTypeID = ct.CategoryTypeID INNER JOIN ServiceNameDetails sn ON cs.ServiceNameID = sn.ServiceNameID INNER JOIN RequestorDetails r ON cs.RequestorID = r.RequestorID INNER JOIN CaseOwnerDetails co ON cs.CaseOwnerID = co.CaseOwnerID"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.dataframe(df)



# Custom CSS style to adjust the button's height
button_style = (
    f'<style>'
    f'.st-eb button {{ height: 60px; }}'  # Set the height for all buttons
    f'</style>'
)

# Display the custom CSS style
st.markdown(button_style, unsafe_allow_html=True)

# Center align the elements vertically
st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction: row;}</style>', unsafe_allow_html=True)


# Center align the elements vertically
st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction: row;}</style>', unsafe_allow_html=True)


if col2.button("SagemakerJumpstart(AI21) Summary"):
    st.write(f"Generating overall summary for: {selected_name}")
    if selected_name!="All":
        # Construct the update query
        update_query = ( "UPDATE CaseSummarization ca INNER JOIN ServiceNameDetails sn ON ca.ServiceNameID = sn.ServiceNameID SET ca.CaseSummaryAI21 = CaseSummarizeAI21(ca.CaseID, ca.Subject, sn.ServiceName, ca.CaseNotes, ca.Priority, ca.Feedback) WHERE ca.CaseID = %s")
        params = (selected_name,)
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(update_query, params)
        connection.commit()

        query = "SELECT CaseID, CaseNotes, CaseSummaryAI21 from CaseSummarization where CaseID= %s"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        styled_df = df.style.set_properties(**{'white-space': 'normal', 'word-wrap': 'break-word'})
        st.table(styled_df)
    else:
         # Construct the update query
        update_query = ( "UPDATE CaseSummarization ca INNER JOIN ServiceNameDetails sn ON ca.ServiceNameID = sn.ServiceNameID SET ca.CaseSummaryAI21 = CaseSummarizeAI21(ca.CaseID, ca.Subject, sn.ServiceName, ca.CaseNotes, ca.Priority, ca.Feedback)")

        # Execute the update query
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(update_query)
        connection.commit()

        query = "SELECT CaseID, CaseNotes, CaseSummaryAI21 from CaseSummarization"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        styled_df = df.style.set_properties(**{'white-space': 'normal', 'word-wrap': 'break-word'})
        st.table(styled_df)

# Button: Generate Sentiment
if col2.button("Sentiment"):
    st.write(f"Generating overall Sentiment for: {selected_name} based on the lastest reviews")
    if selected_name!="All":
        update_query = (
            "UPDATE CaseSummarization SET Sentiment = aws_comprehend_detect_sentiment(feedback, 'en') where CaseID=%s"
        )
        # Execute the update query
        params = (selected_name,)
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(update_query, params)
        connection.commit()

        query = "SELECT CaseID, feedback, CaseSummaryAI21, Sentiment from CaseSummarization WHERE CaseID = %s"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        styled_df = df.style.set_properties(**{'white-space': 'normal', 'word-wrap': 'break-word'})
        st.table(styled_df)
    else:
        update_query = (
            "UPDATE CaseSummarization SET Sentiment = aws_comprehend_detect_sentiment(feedback, 'en')"
        )
        # Execute the update query
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(update_query)
        connection.commit()

        query = "SELECT CaseID, feedback, CaseSummaryAI21, Sentiment from CaseSummarization"
        with connection.cursor(prepared=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        df = pd.DataFrame(data)
        styled_df = df.style.set_properties(**{'white-space': 'normal', 'word-wrap': 'break-word'})
        st.table(styled_df)


# Button: Clear table data
if col1.button("Clear Data"):
    st.write(f"Deleting overall Sentiment and Summary")
    update_query = (
            "UPDATE CaseSummarization SET CaseSummaryAI21 = NULL, Sentiment = NULL"
        )
        # Execute the update query
    cursor.execute(update_query)
    connection.commit()
    st.write("Data Deleted")
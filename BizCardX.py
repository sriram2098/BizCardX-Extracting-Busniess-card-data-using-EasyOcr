import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import mysql.connector as sql
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from function import upload_database, extracted_data, show_database

mydb = sql.connect(host = 'localhost',
                   user = 'root',
                   password = '',
                   database = 'bizcardx')
mycursor = mydb.cursor(buffered = True)

# ------------------------------------------setting page configuration in streamlit---------------------------------------------------------
icon = Image.open("F:\GUVI\Projects\BizCardX\icon.png")
st.set_page_config(page_title='Bizcardx Extraction', 
                   layout="wide",
                   page_icon = icon,
                   menu_items = {'About' : """# This OCR app is created by *Sriram*!"""})

#st.balloons()
st.markdown("<h1 style = 'color : white; margin-left: 110px; margin-top : -60px'>BizCardX Extracting Business Card Data Using OCR</h1>", unsafe_allow_html = True)

#Set-up Background Image
def set_bg():
    st.markdown(f""" <style>.stApp{{
                background : url("https://cutewallpaper.org/21x/c1wdh9x26/1742031029.jpg");
                background-size : cover}}
                </style>""", unsafe_allow_html = True)
set_bg()

selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                        icons=["house","cloud-upload","pencil-square"],
                        default_index=0,
                        orientation="horizontal",
                        styles={"nav-link": {"font-size": "20px", "text-align": "center", "margin": "0px", "--hover-color": "#6495ED"},
                            "icon": {"font-size": "30px"},
                                            "container" : {"max-width": "3000px"},
                                            "nav-link-selected": {"background-color": "#6495ED"}})
file_name = 'thiru'

if selected == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("## :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
        with col2:
            st.markdown(
                        "![Alt Text](https://cdn.dribbble.com/users/2037413/screenshots/4144417/ar_businesscard.gif)")
            
if selected == "Upload & Extract":
    img = Image.open("F:\GUVI\Projects\BizCardX\extract.png")
    st.image(img)
    st.subheader(':violet[Choose image file to extract data]')
    # ---------------------------------------------- Uploading file to streamlit app ------------------------------------------------------
    uploaded = st.file_uploader('Choose a image file', type = ["png", "jpg", "jped"])
    # --------------------------------------- Convert binary values of image to IMAGE ---------------------------------------------------
    if uploaded is not None:
        with open(f'{file_name}', 'wb') as f:
            f.write(uploaded.getvalue())
        # ----------------------------------------Extracting data from image (Image view)-------------------------------------------------
        st.subheader(':violet[Image view of Data]')
        if st.button('Extract Data from Image'):
            extracted = extracted_data(f'{file_name}')
            st.subheader("Extracted the uploaded card")
            st.image(extracted)

        # ----------------------------------------upload data to database----------------------------------------------------------------
        st.subheader(':violet[Upload extracted to Database]')
        if st.button('Upload data'):
            upload_database(f'{file_name}')
            st.success('Data uploaded to Database successfully!', icon="✅")
# --------------------------------------------getting data from database and storing in df variable---------------------------------------
df = show_database()

# MODIFY MENU    
if selected == "Modify":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT Name FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select Name, Designation, Company_name, Address, Contact_number,Mail_id,Website_link,Image from card_data WHERE Name=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input("Company_Name", result[0])
            name = st.text_input("Name", result[1])
            designation = st.text_input("Designation", result[2])
            phone_no = st.text_input("Contact_number", result[3])
            email = st.text_input("Mail_id", result[4])
            link = st.text_input("Website_link", result[5])
            address = st.text_input("Address", result[6])
            

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_data SET company_name=%s,Name=%s,designation=%s,Contact_number=%s,Mail_id=%s,Website_link=%s,Address=%s
                                    WHERE Name=%s""", (company_name,name,designation,phone_no,email,link,address,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT Name FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE Name='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
                st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("select Name, Designation, Company_name, Address, Contact_number,Mail_id,Website_link,Image from card_data")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Name", "Designation", "Company_name", "Address", "Contact_number","Mail_id","Website_link","Image"])
        st.write(updated_df)
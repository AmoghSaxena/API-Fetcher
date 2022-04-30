import streamlit as st
import os
import csv
import time
import subprocess
import streamlit as st
import pandas as pd
from contextlib import contextmanager, redirect_stdout
from io import StringIO

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
	page_title=None,  # String or None. Strings get appended with "• Streamlit".
	page_icon=None,  # String, anything supported by st.image, or None.
)
hide_streamlit_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("CASADIGI")


def run_and_display_stdout(command_args):
    df = pd.DataFrame({"Code Logs!": []})
    element = st.dataframe(df)
    result = subprocess.Popen(command_args, stdout=subprocess.PIPE)
    for line in iter(lambda: result.stdout.readline(), b""):
        element.add_rows({"text": [line.decode("utf-8")]})


shout = False
IP_DVC = 1

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


def auto_column_sort(column_number, row_data):
    if column_number == 1:
        column = column1
    elif column_number == 2:
        column = column2
    elif column_number == 3:
        column = column3
    elif column_number == 4:
        column = column4
    elif column_number == 5:
        column = column5

    with column:
        expander = st.expander(f" CONTROLLER: {row_data[1]}")
        expander.image("controller.png")
        expander.write({'MAC ADDRESS': row_data[0], 'IP ADDRESS': row_data[1]})
        expander.write("""Fill the data below if you want to run the Ansible job""")
        if expander.checkbox(f"Install For {row_data[1]}"):
            global shout
            shout = True
            global IP_DVC
            IP_DVC = row_data[1]


def login_check():
    menu = ["Login"]
    choice = st.sidebar.selectbox("Menu", menu)
    print(choice)
    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        print(username, password)
        if st.sidebar.checkbox("Login"):
            if username == "admin" and password == "admin":
                st.sidebar.success("Logged In as {}".format(username))
                return True
            else:
                st.sidebar.warning("Invalid username/password")
                return False


column_count = 1


output = st.empty()

### Login CHeck ###

if login_check() == True:
    if st.checkbox("Show Controllers"):
        if st.button(f'Refresh Page'):
            with st.spinner('Wait for it...'):
                time.sleep(2)
                st.legacy_caching.clear_cache()
                st.experimental_rerun()
            st.success('Done!')
        column1, column2, column3, column4, column5 = st.columns(5)
        with open('dvcsetups.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != 'MAC':
                    # st.write(column_count)
                    # st.write(row)
                    auto_column_sort(column_count, row)
                    # st.write(row)
                    column_count = 1 if column_count == 5 else (column_count + 1)

    if shout:
        st.header(f"Provide the Details for {IP_DVC}")
        CLOUD_URL = st.text_input("Cloud URL")
        CLOUD_IP = st.text_input("Cloud IP")
        CASA_VER = st.text_input("Casadigi Version")
        if st.button('Install'):
            st.write('INSTALLING')
            run_and_display_stdout(["/usr/local/bin/casadigi-provisioning.sh", IP_DVC, CASA_VER, CLOUD_URL, CLOUD_IP])
            st.info("Executed!")

        else:
            st.write('IDLE')

import csv
import time
import json
import hashlib
import subprocess
import pandas as pd
import streamlit as st
from io import StringIO
from contextlib import contextmanager, redirect_stdout


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
with open("creds.json", "r") as f:
    conf = json.load(f)
creds_read = conf



####### PROGRAM STARTS HERE #######
st.title("CASADIGI")


def run_and_display_stdout(command_args):
    df = pd.DataFrame({"Code Logs!": []})
    element = st.dataframe(df)
    result = subprocess.Popen(command_args, stdout=subprocess.PIPE)
    for line in iter(lambda: result.stdout.readline(), b""):
        element.add_rows({"text": [line.decode("utf-8")]})


shout = False
IP_DVC = 1
show_tiles = True


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
    with column:
        st.write(f" CONTROLLER: {row_data[1]}")
        st.image("controller.png")
        st.write({'Application Id': row_data[0], 'IP ADDRESS': row_data[1]})
        st.write("""Fill the data below if you want to run the Ansible job""")
        if st.checkbox(f"Install For {row_data[1]}"):
            global shout
            shout = True
            global IP_DVC
            IP_DVC = row_data[1]
            global show_tiles
            show_tiles = False


def login_check():
    menu = ["Login"]
    choice = st.sidebar.selectbox("Menu", menu)
    print(choice)
    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        login_password = hashlib.md5()
        user = hashlib.md5()
        login_password.update(password.encode('utf-8'))
        user.update(username.encode('utf-8'))
        print(username, password)
        if st.sidebar.checkbox("Login"):
            print(user.hexdigest())
            print(login_password.hexdigest())
            if user.hexdigest() == creds_read['login_user'] and login_password.hexdigest() == creds_read['login_password']:
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
        if st.button(f'Refresh Page', key='c'):
            with st.spinner('Wait for it...'):
                time.sleep(2)
                st.legacy_caching.clear_cache()
                st.experimental_rerun()
            st.success('Done!')
        column1, column2, column3, column4 = st.columns(4)
        if show_tiles:
            with open('dvcsetups.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] != 'MAC':
                        auto_column_sort(column_count, row)
                        column_count = 1 if column_count == 4 else (column_count + 1)

    if shout:
        st.header(f"Provide the Details for {IP_DVC}")
        CLOUD_URL = st.text_input("Cloud URL")
        CLOUD_IP = st.text_input("Cloud IP")
        CASA_VER = st.text_input("Casadigi Version")
        if st.button('Install', key='e'):
            st.write('INSTALLING')
            my_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1)
            run_and_display_stdout(["/usr/local/bin/casadigi-provisioning.sh", IP_DVC, CASA_VER, CLOUD_URL, CLOUD_IP])
            st.info("Executed!")


        else:
            st.write('IDLE')
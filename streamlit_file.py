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
            footer {visibility: hidden;}
            </style>
            """
#MainMenu {visibility: hidden;}
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


column = 0
column_count = 1
Install_IP = False
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
st.code("""
# TO SEND THE DATA
curl --location --request POST 'http://192.168.3.11:4011/dvc?MAC={MAC_ADDRESS}&IP={IP_ADDRESS}'

# TO GET THE WHOLE LIST OF DATA
curl --location --request GET 'http://192.168.3.11:4011/dvc'

# TO DELETE THE DATA RECORD
curl --location --request DELETE 'http://192.168.3.11:4011/dvc?IP={IP_ADDRESS}'
""",language='bash')

if st.button(f'Refresh Page'):
    with st.spinner('Wait for it...'):
        time.sleep(2)
        st.legacy_caching.clear_cache()
        st.experimental_rerun()
    st.success('Done!')

def run_and_display_stdout(command_args):
    df = pd.DataFrame({"Code Logs!": []})
    element = st.dataframe(df)
    result = subprocess.Popen(command_args, stdout=subprocess.PIPE)
    for line in iter(lambda: result.stdout.readline(), b""):
        element.add_rows({"text": [line.decode("utf-8")]})

column1, column2, column3, column4, column5 = st.columns(5)

output = st.empty()
def auto_column_sort(column_number,row_data):
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
        expander.write({'MAC ADDRESS' : row_data[0], 'IP ADDRESS' : row_data[1]})
        expander.write("""Fill the data below if you want to run the Ansible job""")

with open('dvcsetups.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] != 'MAC':
            auto_column_sort(column_count, row)
            # st.write(row)
            column_count = 1 if column_count == 5 else (column_count + 1)

if True:
    st.text_input("Controller IP")
    st.text_input("Cloud URL")
    st.text_input("Cloud IP")
    command = st.text_input("Casadigi Version")
    if st.button('Install'):
        st.write('INSTALLING')
        run_and_display_stdout(["ping", "8.8.8.8", "-c", "5"])
        st.info("Executed!")

    else:
        st.write('IDLE')

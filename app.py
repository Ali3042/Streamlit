import streamlit as st
from streamlit.runtime.state import session_state
import graphs
from classes import digitalBuilds, Block
from DBController import DBController, Data
    
def generate_selections_dict(broker, sub_class, country, coverage, LoB):
    selections = {}
    if broker:
        selections['Name'] = broker
    if sub_class:
        selections['SubClass'] = sub_class
    if country:
        selections['Policys.Jurisdiction'] = country
    if coverage:
        selections['Coverage'] = coverage
    if LoB:
        selections['LineOfBusiness'] = LoB
    return selections

def filterBar():
    data = Data(dbc)
    col0, col1, col2, col3, col4 = st.columns(5)
        
    # Multi-select boxes with dynamic options from Data function
    with col0:
        LoB = st.multiselect("Line Of Business", data.lineOfBusinessList)
    with col1:
        broker = st.multiselect("Broker", data.brokerList)
    with col3:
        sub_class = st.multiselect("Sub-class", data.subClassList)
    with col2:
        country = st.multiselect("Country", data.jurisdictionList)
    with col4:
        coverage = st.multiselect("Coverage", data.coverageList)
           
    if st.session_state.selections != generate_selections_dict(broker, sub_class, country, coverage, LoB):
        st.session_state.selections = generate_selections_dict(broker, sub_class, country, coverage, LoB)
        st.rerun()

dbc = DBController('database.db')  

# Presumed existing graph functions
graph_functions = [
    graphs.show_graph_1, graphs.show_graph_2, graphs.show_graph_3, 
    graphs.show_graph_4, graphs.show_graph_5, graphs.show_graph_6, 
    graphs.show_graph_7, graphs.show_graph_8, graphs.show_graph_9
]
    
# Function to switch to the internal factors page
def switch_to_internal_factors():
    st.session_state['page'] = 'internal'
    st.rerun()

# Function to switch back to the external factors page
def switch_to_external_factors():
    st.session_state['page'] = 'external'
    st.rerun()

if 'selections' not in st.session_state:
    st.session_state['selections'] = {} 


# Initialize the page state if it doesn't exist
if 'page' not in st.session_state:
    st.session_state['page'] = 'external'
   

if 'basket' not in st.session_state:
    st.session_state.basket = digitalBuilds()   

# Check which page to display
if st.session_state['page'] == 'internal':
    st.set_page_config(page_title='Portfolio Management a Digital Twin', layout='wide') 
    data = Data(dbc)

    st.title("Internal Factors Dashboard")
    # Main content after a top button is clicked
    if True:
        filterBar()
   
        # Expander for switching views
        st.sidebar.image('logo.png', width=80)
        external_factors_button = st.sidebar.button(' External Factors :arrow_left:')
        if external_factors_button:
            switch_to_external_factors()

        # Display all graphs
        for i in range(0, 6, 2):
            cols = st.columns(2)
            with cols[0]:
                graph_functions[i]()
            with cols[1]:
                graph_functions[i + 1]()
        
    
        # Streamlit code for the dropdown menus and inputs
        metric = st.sidebar.selectbox(
            'Select Metric:',
            ('Rate Adequacy', 'RARC', 'Sub to Quote', 'Aggregate Exposure Limit')
        )
    
        value = st.sidebar.slider("Select Modifier:", min_value=-10.0, max_value=10.0, value=0.0, step=0.01, format='%f%%')

        if 'button_clicked' not in st.session_state:
            st.session_state.button_clicked = False

        # Button logic
        if st.sidebar.button('Add➕') and not st.session_state.button_clicked:
            st.session_state.button_clicked = True
            st.session_state.basket.add(Block(st.session_state.selections, metric, value))
            st.toast("Graphs updated.")
            st.rerun()

        # Reset the button click tracker after handling the button action
        if st.session_state.button_clicked:
            st.session_state.button_clicked = False

        # Display the generated sentences as selectable options
        st.sidebar.header("Your Basket:")
        for block in st.session_state.basket.get:
            # Create two columns: one for the button, one for the sentence
            col1, col2 = st.sidebar.columns([1, 4])  # Adjust the ratio as needed

            with col1:
                if st.button("❌", key=block.list):
                    st.session_state.basket.remove(block)
                    st.toast("Graphs updated.")
                    st.rerun()
        
            with col2:
                st.write(block.list) 
 

else:
    st.set_page_config(page_title='Portfolio Management Digital Twin', layout='wide')
    
    st.title("External Factors Dashboard")
    
    filterBar()

    # Sidebar for external factors
    st.sidebar.image('logo.png', width=80)
    internal_factors_button = st.sidebar.button('Internal Factors :arrow_right:')
    
    st.session_state['interest'] = st.sidebar.slider("Interest Rates", min_value=0.0, max_value=10.0, value=5.25, step=0.01, format='%f%%')
    st.session_state['inflation'] = st.sidebar.slider("Claims Inflation", min_value=0.0, max_value=10.0, value=4.60, step=0.01, format='%f%%')
    st.session_state['marketRARC'] = st.sidebar.slider("Market RARC", min_value=-10.0, max_value=10.0, value=0.0, step=0.01, format='%f%%')
    st.session_state['subVolumes'] = st.sidebar.slider("Sub Volumes", min_value=0.0, max_value=100.0, value=50.0, step=0.1, format='%f%%')
    st.session_state['retention'] = st.sidebar.slider("Retention Rate", min_value=0.0, max_value=100.0, value=70.0, step=0.1, format='%f%%')

    if internal_factors_button:
        switch_to_internal_factors()

    # Display all graphs
    for i in range(0, 8, 2):
        cols = st.columns(2)
        with cols[0]:
            graph_functions[i]()
        with cols[1]:
            graph_functions[i + 1]()
    
    # Display the 9th graph in its own row
    graph_functions[8]()
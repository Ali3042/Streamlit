import streamlit as st
from DBController import DBController, Graph, Data
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dicts import coords, maxEpo
import pydeck as pdk


coefficients = {
    # Coefficients for the impact of interest rate changes
    'interest': {
        'GWP': -0.015, # For each 1% decrease in interest rates, GWP decreases by 1.5%.
        'retention': 0.005, # For each 1% decrease in interest rates, retention increases by 0.5%.
        'hit': -0.01, # For each 1% decrease in interest rates, hit ratio decreases by 1%.
        'adequacy': 0.015, # For each 1% decrease in interest rates, rate adequacy increases by 1.5%.
        'ELR': 0.005, # For each 1% decrease in interest rates, ELR increases by 0.5%.
        'RARC': -0.01 # For each 1% decrease in interest rates, RARC decreases by 1%.
    },
    # Coefficients for the impact of retention rate changes
    'retention_rate': {
        'GWP': 0.006, # For each 1% increase in retention rates, GWP increases by 0.6%.
        'retention': 0.002, # For each 1% increase in retention rates, the value of retaining customers increases by 0.2%.
        'hit': 0.005, # For each 1% increase in retention rates, hit ratio increases by 0.5%.
        'adequacy': 0.01, # For each 1% increase in retention rates, rate adequacy increases by 1%.
        'ELR': 0.006, # For each 1% increase in retention rates, ELR increases by 0.6%.
        'RARC': 0.005 # For each 1% increase in retention rates, RARC increases by 0.5%.
    },
    # Coefficients for the impact of inflation rate changes
    'inflation': {
        'GWP': 0.03, # For each 1% increase in inflation, GWP increases by 3%.
        'retention': 0.01, # For each 1% increase in inflation, the value of retaining customers increases by 1%.
        'hit': -0.02, # For each 1% increase in inflation, hit ratio decreases by 2%.
        'adequacy': 0.03, # For each 1% increase in inflation, rate adequacy increases by 3%.
        'ELR': 0.02, # For each 1% increase in inflation, ELR increases by 2%.
        'RARC': -0.015 # For each 1% increase in inflation, RARC decreases by 1.5%.
    },
    # Coefficients for the impact of rate adequacy changes
    'rate_adequacy': {
        'GWP': 0.10, # For each 1% increase in rate adequacy, GWP increases by 10%.
        'retention': 0.02, # For each 1% increase in rate adequacy, the value of retaining customers increases by 2%.
        'hit': -0.015, # For each 1% increase in rate adequacy, hit ratio decreases by 1.5%.
        'adequacy': -0.10, # For each 1% increase in rate adequacy, rate adequacy itself decreases by 10% (counteracting effect).
        'ELR': 0.01, # For each 1% increase in rate adequacy, ELR increases by 1%.
        'RARC': 0.02 # For each 1% increase in rate adequacy, RARC increases by 2%.
    },
    # Coefficients for the impact of submission-to-quote rate changes
    'sub_to_quote': {
        'GWP': -0.006, # For each 10% decrease in sub-to-quote rates, GWP decreases by 6%.
        'retention': -0.005, # For each 10% decrease in sub-to-quote rates, the value of retaining customers decreases by 5%.
        'hit': -0.005, # For each 10% decrease in sub-to-quote rates, hit ratio decreases by 5%.
        'adequacy': 0.003, # For each 10% decrease in sub-to-quote rates, rate adequacy increases by 3%.
        'ELR': -0.003, # For each 10% decrease in sub-to-quote rates, ELR decreases by 3%.
        'RARC': 0.003 # For each 10% decrease in sub-to-quote rates, RARC increases by 3%.
    },
    "Price": {
        "GWP": 0.0065,  # Higher prices might lead to lower GWP due to reduced customer acquisition.
        "retention": -0.006,  # Higher prices could decrease retention rate as customers seek cheaper options.
        "hit": -0.005,  # Higher prices might reduce hit ratio due to lower customer acquisition rates.
        "adequacy": 0.007,  # Higher prices typically indicate better rate adequacy.
        "ELR": -0.004,  # Price increases could lead to a lower ELR if the premium increase is higher than the increase in expected losses.
        "RARC": 0.005   # High prices could improve RARC by leading to better margins.
    },
    "Risk Appetite": {
        "GWP": 0.006,  # A higher risk appetite can increase GWP as more policies are underwritten.
        "retention": 0,   # Risk appetite might not have a direct impact on retention rates.
        "hit": 0.004,  # A higher risk appetite can improve the hit ratio by accepting more proposals.
        "adequacy": -0.004,  # Higher risk appetite could decrease rate adequacy if not managed properly.
        "ELR": 0.005,  # Increased risk appetite could potentially increase the ELR.
        "RARC": 0    # Risk appetite might increase RARC if it leads to more profitable underwriting, but it could also decrease it if risks are not properly priced.
    },
    "ELR": {
        "GWP": 0,    # ELR itself might not directly influence GWP.
        "retention": -0.003,  # Higher ELR could indicate less profitable policies, potentially reducing retention rates.
        "hit": 0,    # ELR might not directly affect the hit ratio.
        "adequacy": -0.008,  # Higher ELR indicates lower rate adequacy.
        "ELR": 0.01,    # This is the same metric, so the effect is direct.
        "RARC": -0.007  # Higher ELR typically reduces RARC.
    }

}


def processGWP(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['GWP'] * count))
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['GWP'] * count * (Data(dbc).calcPerc(block.filters)))
            count += 1
               
    return data

def processRetention(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['retention'] * count))  
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['retention'] * count * Data(dbc).calcPerc(block.filters))
            count += 1
               
    return data

def processHits(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['hit'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['hit'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['hit'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['hit'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['hit'] * count))    
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['hit'] * count * Data(dbc).calcPerc(block.filters))
            count += 1
               
    return data

def processAdequacy(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['adequacy'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['adequacy'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['adequacy'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['adequacy'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['adequacy'] * count))    
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['adequacy'] * count * Data(dbc).calcPerc(block.filters))
            
    return data

def processELR(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['ELR'] * count))    
        count += 1

    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['ELR'] * count * Data(dbc).calcPerc(block.filters))
            
    return data

def processRARC(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 60) * coefficients['retention_rate']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.rateAdequacy) * coefficients['rate_adequacy']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.subToQuote - 70) * coefficients['sub_to_quote']['RARC'] * count))    
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['RARC'] * count * Data(dbc).calcPerc(block.filters))
    return data



# Placeholder functions for each graph
def show_graph_1():
    DBC = DBController("database.db")
    data = Graph(DBC).GWP(st.session_state.selections)
    
    future = processGWP(data['pred'], DBC)

    # Create a figure with a secondary y-axis for the line chart
    fig = make_subplots()

    # Add cumulative GWP values as bars
    fig.add_trace(
        go.Bar(x=list(data['cul'].keys()), y=list(data['cul'].values()), name='Cumulative GWP', marker_color='#e0301e'),
        
    )    

    fig.add_trace(
        go.Bar(x=list(data['acc'].keys()), y=list(data['acc'].values()), name='Actual GWP', marker_color='#eb8c00'),
    )

    fig.add_trace(
        go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), name='Target GWP', mode='lines', line=dict(color='#602320')),
        
    )    
    
    

    #Add forecasted GWP values as a line
    fig.add_trace(
        go.Scatter(x=list(future.keys()), y=list(future.values()), name='Projected GWP', mode='lines+markers', line=dict(color='#000000'), marker=dict(color='#000000')),
    )


    # Customize the layout
    fig.update_layout(
        title_text="GWP Actual vs Forecast",
        xaxis_title="Year",
        yaxis_title="Actual GWP",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
        barmode='overlay'
    )

    # Customize axes
    fig.update_xaxes(title_text="Year")

    # Set custom y-axis range based on the data scale
    fig.update_yaxes(title_text="GWP ($)", secondary_y=False)

    # Display the figure
    st.plotly_chart(fig)



def show_graph_2():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Business Type data from the database
    data = Graph(DBC).BusinessType(st.session_state.selections)
    
    future = processRetention(data['pred'], DBC)
    
    # Create a figure with secondary_y=True to allow for a secondary y-axis for the line chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])

     # Add year-on-year bars for renewing (continued) policies
    fig.add_trace(
        go.Bar(x=list(data['cont'].keys()), y=list(data['cont'].values()), name='Renewing Policies', marker_color='#a32020'),
        secondary_y=False,
    )
    # Add year-on-year bars for new policies
    fig.add_trace(
        go.Bar(x=list(data['new'].keys()), y=list(data['new'].values()), name='New Policies', marker_color='#eb8c00'),
        secondary_y=False,
    )

    # Add a line for the retention rate
    
    fig.add_trace(
        go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), name='Target Retention', mode='lines', line=dict(color='#602320')),
        secondary_y=True,
    )
    
    fig.add_trace(
        go.Scatter(x=list(future.keys()), y=list(future.values()), name='Projected Retention', mode='lines+markers', line=dict(color='#000000'), marker=dict(color='#000000')),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=list(data['ret'].keys()), y=list(data['ret'].values()), name='Retention Rate', mode='lines+markers', line=dict(color='#e0301e'), marker=dict(color='#e0301e')),
        secondary_y=True,
    )
    
   

    # Customize the layout
    fig.update_layout(
        title_text="Business Type split",
        xaxis_title="Year",
        yaxis_title="Number of Policies",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
        barmode='stack',
    )

    # Customize axes
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Number of Policies", secondary_y=False)
    fig.update_yaxes(title_text="Retention Rate", range=[0, 100], secondary_y=True)


    # Display the figure
    st.plotly_chart(fig)


def show_graph_3():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Hit Ratio data from the database
    data = Graph(DBC).HitRate(st.session_state.selections)
    
    qfuture = processHits(data['qpred'], DBC)
    bfuture = processHits(data['bpred'], DBC)
    sfuture = processHits(data['spred'], DBC)

    # Create a line chart for hit ratios
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(
        go.Scatter(x=list(bfuture.keys()), y=list(bfuture.values()), mode='lines+markers', name='Projected QtB', line=dict(color='black'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(qfuture.keys()), y=list(qfuture.values()), mode='lines+markers', name='Projected StQ', line=dict(color='black'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(sfuture.keys()), y=list(sfuture.values()), mode='lines+markers', name='Projected StB', line=dict(color='black'))
    )

    # Add a line for the measure of the number of inquiries that make it to a quote
    fig.add_trace(
        go.Scatter(x=list(data['subQuote'].keys()), y=list(data['subQuote'].values()), mode='lines+markers', name='Sub to Quote', line=dict(color='#eb8c00'), marker=dict(color='#eb8c00'))
    )

    # Add a line for the measure of bound policies divided by quoted policies
    fig.add_trace(
        go.Scatter(x=list(data['quoteBound'].keys()), y=list(data['quoteBound'].values()), mode='lines+markers', name='Quote to Bind', line=dict(color='#e0301e'), marker=dict(color='#e0301e'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(data['subBound'].keys()), y=list(data['subBound'].values()), mode='lines+markers', name='Sub to Bind', line=dict(color='orange'), marker=dict(color='orange'))
    )


    #fig.add_trace(
    #    go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), mode='lines+markers', name='Target hit rate', line=dict(color='black'), marker=dict(color='black'))
    #)

    # Customize the layout
    fig.update_layout(
        title_text="Hit Ratio",
        xaxis_title="Year",
        yaxis_title="Hit Ratio (%)",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple")
    )

    fig.update_yaxes(title_text="Hit Ratio (%)", range=[0, 100], secondary_y=False)
    
    # Display the figure
    st.plotly_chart(fig)

def show_graph_4():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the ELR data from the database
    data = Graph(DBC).ELR(st.session_state.selections)
    
    future = processELR(data['pred'], DBC)

    # Create a figure with a secondary y-axis for the moving average
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add ELR actual values as bars (orange color)
    fig.add_trace(
        go.Bar(x=list(data['acc'].keys()), y=list(data['acc'].values()), name='Actual ELR', marker_color='#eb8c00'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), name='Target ELR', mode='lines', line=dict(color='#602320')),
    )

    # Add moving average line (green color)
    fig.add_trace(
        go.Scatter(x=list(data['cul'].keys()), y=list(data['cul'].values()), name='Moving Average', mode='lines+markers', line=dict(color='red')),
    )
    
    fig.add_trace(
        go.Scatter(x=list(future.keys()), y=list(future.values()), mode='lines+markers', name='Prejected hit rate', line=dict(color='black'), marker=dict(color='black'))
    )

    # Customize the layout
    fig.update_layout(
        title_text="ELR with Moving Average",
        xaxis_title="Date",
        yaxis_title="ELR",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        barmode = "stack",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    # Customize axes
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="ELR", secondary_y=False)

    # Display the figure
    st.plotly_chart(fig)

def show_graph_5():
        # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Hit Ratio data from the database
    data = Graph(DBC).RateAdequecy(st.session_state.selections)
    future = processAdequacy(data['pred'], DBC)
    
    # Create a line chart for hit ratios
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add a line for the measure of the number of inquiries that make it to a quote
    fig.add_trace(
        go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), mode='lines', name='Target rate', line=dict(color='#602320'))
    )

    # Add a line for the measure of bound policies divided by quoted policies
    fig.add_trace(
        go.Scatter(x=list(data['acc'].keys()), y=list(data['acc'].values()), mode='lines+markers', name='Actual rate', line=dict(color='#eb8c00'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(data['cul'].keys()), y=list(data['cul'].values()), mode='lines+markers', name='Rolling Average', line=dict(color='red'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(future.keys()), y=list(future.values()), mode='lines+markers', name='Projected Rate', line=dict(color='black'))
    )


    # Customize the layout
    fig.update_layout(
        title_text="Rate Adequecy",
        xaxis_title="Year",
        yaxis_title="Rate Ratio (%)",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple")
    )
    
    fig.update_yaxes(secondary_y=False)

    # Display the figure
    st.plotly_chart(fig)

def show_graph_6():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Hit Ratio data from the database
    data = Graph(DBC).RARC
    
    future = processRARC(data['pred'], DBC)
    
    # Create a line chart for hit ratios
    fig = go.Figure()

    # Add a line for the measure of the number of inquiries that make it to a quote
    fig.add_trace(
        go.Scatter(x=list(data['aim'].keys()), y=list(data['aim'].values()), mode='lines+markers', name='Target RARC', line=dict(color='#602320'))
    )

    # Add a line for the measure of bound policies divided by quoted policies
    fig.add_trace(
        go.Scatter(x=list(data['acc'].keys()), y=list(data['acc'].values()), mode='lines+markers', name='Actual RARC', line=dict(color='#eb8c00'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(future.keys()), y=list(future.values()), mode='lines+markers', name='Projected RARC', line=dict(color='black'), marker=dict(color='black'))
    )

    # Customize the layout
    fig.update_layout(
        title_text="RARC",
        xaxis_title="Year",
        yaxis_title="RARC",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple")
    )

    # Display the figure
    st.plotly_chart(fig)

def show_graph_7():
    DBC = DBController("database.db")

    # Get the Business Type data from the database
    data = Graph(DBC).SubVolumeByBroker

    # Create a figure
    fig = go.Figure()

    # Add horizontal bars for bound policies
    fig.add_trace(
        go.Bar(y=list(data['bound'].keys()), x=list(data['bound'].values()), name='Bound Policies', marker_color='#eb8c00', orientation='h'),
    )

    # Add horizontal bars for submitted policies
    fig.add_trace(
        go.Bar(y=list(data['sub'].keys()), x=list(data['sub'].values()), name='Submitted Policies', marker_color='#a32020', orientation='h'),
    )

    # Customize the layout
    fig.update_layout(
        title_text="Sub Volume by Broker",
        yaxis_title="Broker",
        xaxis_title="% of Policies",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
        barmode='stack'
    )

    # Customize axes
    fig.update_xaxes(title_text="Percentage of Polocies")
    fig.update_yaxes(title_text="Broker")

    # Display the figure
    st.plotly_chart(fig)

def show_graph_8():
    DBC = DBController("database.db")

    # Get the Business Type data from the database
    data = Graph(DBC).GWPByBroker

    # Create a figure
    fig = go.Figure()

    # Add horizontal bars for bound policies
    fig.add_trace(
        go.Bar(y=list(data.keys()), x=list(data.values()), name='Bound Policies', marker_color='#eb8c00', orientation='h'),
    )


    # Customize the layout
    fig.update_layout(
        title_text="GWP by broker",
        yaxis_title="Broker",
        xaxis_title="% of GWP",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    # Customize axes
    fig.update_xaxes(title_text="Percentage of GWP")
    fig.update_yaxes(title_text="Broker")

    # Display the figure
    st.plotly_chart(fig)

def show_graph_9():
    DBC = DBController("database.db")
    data = Graph(DBC).ExposureMap

    chart_data = []
    for i in list(data.keys()):
        coord = coords[i]
        exposure = data[i]/1000

        # Determine the color based on exposure
        if exposure > maxEpo[i]/1000:
            color = [255, 0, 0, 160]    # Red for overexposed
        else:
            color = [0, 255, 0, 160]  # Green for others

        chart_data.append([coord[0], coord[1], exposure, color])

    chart_data = pd.DataFrame(chart_data, columns=['lon', 'lat', 'limit', 'color'])


    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1,
            pitch=20,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=chart_data,
                get_position='[lat, lon]',
                get_color='color',
                get_radius=['limit'],
            ),
        ],
    ))
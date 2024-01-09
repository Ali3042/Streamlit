import streamlit as st
from DBController import DBController, Graph, Data
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dicts import coords, maxEpo
import pydeck as pdk

month_map = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}

coefficients = {
    'interest': {
        'GWP': 0.01,
        'retention': -0.005,
        'sub': 0.002,
        'ELR': 0.003,
        'rate': -0.01,
        'RARC': 0.015
    },
    'inflation': {
        'GWP': -0.02,
        'retention': 0.0,
        'sub': -0.005,
        'ELR': 0.02,
        'rate': -0.015,
        'RARC': 0.01
    },
    'marketRARC': {
        'GWP': 0.015,
        'retention': 0.01,
        'sub': 0.008,
        'ELR': -0.01,
        'rate': 0.02,
        'RARC': 0.025
    },
    'subVolumes': {
        'GWP': 0.003,
        'retention': 0.002,
        'sub': 0.0015,
        'ELR': -0.0005,
        'rate': 0.001,
        'RARC': -0.001
    },
    'retention': {
        'GWP': 0.0025,
        'retention': 0.0035,
        'sub': 0.001,
        'ELR': -0.001,
        'rate': 0.0005,
        'RARC': -0.0005
    },
    'Rate Adequacy': {
        'GWP': -0.01,
        'retention': 0.005,
        'sub': 0.01,
        'ELR': -0.015,
        'rate': 0.03,
        'RARC': 0.02
    },
    'RARC': {
        'GWP': 0.005,
        'retention': -0.01,
        'sub': 0.02,
        'ELR': 0.015,
        'rate': -0.02,
        'RARC': 0.03
    },
    'Sub to Quote': {
        'GWP': 0.01,
        'retention': 0.005,
        'sub': -0.005,
        'ELR': 0.02,
        'rate': -0.01,
        'RARC': 0.015
    },
    'Aggregate Exposure Limit': {
        'GWP': -0.005,
        'retention': 0.01,
        'sub': 0.005,
        'ELR': -0.02,
        'rate': 0.015,
        'RARC': 0.01
    }
}



def processGWP(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['GWP'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['GWP'] * count))
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
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['retention'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['retention'] * count))
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
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['sub'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['sub'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['sub'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['sub'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['sub'] * count))
        count += 1
        
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['sub'] * count * Data(dbc).calcPerc(block.filters))
            count += 1
               
    return data

def processAdequacy(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['rate'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['rate'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['rate'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['rate'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['rate'] * count))
        count += 1
    
    count = 0
    for block in st.session_state.basket.get: 
        count = 0  
        for i in data:
            data[i] = data[i] \
              + data[i] * (block.value * coefficients[block.metric]['rate'] * count * Data(dbc).calcPerc(block.filters))
            
    return data

def processELR(rawData, dbc):
    data = {}
    count = 0
    for i in rawData:
        data[i] = rawData[i] \
         + (rawData[i] * ((st.session_state.interest - 5.25) * coefficients['interest']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['ELR'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['ELR'] * count))
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
         + (rawData[i] * ((st.session_state.retention - 70) * coefficients['retention']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.marketRARC) * coefficients['marketRARC']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.subVolumes - 50) * coefficients['subVolumes']['RARC'] * count)) \
         + (rawData[i] * ((st.session_state.inflation - 4.6) * coefficients['inflation']['RARC'] * count))
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
        go.Bar(x=list(map(lambda key: key.split('-')[1], data['cul'].keys())), y=list(data['cul'].values()), name='Cumulative GWP', marker_color='#e0301e'),
        
    )    

    fig.add_trace(
        go.Bar(x=list(map(lambda key: key.split('-')[1], data['acc'].keys())), y=list(data['acc'].values()), name='Monthly Bound GWP', marker_color='#eb8c00'),
    )

    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), name='Target GWP', mode='lines', line=dict(color='#602320')),
        
    )    
    
    
    #Add forecasted GWP values as a line
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],future.keys())), y=list(future.values()), name='Projected GWP', mode='lines+markers', line=dict(color='#000000'), marker=dict(color='#000000')),
    )


    # Customize the layout
    fig.update_layout(
        title_text="Gross Written Premium",
        xaxis_title="Year",
        yaxis_title="Actual GWP",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
        barmode='overlay'
    )

    # Customize axes
    fig.update_xaxes(title_text=list(data['acc'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))

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
        go.Bar(x=list(map(lambda key: key.split('-')[1],data['cont'].keys())), y=list(data['cont'].values()), name='Renewal Business', marker_color='#a32020'),
        secondary_y=False,
    )
    # Add year-on-year bars for new policies
    fig.add_trace(
        go.Bar(x=list(map(lambda key: key.split('-')[1],data['new'].keys())), y=list(data['new'].values()), name='New Business', marker_color='#eb8c00'),
        secondary_y=False,
    )

    # Add a line for the retention rate
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), name='Target Retention', mode='lines', line=dict(color='#602320')),
        secondary_y=True,
    )
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],future.keys())), y=list(future.values()), name='Projected Retention', mode='lines+markers', line=dict(color='#000000'), marker=dict(color='#000000')),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['ret'].keys())), y=list(data['ret'].values()), name='Retention Rate', mode='lines+markers', line=dict(color='#e0301e'), marker=dict(color='#e0301e')),
        secondary_y=True,
    )
    
   

    # Customize the layout
    fig.update_layout(
        title_text="Business Type Split",
        xaxis_title="Year",
        yaxis_title="GWP ($)",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
        barmode='stack',
    )

    # Customize axes
    fig.update_xaxes(title_text=list(data['new'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))
    fig.update_yaxes(title_text="Number of Policies", secondary_y=False)
    fig.update_yaxes(title_text="Retention Rate", range=[0, 100], secondary_y=True)


    # Display the figure
    st.plotly_chart(fig)


def show_graph_3():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Hit Ratio data from the database
    data = Graph(DBC).HitRate(st.session_state.selections)
    
    #qfuture = processHits(data['qpred'], DBC)
    #bfuture = processHits(data['bpred'], DBC)
    sfuture = processHits(data['spred'], DBC)

    # Create a line chart for hit ratios
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), mode='lines', name='Target Sub to Bind', line=dict(color='#602320'))
    )

    #fig.add_trace(
    #    go.Scatter(x=list(bfuture.keys()), y=list(bfuture.values()), mode='lines+markers', name='Projected QtB', line=dict(color='black'))
    #)
    
    #fig.add_trace(
    #    go.Scatter(x=list(qfuture.keys()), y=list(qfuture.values()), mode='lines+markers', name='Projected StQ', line=dict(color='black'))
    #)
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],sfuture.keys())), y=list(sfuture.values()), mode='lines+markers', name='Projected Sub to Bind', line=dict(color='black'))
    )

    # Add a line for the measure of the number of inquiries that make it to a quote
    #fig.add_trace(
    #    go.Scatter(x=list(data['subQuote'].keys()), y=list(data['subQuote'].values()), mode='lines+markers', name='Sub to Quote', line=dict(color='#eb8c00'), marker=dict(color='#eb8c00'))
    #)

    # Add a line for the measure of bound policies divided by quoted policies
    #fig.add_trace(
    #    go.Scatter(x=list(data['quoteBound'].keys()), y=list(data['quoteBound'].values()), mode='lines+markers', name='Quote to Bind', line=dict(color='#e0301e'), marker=dict(color='#e0301e'))
    #)
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['subBound'].keys())), y=list(data['subBound'].values()), mode='lines+markers', name='Sub to Bind', line=dict(color='orange'), marker=dict(color='orange'))
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

    fig.update_yaxes(title_text="Hit Ratio (%)", secondary_y=False)
    fig.update_xaxes(title_text=list(data['subBound'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))
    
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
        go.Bar(x=list(map(lambda key: key.split('-')[1],data['acc'].keys())), y=list(data['acc'].values()), name='Monthly Avg.', marker_color='#eb8c00'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), name='Target ELR', mode='lines', line=dict(color='#602320')),
    )

    # Add moving average line (green color)
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['cul'].keys())), y=list(data['cul'].values()), name='YOA Avg.', mode='lines+markers', line=dict(color='red')),
    )
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],future.keys())), y=list(future.values()), mode='lines+markers', name='Projected Avg.', line=dict(color='black'), marker=dict(color='black'))
    )

    # Customize the layout
    fig.update_layout(
        title_text="ELR",
        xaxis_title="Date",
        yaxis_title="ELR",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        barmode = "stack",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    # Customize axes
    fig.update_xaxes(title_text=list(data['acc'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))
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
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), mode='lines', name='Target Rate Adequacy', line=dict(color='#602320'))
    )

    # Add a line for the measure of bound policies divided by quoted policies
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['acc'].keys())), y=list(data['acc'].values()), mode='lines+markers', name='Monthly Avg.', line=dict(color='#eb8c00'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['cul'].keys())), y=list(data['cul'].values()), mode='lines+markers', name='YOA Avg.', line=dict(color='red'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],future.keys())), y=list(future.values()), mode='lines+markers', name='Projected Avg.', line=dict(color='black'))
    )


    # Customize the layout
    fig.update_layout(
        title_text="Rate Adequacy",
        xaxis_title="Year",
        yaxis_title="Rate Ratio (%)",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple")
    )
    
    fig.update_yaxes(secondary_y=False, range=[-1,1])
    fig.update_xaxes(title_text=list(data['acc'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))

    # Display the figure
    st.plotly_chart(fig)

def show_graph_6():
    # Create a database controller instance
    DBC = DBController("database.db")
    
    # Get the Hit Ratio data from the database
    data = Graph(DBC).RARC(st.session_state.selections)
    
    future = processRARC(data['pred'], DBC)
    
    # Create a line chart for hit ratios
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add a line for the measure of the number of inquiries that make it to a quote
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['aim'].keys())), y=list(data['aim'].values()), mode='lines', name='Target RARC', line=dict(color='#602320'))
    )

    # Add a line for the measure of bound policies divided by quoted policies
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['acc'].keys())), y=list(data['acc'].values()), mode='lines+markers', name='Monthly Avg.', line=dict(color='#eb8c00'))
    )
    
    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],future.keys())), y=list(future.values()), mode='lines+markers', name='Projected Avg.', line=dict(color='black'), marker=dict(color='black'))
    )

    fig.add_trace(
        go.Scatter(x=list(map(lambda key: key.split('-')[1],data['cul'].keys())), y=list(data['cul'].values()), mode='lines+markers', name='YOA Avg.', line=dict(color='red'))
    )    

    # Customize the layout
    fig.update_layout(
        title_text="RARC",
        xaxis_title="Year",
        yaxis_title="RARC (%)",
        legend=dict(orientation='h', y=1.0, x=0.5, xanchor='center', yanchor='bottom'),
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple")
    )
        
    fig.update_xaxes(title_text=list(data['acc'].keys())[0].split("-")[0]+" YOA", tickvals=list(month_map.keys()), ticktext=list(month_map.values()))
    fig.update_yaxes(secondary_y=False, range=[-5,5])
    

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
    fig.update_xaxes(title_text="Percentage of Policies")
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
        exposure = data[i]/10000

        # Determine the color based on exposure
        if exposure > maxEpo[i]/1000:
            color = [173, 27, 2 , 160]    # Red for overexposed
        else:
            color = [243, 190, 38 , 160]  # Green for others

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
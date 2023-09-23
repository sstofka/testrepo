#////////////////
# M3 Dash Lab
# Dash Server and MySQL interface not cooperating 
# I will code this in Visual Studio 22
# //////////////

# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

strDir = "C:\\Users\\steve\\Google Drive\\Education\\Python3Coursera\\Capstone\\"
strFile = "spacex_launch_dash.csv"
strPath = strDir + strFile
#When running online use just strFile
spacex_df = pd.read_csv(strPath)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
payload_range = [min_payload,max_payload]


# Create a dash application
app = dash.Dash(__name__)
# REVIEW1: Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

def getLaunchSites(df):
    #returns a numpy array
    arSites = list(df['Launch Site'].unique())
    return arSites

def getSuccesses(df):
    dfGood = df[df['class'] ==1] #Only successful flights
    dfGroup = dfGood.groupby(['Launch Site'])['class'].count().reset_index()
    return dfGroup   

#for the pie chart that shows success and failure of an individual site
#return an array
def getLaunchPerformance(df, strSite):
    dfSite = df[df['Launch Site'] == strSite]
    dfSuccess = dfSite[dfSite['class']==1]
    nSuccess = dfSuccess['class'].count()
    dfFailure = dfSite[dfSite['class']==0]
    nFailure = dfFailure['class'].count()
    return [nSuccess, nFailure] 

# Dash server is struggling with binary & operator
def getSiteByPayload(df, strSite, nRange):    
    if strSite != "ALL":
        dfSite = df[df['Launch Site'] == strSite]        
        dfPayload = dfSite[dfSite['Payload Mass (kg)'] >= nRange[0]]
        dfPayload = dfPayload[dfPayload['Payload Mass (kg)'] <= nRange[1]]
    else:
        dfPayload = df[df['Payload Mass (kg)'] >= nRange[0]]
        dfPayload = dfPayload[dfPayload['Payload Mass (kg)'] <= nRange[1]]        
    return dfPayload

def getDropdownList(df):
    arOptions = [{'label': 'All Sites', 'value': 'ALL'}]
    arSites = getLaunchSites(df)
    arSiteList = [{'label': i, 'value': i} for i in arSites]
    arOptions.extend(arSiteList)
    return arOptions

# Create an app layout. Avoid code clutter within the html layout
strPlaceholder = 'Select a Launch Site here'
styleDropdown = {'width' : '50%', 'padding': '10px', 'font-size': '20px', 'justify_content': 'center'}
styleH1 = {'textAlign': 'center', 'color': '#503D36','font-size': 40}
styleOuter = {'border': '0.05em solid blue', 'width':'80%',  'display': 'flex', 'justify-content': 'center'}
styleSlider = {'width':'80%', 'padding': '10px', 'display': 'flex',\
   'align-items': 'center','justify-content': 'center'}
             
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard', style= styleH1), #End H1 element
              # TASK 1: Add a dropdown list to enable Launch Site selection
              # The default select value is for ALL sites
              html.Div(id="Outer", style = styleOuter,
              children = [dcc.Dropdown(id='site-dropdown',
                           options= getDropdownList(spacex_df),
                           placeholder = strPlaceholder,
                           #searchable = True,
                           style = styleDropdown,
                           value='ALL'), # End dropdown
              html.Br(), #html break
             
              # TASK 2: Add a pie chart to show the total successful launches count for all sites
              # If a specific launch site was selected, show the Success vs. Failed counts for the site 
              #can't get this to show    
              html.Div(html.Div([], id='success_pie_chart')),             
              html.Br(),]
              ), #End of outer div
              html.Div(id="Outer", style = styleSlider,
                       children = 
                       [html.P("Payload range (Kg):", style = styleH1),
                        html.Br()]), #end children of introduction to slider and outer div

                        # TASK 3: Add a slider to select payload range
                        dcc.RangeSlider(0, 10000, 1000, value= payload_range, id='payload-slider'),
                        #end slider                
                        
                        #Task 4: Add a scatter chart to show the correlation between payload and launch success
                        html.Div(id="Outer", style = styleSlider,
                                 children=
                                 [html.Div([], id='success-payload-scatter-chart') #end of blank Div for callback
                                  ]) #end of children and outer div for chart 
             
              ]) #end children of main div


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success_pie_chart', component_property='children'),
              Input(component_id='site-dropdown', component_property='value'))

#value is the string in the dropdown list
def drawPie(value):
    dfGood = getSuccesses(spacex_df)             
        
    if value == "ALL":
        pie_fig = px.pie(dfGood, values='class',
                            names='Launch Site', title='Successful Landings by Launch Site') 
    else: #individual launch site show success and failure
        arLabels = ["Success", "Failure"]
        arValues = getLaunchPerformance(spacex_df, value)
        pie_fig = go.Figure(data=[go.Pie(labels=arLabels, values=arValues)])
    
    return dcc.Graph(figure=pie_fig)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='children'),
              Input(component_id ='payload-slider', component_property='value'),
              Input(component_id='site-dropdown', component_property='value'))

#Args come into the fxn in the order of the inputs above
def drawScatter(nRange, strSite): #an array of min, max
    strType = type(nRange).__name__
    if strType == "None" or strType == "NoneType":
        nRange = [min_payload, max_payload]
    dfPayload = getSiteByPayload(spacex_df, strSite, nRange)
    scatter_fig = px.scatter(dfPayload, x="Payload Mass (kg)", y="class", color="Booster Version Category")
    return dcc.Graph(figure=scatter_fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)









    
    




# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
# MY IMPORTS
import dash_table

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

##  <MY_ADDS>
dropdown_list = spacex_df[['Launch Site']].drop_duplicates(inplace=False)
df2 = pd.DataFrame({'Launch Site':['ALL']})
dropdown_list = dropdown_list.append(df2)
dropdown_list = dropdown_list.sort_values(['Launch Site']).reset_index(drop=True)

#  Alternative method provided by instructor
if 1==0:
    OptionList = [{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()]
    OptionList.insert(0,{'label': 'All', 'value': 'All'})

# Default Pie Chart
fig_default_pie = px.pie(spacex_df, values='class', names='Launch Site', title='Total Success Launches by Site')
fig_default_scatter = px.scatter(spacex_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')

##  </MY_ADDS>


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    dcc.Dropdown(
                                        id='site_dropdown'
                                        , options=[
                                            {'label': i, 'value': i} for i in dropdown_list['Launch Site']
                                        ]
                                        # alternative using method provided by instructor
                                        #, options=OptionList
                                        #, value=OptionList[0]
                                        , value='ALL'
                                        , placeholder="Select a Launch Site here"
                                        , searchable=True
                                        , style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-align-last':'center'}
                                    )
                                ])

                                , html.Br()

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                , html.Div(
                                    #dcc.Graph(id='success-pie-chart')
                                    # default it to all for now so we can confirm it displays
                                    dcc.Graph(id='success-pie-chart', figure=fig_default_pie)
                                )
                                

                                , html.P("Payload range (Kg):")
                                # TASK 3: Add a slider to select payload range
                                , dcc.RangeSlider(
                                    id='payload-slider'
                                    , min=0
                                    , max=10000
                                    , step=100
                                    , value=[min_payload, max_payload]
                                    , marks={
                                        0: '0'
                                        , 2500: '2500'
                                        , 5000: '5000'
                                        , 7500: '7500'
                                        , 10000: '10000'
                                    }
                                )

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                , html.Div(
                                    dcc.Graph(
                                        id='success-payload-scatter-chart'
                                        , figure=fig_default_scatter
                                    )
                                )
                                
                                ,
                            ])  # END - Main app.layout Div
        

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure')
    , Input(component_id='site_dropdown', component_property='value')
)
def get_pie_chart(site_val):
    filtered_df = spacex_df
    if site_val == 'ALL':
        fig = px.pie(
            filtered_df
            , values='class'
            , names= 'Launch Site'
            , title = 'Total Success Launches By Site'
        )
        return fig
        #return[dcc.Graph(figure=fig)]
    else:
        # return the outcomes pichart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==site_val]
        filtered_df = filtered_df.groupby(['Launch Site', 'class']).size().reset_index()
        filtered_df.rename(columns={0:'class count'}, inplace=True)
        fig = px.pie(
            filtered_df
            , values='class count'
            , names= 'class'
            , title = f'Total Success Launches for Site {site_val}'
        )    
        return fig 


##  MY TEST of dropdown callback
@app.callback(
    Output(component_id='callback_test', component_property='children')
    , Input(component_id='site_dropdown', component_property='value')
)
def callbacktest(siteval):
    retval = f'siteval = {siteval}'
    return retval


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure')
    , [
        Input(component_id='site_dropdown', component_property='value')
        , Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(site_val, slider_val):

    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)']>slider_val[0])*(spacex_df['Payload Mass (kg)']<slider_val[1])]
    if site_val == 'ALL':
        fig = px.scatter(
            filtered_df
            , x='Payload Mass (kg)'
            , y='class'
            , color='Booster Version Category'
        )
        return fig
    else:
        # return the outcomes pichart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==site_val]
        filtered_df = filtered_df.groupby(['Launch Site', 'Payload Mass (kg)', 'Booster Version Category','class']).size().reset_index()
        filtered_df.rename(columns={0:'class count'}, inplace=True)
        fig = px.scatter(
            filtered_df
            , x='Payload Mass (kg)'
            , y='class'
            , color='Booster Version Category'
        )
        return fig 



# Run the app
if __name__ == '__main__':
    app.run_server()

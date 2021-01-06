
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
import json
import os
import time

from .Components import sync_div

from app import app

storage = [
    # full string summary of state
    html.Div(id='full-string-summary' ,style={'display': 'none'},children=None),
    dcc.ConfirmDialog(id='confirm-reset',
                      message='Are you sure you want to reset the list? This will delete the shopping list for all users.',
                      ),
]

final_list_children = []
final_list_children.append(html.Label('Shopping List: ',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))
final_list_children.append(html.P('[No shopping list items]',id='shopping-list',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))

days = ['saturday','sunday','monday','tuesday','wednesday','thursday','friday']
weekdays = ['monday','tuesday','wednesday','thursday','friday']
weekends = ['sunday','saturday']

def GetResetMealTableData() :

    _days = ['saturday','sunday','monday','tuesday','wednesday','thursday','friday']
    _weekdays = ['monday','tuesday','wednesday','thursday','friday']
    _weekends = ['sunday','saturday']

    abbrev = {'saturday':'Sat','sunday':'Sun','monday':'Mon','tuesday':'Tue','wednesday':'Wed',
              'thursday':'Thu','friday':'Fri'}

    _data  = [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _days]
    _data += [{'Day':''         ,'Meal':'Breakfasts','Serves':''}]
    _data += [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _weekends]
    _data += [{'Day':''         ,'Meal':'Lunches','Serves':''}]
    _data += [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _weekdays]

    return _data

def SetGlobalShoppingListJsonFile(_table_meals_data,_table_single_ingredients_data) :
    _full_summary = [_table_meals_data,_table_single_ingredients_data]
    _full_summary_dumps = json.dumps(_full_summary)

    # If there was no sync,
    with open('global_shopping_list.json', 'w') as f:
        json.dump(_full_summary, f)

    # Return this string summary, for comparing with file later
    return _full_summary_dumps


dummy_recipes = [
    {'label':'Recipe 1','value':'Recipe 1'},
    {'label':'Recipe 2','value':'Recipe 2'},
    {'label':'Recipe 3','value':'Recipe 3'},
]
dinner_recipes = dummy_recipes
lunch_recipes = dummy_recipes
breakfast_recipes = dummy_recipes

meals_table = dash_table.DataTable(
    id = 'table-meals',
    row_deletable=False,
    editable=True,
    style_cell={'textAlign':'left','padding-left':'15px'},
    style_cell_conditional=[
        {'if': {'column_id': 'Meal'}  ,'width': '5%'},
        {'if': {'column_id': 'Meal'}  ,'width': '75%'},
        {'if': {'column_id': 'Serves'},'width': '20%'},
        {'if': {'column_id': 'Day'}   ,'padding-left': '5px','padding-right':'5px'},
    ],
    style_data_conditional=[
        {'if': {'filter_query': '{Serves} > 2','column_id': 'Serves'},
         'fontWeight':'bold','fontSize':16},
        {'if': {'filter_query': '{Serves} < 2','column_id': 'Serves'},
         'fontWeight': 'bold','fontSize':16},
        {'if': {'filter_query': '{Meal} = "Dinners"'},'backgroundColor': '#fafafa','fontWeight': '','fontSize':12},
        {'if': {'filter_query': '{Meal} = "Breakfasts"'},'backgroundColor': '#fafafa','fontWeight': '','fontSize':12},
        {'if': {'filter_query': '{Meal} = "Lunches"'},'backgroundColor': '#fafafa','fontWeight': '','fontSize':12},
    ],

    data=[],

    columns=[
        {'id': 'Day', 'name': ''},
        {'id': 'Meal', 'name': 'Dinners', 'presentation': 'dropdown'},
        {'id': 'Serves', 'name': 'Serves', 'presentation': 'dropdown'},
    ],

    dropdown_data=[
        {'Meal': {'options':dinner_recipes,
                  'clearable':False},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)],
                   'clearable':False}
         } for day in days
    ] + [{}] + [
        {'Meal': {'options':breakfast_recipes,
                  'clearable':False},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)],
                   'clearable':False}
         } for day in weekends
    ] + [{}] + [
        {'Meal': {'options':lunch_recipes,
                  'clearable':False},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)],
                   'clearable':False}
         } for day in weekdays
    ],
)

single_ingredients_table = dash_table.DataTable(
    id='table-single-ingredients',
    row_deletable=True,
    data=[{'Ingredient':'','Amount':1,'Unit':None},],
    editable=True,

    style_cell={'textAlign': 'left','padding':'5px'},
    style_cell_conditional=[
        {'if': {'column_id': 'Amount'},'textAlign': 'right'},
        {'if': {'column_id': 'Ingredient'},'width': '65%'},
        {'if': {'column_id': 'Amount'},    'width': '15%'},
        {'if': {'column_id': 'Unit'},      'width': '20%'},
    ],

    columns=[
        {'id': 'Ingredient', 'name': 'Ingredient', 'presentation': 'dropdown'},
        {'id': 'Amount', 'name': 'Amount'},
        {'id': 'Unit', 'name': 'Unit', 'presentation': 'dropdown'},
    ],

    dropdown={
        'Ingredient': {
            'options': [
                {'label': i, 'value': i}
                for i in ['Toast Twins','Tomatoes']
            ]
        },
        'Unit': {
            'options': [
                {'label': i, 'value': i}
                for i in ['g','pc']
            ]
        }
    }
)

tags = ['indian','spicy','vegetarian','asian','soup']
tag_buttons = []
for tag in tags :
    tmp = html.Button(id='tag-%s-button'%(tag),children=tag,n_clicks=0,
                      style={'display':'inline-block','verticalAlign':'middle'})
    tag_buttons.append(tmp)


layout = html.Div( # Main Div
    children=[ # Main Div children
        sync_div, # The full-screen sync message/button
        html.Div( # Welcome and Filters
            children=[
                html.H5(children='Welcome, Sarah, to the Grocery List App!'),
                html.Button(id='reset-button',children='Reset all',n_clicks=0,style={'display':'inline-block','verticalAlign':'middle'}),
                html.Label('Filters: ',style={'display':'inline-block','verticalAlign':'middle','marginRight':'10px','marginLeft':'10px'},),
                dcc.Dropdown(id='recipe-time-dropdown',placeholder='Recipe Time',style={'width':'200px','display':'inline-block','verticalAlign':'middle'}),
                dcc.Dropdown(id='cookbook-dropdown',placeholder='Cookbook',style={'width':'200px','display':'inline-block','verticalAlign':'middle'}),
                html.A('Link to recipe',id='cookbook-link',href='https://cern.ch/kurt', target='_blank',style={'display':'inline-block','verticalAlign':'middle','marginLeft':'10px','display':'none'},)
            ],
            style={'margin-left':'1%','margin-right':'1%','height':'80px'},
        ),
        html.Div( # Tags
            children=[
                html.Label('Tags: ',style={'display':'inline-block','verticalAlign':'middle','marginRight':'10px'},),
                *tag_buttons,
            ],
            style={'margin-left':'1%','margin-right':'1%','height':'45px'},
        ),
        html.Div( # Row Div
            children=[
                html.Div(html.Div(meals_table,style={'width':'95%'}),
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'80vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(single_ingredients_table,style={'width':'95%'}),
                          html.Button('Add Row', id='add-rows-button', n_clicks=0),
                          ],
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'80vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(final_list_children)],
                         className='four columns',
                         style={'margin-left':'1%','margin-right':'1%','height':'80vh'},
                        ),

                # here is where all the hidden components get added
                *storage,
            ],
            className='row',
            style={'height':'100%'},
        ), # Row Div End
    ], # Main Div children End
) # Main Div End

# Confirm whether you really wanted to reset the shopping list
@app.callback(Output('confirm-reset', 'displayed'),
              Input('reset-button', 'n_clicks'))
def reset_confirm(n_clicks):
    if n_clicks > 0 :
        return True
    return False

# Add Row Callback + Sync tables callback
@app.callback([Output('table-meals','data'),
               Output('table-single-ingredients','data'),
               ],
              [Input('add-rows-button', 'n_clicks'),
               Input('sync-button','n_clicks'),
               Input('confirm-reset','submit_n_clicks'),
               ],
              [State('full-string-summary','children'),
               State('table-single-ingredients', 'data'),
               State('table-single-ingredients', 'columns'),
               State('table-meals','data'),
               ],
)
def syncTables(add_row_nclicks,sync_nclicks,confirm_reset_nclicks,
               full_string_summary,si_rows,si_columns,meals_data) :

    ctx = dash.callback_context

    # Add rows to single ingredients
    if ctx.triggered and 'add-rows-button' in ctx.triggered[0]['prop_id'] :
        si_rows.append({c['id']: '' for c in si_columns})
        return meals_data,si_rows

    # Replace tables with the full string summary coming from the file
    # (triggered by callback below)
    elif ctx.triggered and 'sync-button' in ctx.triggered[0]['prop_id'] :
        full_summary = json.loads(full_string_summary)
        table_meals = full_summary[0]
        table_single_ingredients = full_summary[1]
        return table_meals,table_single_ingredients

    # Use "starting point" tables
    default_meals_data = GetResetMealTableData()
    default_single_ingredients_data = [{'Ingredient':'','Amount':1,'Unit':None},]

    # If this is a reset, then also remove the json file.
    if ctx.triggered and 'confirm-reset' in ctx.triggered[0]['prop_id'] :
        os.remove('global_shopping_list.json')

    return default_meals_data,default_single_ingredients_data

# Create local full string summary
@app.callback(
    [Output('full-string-summary','children'),
     Output('sync-div','style'),
     ],
    [Input('table-meals','data'),
     Input('table-single-ingredients','data'),
     ],
    [State('full-string-summary','children'),
     State('sync-div','style'),
     ]
)
def create_string_summary(table_meals,table_single_ingredients,
                          previous_string_summary,sync_div_style) :

    # If we are just starting, then we need to set the previous string summary to check against
    # the json file.
    if previous_string_summary == None :
        full_summary = [table_meals,table_single_ingredients]
        previous_string_summary = json.dumps(full_summary)

    # Check if the previous string summary is the same
    if os.path.exists('global_shopping_list.json') :
        with open('global_shopping_list.json', 'r') as f:
            txt = f.readlines()[0]
            if txt == previous_string_summary :
                #print('They are the same!')
                pass
            else :
                #print('They are NOT the same!')
                #print(' - Last local edit: ',previous_string_summary)
                #print(' - From file......: ',txt)
                sync_div_style['display'] = ''
                return txt,sync_div_style

    # If the json file matches the previous state, then proceed
    # (update the json file and make sure the sync div is hidden)
    new_string_summary = SetGlobalShoppingListJsonFile(table_meals,table_single_ingredients)
    sync_div_style['display'] = 'none'

    return new_string_summary,sync_div_style

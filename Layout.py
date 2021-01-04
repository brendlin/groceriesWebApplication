
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

from app import app

recipes_dropdown_style_wrapdiv = {'width':'80%','display': 'inline-block'}
recipes_dropdown_style = {'width':'100%','display': 'inline-block','verticalAlign':'middle'}
portions_style = {'width': '15%','display': 'inline-block','text-align': 'center',
                  'marginRight':'5%',
                  'marginLeft':'0%',
                  'verticalAlign':'middle'}

single_ingredients_dropdown_style = {'width':'100%','display': 'inline-block','verticalAlign':'middle'}
single_ingredients_other_style = {'width': '100%','display': 'inline-block','align': 'left',
                                  #'marginRight':'5%','marginLeft':'5%',
                                  'verticalAlign':'middle'}

serves = html.Label('Serves: ',style={'marginTop':'10px','width': '15%','display': 'inline-block','marginRight':'5%','marginLeft':'0%','verticalAlign':'middle'})
weekly_x_style = {'marginTop':'10px','width': '80%','display': 'inline-block','verticalAlign':'middle'}

storage = [
    # full string summary of state
    html.Div(id='full-string-summary' ,style={'display': 'none'},children=None),
]

final_list_children = []
final_list_children.append(html.Label('Shopping List: ',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))
final_list_children.append(html.P('[No shopping list items]',id='shopping-list',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))

days = ['saturday','sunday','monday','tuesday','wednesday','thursday','friday']
weekdays = ['monday','tuesday','wednesday','thursday','friday']
weekends = ['sunday','saturday']

data_entries = [{'Meal':'%s-dinner'%(day),'Serves':2} for day in days]
data_entries += [{'Meal':'Breakfasts','Serves':''}]
data_entries += [{'Meal':'%s-breakfast'%(day),'Serves':2} for day in weekends]
data_entries += [{'Meal':'Lunches','Serves':''}]
data_entries += [{'Meal':'%s-lunch'%(day),'Serves':2} for day in weekdays]

meals_table = dash_table.DataTable(
    id = 'table-meals',
    row_deletable=False,
    editable=True,
    style_cell={'textAlign':'left','padding-left':'15px'},
    style_cell_conditional=[
        {'if': {'column_id': 'Meal'}  ,'width': '80%'},
        {'if': {'column_id': 'Serves'},'width': '20%'},
    ],
    style_data_conditional=[
        {'if': {'filter_query': '{Serves} > 2','column_id': 'Serves'},
         'fontWeight': 'bold','backgroundColor':'pink'},
        {'if': {'filter_query': '{Serves} < 2','column_id': 'Serves'},
         'fontWeight': 'bold','backgroundColor':'pink'},
        {'if': {'filter_query': '{Meal} = "Dinners"'},'backgroundColor': '#fafafa',},
        {'if': {'filter_query': '{Meal} = "Breakfasts"'},'backgroundColor': '#fafafa',},
        {'if': {'filter_query': '{Meal} = "Lunches"'},'backgroundColor': '#fafafa',},
    ],

    data=data_entries,

    columns=[
        {'id': 'Meal', 'name': 'Dinners', 'presentation': 'dropdown'},
        {'id': 'Serves', 'name': 'Serves', 'presentation': 'dropdown'},
    ],

    dropdown_data=[
        {'Meal': {'options':[{'label': '%s Dinner'%(day.capitalize()),
                              'value': '%s-dinner'%(day)}]
                  ,'clearable':True},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)]
                 ,'clearable':False}
         } for day in days
    ] + [{}] + [
        {'Meal': {'options':[{'label': '%s Breakfast'%(day.capitalize()),
                              'value': '%s-breakfast'%(day)}]
                  ,'clearable':True},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)]
                 ,'clearable':False}
         } for day in weekends
    ] + [{}] + [
        {'Meal': {'options':[{'label': '%s Lunch'%(day.capitalize()),
                              'value': '%s-lunch'%(day)}]
                  ,'clearable':True},
         'Serves':{'options':[{'label': str(i), 'value': i} for i in range(1,11)]
                 ,'clearable':False}
         } for day in weekdays
    ],
)

single_ingredients_table = dash_table.DataTable(
    id='table-single-ingredients',
    row_deletable=True,
    data=[{'Ingredient':'','Amount':None,'Unit':None},],
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
    })

layout = html.Div( # Main Div
    children=[ # Main Div children
        html.H5(children='Welcome, Sarah, to the Grocery List App!'),
        html.Div( # Row Div
            children=[
                html.Div(html.Div(meals_table,style={'width':'95%'}),
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'90vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(single_ingredients_table,style={'width':'95%'}),
                          html.Button('Add Row', id='editing-rows-button', n_clicks=0),
                          html.Div('No Extra Items',style={'marginTop':'10px'}),
                          ],
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'90vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(final_list_children)],
                         className='four columns',
                         style={'margin-left':'1%','margin-right':'1%'},
                        ),

                # here is where all the hidden components get added
                *storage,
            ],
            className='row',
            style={'height':'100%'},
        ), # Row Div End
    ], # Main Div children End
) # Main Div End

# Add Row Callback
@app.callback(
    Output('table-single-ingredients', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table-single-ingredients', 'data'),
    State('table-single-ingredients', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

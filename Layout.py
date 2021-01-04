
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

dinners_children = []
dinners_children.append(html.Label('Weekly Dinners: ',style=weekly_x_style))
dinners_children.append(serves)
for day in ['saturday','sunday','monday','tuesday','wednesday','thursday','friday'] :
    tmp = html.Div(dcc.Dropdown(id='recipes-dropdown-dinner-%s'%(day),placeholder='%s Dinner'%(day.capitalize()),
                                options=list({'label':i,'value':i} for i in ['Recipe 1','Recipe 2','Recipe 3']),
                                style=recipes_dropdown_style,
                                searchable=True),
                   style=recipes_dropdown_style_wrapdiv,)
    dinners_children.append(tmp)
    tmp = dcc.Input(id='portions-dinner-%s'%(day), value='2', type='text',style=portions_style)
    dinners_children.append(tmp)

breakfasts_children = []
breakfasts_children.append(html.Label('Weekend Breakfasts: ',style=weekly_x_style))
breakfasts_children.append(serves)
for day in ['sunday','saturday'] :
    tmp = html.Div(dcc.Dropdown(id='recipes-dropdown-breakfast-%s'%(day),placeholder='%s Breakfast'%(day.capitalize()),
                                options=list({'label':i,'value':i} for i in ['Recipe 1','Recipe 2','Recipe 3']),
                                style=recipes_dropdown_style,
                                searchable=True),
                   style=recipes_dropdown_style_wrapdiv,)
    breakfasts_children.append(tmp)
    tmp = dcc.Input(id='portions-breakfast-%s'%(day), value='2', type='text',style=portions_style)
    breakfasts_children.append(tmp)

lunches_children = []
lunches_children.append(html.Label('Weekend Lunches: ',style=weekly_x_style))
lunches_children.append(serves)
for day in ['monday','tuesday','wednesday','thursday','friday'] :
    tmp = html.Div(dcc.Dropdown(id='recipes-dropdown-lunch-%s'%(day),placeholder='%s Lunch'%(day.capitalize()),
                                options=list({'label':i,'value':i} for i in ['Recipe 1','Recipe 2','Recipe 3']),
                                style=recipes_dropdown_style,
                                searchable=True),
                   style=recipes_dropdown_style_wrapdiv,)
    lunches_children.append(tmp)
    tmp = dcc.Input(id='portions-lunch-%s'%(day), value='2', type='text',style=portions_style)
    lunches_children.append(tmp)

final_list_children = []
final_list_children.append(html.Label('Shopping List: ',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))
final_list_children.append(html.P('[No shopping list items]',id='shopping-list',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))

single_ingredients_table = dash_table.DataTable(
    id='table-single-ingredients',
    row_deletable=True,
    data=[{'Ingredient':'','Amount':None,'Unit':None},],

    style_cell={'textAlign': 'left','padding':'5px','fontWeight':'bold'},
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
    editable=True,
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
                html.Div(dinners_children + breakfasts_children + lunches_children,
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

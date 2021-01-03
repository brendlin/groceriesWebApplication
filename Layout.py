
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

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

single_ingredients_children = []
single_ingredients_children.append(html.Label('Single Ingredient: ',style={'marginTop':'10px','width': '61%','display': 'inline-block','verticalAlign':'middle'}))
single_ingredients_children.append(html.Label('Amount:',style={'marginTop':'10px','width': '17%','display': 'inline-block','marginRight':'0%','marginLeft':'0%','verticalAlign':'middle'}))
single_ingredients_children.append(html.Label('Unit:',style={'marginTop':'10px','width': '17%','display': 'inline-block','marginRight':'0%','marginLeft':'0%','verticalAlign':'middle'}))
tmp = html.Div(dcc.Dropdown(id='single-ingredient',placeholder='Add single ingredient',
                            options=list({'label':i,'value':i} for i in ['Toast Twins','Tomatoes']),
                            style=single_ingredients_dropdown_style,
                            searchable=True),
               style={'width':'61%','display': 'inline-block'})
single_ingredients_children.append(tmp)
tmp = dcc.Input(id='single-ingredient-amount', value='1', type='text',
                style={'width':'17%','display': 'inline-block','verticalAlign':'middle'})
single_ingredients_children.append(tmp)
tmp = html.Div(dcc.Dropdown(id='single-ingredient-unit',placeholder='Unit',
                   options=list({'label':i,'value':i} for i in ['None','g']),
                   style=single_ingredients_other_style,
                   searchable=True),
               style={'width':'17%','display': 'inline-block'})
single_ingredients_children.append(tmp)
tmp = html.Button('Add Item', id='add-item-button',style={'width':'95%'}, n_clicks=0)
single_ingredients_children.append(tmp)
single_ingredients_children.append(html.Div('No Extra Items',style={'marginTop':'10px'}))

final_list_children = []
final_list_children.append(html.Label('Shopping List: ',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))
final_list_children.append(html.P('[No shopping list items]',id='shopping-list',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))

layout = html.Div( # Main Div
    children=[ # Main Div children
        html.H5(children='Welcome, Sarah, to the Grocery List App!'),
        html.Div( # Row Div
            children=[
                html.Div(dinners_children + breakfasts_children + lunches_children,
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'90vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(single_ingredients_children)],
                         className='four columns',
                         style={'border-right':'1px solid #adadad','height':'90vh','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(final_list_children)],
                         className='four columns',
                         style={'margin-left':'1%','margin-right':'1%'},
                        ),
            ],
            className='row',
            style={'height':'100%'},
        ), # Row Div End
    ], # Main Div children End
) # Main Div End

@app.callback(Output('shopping-list', 'children'), Input('single-ingredient', 'value'))
def compute_value(value):
    # compute value and send a signal when done
    return value

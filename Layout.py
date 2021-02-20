
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
import json
import os
import time
import sqlalchemy
import pandas as pd

from .Components import sync_div
from .HelperFunctions import CreateShoppingListFromDF,CreateShoppingListFromDF_Compressed,CreateMealList
from .DatabaseHelpers import (
    GetDatabaseName,
    GetDataframe,
    AddIngredientToDatabase,
    AddRecipeToDatabase,
    SelectFilteredRecipes,
    GetIngredientsFromRecipes,
    GetIngredientLocations,
)


DATABASE = GetDatabaseName()
engine = sqlalchemy.create_engine(DATABASE)

from app import app

storage = [
    # full string summary of state
    html.Div(id='full-string-summary' ,style={'display': 'none'},children=None),
    html.Div(id='filter-string-csv' ,style={'display': 'none'},children=None),
    html.Div(id='available-tags-csv' ,style={'display': 'none'},children=None),
    dcc.ConfirmDialog(id='confirm-reset',
                      message='Are you sure you want to reset the list? This will delete the shopping list for all users.',
                      ),
    dcc.ConfirmDialog(id='confirm-new-recipe',message='',),
    dcc.ConfirmDialog(id='confirm-recipe-mistake',message='',),
    dcc.ConfirmDialog(id='confirm-new-ingredient',message='',),
    dcc.ConfirmDialog(id='confirm-ingredient-mistake',message='',),
]

final_list_children = []
final_list_children.append(html.Label('Shopping List: ',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle','font-weight':'bold'}))
final_list_children.append(html.P('[No shopping list items]',id='shopping-list',style={'marginTop':'10px','width': '100%','display': 'inline-block','verticalAlign':'middle'}))

days = ['saturday','sunday','monday','tuesday','wednesday','thursday','friday']
weekdays = ['monday','tuesday','wednesday','thursday','friday']
weekends = ['sunday','saturday']

def MakeNewRecipeName(recipe_text) :
    return recipe_text.lower().replace(' ','_') + '.txt'

def GetResetMealTableData(mealtime) :

    _days = ['saturday','sunday','monday','tuesday','wednesday','thursday','friday']
    _weekdays = ['monday','tuesday','wednesday','thursday','friday']
    _weekends = ['sunday','saturday']

    abbrev = {'saturday':'Sat','sunday':'Sun','monday':'Mon','tuesday':'Tue','wednesday':'Wed',
              'thursday':'Thu','friday':'Fri'}

    _data = []
    if mealtime == 'Dinners' :
        _data = [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _days]

    if mealtime == 'Breakfasts' :
        _data = [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _weekends]

    if mealtime == 'Lunches' :
        _data = [{'Day':abbrev[day],'Meal':None,'Serves':2} for day in _weekdays]

    if mealtime == 'Other' :
        _data = [{'Day':'%03d'%(i),'Meal':None,'Serves':2} for i in range(5)]

    return _data

def SetGlobalShoppingListJsonFile(_table_meals_data_dinners,_table_meals_data_bfasts,
                                  _table_meals_data_lunches,
                                  _table_meals_data_other,
                                  _table_single_ingredients_data) :
    _full_summary = [_table_meals_data_dinners,
                     _table_meals_data_bfasts,
                     _table_meals_data_lunches,
                     _table_meals_data_other,
                     _table_single_ingredients_data]
    _full_summary_dumps = json.dumps(_full_summary)

    # If there was no sync,
    with open('global_shopping_list.json', 'w') as f:
        json.dump(_full_summary, f)

    # Return this string summary, for comparing with file later
    return _full_summary_dumps


def MakeMealsTable(mealtime) :
    meals_table = dash_table.DataTable(
        id = 'table-meals-%s'%(mealtime.lower()),
        row_deletable=False,
        editable=True,
        style_cell={'textAlign':'left','padding-left':'15px',},
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
            {'if': {'state': 'selected'},'backgroundColor': '#FAFAFA','border': '1px dark gray',},
        ],

        # Populated in dropdowns
        data=[],
        dropdown_data=[],

        columns=[
            {'id': 'Day', 'name': ''},
            {'id': 'Meal', 'name': mealtime, 'presentation': 'dropdown'},
            {'id': 'Serves', 'name': 'Serves', 'presentation': 'dropdown'},
        ],

    )
    return meals_table

meals_table_dinners = MakeMealsTable('Dinners')
meals_table_breakfasts = MakeMealsTable('Breakfasts')
meals_table_lunches = MakeMealsTable('Lunches')
meals_table_other = MakeMealsTable('Other')

def MakeIngredientsTable(id) :
    return dash_table.DataTable(
        id=id,
        row_deletable=True,
        data=[{'Ingredient':'','Amount':1,'Unit':'x'},],
        editable=True,

        style_cell={'textAlign': 'left','padding':'5px'},
        style_cell_conditional=[
            {'if': {'column_id': 'Amount'},'textAlign': 'right'},
            {'if': {'column_id': 'Ingredient'},'width': '65%'},
            {'if': {'column_id': 'Amount'},    'width': '15%'},
            {'if': {'column_id': 'Unit'},      'width': '20%'},
        ],
        style_data_conditional=[
            {'if': {'state': 'selected'},'backgroundColor': '#FAFAFA','border': '1px dark gray',},
        ],

        columns=[
            {'id': 'Ingredient', 'name': 'Ingredient', 'presentation': 'dropdown'},
            {'id': 'Amount', 'name': 'Amount'},
            {'id': 'Unit', 'name': 'Unit', 'presentation': 'dropdown'},
        ],

    )

single_ingredients_table = MakeIngredientsTable('table-single-ingredients')
recipe_ingredients_table = MakeIngredientsTable('table-recipe-ingredients')

tags = ['indian','spicy','vegetarian','asian','soup','pasta']

# tags from database (must be reloaded to find new ones)
tags_df = GetDataframe(engine,'recipe_tags')
tags_empty = list(range(20))
tag_buttons = []
for tag in tags_empty :
    tmp = html.Button(id='tag-%d-button'%(tag),children='button %d'%(tag),n_clicks=0,
                      style={'display':'inline-block','verticalAlign':'middle'})
    tmp_div = html.Div(id='tag-%d-div'%(tag),children=tmp,
                       style={'display':'inline-block','verticalAlign':'middle','display':'none'})
    tag_buttons.append(tmp_div)

# This one determines whether the button div is visible or not
# Also the button names
@app.callback([Output('tag-{}-div'.format(tag), 'style') for tag in tags_empty]
              + [Output('tag-{}-button'.format(tag), 'children') for tag in tags_empty],
              [Input('available-tags-csv','children')],
              [State('tag-{}-div'.format(tag), 'style') for tag in tags_empty]
              + [State('tag-{}-button'.format(tag), 'children') for tag in tags_empty],
              )
def label_buttons(available_tags_csv,*tag_info):

    style_info = list(tag_info[:len(tag_info)//2])
    button_labels = list(tag_info[len(tag_info)//2:])

    # Most of the tag fields are empty, do not display them.
    for i in range(len(style_info)) :
        style_info[i]['display'] = 'none'

    # Catch missing tags
    if available_tags_csv == None :
        return style_info + button_labels

    # For each tag that is available, show a button for it
    for i,tag in enumerate(available_tags_csv.split(',')) :
        if (i+1)*2 > len(tag_info) :
            break
        style_info[i]['display'] = 'inline-block'
        button_labels[i] = tag

    return style_info + button_labels

# Outputs the filter string, and colors the button, based on the number of clicks.
# Make filter string from button inputs
@app.callback([Output('tag-{}-button'.format(tag), 'style') for tag in tags_empty]
              + [Output('filter-string-csv', 'children')],
              [Input('tag-{}-button'.format(tag), 'n_clicks') for tag in tags_empty],
              [State('tag-{}-button'.format(tag), 'children') for tag in tags_empty]
              )
def make_filter_string(*inputs):

    out_str = []
    styles = []

    click_info = inputs[:len(inputs)//2]
    tagname_info = inputs[len(inputs)//2:]

    for i,n_click in enumerate(click_info) :
        if (n_click % 2) :
            out_str.append(tagname_info[i])
            styles.append({'display':'inline-block','verticalAlign':'middle',
                           'background-color':'#bfd8ff'})
        else :
            styles.append({'display':'inline-block','verticalAlign':'middle',})

    return styles + [','.join(out_str)]


new_ingredient_div = html.Div([html.H5(children='Add new ingredient',style={'marginTop':'20px',}),
                               dcc.Input(id='new-ingredient',type='text',
                                         placeholder='Insert new ingredient name',
                                         style={'width':'300px'}),
                               html.Div(id='existing-location-div',
                                        children=[
                                            dcc.Dropdown(id='new-ingredient-location',
                                                         placeholder='Store',
                                                         options=[],
                                                         style={'width':'200px','display':'inline-block',
                                                                'verticalAlign':'middle'}),
                                            html.Button('New location', id='switch-new-location-button', n_clicks=0,
                                                        style={'display':'inline-block','verticalAlign':'middle'}),
                                        ],
                                        ),
                               html.Div(id='new-location-div',
                                        style={'display':'none'},
                                        children=[
                                            dcc.Input(id='new-ingredient-new-location',type='text',
                                                      placeholder='Store name',
                                                      style={'width':'200px'}),
                                            html.Button('cancel', id='switch-existing-location-button', n_clicks=0),
                                        ]
                                        ),
                               html.Button('Add', id='add-ingredient-button', n_clicks=0),
                               ],
                              style={'backgroundColor':'#f0e9e9'})

new_recipe_div = html.Div([html.H5(children='Add new recipe',style={'marginTop':'20px',}),
                           dcc.Input(id='new-recipe-name',type='text',
                                     placeholder='Recipe name',
                                     style={'width':'250px','marginRight':'10px'}),
                           dcc.Input(id='new-recipe-cooktime',type='number',
                                     placeholder='time',style={'width':'80px'}),
                           html.Label('min',style={'display':'inline-block',
                                                   'verticalAlign':'middle',
                                                   'marginLeft':'10px'},),
                           html.Div(id='existing-cookbook-div',
                                    children=[
                                        dcc.Dropdown(id='new-recipe-cookbook',
                                                     placeholder='Cookbook',
                                                     options=[],
                                                     style={'width':'200px','display':'inline-block',
                                                            'verticalAlign':'middle'}),
                                        html.Button('New cookbook', id='switch-new-cookbook-button', n_clicks=0,
                                                    style={'display':'inline-block','verticalAlign':'middle'}),
                                    ],
                                    ),
                           html.Div(id='new-cookbook-div',
                                    style={'display':'none'},
                                    children=[
                                        dcc.Input(id='new-recipe-new-cookbook',type='text',
                                                  placeholder='Cookbook name',
                                                  style={'width':'200px'}),
                                        html.Button('cancel', id='switch-existing-cookbook-button', n_clicks=0),
                                    ]
                                    ),
                           html.Label('Url: ',style={'display':'inline-block'
                                                      ,'verticalAlign':'middle'
                                                      ,'marginRight':'10px'},),
                           dcc.Input(id='new-recipe-url',type='text',
                                     placeholder='(optional)',
                                     style={'width':'300px'}),
                           html.Br(),
                           html.Label('Tags: ',style={'display':'inline-block'
                                                      ,'verticalAlign':'middle'
                                                      ,'marginRight':'10px'},),
                           dcc.Input(id='new-recipe-tags',type='text',
                                     placeholder='(comma-separated)',
                                     style={'width':'300px'}),
                           html.Br(),
                           html.Label('Mealtime(s): ',style={'display':'inline-block'
                                                             ,'verticalAlign':'middle'
                                                             ,'marginRight':'10px'},),
                           dcc.Input(id='new-recipe-mealtimes',type='text',
                                     placeholder='(comma-separated)',
                                     style={'width':'300px'}),
                           html.Br(),
                           html.Div(recipe_ingredients_table,style={'width':'95%'}),
                           html.Button('Add Row', id='add-recipe-ingredient-row-button', n_clicks=0),
                           html.Br(),
                           html.Div(html.Button('Add Recipe', id='add-recipe-button', n_clicks=0),
                                    style={'text-align':'right','width':'95%'}),
                           html.Br(),
                           ],
                          style={'backgroundColor':'#e9eaf0'},
)

layout = html.Div( # Main Div
    children=[ # Main Div children
        sync_div, # The full-screen sync message/button
        html.Div( # Welcome and Filters
            children=[
                html.H5(children='Welcome, Sarah, to the Grocery List App!'),
                html.Button(id='reset-button',children='Reset all',n_clicks=0,style={'display':'inline-block','verticalAlign':'middle'}),
                html.Label('Filters: ',style={'display':'inline-block','verticalAlign':'middle','marginRight':'10px','marginLeft':'10px'},),
                dcc.Input(id='recipe-time-min',placeholder='min-time',type='number',style={'width':'100px','display':'inline-block','verticalAlign':'middle'}),
                html.Label('-',style={'display':'inline-block','verticalAlign':'middle','marginRight':'5px','marginLeft':'5px'},),
                dcc.Input(id='recipe-time-max',placeholder='max-time',type='number',style={'width':'100px','display':'inline-block','verticalAlign':'middle'}),
                html.Label('min',style={'display':'inline-block','verticalAlign':'middle','marginRight':'30px','marginLeft':'10px'},),
                dcc.Dropdown(id='cookbook-dropdown',placeholder='Cookbook Filter',style={'width':'200px','display':'inline-block','verticalAlign':'middle'}),
                html.A('Link to recipe',id='cookbook-link',href='https://cern.ch/kurt', target='_blank',style={'display':'inline-block','verticalAlign':'middle','marginLeft':'10px','display':'none'},)
            ],
            style={'margin-left':'1%','margin-right':'1%'},
            className='no-phone',
        ),
        html.Div( # Tags
            children=[
                html.Label('Tags: ',style={'display':'inline-block','verticalAlign':'middle','marginRight':'10px'},),
                *tag_buttons,
            ],
            style={'margin-left':'1%','margin-right':'1%'}, #,'height':'45px'
            className='no-phone',
        ),
        html.Div( # Row Div
            children=[
                html.Div([html.Div(meals_table_dinners,style={'width':'95%'}),
                          html.Div(meals_table_breakfasts,style={'width':'95%'}),
                          html.Div(meals_table_lunches,style={'width':'95%'}),
                          html.Div(meals_table_other,style={'width':'95%'}),
                          html.Div(html.Br()),
                          ],
                         className='fork columns no-phone',
                         style={'border-right':'1px solid #adadad','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(single_ingredients_table,style={'width':'95%'}),
                          html.Button('Add Row', id='add-rows-button', n_clicks=0),
                          new_ingredient_div,
                          new_recipe_div,
                          html.Div(html.Br()),
                          ],
                         className='fork columns no-phone',
                         style={'border-right':'1px solid #adadad','margin-left':'1%','margin-right':'1%'},
                         ),
                html.Div([html.Div(final_list_children)],
                         className='fork columns',
                         style={'margin-left':'1%','margin-right':'1%'},
                        ),

                # here is where all the hidden components get added
                *storage,
            ],
            className='row',
            style={'height':'100%','margin-top':'10px'},
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

# Confirm whether you really wanted to add a new recipe
@app.callback([Output('confirm-new-recipe', 'displayed'),
               Output('confirm-new-recipe','message'),
               Output('confirm-recipe-mistake', 'displayed'),
               Output('confirm-recipe-mistake','message'),
               ],
              Input('add-recipe-button', 'n_clicks'),
              [State('new-recipe-name','value'),
               State('new-recipe-cooktime','value'),
               State('new-recipe-cookbook','value'),
               State('new-recipe-new-cookbook','value'),
               State('new-recipe-url','value'),
               State('new-cookbook-div','style'),
               State('new-recipe-tags','value'),
               State('new-recipe-mealtimes','value'),
               State('table-recipe-ingredients','data'),
               ]
              )
def new_recipe_confirm(n_clicks,
                       new_recipe_name,
                       new_recipe_cooktime,
                       new_recipe_cookbook,
                       new_recipe_new_cookbook,
                       new_recipe_url,
                       new_cookbook_div,
                       new_recipe_tags,
                       new_recipe_mealtimes,
                       recipe_ingredients_data
                       ):
    if n_clicks <= 0 :
        return False,'',False,''

    err_msg = 'There is a mistake in your recipe ({}) - please check.'
    confirm_msg = 'Adding new recipe \"{}\" -- please confirm.'

    if not new_recipe_name :
        return False,'',True,err_msg.format('no name given')

    if MakeNewRecipeName(new_recipe_name) in os.listdir('recipes') :
        return False,'',True,err_msg.format('recipe with this name already exists')

    if new_recipe_cooktime == None or new_recipe_cooktime == '' :
        return False,'',True,err_msg.format('no cooktime given')

    # If new cookbook div is active:
    if ('display' not in new_cookbook_div.keys()) or (new_cookbook_div['display'] != 'none') :
        if not new_recipe_new_cookbook :
            return False,'',True,err_msg.format('no new cookbook name given')
    else :
        if not new_recipe_cookbook :
            return False,'',True,err_msg.format('no cookbook given')

    if not new_recipe_tags :
        return False,'',True,err_msg.format('no tags given')

    if not new_recipe_mealtimes :
        return False,'',True,err_msg.format('no mealtimes given')

    for meal in new_recipe_mealtimes.split(',') :
        if meal.lstrip().rstrip().lower() not in ['breakfast','lunch','dinner','other'] :
            return False,'',True,err_msg.format('Did not recognize mealtime \"{}\"').format(meal)

    for row in recipe_ingredients_data :
        if not row['Ingredient'] :
            return False,'',True,err_msg.format('ingredient missing in table')

        if row['Ingredient'] and not row['Amount'] :
            tmp_msg = 'no amount given for ingredient %s'%(row['Ingredient'])
            return False,'',True,err_msg.format(tmp_msg)

        if row['Ingredient'] and not row['Unit'] :
            tmp_msg = 'no unit given for ingredient %s'%(row['Ingredient'])
            return False,'',True,err_msg.format(tmp_msg)

    return True,confirm_msg.format(new_recipe_name),False,''

# Switch to/from adding a new cookbook
@app.callback([Output('existing-cookbook-div', 'style'),
               Output('new-cookbook-div', 'style'),
               ],
              [Input('switch-new-cookbook-button', 'n_clicks'),
               Input('switch-existing-cookbook-button', 'n_clicks'),
               ])
def switch_new_cookbook(n_clicks_new,n_clicks_exising):

    ctx = dash.callback_context
    if ctx.triggered and 'switch-new' in ctx.triggered[0]['prop_id'] :
        return {'display':'none'},{}
    if ctx.triggered and 'switch-existing' in ctx.triggered[0]['prop_id'] :
        return {},{'display':'none'}

    return {},{'display':'none'}

# Switch to/from adding a new location
@app.callback([Output('existing-location-div', 'style'),
               Output('new-location-div', 'style'),
               ],
              [Input('switch-new-location-button', 'n_clicks'),
               Input('switch-existing-location-button', 'n_clicks'),
               ])
def switch_new_location(n_clicks_new,n_clicks_exising):

    ctx = dash.callback_context
    if ctx.triggered and 'switch-new' in ctx.triggered[0]['prop_id'] :
        return {'display':'none'},{}
    if ctx.triggered and 'switch-existing' in ctx.triggered[0]['prop_id'] :
        return {},{'display':'none'}

    return {},{'display':'none'}


# Add Row Callback + Sync tables callback
@app.callback([Output('table-meals-dinners','data'),
               Output('table-meals-breakfasts','data'),
               Output('table-meals-lunches','data'),
               Output('table-meals-other','data'),
               Output('table-single-ingredients','data'),
               ],
              [Input('add-rows-button', 'n_clicks'),
               Input('sync-button','n_clicks'),
               Input('confirm-reset','submit_n_clicks'),
               ],
              [State('full-string-summary','children'),
               State('table-single-ingredients', 'data'),
               State('table-meals-dinners','data'),
               State('table-meals-breakfasts','data'),
               State('table-meals-lunches','data'),
               State('table-meals-other','data'),
               ],
)
def syncTables(add_row_nclicks,sync_nclicks,confirm_reset_nclicks,
               full_string_summary,si_rows,
               meals_data_dinners,meals_data_breakfasts,meals_data_lunches,
               meals_data_other) :

    ctx = dash.callback_context

    # Add rows to single ingredients
    if ctx.triggered and 'add-rows-button' in ctx.triggered[0]['prop_id'] :
        si_rows.append({'Ingredient':'','Amount':1,'Unit':'x'})
        return meals_data_dinners,meals_data_breakfasts,meals_data_lunches,meals_data_other,si_rows

    # Replace tables with the full string summary coming from the file
    # (triggered by callback below)
    elif ctx.triggered and 'sync-button' in ctx.triggered[0]['prop_id'] :
        full_summary = json.loads(full_string_summary)
        table_meals_dinners = full_summary[0]
        table_meals_bfasts = full_summary[1]
        table_meals_lunches = full_summary[2]
        table_meals_other = full_summary[3]
        table_single_ingredients = full_summary[4]
        return table_meals_dinners,table_meals_bfasts,table_meals_lunches,table_meals_other,table_single_ingredients

    # Use "starting point" tables
    default_dinners = GetResetMealTableData('Dinners')
    default_bfasts = GetResetMealTableData('Breakfasts')
    default_lunches = GetResetMealTableData('Lunches')
    default_other = GetResetMealTableData('Other')
    default_single_ingredients_data = [{'Ingredient':'','Amount':1,'Unit':'x'},]

    # If this is a reset, then also remove the json file.
    if ctx.triggered and 'confirm-reset' in ctx.triggered[0]['prop_id'] :
        os.remove('global_shopping_list.json')

    return default_dinners,default_bfasts,default_lunches,default_other,default_single_ingredients_data

# Create local full string summary
@app.callback(
    [Output('full-string-summary','children'),
     Output('sync-div','style'),
     Output('shopping-list','children'),
     ],
    [Input('table-meals-dinners','data'),
     Input('table-meals-breakfasts','data'),
     Input('table-meals-lunches','data'),
     Input('table-meals-other','data'),
     Input('table-single-ingredients','data'),
     ],
    [State('full-string-summary','children'),
     State('sync-div','style'),
     State('shopping-list','children'),
     ]
)
def create_string_summary(table_meals_dinners,table_meals_bfasts,table_meals_lunches,
                          table_meals_other,
                          table_single_ingredients,
                          previous_string_summary,sync_div_style,current_shopping_list) :

    # If we are just starting, then we need to set the previous string summary to check against
    # the json file.
    if previous_string_summary == None :
        full_summary = [table_meals_dinners,table_meals_bfasts,table_meals_lunches,
                        table_meals_other,
                        table_single_ingredients]
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
                return txt,sync_div_style,current_shopping_list

    # If the json file matches the previous state, then proceed
    # (update the json file and make sure the sync div is hidden)
    new_string_summary = SetGlobalShoppingListJsonFile(table_meals_dinners,
                                                       table_meals_bfasts,
                                                       table_meals_lunches,
                                                       table_meals_other,
                                                       table_single_ingredients)
    sync_div_style['display'] = 'none'

    #
    # Create the shopping list
    #

    #print (table_meals)
    meals  = list(a['Meal'] for a in table_meals_dinners)
    meals += list(a['Meal'] for a in table_meals_bfasts)
    meals += list(a['Meal'] for a in table_meals_lunches)
    meals += list(a['Meal'] for a in table_meals_other)
    #print('Meals:',meals)

    meals_df = pd.DataFrame(table_meals_dinners + table_meals_bfasts + table_meals_lunches + table_meals_other)
    #print(meals_df)

    # If there are duplicate meals, aggregate them together.
    meals_df_agg = meals_df.groupby(by='Meal').sum()
    meals_df_agg['Serves'] = meals_df_agg['Serves'].astype(int)
    #print(meals_df_agg)

    # This is the serving scale factor dict
    scale_factor_dict = meals_df_agg['Serves'].to_dict()

    #
    # Get the recipe quantities for each meal
    #
    unique_meals_list = list(meals_df_agg.index)
    meals_ingredients_df = GetIngredientsFromRecipes(engine,unique_meals_list)
    #print(meals_ingredients_df)

    # Change units to abbrev
    units_dict = GetDataframe(engine,'units').set_index('unit_name').to_dict()['abbreviation']
    meals_ingredients_df['unit_abbrev'] = meals_ingredients_df['unit_name'].map(units_dict)

    # Multiply by the scale factor of servings
    meals_ingredients_df['shopping_list_q'] = meals_ingredients_df['quantity']
    meals_ingredients_df['shopping_list_q'] *= (0.5 * meals_ingredients_df['recipe_name'].map(scale_factor_dict))

    columns = ['recipe_name','ingredient_name','shopping_list_q','unit_abbrev','ingredient_loc']
    meals_ingredients_df = meals_ingredients_df[columns]
    #print(meals_ingredients_df)

    #
    # Now for the extra ingredients
    #
    single_ingredients_df = pd.DataFrame(table_single_ingredients)
    #print(single_ingredients_df)

    ingr_loc_dict = GetIngredientLocations(engine,single_ingredients_df['Ingredient'])
    #print(ingr_loc_dict)
    single_ingredients_df['ingredient_loc'] = single_ingredients_df['Ingredient'].map(ingr_loc_dict)
    single_ingredients_df['recipe_name'] = 'extras'
    single_ingredients_df['shopping_list_q'] = single_ingredients_df['Amount'].astype(float)
    single_ingredients_df.rename(columns={'Ingredient':'ingredient_name',
                                          'Unit':'unit_abbrev'},inplace=True)
    single_ingredients_df = single_ingredients_df[columns]
    #print(single_ingredients_df)

    #
    # Combine recipes with extras
    #
    all_ingredients_df = pd.concat([meals_ingredients_df,single_ingredients_df],ignore_index=False)
    #print(all_ingredients_df)


    # Group by ingredient_name and unit,
    # Aggregate quantities,
    # Promote ingredient_name and unit back to columns (reset_index)
    groupby = ['ingredient_loc','ingredient_name','unit_abbrev']
    agg = {'shopping_list_q':'sum'}
    all_ingredients_df = all_ingredients_df.groupby(groupby).agg(agg)
    all_ingredients_df = all_ingredients_df.reset_index()
    #print(all_ingredients_df)

    shopping_list = CreateShoppingListFromDF_Compressed(all_ingredients_df)
    shopping_list.append(html.Hr(style={'marginTop':'5px','marginBottom':'0px'}))
    if True in list(a['Meal'] != None for a in table_meals_dinners) :
        shopping_list += CreateMealList(table_meals_dinners,'Dinners')
    if True in list(a['Meal'] != None for a in table_meals_bfasts) :
        shopping_list += CreateMealList(table_meals_bfasts,'Breakfasts')
    if True in list(a['Meal'] != None for a in table_meals_lunches) :
        shopping_list += CreateMealList(table_meals_lunches,'Lunches')
    if True in list(a['Meal'] != None for a in table_meals_other) :
        shopping_list += CreateMealList(table_meals_other,'Other')

    return new_string_summary,sync_div_style,shopping_list


# Confirm whether you really wanted to add a new ingredient
@app.callback([Output('confirm-new-ingredient', 'displayed'),
               Output('confirm-new-ingredient','message'),
               Output('confirm-ingredient-mistake', 'displayed'),
               Output('confirm-ingredient-mistake','message'),
               ],
              [Input('add-ingredient-button','n_clicks'),
               ],
              [State('new-ingredient','value'),
               State('new-ingredient-location','value'),
               State('new-ingredient-new-location','value'),
               State('new-location-div','style'),
               State('table-single-ingredients','dropdown'),
               ]
              )
def new_ingredient_confirm(n_clicks,
                           new_ingredient_name,
                           new_ingredient_location,
                           new_ingredient_new_location,
                           new_location_div,
                           existing_ingredients,
                           ) :

    if n_clicks <= 0 :
        return False,'',False,''

    err_msg = 'There is a mistake in your ingredient ({}) - please check.'
    confirm_msg = 'Adding new ingredient \"{}\" -- please confirm.'

    if not new_ingredient_name :
        return False,'',True,err_msg.format('no name given')

    # If new cookbook div is active:
    if ('display' not in new_location_div.keys()) or (new_location_div['display'] != 'none') :
        if not new_ingredient_new_location :
            return False,'',True,err_msg.format('no new store name given')
    else :
        if not new_ingredient_location :
            return False,'',True,err_msg.format('no store given (just guess)')

    #print(existing_ingredients['Ingredient']['options'])
    ingredients_list = list(a['label'] for a in existing_ingredients['Ingredient']['options'])
    if new_ingredient_name.lower() in ingredients_list :
        return False,'',True,err_msg.format('ingredient %s already exists'%(new_ingredient_name))

    return True,confirm_msg.format(new_ingredient_name),False,''


# Update the list of available ingredients
@app.callback([Output('table-single-ingredients','dropdown'),
               Output('table-recipe-ingredients','dropdown'),
               Output('new-ingredient','value'),
               Output('new-ingredient-location','value'),
               Output('new-ingredient-new-location','value'),
               Output('new-ingredient-location','options'),
               ],
              [Input('confirm-new-ingredient','submit_n_clicks'),
               ],
              [State('new-ingredient','value'),
               State('table-single-ingredients','dropdown'),
               State('new-ingredient-location','options'),
               State('new-ingredient-location','value'),
               State('new-ingredient-new-location','value'),
               State('new-location-div','style'),
               ]
              )
def update_ingredients(add_ingredient_n_clicks,
                       new_ingredient,
                       existing_ingredients,
                       existing_locations,
                       new_ingredient_location,
                       new_ingredient_new_location,
                       new_location_div,
                       ) :

    ctx = dash.callback_context

    # Add ingredient
    if ctx.triggered and 'confirm-new-ingredient' in ctx.triggered[0]['prop_id'] :

        i = new_ingredient
        existing_ingredients['Ingredient']['options'].append({'label':i,'value':i})

        the_ingredient_location = new_ingredient_location
        # If there is a new location...
        if ('display' not in new_location_div.keys()) or (new_location_div['display'] != 'none') :
            the_ingredient_location = new_ingredient_new_location
            existing_locations.append({'label':the_ingredient_location,
                                       'value':the_ingredient_location})

        text = []
        text.append('%s, %s'%(new_ingredient,the_ingredient_location))

        with open('recipes/ingredients.txt','a') as f :
            for t in text :
                f.write(t+'\n')

        AddIngredientToDatabase(engine,new_ingredient,the_ingredient_location)

        return existing_ingredients,existing_ingredients,'','','',existing_locations

    # print('Accessing database')
    units_df = GetDataframe(engine,'units')
    units_abbrev = sorted(list(units_df['abbreviation']))

    ingredients_df = GetDataframe(engine,'ingredients')
    ingredient_locs = sorted(set(ingredients_df['ingredient_loc']))

    ingredients = sorted(list(ingredients_df['ingredient_name']))
    # print('Accessing database complete')

    # Start-up behavior
    location_options = [{'label': i, 'value': i} for i in ingredient_locs]
    unit_options = [{'label': i, 'value': i} for i in units_abbrev]
    ingredient_options = [{'label': i, 'value': i} for i in ingredients]

    columns_dropdown={
        'Ingredient': {'options': ingredient_options,'clearable':False,},
        'Unit': {'options': unit_options,'clearable':False,}
    }

    return columns_dropdown,columns_dropdown,'','','',location_options


#
# Helper function to keep the current choice from disappearing
#
def KeepUserChoiceAsOption(_table_meals_data,_dropdown) :
    for i,row in enumerate(_table_meals_data) :
        if not row['Meal'] :
            continue
        val = row['Meal']
        _dropdown[i]['Meal']['options'].append({'label':val,'value':val})

    return


# Add a recipe / update the list of available recipes
# Add Row to recipe ingredients table
@app.callback([Output('table-meals-dinners','dropdown_data'),
               Output('table-meals-breakfasts','dropdown_data'),
               Output('table-meals-lunches','dropdown_data'),
               Output('table-meals-other','dropdown_data'),
               Output('cookbook-dropdown','options'),
               Output('new-recipe-cookbook','options'),
               Output('new-recipe-name','value'),
               Output('new-recipe-cooktime','value'),
               Output('new-recipe-cookbook','value'),
               Output('new-recipe-new-cookbook','value'),
               Output('new-recipe-url','value'),
               Output('new-recipe-tags','value'),
               Output('new-recipe-mealtimes','value'),
               Output('table-recipe-ingredients', 'data'),
               Output('available-tags-csv','children')
               ],
              [Input('confirm-new-recipe','submit_n_clicks'),
               Input('add-recipe-ingredient-row-button', 'n_clicks'),
               # Filters
               Input('filter-string-csv','children'),
               Input('recipe-time-min','value'),
               Input('recipe-time-max','value'),
               Input('cookbook-dropdown','value'),
               ],
              [State('new-recipe-name','value'),
               State('new-recipe-cooktime','value'),
               State('new-recipe-cookbook','value'),
               State('new-recipe-new-cookbook','value'),
               State('new-recipe-url','value'),
               State('new-cookbook-div','style'),
               State('new-recipe-tags','value'),
               State('new-recipe-mealtimes','value'),
               State('table-recipe-ingredients','data'),
               State('table-recipe-ingredients', 'columns'),
               State('table-meals-dinners','data'),
               State('table-meals-breakfasts','data'),
               State('table-meals-lunches','data'),
               State('table-meals-other','data'),
               ]
              )
def update_recipes(confirm_new_recipe_nclicks,
                   add_recipe_ingredient_row_button_nclicks,
                   # Filters
                   tag_filter_csv,
                   recipe_time_minimum,
                   recipe_time_max,
                   cookbook_filter,
                   new_recipe_name,
                   new_recipe_cooktime,
                   new_recipe_cookbook,
                   new_recipe_new_cookbook,
                   new_recipe_url,
                   new_cookbook_div,
                   new_recipe_tags,
                   new_recipe_mealtimes,
                   recipe_ingredients_data,
                   recipe_ingredients_columns,
                   current_table_meals_dinners,
                   current_table_meals_bfasts,
                   current_table_meals_lunches,
                   current_table_meals_other,
                   ) :

    ctx = dash.callback_context

    # Add row to recipe ingredients table
    if ctx.triggered and 'add-recipe-ingredient-row-button' in ctx.triggered[0]['prop_id'] :
        recipe_ingredients_data.append({c['id']: '' for c in recipe_ingredients_columns})

    # If this is a new recipe ...
    if ctx.triggered and 'confirm-new-recipe' in ctx.triggered[0]['prop_id'] :

        the_recipe_cookbook = new_recipe_cookbook

        # If there is a new cookbook...
        if ('display' not in new_cookbook_div.keys()) or (new_cookbook_div['display'] != 'none') :
            the_recipe_cookbook = new_recipe_new_cookbook

        text = []
        text.append('Property.cooktime_minutes: %d'%(new_recipe_cooktime))
        text.append('Property.recipe_book: %s'%(the_recipe_cookbook))
        if new_recipe_url :
            text.append('Property.recipe_url: %s'%(new_recipe_url))
        text.append('Property.recipe_tags: %s'%(new_recipe_tags))
        text.append('Property.recipe_mealtimes: %s'%(new_recipe_mealtimes))

        units_dict = GetDataframe(engine,'units').set_index('unit_name').to_dict()['abbreviation']
        units_dict = {value:key for key, value in units_dict.items()}
        # print('units_dict:',units_dict)

        for row in recipe_ingredients_data :
            if not row['Ingredient'] :
                continue

            amount = ''
            if row['Amount'] and row['Unit'] :
                amount = '{} {}'.format(row['Amount'],units_dict[row['Unit']])
            else :
                amount = '{}'.format(row['Amount'])

            text.append('Ingredient.{}: {}'.format(row['Ingredient'],amount))

        #print('Adding new recipe: %s'%(MakeNewRecipeName(new_recipe_name)))
        #print('\n'.join(text))

        with open('recipes/%s'%(MakeNewRecipeName(new_recipe_name)),'w') as f :
            for t in text :
                f.write(t+'\n')

        AddRecipeToDatabase(engine,
                            new_recipe_name,
                            new_recipe_cooktime,
                            the_recipe_cookbook,
                            new_recipe_url,
                            new_recipe_tags,
                            new_recipe_mealtimes,
                            recipe_ingredients_data,
                            units_dict
                            )

        recipe_ingredients_data = [{'Ingredient':'','Amount':1,'Unit':'x'},]
        new_recipe_name = ''
        new_recipe_cooktime = ''
        new_recipe_cookbook = ''
        new_recipe_new_cookbook = ''
        new_recipe_url = ''
        new_recipe_tags = ''
        new_recipe_mealtimes = ''

    dinner_recipes = SelectFilteredRecipes(engine,mealtime='dinner',
                                           cookbook=cookbook_filter,
                                           tags=tag_filter_csv,
                                           cooktime_min=recipe_time_minimum,
                                           cooktime_max=recipe_time_max,
                                           )
    #print(dinner_recipes)

    lunch_recipes = SelectFilteredRecipes(engine,mealtime='lunch',
                                          cookbook=cookbook_filter,
                                          tags=tag_filter_csv,
                                          cooktime_min=recipe_time_minimum,
                                          cooktime_max=recipe_time_max,
                                          )

    breakfast_recipes = SelectFilteredRecipes(engine,mealtime='breakfast',
                                              cookbook=cookbook_filter,
                                              tags=tag_filter_csv,
                                              cooktime_min=recipe_time_minimum,
                                              cooktime_max=recipe_time_max,
                                              )

    other_recipes = SelectFilteredRecipes(engine,mealtime='other',
                                          cookbook=cookbook_filter,
                                          tags=tag_filter_csv,
                                          cooktime_min=recipe_time_minimum,
                                          cooktime_max=recipe_time_max,
                                          )

    serves_dict = {'options':[{'label': str(i), 'value': i} for i in range(1,11)],
                   'clearable':False}

    dropdown_dinners = [{'Meal':{'options':dinner_recipes[:],'clearable':False},
                         'Serves':serves_dict} for day in days]
    dropdown_bfasts = [{'Meal': {'options':breakfast_recipes[:],'clearable':False},
                        'Serves':serves_dict} for day in weekends]
    dropdown_lunches = [{'Meal': {'options':lunch_recipes[:],'clearable':False},
                         'Serves':serves_dict} for day in weekdays]
    dropdown_other = [{'Meal': {'options':other_recipes[:],'clearable':False},
                       'Serves':serves_dict} for day in weekdays]

    # Make sure that regardless of the filter, the users choice does not disappear.
    KeepUserChoiceAsOption(current_table_meals_dinners,dropdown_dinners)
    KeepUserChoiceAsOption(current_table_meals_bfasts,dropdown_bfasts)
    KeepUserChoiceAsOption(current_table_meals_lunches,dropdown_lunches)
    KeepUserChoiceAsOption(current_table_meals_other,dropdown_other)

    # print('Accessing database')
    cookbooks_df = GetDataframe(engine,'recipe_book')
    cookbooks = sorted(list(cookbooks_df['recipe_book_short']))

    tags_df = GetDataframe(engine,'recipe_tags')
    available_tags = ','.join(sorted(list(set(list(tags_df['recipe_tag'])))))
    # print('Accessing database complete')

    cookbook_options = [{'label': i, 'value': i} for i in cookbooks]

    return (dropdown_dinners,dropdown_bfasts,dropdown_lunches,dropdown_other,cookbook_options,
            cookbook_options,
            new_recipe_name,new_recipe_cooktime,new_recipe_cookbook,new_recipe_new_cookbook,
            new_recipe_url,new_recipe_tags,new_recipe_mealtimes,recipe_ingredients_data,
            available_tags)

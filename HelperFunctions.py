
import dash_html_components as html

def CreateShoppingListFromDF(all_ingredients_df) :
    # The input is a groupby defined in Layout

    text = []
    current_store = ''

    for index, row in all_ingredients_df.iterrows() :
        if row['ingredient_loc'] != current_store :
            if current_store != '' :
                text.append(html.Br())
            text.append('{}:'.format(row['ingredient_loc']))
            text.append(html.Br())
            current_store = row['ingredient_loc']
        amount = str(row['shopping_list_q'])
        if amount[-2:] == '.0' :
            amount = amount[:-2]
        text.append(' - {}: {} {}'.format(row['ingredient_name'],amount,row['unit_abbrev']))
        text.append(html.Br())

    return text


def CreateShoppingListFromDF_Compressed(all_ingredients_df) :
    # The input is a groupby defined in Layout

    single_line = ''
    text = []
    current_store = ''

    divider = ' '+ u"\u00B7" + ' '

    for index, row in all_ingredients_df.iterrows() :
        if row['ingredient_loc'] != current_store :
            if current_store != '' :
                text.append(single_line.rstrip(divider))
                single_line = ''
                text.append(html.Br())
                text.append(html.Br())
            text.append('{}:'.format(row['ingredient_loc']))
            text.append(html.Br())
            current_store = row['ingredient_loc']
        amount = str(row['shopping_list_q'])
        if amount[-2:] == '.0' :
            amount = amount[:-2]

        tmp = '{} ({}{})'.format(row['ingredient_name'],amount,row['unit_abbrev'])
        tmp = tmp.replace(' ',u"\u00A0") # non-breaking space
        tmp = tmp.replace('-',u"\u2011") # non-breaking hyphen
        single_line += tmp
        single_line += divider
        # text.append(html.Br())

    text.append(single_line.rstrip(divider))
    return text


def CreateMealList(table_meals) :

    text = []
    text.append(html.Br())

    text.append('Dinners:')
    text.append(html.Br())
    for meal_dict in table_meals :
        if not meal_dict['Day'] :
            text.append(html.Br())
            text.append(meal_dict['Meal']+':')
            text.append(html.Br())
        elif not meal_dict['Meal'] :
            #text.append('%s: %s'%(meal_dict['Day'],''))
            #text.append(html.Br())
            pass
        else :
            text.append('%s: %s'%(meal_dict['Day'],meal_dict['Meal']))
            text.append(html.Br())

    return text

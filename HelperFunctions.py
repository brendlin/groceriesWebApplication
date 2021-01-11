
import dash_html_components as html

def isFloat(_str) :
    try:
        float(_str)
    except ValueError:
        return False
    except TypeError:
        return False
    return True

def AddMeasurements(val1,unit1,val2,unit2) :
    # print ('combining \"',val1,'\"',unit1,'\"',val2,'\"',unit2,'\"')

    # If the units are the same, then this is easy:
    if (unit1 == unit2) or (not unit1 and not unit2) :
        val1 = val1 if isFloat(val1) else 0
        val2 = val2 if isFloat(val2) else 0
        return str(float(val1)+float(val2)),unit1

    # Default: no idea. Combine strings with a "+" (will be formatted well below)
    return '%s+%s'%(val1,val2),'%s+%s'%(unit1,unit2)

def TallyAmounts(table_single_ingredients) :
    
    ingredients = set(a['Ingredient'] for a in table_single_ingredients)
    output = []

    for ingredient in ingredients :
        # print(ingredient)
        tmp = dict()
        tmp['Ingredient'] = ingredient
        for mention in list(a for a in table_single_ingredients if a['Ingredient'] == ingredient) :
            if 'Amount' not in tmp.keys() :
                tmp['Amount'] = mention['Amount']
                tmp['Unit'] = mention['Unit']
            else :
                tmp['Amount'],tmp['Unit'] = AddMeasurements(tmp['Amount'],tmp['Unit'],
                                                            mention['Amount'],mention['Unit'])

        output.append(tmp)

    return output

def CreateShoppingList(table_meals,table_single_ingredients) :

    text = []

    # print(table_single_ingredients)

    tallied_ingredients = TallyAmounts(table_single_ingredients)

    for idict in tallied_ingredients :

        unit = idict['Unit'] if idict['Unit'] else ''

        # Catching cases of empty rows, "0" specified.
        if not idict['Ingredient'] :
            continue
        elif isFloat(idict['Amount']) and float(idict['Amount']) == 0 :
            continue

        # No amount specified: just put the ingredient name (like "tomatoes")
        elif not idict['Amount'] :
            text.append('%s'%(idict['Ingredient']))

        # Formatting for mixed measurements
        elif type(idict['Amount']) == type(str()) and ('+' in idict['Amount']) and ('+' in unit) :
            tmp = []
            for i in range(len(idict['Amount'].split('+'))) :
                tmp.append('%s%s'%(idict['Amount'].split('+')[i],unit.split('+')[i]))
            # print(tmp)
            text.append('%s: %s'%(idict['Ingredient'],' + '.join(tmp)))

        # Normal situation: ingredient, amount.
        else :
            text.append('%s: %s%s'%(idict['Ingredient'],idict['Amount'],unit))

        text.append(html.Br())

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

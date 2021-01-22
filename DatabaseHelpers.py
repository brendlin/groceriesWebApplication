
import os
import pandas as pd
import sqlalchemy

def GetDatabaseName() :
    # PythonAnywhere database
    tmp = 'mysql+pymysql://{username}:{password}@{hostname}/{databasename}'
    DATABASE = tmp.format(username='kurtbrendlinger',
                          password='ILoveSnickers',
                          hostname='kurtbrendlinger.mysql.pythonanywhere-services.com',
                          databasename='kurtbrendlinger$groceries',
                          )

    # Local database
    if not os.environ.get('PYTHONANYWHERE_DOMAIN') :
        # 'mysql+pymysql://root:atlaslap44@localhost/groceries'
        DATABASE = tmp.format(username='root',
                              password='atlaslap44',
                              hostname='localhost',
                              databasename='groceries',
                              )

    return DATABASE


def GetDataframe(engine,table_name) :
    with engine.connect() as con :
        
        query = 'SELECT * FROM %s'%(table_name)
        df = pd.read_sql_query(query,con)

    return df


def GetIngredientLocations(engine,ingredient_names) :

    if not len(list(ingredient_names)) :
        return dict()

    with engine.connect() as con :

        txt = 'SELECT ingredient_name,ingredient_loc FROM ingredients'

        filters = []
        for i in ingredient_names :
            filters.append('ingredient_name = "%s"'%(i))

        filter_txt = ''
        if filters :
            filter_txt = ' WHERE '+' OR '.join(filters)

        query = txt + filter_txt
        #print(query)
        df = pd.read_sql_query(query,con)
        #print(df)
        #print(df.set_index('ingredient_name').to_dict()['ingredient_loc'])

    # Return a dictionary
    ret_dict = df.set_index('ingredient_name').to_dict()['ingredient_loc']
    return ret_dict


def GetIngredientsFromRecipes(engine,recipes=[]) :

    # If there are no recipes selected, then should return an empty list.
    # This is a hack to force that.
    if not recipes :
        recipes.append('no_recipe_ever')

    with engine.connect() as con :

        txt  = 'SELECT recipe_quantities.*, ingredient_loc'
        txt += ' from recipe_quantities INNER JOIN ingredients'
        txt += ' ON recipe_quantities.ingredient_name = ingredients.ingredient_name'

        filters = []
        for i in recipes :
            filters.append('recipe_name = "%s"'%(i))

        filter_txt = ''
        if filters :
            filter_txt = ' WHERE '+' OR '.join(filters)

        query = txt + filter_txt
        #print(query)
        df = pd.read_sql_query(query,con)

    return df

def SelectFilteredRecipes(engine,mealtime=None,cookbook=None,
                          tags=None,cooktime_min=None,cooktime_max=None) :

    with engine.connect() as con :

        txt  = 'SELECT recipes.recipe_name FROM recipes'
        if mealtime :
            txt += ' INNER JOIN recipe_mealtimes'
            txt += ' ON recipes.recipe_name = recipe_mealtimes.recipe_name'
        if tags :
            txt += ' INNER JOIN recipe_tags'
            txt += ' ON recipes.recipe_name = recipe_tags.recipe_name'

        filters = []
        if mealtime :
            filters.append('recipe_mealtime = "%s"'%(mealtime))
        if cookbook :
            filters.append('recipe_book_short = "%s"'%(cookbook))
        if (cooktime_min != None) and (cooktime_max == None or cooktime_min < cooktime_max) :
            filters.append('cooktime_minutes >= %d'%(cooktime_min))
        if (cooktime_max != None) and (cooktime_min == None or cooktime_min < cooktime_max) :
            filters.append('cooktime_minutes <= %d'%(cooktime_max))
        if tags :
            for tag in tags.split(',') :
                filters.append('recipe_tag = "%s"'%(tag))

        filter_txt = ' WHERE '+' AND '.join(filters)

        query = txt + filter_txt
        #print(query)
        df = pd.read_sql_query(query,con)

    # Return a list of {'label':'blah','value':'blah'} dictionaries
    tmp = df['recipe_name']
    return [{'label':a,'value':a} for a in tmp]

def AddIngredientToDatabase(engine,ingredient,location) :

    txt  = 'INSERT IGNORE INTO ingredients (ingredient_name,ingredient_loc)'
    txt += ' VALUES (:ingredient_name, :ingredient_loc);'
    insert_ingredient_text = txt

    tmp_dict = {'ingredient_name': ingredient.lstrip().rstrip().lower(),
                'ingredient_loc': location.lstrip().rstrip().lower()}
    with engine.connect() as con:
        con.execute(sqlalchemy.sql.text(insert_ingredient_text), **tmp_dict)

    return

def AddRecipeToDatabase(engine,
                        recipe_name,
                        recipe_cooktime,
                        recipe_cookbook,
                        recipe_url,
                        recipe_tags,
                        recipe_mealtimes,
                        recipe_ingredients_data,
                        units_dict, # translating the unit abbreviations to full unit name
                        units_are_abbreviated=True
                        ) :

    with engine.connect() as con:

        # insert cookbook
        sql  = 'INSERT IGNORE INTO recipe_book (recipe_book_short)'
        sql += ' VALUES (:recipe_book_short);'

        tmp_dict = {'recipe_book_short': recipe_cookbook.rstrip().lstrip().lower(),}
        #print(tmp_dict)
        con.execute(sqlalchemy.sql.text(sql), **tmp_dict)

        # insert recipe name
        sql  = 'INSERT IGNORE INTO recipes (recipe_name,recipe_book_short,cooktime_minutes,recipe_url)'
        sql += ' VALUES (:recipe_name, :recipe_book_short, :cooktime_minutes, :recipe_url);'

        tmp_dict = {'recipe_name': recipe_name.rstrip().lstrip().lower(),
                    'recipe_book_short':recipe_cookbook.rstrip().lstrip().lower(),
                    'cooktime_minutes':recipe_cooktime,
                    'recipe_url':recipe_url.rstrip().lstrip().lower(),
                    }
        #print(tmp_dict)
        con.execute(sqlalchemy.sql.text(sql), **tmp_dict)

        # insert recipe quantity
        for quantity_dict in recipe_ingredients_data :

            sql  = 'INSERT IGNORE INTO recipe_quantities (recipe_name,ingredient_name,quantity,unit_name)'
            sql += ' VALUES (:recipe_name, :ingredient_name, :quantity, :unit_name);'

            if not quantity_dict['Ingredient'] :
                continue

            unit_name = quantity_dict['Unit']
            if units_are_abbreviated :
                unit_name = units_dict[quantity_dict['Unit']]

            tmp_dict = {'recipe_name': recipe_name.rstrip().lstrip().lower(),
                        'ingredient_name': quantity_dict['Ingredient'],
                        'quantity':float(quantity_dict['Amount']),
                        'unit_name':unit_name,
                        }
            #print(tmp_dict)
            con.execute(sqlalchemy.sql.text(sql), **tmp_dict)

        # insert mealtimes
        for mealtime in recipe_mealtimes.split(',') :
            sql  = 'INSERT IGNORE INTO recipe_mealtimes (recipe_name,recipe_mealtime)'
            sql += ' VALUES (:recipe_name, :recipe_mealtime);'

            tmp_dict = {'recipe_name': recipe_name.rstrip().lstrip().lower(),
                        'recipe_mealtime': mealtime.rstrip().lstrip().lower(),
                        }
            #print(tmp_dict)
            con.execute(sqlalchemy.sql.text(sql), **tmp_dict)

        # insert tags
        for tag in recipe_tags.split(',') :
            sql  = 'INSERT IGNORE INTO recipe_tags (recipe_name,recipe_tag)'
            sql += ' VALUES (:recipe_name, :recipe_tag);'

            tmp_dict = {'recipe_name': recipe_name.rstrip().lstrip().lower(),
                        'recipe_tag': tag.rstrip().lstrip().lower(),
                        }
            #print(tmp_dict)
            con.execute(sqlalchemy.sql.text(sql), **tmp_dict)

    return

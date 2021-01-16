
import pandas as pd
import sqlalchemy

def GetDataframe(engine,table_name) :
    with engine.connect() as con :
        
        query = 'SELECT * FROM %s'%(table_name)
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

    tmp_dict = {'ingredient_name': ingredient.lower(), 'ingredient_loc': location.lower()}
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
                        recipe_ingredients_data
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

            sql  = 'INSERT INTO recipe_quantities (recipe_name,ingredient,quantity,unit_name)'
            sql += ' VALUES (:recipe_name, :ingredient, :quantity, :unit_name);'

            tmp_dict = {'recipe_name': recipe_name.rstrip().lstrip().lower(),
                        'ingredient': quantity_dict['Ingredient'],
                        'quantity':float(quantity_dict['Amount']),
                        'unit_name':quantity_dict['Unit'],
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


# Add recipe by filename
# def AddRecipeFileToDatabase(recipe,fname) :

#     with open(fname) as f:

#         lines = f.readlines()

#         # Add recipe to list
#         cookbook = 'None'
#         for line in lines :
#             if 'cookbook' in line :
#                 cookbook = line.split(':')[-1].lstrip().rstrip()
        
#         # Add recipe and cookbook
#         with engine.connect() as con:
#             print('Adding \"%s\", with reference \"%s\", to database.'%(recipe,cookbook))
#             tmp_dict = {'recipe_name': recipe, 'reference': cookbook}
#             con.execute(sqlalchemy.sql.text(insert_recipe_text), **tmp_dict)
        
#         # Add ingredients, recipe lines
#         for line in lines :

#             if 'cookbook' in line :
#                 continue

#             grocery_store = None
#             for g in ['lidl','rewe'] :
#                 if g in line :
#                     grocery_store = g
#                     line = line.replace(g,'')

#             ingredient = line.split(':')[0].lstrip().rstrip()
#             amount_str = line.split(':')[1].lstrip().rstrip()
#             amount = amount_str.split()[0].lstrip().rstrip()

#             unit = None
#             if len(amount_str.split()) > 1 :
#                 unit = amount_str.split()[1].lstrip().rstrip()

#             text = '\"%s\": \"%s\" \"%s\"'%(ingredient,amount,unit)
#             if grocery_store :
#                 text += ' at \"%s\"'%(grocery_store)
#             print (text)
            
#             with engine.connect() as con:

#                 ## insert ingredients
#                 ingr_list = list(a[0] for a in con.execute(sqlalchemy.sql.text('SELECT * FROM ingredients')))
#                 for existing_ingr in ingr_list :
#                     if existing_ingr+'s' == ingredient or existing_ingr == ingredient+'s' :
#                         print ('Replacing %s with %s'%(ingredient,existing_ingr))
#                         ingredient = existing_ingr

#                 tmp_dict = {'ingredient_name': ingredient, 'ingredient_loc': grocery_store}
#                 con.execute(sqlalchemy.sql.text(insert_ingredients_text), **tmp_dict)

#                 ## insert recipe quantity
#                 units_list = list(a[0] for a in con.execute(sqlalchemy.sql.text('SELECT * FROM units')))
#                 abbrev_list = list(a[1] for a in con.execute(sqlalchemy.sql.text('SELECT * FROM units')))
#                 for a,abbrev in enumerate(abbrev_list) :
#                     if unit == abbrev and unit != units_list[a] :
#                         print('Replacing %s with %s'%(unit,units_list[a]))
#                         unit = units_list[a]
                
#                 if (unit not in units_list) and (unit != None) :
#                     print('Error! %s not in units list. Check.'%(unit))
#                     break

#                 tmp_dict = {'recipe_name': recipe,
#                             'ingredient': ingredient,
#                             'quantity':float(amount),
#                             'unit_name':unit}
#                 con.execute(sqlalchemy.sql.text(insert_recipe_quantity), **tmp_dict)

#     return

delete_tables = 'DROP TABLE IF EXISTS recipe_quantities, recipes, ingredients, units, recipe_book, recipe_tags, recipe_mealtimes;'

create_commands = dict()

create_commands['units']  = 'CREATE TABLE units ('
create_commands['units'] += '    unit_name VARCHAR(100) PRIMARY KEY,'
create_commands['units'] += '    abbreviation VARCHAR(50)'
create_commands['units'] += ');'

create_commands['ingredients']  = 'CREATE TABLE ingredients ('
create_commands['ingredients'] += '    ingredient_name VARCHAR(100) PRIMARY KEY,'
create_commands['ingredients'] += '    ingredient_loc VARCHAR(50)'
create_commands['ingredients'] += ');'

create_commands['recipe_book']  = 'CREATE TABLE recipe_book ('
create_commands['recipe_book'] += '    recipe_book_short VARCHAR(200) PRIMARY KEY,'
create_commands['recipe_book'] += '    recipe_book_long VARCHAR(400)'
create_commands['recipe_book'] += ');'

create_commands['recipes']  = 'CREATE TABLE recipes ('
create_commands['recipes'] += '    recipe_name VARCHAR(200) PRIMARY KEY,'
create_commands['recipes'] += '    recipe_book_short VARCHAR(200) REFERENCES recipe_book,'
create_commands['recipes'] += '    cooktime_minutes NUMERIC(3)'
create_commands['recipes'] += ');'

create_commands['recipe_quantities']  = 'CREATE TABLE recipe_quantities ('
create_commands['recipe_quantities'] += '    recipe_name VARCHAR(200) REFERENCES recipes,'
create_commands['recipe_quantities'] += '    ingredient VARCHAR(100) REFERENCES ingredients,'
create_commands['recipe_quantities'] += '    PRIMARY KEY (recipe_name,ingredient),'
create_commands['recipe_quantities'] += '    quantity NUMERIC(3),'
create_commands['recipe_quantities'] += '    unit_name VARCHAR(100) REFERENCES units'
create_commands['recipe_quantities'] += ');'

## Because each recipe can have multiple tags, normalize it
create_commands['recipe_tags']  = 'CREATE TABLE recipe_tags ('
create_commands['recipe_tags'] += '    recipe_name VARCHAR(200) REFERENCES recipes,'
create_commands['recipe_tags'] += '    recipe_tag VARCHAR(200),'
create_commands['recipe_tags'] += '    PRIMARY KEY (recipe_name,recipe_tag)'
create_commands['recipe_tags'] += ');'

## Because each recipe can have multiple mealtimes, normalize it
create_commands['recipe_mealtimes']  = 'CREATE TABLE recipe_mealtimes ('
create_commands['recipe_mealtimes'] += '    recipe_name VARCHAR(200) REFERENCES recipes,'
create_commands['recipe_mealtimes'] += '    recipe_mealtime VARCHAR(200),'
create_commands['recipe_mealtimes'] += '    PRIMARY KEY (recipe_name,recipe_mealtime)'
create_commands['recipe_mealtimes'] += ');'

def RecreateTables(engine) :

    with engine.connect() as con :

        con.execute(sqlalchemy.sql.text(delete_tables))
        for k in create_commands.keys() :
            con.execute(sqlalchemy.sql.text(create_commands[k]))

    return


import os
import sys
import sqlalchemy
from DatabaseHelpers import AddRecipeToDatabase,AddIngredientToDatabase,GetDatabaseName

# usage: python3 restore_database.py recipe_dir
the_dir = sys.argv[1]


DATABASE = GetDatabaseName()

# Add recipe by filename
def AddRecipeFileToDatabase(recipe,fname) :

    prop_names = ['cooktime_minutes','recipe_book',
                  'recipe_url','recipe_tags','recipe_mealtimes']

    properties = dict()
    recipe_quantity_dicts = []

    with open(fname) as f:

        unknown_text = []

        for line in f.readlines() :
            line = line.replace('\n','')

            isprop = True in list(prop in line for prop in prop_names)
            if isprop :
                for prop in prop_names :
                    if 'Property.%s'%(prop) in line :
                        properties[prop] = line.split(':')[1].rstrip().lstrip()
                        break
            elif 'Ingredient.' in line :
                tmp = line.split(':')
                if len(tmp) < 2 :
                    print('Error: ingredient line in file {} not understandable'.format(fname))
                    print(line)
                    sys.exit()
                ingr = tmp[0].replace('Ingredient.','')
                q_unit = tmp[1].split()
                if len(q_unit) < 2 :
                    print('Error: ingredient line in file {} not understandable'.format(fname))
                    print(line)
                    sys.exit()                    
                q = q_unit[0]
                unit = q_unit[1]
                recipe_quantity_dicts.append({'Ingredient':ingr,
                                              'Amount':q,'Unit':unit})
            else :
                print('Error: unknown line in file {}:'.format(fname))
                print(line)
                sys.exit()


    # Make sure all the properties are defined
    for prop in prop_names :
        if prop not in properties.keys() :
            print('Error: file {} missing property {}'.format(fname,prop))
            sys.exit()

    engine = sqlalchemy.create_engine(DATABASE)
    AddRecipeToDatabase(engine,
                        recipe.replace('_',' '),
                        properties['cooktime_minutes'],
                        properties['recipe_book'],
                        properties['recipe_url'],
                        properties['recipe_tags'],
                        properties['recipe_mealtimes'],
                        recipe_quantity_dicts,
                        {},
                        units_are_abbreviated=False,
                        )

    return


def AddIngredientsByFile(fname) :

    ingredients = []
    locations = []

    with open(fname) as f:

        for line in f.readlines() :
            line = line.replace('\n','')

            tmp = line.split(',')
            if len(tmp) < 2 :
                print('Error: ingredient from ingredients.txt not understandable')
                print(line)
                sys.exit()

            ingredients.append(tmp[0].lstrip().rstrip())
            locations.append(tmp[1].lstrip().rstrip())

    engine = sqlalchemy.create_engine(DATABASE)
    for ingr,loc in zip(ingredients,locations) :
        AddIngredientToDatabase(engine,ingr,loc)

    return

#
# Start with ingredients
#
the_ingredients_file = os.path.join(the_dir, 'ingredients.txt')
AddIngredientsByFile(the_ingredients_file)

#
# Then add the recipes
#
for i in os.listdir(the_dir) :
    if i.startswith('.') :
        continue
    if i.endswith('~') :
        continue
    if i == 'ingredients.txt' :
        continue

    recipe_name = i.replace('.txt','')
    AddRecipeFileToDatabase(recipe_name,os.path.join(the_dir, i))

print('done')

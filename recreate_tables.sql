
DROP TABLE IF EXISTS recipe_quantities, recipes, ingredients, units, recipe_book, recipe_tags, recipe_mealtimes;

CREATE TABLE units (
    unit_name VARCHAR(100) PRIMARY KEY,
    abbreviation VARCHAR(50)
);

INSERT IGNORE INTO units (unit_name, abbreviation)
VALUES ('milliliters','ml'), ('grams','g'), ('thumbs','thumbs'),
('cups','c'), ('teaspoons','tsp'), ('tablespoons','tbsp'), ('cloves','cloves'),('units','x');

CREATE TABLE ingredients (
    ingredient_name VARCHAR(100) PRIMARY KEY,
        ingredient_loc VARCHAR(50)
	);

INSERT IGNORE INTO ingredients (ingredient_name, ingredient_loc)
VALUES ('avocado','rewe'), ('garlic','lidl'), ('spaghetti','rewe'), ('olive oil','lidl'),
('lemon','rewe'), ('walnuts','lidl'), ('parmesan','rewe'),
('ear cleaners','budni');

CREATE TABLE recipe_book (
    recipe_book_short VARCHAR(200) PRIMARY KEY
);

INSERT IGNORE INTO recipe_book (recipe_book_short)
VALUES ('nytimes'), ('chris kochtute'), ('no cookbook');

CREATE TABLE recipes (
    recipe_name VARCHAR(200) PRIMARY KEY,
    recipe_book_short VARCHAR(200) REFERENCES recipe_book,
    cooktime_minutes NUMERIC(3),
    recipe_url VARCHAR(400)
);

INSERT IGNORE INTO recipes (recipe_name,recipe_book_short,cooktime_minutes)
VALUES ('avocado pasta','no cookbook',20);

CREATE TABLE recipe_quantities (
    recipe_name VARCHAR(200) REFERENCES recipes,
    ingredient VARCHAR(100) REFERENCES ingredients,
    PRIMARY KEY (recipe_name,ingredient),
    quantity NUMERIC(3),
    unit_name VARCHAR(100) REFERENCES units
);

INSERT IGNORE INTO recipe_quantities (recipe_name,ingredient,quantity,unit_name)
VALUES
('avocado pasta','avocado',2,'units'),
('avocado pasta','garlic',2,'cloves'),
('avocado pasta','spaghetti',300,'grams'),
('avocado pasta','olive oil',2,'tablespoons'),
('avocado pasta','lemon',1,'units'),
('avocado pasta','walnuts',100,'grams'),
('avocado pasta','parmesan',100,'grams');

-- Because each recipe can have multiple tags, normalize it
CREATE TABLE recipe_tags (
    recipe_name VARCHAR(200) REFERENCES recipes,
    recipe_tag VARCHAR(200),
    PRIMARY KEY (recipe_name,recipe_tag)
);

INSERT IGNORE INTO recipe_tags (recipe_name,recipe_tag)
VALUES
('avocado pasta','pasta');

-- Because each recipe can have multiple mealtimes, normalize it
CREATE TABLE recipe_mealtimes (
    recipe_name VARCHAR(200) REFERENCES recipes,
    recipe_mealtime VARCHAR(200),
    PRIMARY KEY (recipe_name,recipe_mealtime)
);

INSERT IGNORE INTO recipe_mealtimes (recipe_name,recipe_mealtime)
VALUES
('avocado pasta','dinner');

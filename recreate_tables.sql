
DROP TABLE IF EXISTS recipe_quantities, recipes, ingredients, units, recipe_book, recipe_tags, recipe_mealtimes;

CREATE TABLE units (
    unit_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (unit_name),
    abbreviation VARCHAR(50)
) ENGINE=InnoDB;

INSERT IGNORE INTO units (unit_name, abbreviation)
VALUES ('milliliters','ml'), ('grams','g'), ('thumbs','thumbs'),
('cups','c'), ('teaspoons','tsp'), ('tablespoons','tbsp'), ('cloves','cloves'),('units','x');

CREATE TABLE ingredients (
    ingredient_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (ingredient_name),
    ingredient_loc VARCHAR(50)
) ENGINE=InnoDB;

INSERT IGNORE INTO ingredients (ingredient_name, ingredient_loc)
VALUES ('avocado','rewe'), ('garlic','lidl'), ('spaghetti','rewe'), ('olive oil','lidl'),
('lemon','rewe'), ('walnuts','lidl'), ('parmesan','rewe'),
('ear cleaners','budni');

CREATE TABLE recipe_book (
    recipe_book_short VARCHAR(200) NOT NULL,
    PRIMARY KEY (recipe_book_short)
) ENGINE=InnoDB;

INSERT IGNORE INTO recipe_book (recipe_book_short)
VALUES ('nytimes'), ('chris kochtute'), ('no cookbook');

CREATE TABLE recipes (
    recipe_name VARCHAR(200) PRIMARY KEY,
    recipe_book_short VARCHAR(200),
    INDEX recipe_book_short_index(recipe_book_short),
    FOREIGN KEY(recipe_book_short)
        REFERENCES recipe_book(recipe_book_short)
	ON DELETE CASCADE,
    cooktime_minutes NUMERIC(3),
    recipe_url VARCHAR(400)
) ENGINE=InnoDB;

INSERT IGNORE INTO recipes (recipe_name,recipe_book_short,cooktime_minutes)
VALUES ('avocado pasta','no cookbook',20);

CREATE TABLE recipe_quantities (
    recipe_name VARCHAR(200),
    INDEX recipe_name_index(recipe_name),
    FOREIGN KEY(recipe_name)
        REFERENCES recipes(recipe_name)
	ON DELETE CASCADE,
    ingredient_name VARCHAR(100),
    -- Apparently an index on a referenced foreign key is required in mysql.
    INDEX ingredient_index(ingredient_name),
    FOREIGN KEY(ingredient_name)
        REFERENCES ingredients(ingredient_name)
	ON DELETE CASCADE,
    PRIMARY KEY (recipe_name,ingredient_name),
    quantity NUMERIC(3),
    unit_name VARCHAR(100),
    INDEX unit_name_index(unit_name),
    FOREIGN KEY(unit_name)
        REFERENCES units(unit_name)
	ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT IGNORE INTO recipe_quantities (recipe_name,ingredient_name,quantity,unit_name)
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
    recipe_name VARCHAR(200),
    INDEX recipe_name_index(recipe_name),
    FOREIGN KEY(recipe_name)
        REFERENCES recipes(recipe_name)
	ON DELETE CASCADE,
    recipe_tag VARCHAR(200),
    PRIMARY KEY (recipe_name,recipe_tag)
) ENGINE=InnoDB;

INSERT IGNORE INTO recipe_tags (recipe_name,recipe_tag)
VALUES
('avocado pasta','pasta');

-- Because each recipe can have multiple mealtimes, normalize it
CREATE TABLE recipe_mealtimes (
    recipe_name VARCHAR(200),
    INDEX recipe_name_index(recipe_name),
    FOREIGN KEY(recipe_name)
        REFERENCES recipes(recipe_name)
	ON DELETE CASCADE,
    recipe_mealtime VARCHAR(200),
    PRIMARY KEY (recipe_name,recipe_mealtime)
) ENGINE=InnoDB;

INSERT IGNORE INTO recipe_mealtimes (recipe_name,recipe_mealtime)
VALUES
('avocado pasta','dinner');

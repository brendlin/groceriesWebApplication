
from app import app

import sys
sys.path.insert(0, "../")

from groceriesWebApplication.Layout import layout

# This is apparently okay to deploy too.
if __name__ == '__main__':
    app.title = 'Groceries App'
    app.layout = layout
    app.run_server(debug=True)

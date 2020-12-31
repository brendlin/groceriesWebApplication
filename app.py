
# This file is special in the sense that it needs to be called app,
# and needs to contain the dash.Dash instance which is also called app.
# (Other projects will be looking for an object called "app" in the current working directory)

import dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)

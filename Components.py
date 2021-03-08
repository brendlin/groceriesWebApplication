
import dash_html_components as html

sync_button = html.Button(id='sync-button',children='Sync',n_clicks=0,
                          className='button buttonPhone',
                          style={'verticalAlign':'bottom','background-color':'white'})

sync_button_wrapdiv = html.Div(sync_button,
                               style={'display':'inline-block','verticalAlign':'middle'})

sync_message = html.Div('Don\'t worry: you will only lose the last change you just made.',
                        style={'marginTop':'10px','background-color':'white'})

sync_wrapdiv = html.Div(children=[sync_button_wrapdiv,sync_message],
                        style={'background-color':'white','padding':'10px 10px'},
                        )

sync_div = html.Div(id='sync-div', # This is the sync box
                    children=[sync_wrapdiv],
                    style={
                        'text-align': 'center',
                        'background-color':'rgba(255, 255, 255, 0.6)',
                        'position':'fixed',
                        'width':'100%',
                        'height':'100%',
                        'z-index':'1000',
                        'padding-top':'40vh',
                        'display':'none',
                    },
                    )

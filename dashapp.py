import dash
import dash_core_components as dcc
import dash_html_components as html
import random
from dash.dependencies import Input, State, Output, Event
from geopy import geocoders
from plotly import graph_objs as go
import plotly
plotly.plotly.sign_in('ryanmusa', 'Z3jyFvLhvvNAXdAU0Jd2')


# Dog fields
from find_pets.query_petfinder import list_breeds, find_dogs
DOG_BREEDS = list_breeds('dog')

gn = geocoders.GeoNames(username='ryanmusa')
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoicnlhbm11c2EiLCJhIjoiY2ppYXM0Znk5MTd5YjNwcDA4N2lwcmpkeiJ9.Eppny8F_7fArZ0D0wLd9Cw'


"""
html.Div('Let\'s find a dog to adopt near...'),
dcc.Input( 
    id='location-input',
    placeholder='Enter a location',
    type='text',
    value='10027'
),
html.Div('Dogs to search for: '),

dcc.Dropdown(
    id='dog-dropdown',
    options=[{'label':breed, 'breed-value':breed} for breed in DOG_BREEDS],
    value='Great Pyrenees',
    multi=True,
    searchable=True
)#,

html.Button(id='find-dogs-button', type='submit', children='Let\'s find some dogs!'),
html.Div(id='debug-container'),
dcc.Graph(id='main_graph'),#, figure=fig),
html.Div(id='dogs-json-cache'),#, style={'display': 'none'}),
html.Div(id='breeds-list')#, style={'display': 'none'})
"""


layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Adoptable Dogs',
    mapbox=dict(
        accesstoken=MAPBOX_ACCESS_TOKEN,
        style="dark",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)
fig = dict(data=[], layout=layout)


### Layout:
"""
dcc.Dropdown(
    id='dog-dropdown',
    options=[{'label':breed, 'breed-value':breed} for breed in DOG_BREEDS],
    value='Great Pyrenees',
    multi=True,
    searchable=True
),
html.Div(id='breeds-list'),#, style={'display': 'none'})
dcc.Graph(id='main_graph', figure=fig),
html.Img(id='image')
"""


"""
html.Div('Dogs to search for: '),
dcc.Dropdown(
    id='dog-dropdown',
    options=[{'label':breed, 'breed-value':breed} for breed in DOG_BREEDS],
    value='Great Pyrenees',
    multi=True,
    searchable=True
),
html.Div(id='debug-container'),
html.Div(id='dogs-json-cache'),#, style={'display': 'none'}),
html.Div(id='breeds-list'),#, style={'display': 'none'})
"""

app = dash.Dash()
app.title = 'Happy Birthday Babby!'
app.scripts.config.serve_locally=True
app.layout = html.Div([
    html.Div('Let\'s find a dog to adopt near...'),
    dcc.Input( 
        id='location-input',
        placeholder='Enter a location',
        type='text',
        value='95051'
    ),
    html.Button(id='find-dogs-button', type='submit', children='Let\'s find some dogs!'),
    dcc.Graph(id='main_graph', figure=fig),
    html.A(html.Img(id='image'), id='image-link', href='')

])

@app.callback(
    Output('image-link', 'href'),
    [Input('main_graph', 'clickData')]
)
def update_dog_link(clickData):
    print('Attempting to update URL...') 
    if clickData:
        data = clickData['points']
        if data:
            dog_url = 'https://www.petfinder.com/petdetail/' + data[0]['customdata'][0]
            #print("Selected URL: "+url)
            return dog_url
    return "https://s3.amazonaws.com/cdn-origin-etr.akc.org/wp-content/uploads/2017/11/12200322/Great-Pyrenees-on-White-031.jpg"

@app.callback(
    Output('image', 'src'),
    [Input('main_graph', 'clickData')]
)
def update_image_src(clickData):
    print('Attempting to update URL...') 
    if clickData:
        data = clickData['points']
        if data:
            img_url = data[0]['customdata'][1]
            #print("Selected URL: "+url)
            return img_url
    return "https://vignette.wikia.nocookie.net/uncyclopedia/images/4/44/White_square.png/revision/latest?cb=20061003200043"



"""
@app.callback(
    Output('dogs-json-cache', 'children'),
    [Input('dog-dropdown', 'value')],
    [State('location-input', 'value')]
)
def update_data_cache(breeds, location):
    return 'Updating cache for dogs near {0} that are of breeds: "{1}"'.format(location, breeds)


@app.callback(
    Output('debug-container', 'children'),
    [Input('find-dogs-button', 'n_clicks')],
    [State('location-input', 'value'), State('dog-dropdown', 'value')]
)
def update_output(n_clicks, location, breeds):
    return 'We are looking for dogs near {0} that are of breeds: "{1}"'.format(location, breeds)
"""

def get_traces(zip_code, breeds):
    traces = []

    if len(zip_code) is 5 and zip_code.isdigit():
        for breed in breeds:
            breed_dogs = []
            dogs = find_dogs(zip_code, breed)
            for dog in dogs:
                if dog.location and dog.photo:
                    breed_dogs.append(dog)
            
            traces.append(
                go.Scattermapbox(
                    lat=[d.location.latitude + random.random()*.01 - .005 for d in breed_dogs],
                    lon=[d.location.longitude + random.random()*.01 - .005 for d in breed_dogs],
                    #text=[d.name + random.random()*.01 - .005 for d in breed_dogs],
                    mode='markers',
                    marker=dict(
                        size=14
                    ),
                    name=breed,
                    legendgroup=breed,
                    customdata=[[d.id, d.photo] for d in breed_dogs],
                    hovertext=[d.name for d in breed_dogs],
                    hoverinfo="text"
                )
            )

    return traces


@app.callback(
    Output('main_graph', 'figure'),
    [Input('find-dogs-button', 'n_clicks')],
    [State('location-input', 'value')]
)
def center_main_figure(n_clicks, location_desc):
    breeds = ['Great Pyrenees', 'Bernese Mountain Dog', 'Golden Retriever', 
                'Newfoundland Dog', 'Nova Scotia Duck Tolling Retriever',
                'Greater Swiss Mountain Dog']
    traces = get_traces(location_desc, breeds)

    if len(location_desc) is 5 and location_desc.isdigit():
        zip_code = location_desc
        location = gn.geocode(zip_code+" USA")
        if not location:
            location = gn.geocode(zip_code)
    else:
        if "USA" not in location_desc:
            location = gn.geocode(location_desc+" USA")
        if not location:
            location = gn.geocode(location_desc)

    print(location)
    if location:
        layout['mapbox']['center']['lat'] = location.latitude
        layout['mapbox']['center']['lon'] = location.longitude
        layout['mapbox']['zoom'] = 7
    else:
        layout['mapbox']['center']['lat'] = 45.5
        layout['mapbox']['center']['lon'] = -73.5
        layout['mapbox']['zoom'] = 7
    
    
    figure = dict(data=traces, layout=layout)
    return figure



if __name__ == '__main__':
    app.run_server()
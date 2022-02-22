"""Routes for parent Flask app."""
from flask import current_app as app, flash, redirect
import dash
import os
import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px

import firebase_admin

from flask import Flask, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from firebase_admin import credentials, firestore, initialize_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange

topbar = Navbar(
    View('News', 'get_news'),
    View('Live', 'get_live'),
    View('Programme', 'get_programme'),
    View('Classement', 'get_classement'),
    View('Contact', 'get_contact'),
    )

# registers the "top" menubar
nav = Nav()
nav.register_element('top', topbar)

app = Flask(__name__)
Bootstrap(app)

cred = credentials.Certificate("key.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
company_funding_ref = db.collection('company_funding_2')
company_funding_docs = db.collection('company_funding_2').stream()
company_funding_dict = list(map(lambda x: x.to_dict(), company_funding_docs))
data = pd.DataFrame(company_funding_dict)
data["fundedDate"] = pd.to_datetime(data["fundedDate"], format="%d-%b-%y")
data.sort_values("fundedDate", inplace=True)

class Record(object):
    def __init__(self, name, numEmps, category, city, state, fundedDate, raisedAmt, currency, round):
        self.name = name
        self.numEmps = numEmps
        self.category = category
        self.city = city
        self.state = state
        self.fundedDate = fundedDate
        self.raisedAmt = raisedAmt
        self.currency = currency
        self.round = round

    def __repr__(self):
        return(
            f'Record(\
                name={self.name}, \
                numEmps={self.numEmps}, \
                category={self.category}, \
                city={self.city}, \
                state={self.state}\
                fundedDate={self.fundedDate}\
                raisedAmt={self.raisedAmt}\
                currency={self.currency}\
                round={self.round}\
            )'
        )

# +++++++++++++++++++++++
# forms with Flask-WTF

# form for add_record and edit_or_delete
# each field includes validation requirements and messages
class AddRecord(FlaskForm):
    # id used only by update/edit
    record_type = SelectField('New record or updating existing record?',
        choices=[ ('new', 'New'), ('update','Update existing')],
        default='new')
    id_field = StringField(
        'Record ID (for updates)',
        default='')
    name = StringField(
        'Company name',
        [InputRequired()])
    numEmps = IntegerField(
        'Number of employees',
        default=1)
    category = SelectField('Company category',
        choices=[('', ''), ('biotech', 'Biotechnology'),
        ('cleantech', 'Clean Technology'),
        ('consulting', 'Consulting'),
        ('hardware', 'Hardware'),
        ('mobile', 'Mobile'),
        ('software', 'Software'),
        ('web', 'Web'),
        ('other', 'Other')],
        default='web')
    city = SelectField('Company location (City)',
        choices=[ ('', ''), ('acton','Acton'), ('agoura hills','Agoura Hills'), ('alameda','Alameda'), ('albuquerque','Albuquerque'), ('aliso viejo','Aliso Viejo'), ('allentown','Allentown'), ('american fork','American Fork'), ('andover','Andover'), ('ann arbor','Ann Arbor'), ('arlington','Arlington'), ('ashland','Ashland'), ('astoria','Astoria'), ('atlanta','Atlanta'), ('austin','Austin'), ('baltimore','Baltimore'), ('bellevue','Bellevue'), ('berkeley','Berkeley'), ('berwyn','Berwyn'), ('beverly hills','Beverly Hills'), ('boca raton','Boca Raton'), ('boise','Boise'), ('boston','Boston'), ('bothell','Bothell'), ('boulder','Boulder'), ('brisbane','Brisbane'), ('brooklyn','Brooklyn'), ('brooklyn, new york','Brooklyn, New York'), ('burbank','Burbank'), ('burlingame','Burlingame'), ('burlington','Burlington'), ('cambridge','Cambridge'), ('campbell','Campbell'), ('carlsbad','Carlsbad'), ('carmel','Carmel'), ('carrollton','Carrollton'), ('cary','Cary'), ('centennial','Centennial'), ('chantilly','Chantilly'), ('charlotte','Charlotte'), ('chevy chase','Chevy Chase'), ('chicago','Chicago'), ('colorado springs','Colorado Springs'), ('corvallis','Corvallis'), ('culver city','Culver City'), ('cupertino','Cupertino'), ('dallas','Dallas'), ('del mar','Del Mar'), ('denver','Denver'), ('durham','Durham'), ('edison','Edison'), ('el segundo','El Segundo'), ('emeryville','Emeryville'), ('estero','Estero'), ('eugene','Eugene'), ('fairfield','Fairfield'), ('fort lauderdale','Fort Lauderdale'), ('foster city','Foster City'), ('gilbert','Gilbert'), ('grand forks','Grand Forks'), ('hamden','Hamden'), ('hartford','Hartford'), ('hollywood','Hollywood'), ('houston','Houston'), ('indianapolis','Indianapolis'), ('inglewood','Inglewood'), ('ir vine','Ir vine'), ('irvine','Irvine'), ('ithaca','Ithaca'), ('jersey city','Jersey City'), ('kennebunk','Kennebunk'), ('kennewick','Kennewick'), ('king of prussia','King of Prussia'), ('kirkland','Kirkland'), ('la canada','La Canada'), ('la jolla','La Jolla'), ('lakeland','Lakeland'), ('largo','Largo'), ('leesburg','Leesburg'), ('lehi','Lehi'), ('lexington','Lexington'), ('lindon','Lindon'), ('livermore','Livermore'), ('livingston','Livingston'), ('los altos','Los Altos'), ('los angeles','Los Angeles'), ('los gatos','Los Gatos'), ('marina del rey','Marina Del Rey'), ('maynard','Maynard'), ('mclean','McLean'), ('media','Media'), ('menlo park','Menlo Park'), ('metuchen','Metuchen'), ('miami','Miami'), ('mill valley','Mill Valley'), ('millbrae','Millbrae'), ('mishawaka','Mishawaka'), ('monterey','Monterey'), ('morrisville','Morrisville'), ('mountain view','Mountain View'), ('n. branch','N. Branch'), ('naples','Naples'), ('needham','Needham'), ('new  york','New  York'), ('new haven','New Haven'), ('new london','New London'), ('new orleans','New Orleans'), ('new york','New York'), ('new york city','New York City'), ('new yorl','New Yorl'), ('newport beach','Newport Beach'), ('newton','Newton'), ('north andover','North Andover'), ('north brunswick','North Brunswick'), ('north palm beach','North Palm Beach'), ('norwalk','Norwalk'), ('oakland','Oakland'), ('oakmont','Oakmont'), ('omaha','Omaha'), ('orem','Orem'), ('orlando','Orlando'), ('palo alto','Palo Alto'), ('pasadena','Pasadena'), ('patchogue','Patchogue'), ('peoria','Peoria'), ('petaluma','Petaluma'), ('philadelphia','Philadelphia'), ('phoenix','Phoenix'), ('pittsburgh','Pittsburgh'), ('placentia','Placentia'), ('plano','Plano'), ('pleasanton','Pleasanton'), ('portland','Portland'), ('providence','Providence'), ('provo','Provo'), ('raleigh','Raleigh'), ('redmond','Redmond'), ('redwood city','Redwood City'), ('redwood shores','Redwood Shores'), ('reston','Reston'), ('richardson','Richardson'), ('richfield','Richfield'), ('rockville','Rockville'), ('rolling meadows','Rolling Meadows'), ('roslyn heights','Roslyn Heights'), ('salt lake city','Salt Lake City'), ('san bruno','San Bruno'), ('san carlos','San Carlos'), ('san diego','San Diego'), ('san francisco','San Francisco'), ('san jose','San Jose'), ('san mateo','San Mateo'), ('san ramon','San Ramon'), ('sandy','Sandy'), ('santa ana','Santa Ana'), ('santa barbara','Santa Barbara'), ('santa clara','Santa Clara'), ('santa monica','Santa Monica'), ('sausalito','Sausalito'), ('schaumburg','Schaumburg'), ('scottsdale','Scottsdale'), ('seattle','Seattle'), ('shelton','Shelton'), ('sherman oaks','Sherman Oaks'), ('silver spring','Silver Spring'), ('skokie','Skokie'), ('solana beach','Solana Beach'), ('south san francisco','South San Francisco'), ('st. louis','St. Louis'), ('stamford','Stamford'), ('sterling','Sterling'), ('sunnyvale','Sunnyvale'), ('tampa','Tampa'), ('tempe','Tempe'), ('toledo','Toledo'), ('venice','Venice'), ('vienna','Vienna'), ('waltham','Waltham'), ('washington','Washington'), ('washinton','Washinton'), ('watertown','Watertown'), ('wayne','Wayne'), ('wellesley','Wellesley'), ('west hollywood','West Hollywood'), ('west palm beach','West Palm Beach'), ('westborough','Westborough'), ('westlake village','Westlake Village'), ('westport','Westport'), ('westwood','Westwood'), ('winston-salem','Winston-Salem'), ('woburn','Woburn'), ('woodside','Woodside'),
        ('other', 'Other') ],
        default='other')
    state = SelectField('Company location (State)',
        choices=[ ('', ''), ('az','AZ'), ('ca','CA'), ('co','CO'), ('ct','CT'), ('dc','DC'), ('fl','FL'), ('ga','GA'), ('ia','IA'), ('id','ID'), ('il','IL'), ('in','IN'), ('la','LA'), ('ma','MA'), ('md','MD'), ('me','ME'), ('mi','MI'), ('mn','MN'), ('mo','MO'), ('nc','NC'), ('nd','ND'), ('ne','NE'), ('nj','NJ'), ('nm','NM'), ('ny','NY'), ('oh','OH'), ('or','OR'), ('pa','PA'), ('ri','RI'), ('tn','TN'), ('tx','TX'), ('ut','UT'), ('va','VA'), ('wa','WA'),
        ('other', 'Other') ],
        default='other')
    fundedDate = StringField(
        'Funded Date (DD-Mmm-YY)',
        default='01-Jan-22')
    raisedAmt = IntegerField('Raised amount',[InputRequired()])
    currency = SelectField('Raised currency',
        choices=[ ('', ''), ('cad','CAD'), ('eur','EUR'), ('usd','USD'),
        ('other', 'Other') ],
        default='usd')
    round = SelectField('Funding round',
        choices=[ ('', ''), ('a','a'), ('angel','angel'), ('b','b'), ('c','c'), ('d','d'), ('debt_round','debt_round'), ('e','e'), ('seed','seed'), ('unattributed','unattributed'),
        ('other', 'Other') ],
        default='')
    submit = SubmitField('Add/Update Record')

# small form
class DeleteForm(FlaskForm):
    id = StringField('Record ID (for updates)', [InputRequired()])
    submit = SubmitField('Delete Record')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/download")
def download():
    return render_template('download.html')

@app.route("/add/", methods=["GET", "POST", 'PUT'])
def add_record():
    form = AddRecord()
    new_doc_ref = request.args.get('new_doc_ref')
    
    if request.method == 'POST':
        # if request.form['submit'] == 'add':
        if form.validate_on_submit():
            print(request.form['record_type'])
            if request.form['record_type'] == 'update':
                try:
                    record = {
                        'id' : request.form['id_field'],
                        'company' : request.form['name'],
                        'numEmps' : request.form['numEmps'],
                        'category' : request.form['category'],
                        'city' : request.form['city'],
                        'state' : request.form['state'],
                        'fundedDate' : request.form['fundedDate'],
                        'raisedAmt' : request.form['raisedAmt'],
                        'currency' : request.form['currency'],
                        'round' : request.form['round']
                    }
                    company_funding_ref.document(record['id']).set(record)
                    flash('Your changes have been saved.')
                    return redirect(url_for('add_record', new_doc_ref=record['id']))
                except Exception as e:
                    return f"An Error Occured: {e}"
            else:
                try:
                    record = {
                        'company' : request.form['name'],
                        'numEmps' : request.form['numEmps'],
                        'category' : request.form['category'],
                        'city' : request.form['city'],
                        'state' : request.form['state'],
                        'fundedDate' : request.form['fundedDate'],
                        'raisedAmt' : request.form['raisedAmt'],
                        'currency' : request.form['currency'],
                        'round' : request.form['round']
                    }
                    new_doc = company_funding_ref.add(record)
                    print(new_doc[1].id)
                    new_doc_ref = new_doc[1].id
                    # print('Successfully added a record with ID {new_doc_ref[1].id}!')
                    return redirect(url_for('add_record', new_doc_ref=new_doc[1].id))
                except Exception as e:
                    return f"An Error Occured: {e}"
        return redirect(url_for('add_record'), new_doc_ref=new_doc_ref)
        # elif request.form['submit'] == 'delete':
        #     print('deleting')
    return render_template('add_record.html', form = form, variable=new_doc_ref)
    # return render_template('add_record.html')
    # try:
    #     record = {
    #         u'company' : u'test_company', 
    #         u'numEmps' : 10, 
    #         u'category' : u'web', 
    #         u'city' : u'San Francisco', 
    #         u'state' : u'CA', 
    #         u'fundedDate' : u'01-Oct-07',
    #         u'raisedAmt' : 10000, 
    #         u'currency' : u'USD', 
    #         u'round' : u'a'
    #     }
    #     company_funding_ref.add(record)
    #     return jsonify({"success": True}), 200
    # except Exception as e:
    #     return f"An Error Occured: {e}"

    # return '''
    #           <form method="POST">
    #               <div><label>Language: <input type="text" name="language"></label></div>
    #               <div><label>Framework: <input type="text" name="framework"></label></div>
    #               <input type="submit" value="Submit">
    #           </form>'''

    # form1 = AddRecord()
    # if form1.validate_on_submit():
    #     name = request.form['name']
    #     numEmps = request.form['numEmps']
    #     category = request.form['category']
    #     city = request.form['city']
    #     state = request.form['state']
    #     fundedDate = request.form['fundedDate']
    #     raisedAmt = request.form['raisedAmt']
    #     currency = request.form['currency']
    #     round = request.form['round']
    #     # the data to be inserted into Sock model - the table, socks
    #     record = Record(name, numEmps, category, city, state, fundedDate, raisedAmt, currency, round)
    #     # adds record to database
    #     company_funding_ref.add(record.to_dict())
    #     # create a message to send to the template
    #     message = f"The data for sock {name} has been submitted."
    #     return render_template('add_record.html', message=message)
    # else:
    #     # show validaton errors
    #     # see https://pythonprogramming.net/flash-flask-tutorial/
    #     for field, errors in form1.errors.items():
    #         for error in errors:
    #             flash("Error in {}: {}".format(
    #                 getattr(form1, field).label.text,
    #                 error
    #             ), 'error')
    #     return render_template('add_record.html', form1=form1)
        
        # id = request.json['id']
        # company_funding_ref.document(id).set(request.json)
        # return jsonify({"success": True}), 200
    # except Exception as e:
    #     print("An Error Occured: {e}")

@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    try:
        # Check if ID was passed to URL query
        doc_id = request.args.get('id') 
        if doc_id:
            doc = company_funding_ref.document(doc_id).get()
            return jsonify(doc.to_dict()), 200
        else:
            all_docs = [doc.to_dict() for doc in company_funding_ref.stream()]
            return jsonify(all_docs), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        id = request.json['id']
        company_funding_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        print("An Error Occured: {e}")

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    """
        delete() : Delete a document from Firestore collection
    """
    form1 = DeleteForm()
    if request.method == 'POST':
        try:
            id = request.form['id']
            print(id)
            company_funding_ref.document(id).delete()
            flash('The record has been successfully deleted.')
            return redirect(url_for('delete'))
        except Exception as e:
            return f"An Error Occured: {e}"
    return render_template('delete_record.html', form = form1)
    # try:
    #     # Check for ID in URL query
    #     company_id = request.args.get('id')
    #     company_funding_ref.document(company_id).delete()
    #     return jsonify({"success": True}), 200
    # except Exception as e:
    #     print("An Error Occured: {e}")

external_stylesheets = [
        {
            "href": "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap",
            "rel": "stylesheet",
        },
    ]
dash_app = dash.Dash(
    server=app,
    routes_pathname_prefix='/dashapp/', 
    external_stylesheets=external_stylesheets
)
dash_app.layout = html.Div(
        children=[
            html.Nav(
                className = "navbar navbar-expand-lg navbar-light bg-light",
                children=[
                    html.A('Home', className="nav-item nav-link", href='/'),
                    html.A('Analyzer', className="nav-item nav-link", href='/dashapp/'),
                    html.A('Add/Update a record', className="nav-item nav-link", href='/add'),
                    html.A('Delete a record', className="nav-item nav-link", href='/delete')
                    ],
                    ),
            html.Div(
                children=[
                    html.H1(children="Funding Analyzer", className="header-title"),
                    html.H1(children="CFMT", className="header-title"),
                    html.P(
                        children="Analyzer tool"
                        " for company funding"
                        " in the US.",
                        className="header-description",
                    ),
                ],
                className="header",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(children="State", className="menu-title"),
                            dcc.Dropdown(
                                id="state-filter",
                                options=[
                                    {"label": state, "value": state}
                                    for state in np.sort(data.state.unique())
                                ],
                                value="CA",
                                clearable=True,
                                className="dropdown",
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Div(children="Category", className="menu-title"),
                            dcc.Dropdown(
                                id="category-filter",
                                options=[
                                    {"label": category, "value": category}
                                    for category in data.category.unique() if not pd.isnull(category)
                                ],
                                value="web",
                                clearable=True,
                                className="dropdown",
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                children="Date Range", className="menu-title"
                            ),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=data.fundedDate.min().date(),
                                max_date_allowed=data.fundedDate.max().date(),
                                start_date=data.fundedDate.min().date(),
                                end_date=data.fundedDate.max().date(),
                            ),
                        ]
                    ),
                ],
                className="menu",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id="funding-chart",
                            config={"displayModeBar": False},
                        ),
                        className="card",
                    ),
                    html.Div(
                        children=dcc.Graph(
                            id="category-chart"
                        ),
                    ),
                ],
                className="wrapper",
            ),
        ]
    )


@dash_app.callback(
    [Output("funding-chart", "figure"), Output("category-chart", "figure")],
    [
        Input("state-filter", "value"),
        Input("category-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(state, category, start_date, end_date):
    category_filter = True  #get all categories if category is empty
    if category:
        category_filter = (data.category == category)
    mask = (
        (data.state == state)
        & (data.category == category_filter)
        & (data.fundedDate >= start_date)
        & (data.fundedDate <= end_date)
    )
    filtered_data = data.loc[mask, :]
    # pie_filtered = data.loc[data['category']==category]
    funding_chart_figure = {
        "data": [
            {
                "x": filtered_data["fundedDate"],
                "y": filtered_data["raisedAmt"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Raised fundings by date",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    category_chart_figure = px.pie(data_frame=filtered_data, values='raisedAmt', names='category', title='Raised funding by category')
    return funding_chart_figure, category_chart_figure

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
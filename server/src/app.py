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

@app.route("/delete_success")
def delete_success():
    return render_template('delete_success.html')

@app.route("/add_success/<doc_id>")
def add_success(doc_id):
    return render_template('add_success.html', variable=doc_id)

@app.route("/delete_error")
def delete_error():
    return render_template('delete_error.html')

@app.route("/add/", methods=["GET", "POST", 'PUT'])
def add_record():
    form = AddRecord()
    new_doc_ref = request.args.get('new_doc_ref')
    
    if request.method == 'POST':
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
                    return redirect(url_for('add_success', doc_id=new_doc[1].id))
                except Exception as e:
                    return f"An Error Occured: {e}"
        return redirect(url_for('add_record'), new_doc_ref=new_doc_ref)
    return render_template('add_record.html', form = form)

@app.route('/list', methods=['GET'])
def read():
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
            return redirect(url_for('delete_success'))
        except Exception as e:
            return redirect(url_for('delete_error'))
    return render_template('delete_record.html', form = form1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
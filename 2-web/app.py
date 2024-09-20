from flask import Flask, render_template, request, Response
import pandas
import geopandas
import sqlite3
import json
from shapely import wkb
from matplotlib import rcParams

app = Flask(__name__)
app.config.from_pyfile('config.py')

# auto layout for graphs
rcParams.update({'figure.autolayout': True})

# start database connection
conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map_home/")
def map_home():
    """
    Generates the filter list and renders the map.html template
    """
    provinces = cursor.execute("select distinct(province) from commune").fetchall()
    provinces = [provinces[0] for provinces in provinces]

    # generate preview map
    map = cursor.execute("select geometry from commune where province like 'santiago';")

    # format the data into a dataframe
    dataframe = pandas.DataFrame(map, columns=['geometry'])
    dataframe['geometry'] = dataframe['geometry'].apply(wkb.loads) # type: ignore
    geodataframe = geopandas.GeoDataFrame(data=dataframe, geometry='geometry', crs='EPSG:3857') # type: ignore
 
    map = geodataframe.explore(cmap='OrRd', legend=True)._repr_html_()

    return render_template("map.html", provinces=provinces, map=map)

@app.route("/map_index_reports/<province>/")
def map_index_reports(province):
    # return list of reports for the selected province
    cursor.execute("""
    select report.name
    from report
    join data on data.report_id = report.id
    join commune on commune.id = data.commune_id
    where commune.province = ?
    group by report.id
    having sum(data.value) > 0;
    """, (province,))

    reports = cursor.fetchall()

    return json.dumps({"reports": reports})

@app.route("/map_index_years/<province>/<report>/")
def map_index_years(province, report):
    # return list of years for the selected report and province
    cursor.execute("""
    select data.year
    from data
    join commune on data.commune_id = commune.id
    join report on data.report_id = report.id
    where
        commune.province = ? AND
        report.name = ?
    group by year
    having sum(data.value) > 0;
    """, (province, report,))

    years = cursor.fetchall()

    print(years)

    return json.dumps({"years": years})

@app.route("/map/<province>/<report>/<year>/")
def map(report, year, province):
    """
    Called from map.html, used to generate the map which is sent dynamically to the client
    """
    
    cursor.execute("""
    select commune.name, SUM(value), commune.geometry
    from data
    join report on data.report_id = report.id
    join commune on data.commune_id = commune.id
    where
        report.name = ? and
        data.year = ? and
        province like ?
    group by commune.id;
    """, (report, year, province))
    communes = cursor.fetchall()

    # format the data into a dataframe
    dataframe = pandas.DataFrame(communes, columns=['name', 'count', 'geometry'])
    dataframe['geometry'] = dataframe['geometry'].apply(wkb.loads) # type: ignore
    geodataframe = geopandas.GeoDataFrame(data=dataframe, geometry='geometry', crs='EPSG:3857') # type: ignore

    # create the heatmap into a folium map
    map = geodataframe.explore(column='count', cmap='OrRd', legend=True)

    # return the map as html
    return map._repr_html_() 
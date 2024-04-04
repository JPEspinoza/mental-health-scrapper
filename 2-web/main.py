from flask import Flask, render_template, request, Response
import pandas
import geopandas
import sqlite3
import io
from shapely import wkb
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

app = Flask(__name__)

def database() -> sqlite3.Cursor:
    conn = sqlite3.connect("/db.sqlite3")
    return conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/consultations_by_year_province")
def consultations_by_year_province():
    # heatmap of number of consultas by age in any year
    """
    Corresponde a la Intervención ambulatoria individual o grupal, realizada por un profesional, técnico y/o gestor comunitario. La intervención incluye consejería, evaluación y confirmación diagnóstica, elaboración de plan de cuidados integrales, psicoeducación, acciones de emergencia y desastres, entre otras prestaciones.
    Estas atenciones que se describen en este apartado, se analizan desde un punto de vista territorial a nivel nacional, región y Servicio de Salud. Además, se describe los resultados según sexo, grupo de edad y tipo de prestación (profesional/técnico) según año y mes.
    Fuente: REMA 06
    """

    # get the year from the url
    year = request.args.get('year', default=2023, type=int)
    province = request.args.get('province', default='Santiago', type=str)

    # get the data from the database
    cursor = database()
    cursor.execute("""
        select commune.name, SUM(value), commune.geometry
        from report
        join commune on report.commune_id = commune.id
        where report = 'MentalByGender' and
            year = ? and
            province like ?
        group by commune.id
    """, (year, province))
    communes = cursor.fetchall()

    # format the data into a dataframe
    dataframe = pandas.DataFrame(communes, columns=['name', 'count', 'geometry'])
    dataframe['geometry'] = dataframe['geometry'].apply(wkb.loads)
    geodataframe = geopandas.GeoDataFrame(data=dataframe, geometry='geometry', crs='EPSG:3857') # type: ignore

    # create the heatmap into a folium map
    map = geodataframe.explore(column='count', cmap='OrRd', legend=True)

    # return the map as html
    return map._repr_html_() 

@app.route("/consultations_per_1k_by_year_province")
def consultations_per_1k_by_year_province():
    # get the year from the url
    year = request.args.get('year', default=2023, type=int)
    province = request.args.get('province', default='Santiago', type=str)

    # get the data from the database
    cursor = database()
    cursor.execute("""
        select commune.name, SUM(report.value)*1000 / commune.population, commune.geometry
        from report
        join commune on report.commune_id = commune.id
        where report = 'MentalByGender' and
            year = ? and
            province like ?
        group by commune.id
    """, (year, province))
    communes = cursor.fetchall()

    # format the data into a dataframe
    dataframe = pandas.DataFrame(communes, columns=['name', 'count', 'geometry'])
    dataframe['geometry'] = dataframe['geometry'].apply(wkb.loads)
    geodataframe = geopandas.GeoDataFrame(data=dataframe, geometry='geometry', crs='EPSG:3857') # type: ignore

    # create the heatmap into a folium map
    map = geodataframe.explore(column='count', cmap='OrRd', legend=True)

    # return the map as html
    return map._repr_html_() 

@app.route("/consultations_age_by_commune")
def consultations_age_by_commune():
    # consultations per age group, per year, for commune
    commune = request.args.get('commune', default='Santiago', type=str)

    cursor = database()
    cursor.execute(f"""
    SELECT cohort, SUM(value), year
    FROM report
    JOIN commune ON report.commune_id = commune.id
    WHERE commune.name like ? AND
          report = 'MentalByAge' 
    GROUP BY cohort, year
    """, (commune,))
    data = cursor.fetchall()

    data = pandas.DataFrame(data, columns=["cohort", "value", "year"])
    # make bar plot, y axis is value, x axis is cohort. Each bar is split into multiple bars, colored by the year
    data = data.pivot(index='year', columns='cohort', values='value')
    
    output = io.BytesIO()

    # plot data into png
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.title.set_text(f"Consultas por edad en {commune}")
    ax.axes.set_xlabel("Edad") # type: ignore
    ax.axes.set_ylabel("Consultas") # type: ignore
    data.plot(kind='bar', ax=ax)
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


@app.route('/consultations_per_month_by_commune_year')
def consultations_per_month():
    year = request.args.get('year', default=2020, type=int)
    province = request.args.get('commune', default='Penalolen', type=str)

    months = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]

    cursor = database()
    cursor.execute("""
    select cohort, sum(value) as value
    from report
    join commune on report.commune_id = commune.id
    where report.report = 'MentalByMonth' and
        commune.name like ? and
        report.year = ?
    group by cohort
    """, (province, year))
    data = cursor.fetchall()

    data = pandas.DataFrame(data, columns=["cohort", "value"])

    # sort by month
    data['cohort'] = pandas.Categorical(data['cohort'], categories=months, ordered=True)
    data = data.sort_values('cohort')

    # set cohort to index
    data = data.set_index('cohort')

    output = io.BytesIO()

    # plot data into png
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.title.set_text(f"Consultas por mes en Penalolen")
    ax.axes.set_xlabel("Mes") # type: ignore
    ax.axes.set_ylabel("Consultas") # type: ignore
    data.plot(kind='bar', ax=ax)
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')

@app.route('/establishment_location')
def establishment_location():
    # get location of all establishments in santiago
    cursor = database()
    cursor.execute("""
    SELECT establishment.name, establishment.lat, establishment.lon, sum(report.value)
    FROM establishment
    JOIN commune ON establishment.commune_id = commune.id
    left join report on report.establishment_id = establishment.id and report.report = 'MentalByGender'
    WHERE commune.province like 'Santiago'
    group by establishment.id;
    """)

    establishments = cursor.fetchall()

    establishments = pandas.DataFrame(establishments, columns=["name", "lat", "lon", "value"])
    establishments = geopandas.GeoDataFrame(
        data=establishments, 
        geometry=geopandas.points_from_xy(
            establishments['lon'],
            establishments['lat'],
            crs="EPSG:4326"
        )
    )
    map = establishments.explore()
    return map._repr_html_()

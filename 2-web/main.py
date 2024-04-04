from flask import Flask, render_template, request, Response
import pandas
import geopandas
import sqlite3
import io
from shapely import wkb
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

def database() -> sqlite3.Cursor:
    conn = sqlite3.connect("/db.sqlite3")
    return conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/consultations_by_year")
def consultations_by_year():
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
    cursor.execute(f"""
        select commune.name, SUM(value), commune.geometry
        from report
        join commune on report.commune_id = commune.id
        where report = 'MentalByGender' and
            year = {year} and
            province like '{province}'
        group by commune.id
    """)
    communes = cursor.fetchall()

    # format the data into a dataframe
    dataframe = pandas.DataFrame(communes, columns=['name', 'count', 'geometry'])
    dataframe['geometry'] = dataframe['geometry'].apply(wkb.loads)
    geodataframe = geopandas.GeoDataFrame(data=dataframe, geometry='geometry', crs='EPSG:3857') # type: ignore

    # create the heatmap into a folium map
    map = geodataframe.explore(column='count', cmap='OrRd', legend=True)

    # return the map as html
    return map._repr_html_() 

@app.route("/consultations_per_capita_by_year")
def consultations_per_capita_by_year():
    # get the year from the url
    year = request.args.get('year', default=2023, type=int)
    province = request.args.get('province', default='Santiago', type=str)

    # get the data from the database
    cursor = database()
    cursor.execute(f"""
        select commune.name, SUM(report.value)*1.0 / commune.population*1.0, commune.geometry
        from report
        join commune on report.commune_id = commune.id
        where report = 'MentalByGender' and
            year = {year} and
            province like '{province}'
        group by commune.id
    """)
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
    commune = request.args.get('commune', default='Maipu', type=str)

    cursor = database()
    cursor.execute(f"""
    SELECT cohort, SUM(value), year
    FROM report
    JOIN commune ON report.commune_id = commune.id
    WHERE commune.name like '{commune}' AND
          report = 'MentalByAge' 
    GROUP BY cohort, year
    """)
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


@app.route('/consultations_per_month')
def consultations_per_month():
    cursor = database()
    cursor.execute(f"""
    select cohort, value
    from report
    join commune on report.commune_id = commune.id
    where report.report = 'MentalByMonth' and
        commune.name = 'Aisen' and
        report.year = 2019
    """)
    data = cursor.fetchall()

    data = pandas.DataFrame(data, columns=["cohort", "value", "year"])
    # make bar plot, y axis is value, x axis is cohort. Each bar is split into multiple bars, colored by the year
    data = data.pivot(index='year', columns='cohort', values='value')

    return data.to_html()
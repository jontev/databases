# Created postgresql DB, filled with interesting data, created (very) primitive website to show results
# of three custom made queries displaying interesting phenomena in the data
# all done remotely on school server (so ssh into the server then using vim blabla)


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request
import psycopg2

db = SQLAlchemy()
conn = psycopg2.connect(dbname="cc3201", user="cc3201", password="Pahno3Poayao", host="cc3201.dcc.uchile.cl", port="5537")
cur = conn.cursor()

app=Flask(__name__)

class Consulta3(db.Model):
    state = db.Column(db.String, primary_key=True)
    share_white = db.Column(db.Float) #skiter i mellan 0 och 100
    share_black = db.Column(db.Float)
    share_native_american = db.Column(db.Float)
    share_asian = db.Column(db.Float)
    share_hispanic = db.Column(db.Float)
    ingreso = db.Column(db.Integer)

    def __repr__(self):
        return '{} {} {} {} {} {} {}'.format(self.state, self.share_white, self.share_black, self.share_native_american, self.share_asian
            ,self.share_hispanic, self.ingreso)
    def serialize(self):
        return dict(state=self.state, psw=self.share_white, psb=self.share_black, psn=self.share_native_american, psa=self.share_asian,
            psh=self.share_hispanic, ingreso=self.ingreso )

class Consulta2(db.Model):
    state =db.Column(db.String, primary_key=True)
    city=db.Column(db.String,primary_key=True)
    ranking_most_violent=db.Column(db.Integer)
    ranking_most_educated=db.Column(db.Integer)
    ranking_least_poor=db.Column(db.Integer)
   
    def __repr__(self):
        return '{} {} {} {} {}'.format(self.state, self.city, self.ranking_most_violent,self.ranking_most_educated, self.ranking_least_poor)
        
    def serialize(self):
    	return dict(state=self.state, city=self.city, ranking_most_violent=self.ranking_most_violent,ranking_most_educated=self.ranking_most_educated,
            ranking_least_poor=self.ranking_least_poor)
class Consulta1(db.Model):
    state = db.Column(db.String, primary_key=True)
    cantidad = db.Column(db.Integer)
    def __repr__(self):
        return '{} {}'.format(self.state, self.cantidad)
    def serialize(self):
        return dict(state=self.state, cantidad=self.cantidad)



@app.route('/consulta3', methods=['GET','POST'])
def consulta3():

    res = []
    if request.method=="POST":
        state=request.form['state']
    else: return render_template('consulta3.html', results=res)

    try:
        cur.execute("""
            SELECT RazaPorEstado.state, psw, psb, psn, psa, psh, ipe.ingreso FROM RazaPorEstado, (SELECT state, FLOOR(AVG(median_income)) AS ingreso FROM
            socioeconomics GROUP BY state) AS ipe WHERE RazaPorEstado.state=ipe.state AND RazaPorEstado.state= (%s)
            """, (state,))
        rows = cur.fetchall()
        for row in rows:
            c3 = Consulta3(state=row[0], share_white=row[1], share_black=row[2], share_native_american=row[3], share_asian=row[4],
                share_hispanic=row[5], ingreso=row[6])
            res.append(c3)
        return render_template('consulta3.html', results=res)
    except Exception as e:
        print(e)
        cur.execute("ROLLBACK")
        conn.close()
        return "fail"
@app.route('/consulta2', methods=['GET'])
def consulta2():
    res = []
    try:
        cur.execute(
        """SELECT mostviolent.state, mostviolent.city, mostviolent.rank as ranking_most_violent, foo.edu as ranking_most_educated, 
        foo.edu as ranking_least_poor FROM mostviolent JOIN (SELECT rankedu.state as state, rankedu.city as city,
        rankedu.rank as edu, rankpov.rank as pov FROM rankedu JOIN rankpov ON rankedu.city=rankpov.city AND rankedu.state=rankpov.state
        ) AS foo ON mostviolent.city=foo.city AND mostviolent.state=foo.state""")
        rows = cur.fetchall()

        for row in rows:
            c2 = Consulta2(state=row[0], city=row[1], ranking_most_violent=row[2], ranking_most_educated=row[3], ranking_least_poor=row[4])
            res.append(c2)
        return render_template('consulta2.html', results=res)
    except Exception as e:
        cur.execute("ROLLBACK")
        conn.close()
        return "try again"
@app.route('/consulta1', methods=['GET','POST'])
def consulta1():
    res = []
    if request.method=="POST":
        state=request.form['state']
    else:
        return render_template('consulta1.html', results=res)
    try:
        cur.execute("""
            SELECT state, COUNT(state) AS cantidad FROM killings WHERE state= (%s) GROUP BY state"""
            , (state,))
        rows = cur.fetchall()
        for row in rows:
            c1 = Consulta1(state=row[0], cantidad=row[1])
            res.append(c1)
        return render_template('consulta1.html', results=res)
    except Exception as e:
        cur.execute("ROLLBACK")
        conn.close()
        return "lol"

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')




if __name__=="__main__":
	app.run()
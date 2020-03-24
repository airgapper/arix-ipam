from flask import Flask, render_template, request, Markup, redirect
from database import IPAMDatabase

app = Flask(__name__)
db = IPAMDatabase("mongodb://localhost:27017")


@app.route("/")
def route_index():
    assigned = ""
    for _prefix in db.get():
        assigned += """
        <tr>
            <td>""" + str(_prefix["inet6num"]) + """</td>
            <td>""" + str(_prefix["netname"]) + """</td>
            <td>""" + str(_prefix["descr"]) + """</td>
            <td><a href="/delete?prefix=""" + str(_prefix["inet6num"]) + """" class="btn btn-danger">Delete</a></td>
        </tr>
        """

    return render_template("index.html",
                           assigned=Markup(assigned),
                           next_prefix=db.available[0],
                           available=len(db.available))


@app.route("/assign", methods=["GET", "POST"])
def route_assign():
    if request.method == "GET":
        return redirect("/")
    elif request.method == "POST":
        callsign = request.form["callsign"]
        purpose = request.form["purpose"]

        if (callsign != "") and (purpose != ""):
            db.assign("ARIX-" + callsign, "ARIX " + callsign + " allocation for " + purpose)

        return redirect("/")


@app.route("/delete")
def route_delete():
    db.delete(request.args.get("prefix"))
    return redirect("/")


app.run("localhost", port=5000, debug=True)

import os
import re
from flask import *
from werkzeug.utils import secure_filename
from Opencv.houghtest import mainhough, although
from pubchemprops.pubchemprops import get_second_layer_props

app=Flask(__name__)
app.config["UPLOAD_FOLDER"]="static"
app.secret_key="sdafsdf"
# global chem_name
# chem_name=""
def boldletters(letstr):
    liststr=list(letstr)
    final_lore=[]
    positions=[]
    for l in liststr:
        if l.isalpha():
            final_lore.append(l)
        else:
            positions.append(l)
    return " ".join(final_lore),"".join(positions)
@app.route("/")
def home_page():
    return render_template("home.html")
@app.route("/home",methods=["get","post"])
def main_page():
    image_link=""
    img_file=request.files.get("image_select")
    if img_file:
        filename=secure_filename(img_file.filename)
        image_link=os.path.join(app.config["UPLOAD_FOLDER"],filename)
        img_file.save(image_link)
    # print(image_link)
    houghcompute,imgstring=although(f"{image_link}")
    c_letters,c_pos=imgstring
    clearprops="Boiling Point, Melting Point, Flash Point, Solubility, Density, Vapor Density, Vapor Pressure, Viscosity, Heat of Combustion, Heat of Vaporization, Ionization Potential, Dissociation Constants".split(", ")
    chem_name=c_letters.replace(" ","-")
    session["chemname"]=chem_name
    session["img"]=image_link
    session["clet"]=c_letters
    session["cpos"]=c_pos
    session["choose"]=clearprops
    # session["path"]="static/modified_output.jpg"
    return render_template("index.html",img_url=image_link,houghed="static/modified_output.jpg",
                           curr_letters=c_letters,c_poss=c_pos,options=clearprops)
@app.route("/submit",methods=["POST"])
def get_props():
    global chem_name
    selected_props=request.form.getlist("cmpds")
    mainlist = {}
    failedprops = []
    for val in selected_props:
        # print(val)
        try:
            mainlist[val] = (
                get_second_layer_props(session.get("chemname"), [val])[val][0]["Value"]["StringWithMarkup"][0]["String"])
        except (KeyError, IndexError, TypeError):
            failedprops.append(val)
            continue
    return render_template("index.html",collected_props=mainlist,failed=failedprops,img_url=session["img"],houghed="static/modified_output.jpg",
                           curr_letters=session["clet"],c_poss=session["cpos"],options=session["choose"])

if __name__=="__main__":
    app.run(host="0.0.0.0",port=80,debug=True)
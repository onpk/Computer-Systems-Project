import pubchempy as ppy
from pubchemprops.pubchemprops import *
vals=ppy.get_compounds("O=S(=[O])(O[H])O[H]","smiles")
lore=vals[0]
#print(lore.record)
# print(vals[0].synonyms)
propstring="Wikipedia, Boiling Point, Melting Point, Flash Point, Solubility, Density, Vapor Density, Vapor Pressure, Viscosity, Heat of Combustion, Heat of Vaporization, Ionization Potential, Dissociation Constants"
mainlist={}
failedprops=[]
for val in propstring.split(", "):
    print(get_first_layer_props("1-bromo-2-methylbutane",["Complexity"]))
    try:
        mainlist[val]=(get_second_layer_props("1-bromo-2-methylbutane",[val])[val][0]["Value"]["StringWithMarkup"][0]["String"])
    except (KeyError,IndexError,TypeError):
        failedprops.append(val)
        continue
pluh=get_second_layer_props("acetic-acid",["Boiling Point"])["Boiling Point"][0]["Value"]["StringWithMarkup"][0]["String"]
pluh2=get_second_layer_props("acetic-acid",["Melting Point"])["Melting Point"][0]["Value"]["StringWithMarkup"][0]["String"]
pluh3=get_second_layer_props("acetic-acid",["Solubility"])["Solubility"][0]["Value"]["StringWithMarkup"][0]["String"]
print(mainlist)
print(failedprops)
# print(ppy.get_properties("Volume3D",lore.cid))
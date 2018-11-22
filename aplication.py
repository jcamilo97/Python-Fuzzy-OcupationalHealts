from flask import Flask, render_template
from flask import request
import Forms

# fuzzy
import numpy as np
import skfuzzy as fuzz
import operator

x_ruido = np.arange(0, 121, 1)
x_radiaciones_ionz = np.arange(0, 601, 1)
x_iluminacion  = np.arange(0, 501, 1)
x_temperatura = np.arange(-15,30,1)

rangos_variable = [ x_ruido, x_radiaciones_ionz, x_iluminacion, x_temperatura]
#   * ruido
ruido_lo = fuzz.trimf(x_ruido, [0, 0, 95])
ruido_md = fuzz.trimf(x_ruido, [0, 85, 110])
ruido_hi = fuzz.trimf(x_ruido, [105, 120, 120])
arr_ru = [ ruido_lo,ruido_md, ruido_hi]
#    * Radiaciones Ionizantes
radiaciones_ionz_lo = fuzz.trimf(x_radiaciones_ionz, [0, 0, 100])
radiaciones_ionz_md = fuzz.trimf(x_radiaciones_ionz, [0, 50, 400])
radiaciones_ionz_hi = fuzz.trimf(x_radiaciones_ionz, [200, 600, 600])
arr_rdonz = [radiaciones_ionz_lo, radiaciones_ionz_md, radiaciones_ionz_hi]
#    * iluminacion
iluminancion_lo = fuzz.trimf(x_iluminacion, [0, 0, 100])
iluminancion_md = fuzz.trimf(x_iluminacion, [90, 100, 500])
iluminancion_hi = fuzz.trimf(x_iluminacion, [490, 500, 500])
arr_ilum = [iluminancion_lo, iluminancion_md, iluminancion_hi]
#    * temperatura
temperatura_lo = fuzz.trimf(x_temperatura, [-10, -10, 10])
temperatura_md = fuzz.trimf(x_temperatura,[9, 9, 27])
temperatura_hi = fuzz.trimf(x_temperatura,[25, 30,30])

arr_tem = [temperatura_lo, temperatura_md, temperatura_hi]

set_vars = {'ruido':arr_ru, 'radiacionesonz':arr_rdonz, 'iluminacion':arr_ilum,'temperatura':arr_tem }

def cal_pertenencia(x_val,fun,valor):
    lo = fuzz.interp_membership(x_val, fun[0], valor)
    md = fuzz.interp_membership(x_val, fun[1], valor)
    hi = fuzz.interp_membership(x_val, fun[2], valor)
    print("func prt",lo,md,hi)
    return lo, md, hi

def calniveldeficiencia(onelow, twomedium, treehigth):
    print("caldef val", onelow, twomedium, treehigth)
    r = {2:onelow, 6:twomedium, 10:treehigth}
    print("rrr",r)
    return sorted(r.items(), key=operator.itemgetter(1))[2][0]

def cal_acept_riesgo(riesgo):
    if riesgo == 20:
        return "ACEPTABLE"
    elif riesgo >= 40 and riesgo <=120:
        return "ACEPTABLE"
    elif riesgo >= 150 and riesgo <=500:
        return "NO ACEPTABLE"
    elif riesgo >= 600:
        return "NO ACEPTABLE"
    return "value not match"

app = Flask(__name__)

variables = [
    {'name':'ruido', 'mag': 'Decibeles'},
    {'name': 'radiacionesonz', 'mag':'rem (J/kg)'},
    {'name': 'iluminacion', 'mag': 'Lux= 1 Lumen x M2'},
    {'name': 'temperatura', 'mag':'grados centrigrados'}
]

@app.route("/fuzzy", methods=['GET', 'POST'])
def hello():
    data_form = Forms.CareForm(request.form)
    resultdesfuzy = []
    showresul = False
    title="app para calcular el grado de riesgo"
    if request.method == 'POST':
        select = request.form
        print(select)
        vals = ['ruido','radiacionesonz', 'iluminacion', 'temperatura']
        for x in range(0,4):
            clave = vals[x]
            funcion_rango = rangos_variable[x]
            funcion_trim = set_vars[clave]
            valor_variable = select.get(clave)
            print(len(funcion_rango))
            print("fun_trim",len(funcion_trim))
            print(valor_variable)
            low, med, hig = cal_pertenencia(funcion_rango,funcion_trim, valor_variable)
            print(low,med,hig)
            nv_expocison = int(select.get("nv_exp_"+clave))
            nv_consecuencia = int(select.get("nv_cons_"+clave))
            nv_deficiencia = calniveldeficiencia(low, med, hig)
            nv_probabilidad = nv_deficiencia * nv_expocison
            nv_riesgo = nv_probabilidad * nv_consecuencia
            result = cal_acept_riesgo(nv_riesgo)
            resultdesfuzy.append({'name':clave,'val':result})
            print(select.get(clave),select.get("nv_exp_"+clave), select.get("nv_cons_"+clave),'\n')
        showresult= True
        return render_template('index.html', title=title, 
        variables= variables,
        nvexpo=[{'value':1},{'value':2},{'value':3},{'value':4}], 
        nvcons=[{'value':10},{'value':25},{'value':60},{'value':100}],
        result= resultdesfuzy,
        showresul = True)

   
    print(resultdesfuzy)
    return render_template('index.html', title=title, 
         variables= variables,
        nvexpo=[{'value':1},{'value':2},{'value':3},{'value':4}], 
        nvcons=[{'value':10},{'value':25},{'value':60},{'value':100}],
        result= resultdesfuzy,
        showresul = False,
         form = data_form)

if __name__ == '__main__':
    app.run()
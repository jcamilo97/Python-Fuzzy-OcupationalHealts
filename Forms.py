# from flask_wtf import Form
from wtforms import Form
from wtforms import StringField, TextField

class CareForm(Form):
    nameriesgo = StringField('valor del riesgo')
    niveldeficiencia = TextField('nivel de expocicion')
    nivelconsecuencia = TextField('nivel de consecuencia')
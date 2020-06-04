"""
This removes missing docstring
"""

from flask import Flask, render_template, request
#from pipelengthCal import calculatePipeLength 
from Functions.pipelengthCal import calculatePipeLength



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':

        pipelength = calculatePipeLength()
        if (pipelength == 0):
            return render_template('index.html', message = "cold fluid final temp cannot be less than its initial temp OR hot water exit temperature is lower than cold fluid final temp")

        return render_template('success.html', message = "Pipe length is {} metres".format(round(pipelength,2)))




if __name__ == "__main__":
    app.debug = True
    app.run()

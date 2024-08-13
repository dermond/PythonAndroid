from flask import Flask
from PIL import Image
import numpy as np
import Evaluation as Evaluation
import joblib #jbolib模块
import os


app = Flask(__name__)
@app.route('/TEST')
def index():

   
    global forest 
    result = Evaluation.Predicted(forest);
    return result
 
@app.route('/UpdateModel')
def Update():
     global forest 
     forest = joblib.load(os.getcwd()+'/forest.pkl')
     return "Model Update OK"



if __name__ == '__main__':
   
    forest = joblib.load(os.getcwd()+'/forest.pkl')
    app.run(host='127.0.0.1',port=800, debug=True)
   
  
#
#
#@app.route("/post_submit", methods=['GET', 'POST'])
#def submit():
#    if request.method == 'POST':
#        return 'Hello ' + request.values['username']    
#    return render_template('post_submit.html')
#
 
from flask import Flask,request, render_template
from channelInfo import getChannelInfo

app=Flask(__name__)
@app.route("/")
def index():
    md,ch,vd=getChannelInfo("Youtube")
    return render_template("index.html",d=md,ch=ch,vd=vd)
@app.route('/channel', methods=['POST'])
def handle_data():
    try:
      search = request.form['search2']
    except:
      search="YouTube"
    md,ch,vd=getChannelInfo(search)
    
    return render_template("index.html",d=md,ch=ch,vd=vd)
if __name__ == "__main__":
    
    app.run(debug=True)
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd
import psutil
import os
import sys
import seaborn as sns
from flask import Flask, render_template, request
from datetime import datetime
import time
from flask_socketio import SocketIO, emit

application = Flask(__name__)

cpuusage=psutil.cpu_percent(2)
x=cpuusage/100
ramusage=psutil.virtual_memory()[2]
y=ramusage/100

application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application)

sns.set()
sns.set_context("paper")
sns.set_style("ticks", {'axes.facecolor': 'white',   'grid.color': '.8', 'grid.linestyle': u'-'})
sns.set_palette("bright")
DataPointCount = 0
df = pd.DataFrame()
firstrequest = False
disconnectCount = 0
connecttime = time.time()

@socketio.on('connect', namespace='/')
def test_connect():
    global disconnectCount, connecttime
    disconnectCount = 0
    emit('my response', {'data': 'Connected'})
    connecttime = time.time()
    ip = request.environ['REMOTE_ADDR']
    print('{} connected    @ {}'.format(ip, datetime.now().strftime("%H:%M:%S on %d/%m/%y")))

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    global disconnectCount, DataPointCount, firstrequest, df
    disconnectCount += 1
    ip = request.environ['REMOTE_ADDR']
    print('{} disconnected @ {}'.format(ip, datetime.now().strftime("%H:%M:%S on %d/%m/%y")))

@application.route('/')
def index():
    global width, DataPointCount, df, clock, startClock, firstrequest, connecttime
    width = 2
    if not firstrequest:
        firstrequest = True
        startClock = datetime.now()
        clock = datetime.now()
        
        

    while True:
        try:
            # If clock var is not equal to actual clock, run this...
            if clock != datetime.now():
                TD = datetime.now() - startClock
                CpuVal = psutil.cpu_percent(interval=None, percpu=False)
                RamVal = psutil.virtual_memory()[2]
                df2 = pd.DataFrame({'%CPU': CpuVal, '%RAM': RamVal, 
                                    'Time':datetime.now().strftime("%S")},
                                   index=[DataPointCount])
                df = df.append(df2)
              
                df.set_index("Time", drop=True, inplace=True)

                if DataPointCount > 2:
                    plt.figure()
                    
                    if DataPointCount % 500 == 0:
                        width = width / 1.3
                        if width < 0.5:
                            width = 0.5

                  
                    df.plot(ylim=(0, 120), linewidth=1, alpha=0.5)
                    plt.Axes.set_autoscalex_on(plt, True)
                    plt.minorticks_off()
                    
                    
                    
                  
                    df.plot(marker='o')
                    TD = str(TD)
                    plt.xlabel('Echantillons: {}'.format(DataPointCount),color="c")
                    plt.ylabel("Utilisation en %",color="r")
                    TD = TD.split('.')[0]
                    plt.title("Time:\n{}".format(TD) , color='red')
                    img_base64 = BytesIO()
                    plt.savefig(img_base64, format='jpg', dpi=120)
                    img = base64.b64encode(img_base64.getvalue())
                    img = str(img)
                    img = img[2:-1]
                    DataPointCount += 1
                    plt.close('all')
                    if time.time() - connecttime > 10:
                        DataPointCount = 0
                        firstrequest = False
                        df = pd.DataFrame()
                        connecttime = time.time()
                    else:
                        return render_template('index.html', value=img,cpu=x,ram=y)

                DataPointCount += 1
                plt.close('all')
               

        except(KeyboardInterrupt, SystemExit):
            return 0

	
	 if __name__ == '__main__':
    print('Server Up !')
    socketio.run(application, host='0.0.0.0', port=8080)

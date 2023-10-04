#!/Users/hector/anaconda3/envs/test-gui/bin/python

import PySimpleGUI as sg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seawater
import os.path

def cluster_throw(df):

    ind = df.index[df.Conductivity>2]
    output = np.ones_like(df.Conductivity)*-1
    c = 0
    for i,j in zip(ind[0:-1], ind[1:]):
            if j-i <=1:
                output[i] = c
                output[j] = c
            else:
                output[i] = c
                c += 1
                output[j] = c

    return output

def analyze_ctd(fName):

    nSkip = 9
    
    df = pd.read_csv(fName,
                     skiprows=nSkip,
                     delimiter="\t",
                     names=["Pressure", "Temperature", "Conductivity"],
                    )
    metadata = {}
    with open(fName) as fd:
        for i in range(nSkip):
            tmp = next(fd).split(": ")
            metadata[tmp[0]] = tmp[1]
    
    # Calculate throw number
    df['Lances'] = cluster_throw(df)
    
    # Calculate time
    time = pd.date_range(start=metadata['Now'], periods=len(df), freq="200ms")
    df['time'] = time

    # Conductivity of seawater at 35 C 
    C35 = 4.2914 #Siemens/meter
    C35 = 42.914 #mS/cm
    seawater.salrt(35)

    # Calculate conductivity ratio, salinity and density
    df['Cond_Ratio'] = df.Conductivity/C35
    df['Salinity'] = seawater.eos80.salt(df['Cond_Ratio'], df['Temperature'], df['Pressure'])
    df['Density'] = seawater.eos80.dens(df['Salinity'], df['Temperature'], df['Pressure'])

    suffix = fName.split(".txt")[0].split("/")[-1]

    fig,ax = plt.subplots(figsize=(8,3))
    
    for i,g in enumerate(df.Lances.unique()):
        tmp = df[df.Lances==g]
        ax.plot(tmp.time, tmp.Salinity, marker="o", lw=0, color="C"+str(i), label="Lance {}".format(i))
    ax.legend()
    _ = ax.set_ylabel("Salinidad [psu]")
    fig.savefig("Salinidad_{}.png".format(suffix))
    
    fig,ax = plt.subplots(figsize=(8,3))
    
    for i,g in enumerate(df.Lances.unique()):
        tmp = df[df.Lances==g]
        ax.plot(tmp.time, tmp.Density, marker="o", lw=0, color="C"+str(i), label="Lance {}".format(i))
    ax.legend()
    _ = ax.set_ylabel(r"Density [kg m$^{-3}$]")
    fig.savefig("Densidad_{}.png".format(suffix))
    
    return

# Build layout

layout = [[sg.T("")],
          [sg.Text("Choose file to analyze: "), 
           sg.Input(),
           sg.FileBrowse(key="-IN-")
          ],[sg.Button("Submit")]
         ]

# Building Window
window = sg.Window('My File Browser', layout, size=(600,150))
    
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Submit":
        print("Analyzing {}".format(values["-IN-"]))

    _ = analyze_ctd(values["-IN-"])

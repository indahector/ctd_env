#!/Users/hector/anaconda3/envs/test-gui/bin/python

# import PySimpleGUI as sg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seawater
import os.path

#-----------------------------------------------------------------------------
def cluster_throw(df, threshold=0):

    ind = df.index[df.Conductivity>threshold]
    output = np.ones_like(df.Conductivity, dtype="int")*-1
    
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

#-----------------------------------------------------------------------------
def read_ctd(fName):
    nSkip = 9
    
    df = pd.read_csv(fName,
                     skiprows=nSkip,
                     delimiter="\t",
                     names=["Pressure", "Temperature", "Conductivity"],
                    )
    metadata = {}
    with open(fName, encoding="UTF-8") as fd:
        for i in range(nSkip):
            tmp = next(fd).split(": ")
            key = tmp[0]
            val = tmp[1].replace("\n","")
            metadata[key] = val

    return df, metadata

#-----------------------------------------------------------------------------
def separate_throws(df, metadata, threshold=0):
    """
    S Performs Single measurement
    M1 Performs continuous measurement at 1Hz
    M2 Performs continuous measurement at 2Hz
    M4 Performs continuous measurement at 4Hz
    M8 Performs continuous measurement at 8Hz
    M Performs continuous measurements at previously used rate
    Pn.nn Performs profile at a depth increment of n.nn, as set by the operator, in the
    current profiling units (see command #018)
    """

    frequencies = {"S": None,
                   "M1": "1000ms",
                   "M2": "500ms",
                   "M4": "250ms",
                   "M8": "125ms",
                  }
    
    # Calculate throw number
    # df['Lances'] = cluster_throw(df, threshold=threshold)
    df['Lances'] = cluster_throw(df, threshold<threshold)

    # Calculate time
    time = pd.date_range(start=metadata['Now'], periods=len(df), 
                         freq=frequencies[metadata["Mode"]]
                        )
    df['time'] = time

    return df

#-----------------------------------------------------------------------------
def calculate_ctd(df):
    
    # Conductivity of seawater at 35 C 
    C35 = 4.2914 #Siemens/meter
    C35 = 42.914 #mS/cm
    seawater.salrt(35)

    # Calculate conductivity ratio, salinity and density
    df['Cond_Ratio'] = df.Conductivity/C35
    df['Salinity'] = seawater.eos80.salt(df['Cond_Ratio'], df['Temperature'], df['Pressure'])
    df['Density'] = seawater.eos80.dens(df['Salinity'], df['Temperature'], df['Pressure'])

    return df  

#-----------------------------------------------------------------------------
def output_throws(df, metadata):

    template = []
    for k,v in metadata.items():
        template.append("{}: {}\n".format(k,v))
    template.append("{}")
    template = "".join(template)
    
    date = metadata["Now"].replace("/","-").replace(" ","T")
    site = metadata["Site info"]
    fName = "Datos_procesados/{}_{}".format(site, date)
    
    df = df[df.Lances>=0]

    for g in df.Lances.unique():
        tmp = df[df.Lances==g]
        tmp = tmp.loc[:, ['time','Pressure','Temperature','Conductivity','Salinity','Density']]
        tmp_fName = fName + "_Lance{}.txt".format(g)
        with open(tmp_fName, 'w') as fp:
            fp.write(template.format(tmp.to_csv(index=False, sep='\t')))

    return 

#-----------------------------------------------------------------------------
def analyze_ctd(fName, plot=False):

    # Read CTD original data
    df, metadata = read_ctd(fName)

    # Separate CTD throws 
    df = separate_throws(df, metadata)

    df = calculate_ctd(df)
    
    output_throws(df, metadata)
    
    if plot:
        fig0, fig1 = plot_ctd(df)
        suffix = fName.split(".txt")[0].split("/")[-1]
        fig0.savefig("Plots/Salinidad_{}.png".format(suffix))
        fig1.savefig("Plots/Densidad_{}.png".format(suffix))
        return df, fig0, fig1
    else:
        return df

#-----------------------------------------------------------------------------
def plot_ctd(df):

    fig0,ax = plt.subplots(figsize=(8,3))
    for g in df.Lances.unique():
        if g>=0:
            tmp = df[df.Lances==g]
            ax.plot(tmp.time, tmp.Salinity, marker=".", lw=0, color="C"+str(g), label="Lance {}".format(g))
    ax.legend()
    _ = ax.set_ylabel("Salinidad [psu]")

    fig1,ax = plt.subplots(figsize=(8,3))
    for g in df.Lances.unique():
        if g>=0:
            tmp = df[df.Lances==g]
            ax.plot(tmp.time, tmp.Density, marker="o", lw=0, color="C"+str(g), label="Lance {}".format(g))
    ax.legend()
    _ = ax.set_ylabel(r"Density [kg m$^{-3}$]")

    return fig0, fig1

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    
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

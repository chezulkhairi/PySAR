## Welcome to PySAR!   
   
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/yunjunz/PySAR)
[![Badges](http://img.shields.io/:badges-7/7-ff6799.svg)](https://github.com/yunjunz/PySAR)
       
PySAR is a open-source Python package for InSAR (Interferometric Synthetic Aperture Radar) time series analysis. It reads stack of interferograms (coregistered and unwrapped) in ROI_PAC, Gamma and ISCE format, and produces three dimensional (2D in space and 1D in time) ground displacement. It includes a routine time series analysis (pysarApp.py) and some independent toolboxs. PySAR is built on the initial work done by [Scott Baker](https://github.com/bakerunavco). [Alfredo Terrero](https://github.com/stackTom) developed the code to prepare UNAVCO InSAR product for [time series web viewer](http://insarmaps.miami.edu).      
   
### 1. Installation   

#### 1.1 Pre-requisite
We recommend using [Anaconda](https://www.anaconda.com/) to install the python environment and the prerequisite packages. You will need:   
- [Python2.7](https://www.anaconda.com/download/)
- Numpy
- Scipy
- h5py
- Matplotlib
- Basemap (optional, for plotting in geo coordinate)
- pykml (optional, for Google Earth KMZ file output)
- joblib (optional, for parallel processing)
- [PyAPS](http://earthdef.caltech.edu/projects/pyaps/wiki/Main) (optional, for tropospheric correction using weather re-analysis models, i.e. ERA-Interim, NARR, MERRA)

Here is a example on Mac OSX using csh/tcsh:   

Add the following in ~/.cshrc file and source it.   

    ############################ Python ############################### 
    setenv PYTHON2DIR  ~/python/anaconda2
    setenv PATH        ${PYTHON2DIR}/bin:${PATH}

Install Xcode with command line tools, follow instructions [here](https://github.com/yunjunz/macOS_Setup).

Then run the following in your terminal:   

    cd ~/python
    wget https://repo.continuum.io/archive/Anaconda2-4.4.0-MacOSX-x86_64.sh
    chmod +x Anaconda2-4.4.0-MacOSX-x86_64.sh
    ./Anaconda2-4.2.0-MacOSX-x86_64.sh -b -p $PYTHON2DIR
    $PYTHON2DIR/bin/conda config --add channels conda-forge
    $PYTHON2DIR/bin/conda install basemap joblib pykml --yes   
   
For PyAPS installation, please refer to [PyAPS's Wiki at Caltech](http://earthdef.caltech.edu/projects/pyaps/wiki/Main)


##### 1.2 PySAR   
Download the latest released version at [https://github.com/yunjunz/PySAR/releases](https://github.com/yunjunz/PySAR/releases), or use the command below.    
   
    cd ~/python
    wget https://github.com/yunjunz/PySAR/archive/v1.2.0.tar.gz
    tar -zxvf v1.2.0.tar.gz
   
or download the development version using git:   
   
    cd ~/python
    git clone https://github.com/yunjunz/PySAR.git
   
To use the package, you need to setup the environment. Depending on your shell, you may use commands below to setup pysar, by adding the following to your source file. They are for:   
1. To make pysar importable in python, by adding the path to PySAR directory to your $PYTHONPATH    
2. To make utility scripts available in command line, by adding ${PYSAR_HOME}/pysar and ${PYSAR_HOME}/shellscripts to your $path.   
   
For bash user, add to your .bashrc file:   

    if [ -z ${PYTHONPATH+x} ]; then export PYTHONPATH=""; fi
    export PYSAR_HOME=~/python/PySAR        #for released version, "~/python/PySAR-1.2.0"
    export PYTHONPATH=${PYSAR_HOME}:${PYTHONPATH}  
    export PATH=${PYSAR_HOME}/pysar:${PYSAR_HOME}/shellscripts:${PATH}   

For csh/tcsh user, add to your .cshrc file:   

    if ( ! $?PYTHONPATH ) then
        setenv PYTHONPATH ""
    endif
    setenv PYSAR_HOME  ~/python/PySAR       #for released version, "~/python/PySAR-1.2.0"
    setenv PYTHONPATH  ${PYSAR_HOME}:${PYTHONPATH}
    setenv PATH        ${PYSAR_HOME}/pysar:${PYSAR_HOME}/shellscripts:${PATH}
   
   
### 2. Running PySAR

The current version is compatible with ROI_PAC and Gamma products. PySAR reads unwrapped interefrograms (at the same coordinate system: radar or geo) and the baseline files for each interefrogram. You need to give the path to where the interferograms are and PySAR takes care of the rest!   

Run pysarApp.py -h see the processing options.   
Run pysarApp.py -g to generate a default template file and see the detailed settings.   

#### Example: [Kuju Volcano example with ALOS data](https://github.com/yunjunz/PySAR/wiki/Example)   

Download the test data: [Download Link](https://miami.app.box.com/v/pysar-demo-KujuAlosAT422F650) and unzip it.   

Create a custom template file:   

    cd ~/KujuAlosAT422F650/PYSAR
    vi KujuAlosAT422F650_template.txt
   
Include the following pysar options in your template:   

    ##———————————————————————————————— Data Loading ——————————————————————————————##
    # RADAR COORD ROIPAC PRODUCTS
    pysar.unwrapFiles    = ~/KujuAlosAT422F650/ROIPAC/RADAR/filt_*.unw
    pysar.corFiles       = ~/KujuAlosAT422F650/ROIPAC/RADAR/filt_*.cor
    pysar.geomap         = ~/KujuAlosAT422F650/ROIPAC/RADAR/geomap*.trans
    pysar.dem.radarCoord = ~/KujuAlosAT422F650/ROIPAC/RADAR/radar*.hgt
    pysar.dem.geoCoord   = ~/KujuAlosAT422F650/ROIPAC/RADAR/*.dem
    
    pysar.reference.lalo      = 33.0655, 131.2076
    pysar.deramp              = plane     
    
Save your template file and run PySAR as:   

    pysarApp.py KujuAlosAT422F650_template.txt

Inside pysarApp.py, it reads the unwrapped interferograms, refernces all of them to the same coherent pixel (a seed point point), calculates the phase closure and estimates the unwrapping errors (if it has been asked for), inverts the interferograms, calculates a parameter called "temporal_coherence" which can be used to evaluate the quality of inversion, removes ramps or surface from time-series epochs, corrects dem errors, corrects local oscilator drift (for Envisat only), corrects stratified tropospheric delay (using pyaps and using phase-elevation approach), ... and finally estimates the velocity.   

Use view.py to view any pysar output.   

Use tsviewer.py to plot the time-series for each point (relative to the refernce point and epoch!).    

#### Build your own processing recipe   

PySAR is a toolbox with a lot of individual utility scripts, highly modulized in python. Check its documentaion or simple run it with -h to see its usage, you could build your own customized processing recipe!

   
### 3. Documentation
   
- Manual: [PDF](https://github.com/yunjunz/PySAR/blob/master/docs/Manual-1.2.0_201708.pdf), [HTML](https://github.com/yunjunz/PySAR/blob/master/docs/Manual-1.2.0_201708.html.zip)
- Wiki: Check our [Github Wiki](https://github.com/yunjunz/PySAR/wiki) to see the example data, paper references, file naming convention and more.
   
### 4. Google Group

Join our google group [https://groups.google.com/forum/#!forum/py-sar](https://groups.google.com/forum/#!forum/py-sar) to ask questions, get notice of latest features pushed to you!

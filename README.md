# TP_PID-Controler

A PyQt interface to monitor a PID_Controler (Teensy microcontroler) via the serial USB link. 
Download the zip of this repository using the green button [Code v] at the top right of this page, then unzip the file to install the directory `TP_PID-Controler_master` within your personnal disk tree on your computer.

In the following we name __console__ the "Anaconda prompt" window (window 10 or 11) or the terminal (macOS or GNU/Linux).

You need to run this PyQt application within a __Python Virtual Environment__ (PVE) with Python 3.10:</br>

- If you are an ENSAM student you already have a PVE (named `minfo` for the Math-Info activity) installed on your laptop or on the school computers.

- If you don't already have any PVE available, you can follow this link <A href="https://savoir.ensam.eu/moodle/mod/resource/view.php?id=10170">Document d'installation...</A> until the command (slide 4):<br>
`conda activate pyml`<br>
Then in the _console_, update the `conda` command with: `conda update -n base -c defaults conda`<br>
and populate the PVE with: `conda env update -n minfo --file <path-of-PVE.yml>`<br>
replacing `<path-of-PVE.yml>` by the acces path of the file `PVE.yml` on your computer:
    -[Windows] something like `C:\Users\you\...\PVE.yml` found thanks to the file browser.
    -[macOS, Linux] something like `/home/users/you/.../PVE.yml` found thanks to the file browser.
 
When done, to run the application type in the console (with the _minfo_ PVE activated):<br>
`cd <path-of-folder-"PID_Controler">`<br>
replacing `<path-of-folder-"PID_Controler">` by the acces path of the folder `PID_Controler` on your computer:
-[Windows]: something like `C:\Users\you\...\TP_PID-Controler_master\PID_Controler` found thanks to the file browser.
-[macOS, Linux]: something like `/home/users/you/.../TP_PID-Controler_master/PID_Controler` found thanks to the file browser.

Then run the application with:<br>
`python main.py`<br>



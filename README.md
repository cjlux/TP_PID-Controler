# TP_PID-Controler

A PyQt interface to monitor a PID_Controler (Teensy microcontroler) via the serial USB link. 
Download the zip of the GitHub repository __TP_PID-Controler__ using the green button [code v] at the top right of the site, the unzip the file to install the directory `TP_PID-Controler_master` within your working directory on your computer.

In the following we name __console__ the "Anaconda prompt" window (window 10 or 11)or the terminal (macOS or GNU/Linux).

You need to run this PyQt application within a __Python Virtual Environment__ (PVE) runing Python 3.10:</br>

- If you are an ENSAM student you already have a PVE (named `minfo` for the Math-Info activity) installed on your laptop or on the school computers.

- If you don't already have any PVE available, you can follow this link <A href="https://savoir.ensam.eu/moodle/mod/resource/view.php?id=10170">Document d'installation...</A> until the command (slide 4):<br>
`conda activate pyml`<br>
Then in the _console_ update the `conda` command with: `conda update -n base -c defaults conda`<br>
and populate the PVE with: `conda env update -n minfo --file <path-of-the-file-PVE.yml>`<br>
replacing `<path-of-the-file-PVE.yml>` by the acces path of the file `PVE.yml` (something like `C:\Users\you\...\PVE.yml` found thanks to the file browser).
 
When done, to run the application type in the console (with the _minfo_ PVE activated):<br>
`cd <path_of_the_folder_PID_Controler>`<br>
replacing `<path-of-the-folder-"PID_Controler">` by the acces path of the folder `PID_Controler` on your computer (something like `C:\Users\you\...\TP_PID-Controler_master\PID_Controler`) found thanks to the file browser.
Then hust type in:<br>
`python main.py<br>



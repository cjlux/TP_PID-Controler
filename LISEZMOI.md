# TP_PID-Controleur

Ce dépôt propose une application PyQt pour surveiller un PID_Controler (microcontrôleur Teensy) via le bus série USB.
Télécharger le zip à l'aide du bouton vert [Code v] en haut à droite de cette page, puis décompresser le fichier pour installer le répertoire `TP_PID-Controler_master` au sein de votre arborescence personnelle sur votre ordinateur.

Vous devrez exécuter l'interface PyQt dans un __Environment Virtual Python__ (EVP) avec Python 3.10 :</br>

Dans ce qui suit, "__(minfo) console__" désigne la fenêtre "Anaconda prompt" (fenêtre 10 ou 11) ou le terminal (macOS ou GNU/Linux) avec  __l'EVP minfo PVE activé__ :

- Si vous êtes étudiant à l'ENSAM vous disposez déjà d'un EVP __minfo__ pour l'activité Math-Info installé sur votre ordinateur portable ou sur les ordinateurs de l'école.
Il vous suffit d'ajouter les modules __pyserial__ et __pyqtgraph__. Pour ce faire, tapez dans la console __(minfo)__ :<br>
`conda installe pyserial pyqtgraph -y`

- Si vous n'avez pas encore d'EVP disponible, vous pouvez suivre ce lien <A href="https://savoir.ensam.eu/moodle/mod/resource/view.php?id=10170">Document d' installation...</A> jusqu'à la commande (diapositive 4) :<br>
`conda active minfo`<br>
Ensuite, dans la console __(minfo)__, mettre à jour `conda` avec la commande :<br>
`conda update -n base -c defaults conda`<br>
et compléter l'EVP en tapant la commande :<br>
`conda env update -n minfo --file <chemin du fichier PVE.yml>`<br>
en remplaçant `<chemin du fichier PVE.yml>` par le chemin d'accès du fichier `PVE.yml` sur votre ordinateur (trouvé grâce au navigateur de fichiers) :<br>
->[Windows] : quelque chose comme `C:\Users\you\...\PVE.yml`<br>
->[macOS, Linux] : quelque chose comme `/home/users/you/.../PVE.yml`.<br>

Une fois terminé, se déplacer dans le dossier racine du projet en tapant la commande `cd` (changer de répertoire) dans la console __(minfo)__ :<br>
`cd <chemin-du-dossier-"PID_Controler_master">`<br>
en remplaçant `<chemin-du-dossier-"PID_Controler_master">` par le chemin d'accès du dossier `PID_Controler_master` sur votre ordinateur (trouvé grâce au navigateur de fichiers) :<br>
-> [Windows] : quelque chose comme `C:\Users\you\...\TP_PID-Controler_master\PID_Controler_master`<br>
->[macOS, Linux] : quelque chose comme `/home/users/you/.../TP_PID-Controler_master/PID_Controler_master`.

Enfin, lancer l'application depuis la console __(minfo)__ avec la commande :<br>
`python main.py`<br>

Enjoy...
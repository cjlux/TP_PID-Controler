#include <Encoder.h>

// PRAMAETRES PID POUR ROUE ET PILE 9V
 float kp = 0.08; // 0.08 //0.01 // entre 0.2 et 0.5 (avec D)
 float ki = 0.02; // 0.02 //0.01 // 0.03
 float kd = 0.02; // 0.02 //0.1 // 

// PRAMAETRES PID POUR MASSE RONDE ET 9V
//float kp = 0.05; // entre 0.2 et 0.5 (avec D)
//float ki = 0.01; // 0.03
//float kd = 0.00; // 


int consigne  = 2500; // consigne pour PID

long erreur = 0 ; // consigne - mesure
long erreur_precedente = 0 ; // 
long cmd = 0 ; // de 0 à 255
long somme_erreur = 0 ; // pour PI
float delta_erreur = 0 ; // pour PID

// GPIO
const byte IN1 = 0;
const byte IN2 = 1 ;
const byte PINLED = 13;
const byte ENCODEURA = 7;
const byte ENCODEURB = 8;

// Encoder
volatile long speed = 0; // vitesse du moteur
volatile long speed_n_1 = 0; // vitesse du moteur n-1
volatile long speed_moy = 0; // vitesse du moteur moyen

// commandes
int commande = 255 ; // vitesse de la commande
int mode = 0 ; //mode=0 off; 1=avance, 2=recule
int commande_last = 100 ; // ancienne commande
int mode_last = 1 ; // ancien mode


// Display
unsigned long millis_old = 0 ; // pour mesure timings

// DATA STORAGE
volatile int nb = 0;
const int nb_max = 50;
volatile int tableau[nb_max];
long int millis0 = 0;


int serieContinu = 0; // 1 qd on veut avoir la donnée en direct

// TIMER
IntervalTimer myTimer;

Encoder myEnc(ENCODEURA, ENCODEURB);

// SETUP
void setup()
{
  // INITMOTEUR
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  analogWriteFrequency(IN1, 100);
  analogWriteFrequency(IN2, 50);
  stopMotor();

  // INIT LED
  pinMode(PINLED, OUTPUT);
  digitalWrite(PINLED, LOW);

  // INIT ENCODER
  pinMode(ENCODEURA, INPUT_PULLUP);
  pinMode(ENCODEURB, INPUT_PULLUP);

  // INIT MONITEUR SERIE
  Serial.begin(115200); // Définit vitesse de transmission série
  delay(2000);
  //Serial.println("Execution du controle par clavier");
  //Serial.println("z avance, s recule, x arret, +/- vitesse");
  millis_old = micros();

  // INIT TIMER
  myTimer.begin(timerIsr, 1000);  // 100000 => 0.1s period  change this value to a lower one for more interrupt / seconds

}

void loop()
{
  // HANDLE SERIAL COM
  if (Serial.available()) {
    char val = Serial.read();           //récupération des caractères sur le port série
    if (val != -1)
    {
      switch (val)
      {
        case 'a': // Control
          backward(0); // en avant vitesse
          mode = 3; // PI
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état bas en marche avant
          break;

        case '1': // Kp*1.25
          kp = kp * 1.25;
          break;
        case '2': // Kp/1.25
          kp = kp / 1.25;
          break;
        case '3': // Ki*1.25
          ki = ki * 1.25;
          break;
        case '4': // Ki/1.25
          ki = ki / 1.25;
          break;
        case '5': // Kd*1.25
          kd = kd * 1.25;
          break;
        case '6': // Kd/1.25
          kd = kd / 1.25;
          break;

        case 'z': // Forward
          forward (commande); // en avant vitesse
          mode = 1;
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état bas en marche avant
          break;

        case 's': // Backward
          backward (commande); // en arrière vitesse
          mode = 2;
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état haut en marche arrière
          break;

        case 'c': // Start Data flow
          serieContinu = 1;
          millis0 = millis();
          break;

        case 'b': // Stop Data flow
          serieContinu = 0;
          break;

        case '+': // Accelerates
          commande += 10;
          if (commande > 255) commande = 255;
          if (mode == 1) {
            forward (commande); // en avant vitesse
          } else if (mode == 2) {
            backward (commande); // en arrière vitesse
          }
          break;

        case '-': // Decelerates
          commande -= 10;
          if (commande < 0) commande = 0;

          if (mode == 1) {
            forward (commande); // en avant vitesse
          } else if (mode == 2) {
            backward (commande); // en arrière vitesse
          }
          break;
        case 'x': // Stop Motor
          stopMotor();
          mode = 0;
          somme_erreur = 0 ;
          break;

        case 'd': // Send data array
          for (int i = 0; i < nb ; i++) {
            Serial.println(tableau[i]);
          }
          nb = 0 ; // RAZ pour tableau mémoire
          break;
      }
    }
    else stopMotor();
  }

  // DISPLAY DATA
  if (mode_last != mode) {
    //Serial.print ("mode : "); Serial.println (mode);
  }

  if (commande_last != commande) {
    //Serial.print ("commande : "); Serial.println (commande);
  }
  /*
    if ( mode != 0) {
    millis_now = micros();
    if ( millis_now - millis_old > 100000) {
      millis_old = millis_now;
      Serial.print(millis());
      Serial.print(" , ");  Serial.print(speed);
      Serial.print(" , ");  Serial.print(commande);
      Serial.print(" , ");  Serial.println(mode);
    }
    }
  */

  commande_last = commande;
  mode_last = mode;
}

// MOTORS
void stopMotor() //Stop
{
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);
}

void forward (char motorSpeed) // En avant
{
  analogWrite (IN1, motorSpeed); // Contrôle de vitesse en PWM
  analogWrite (IN2, 0);
}

void backward (char motorSpeed) // En arrière
{
  analogWrite (IN2, motorSpeed);
  analogWrite (IN1, 0);
}

// Timer event to calculate speed from encoder and print data
void timerIsr()
{
  // speed = myEnc.read(); // on a le nombre de tick ( signé ) par unité de temps  = vitesse
  speed = myEnc.read(); // on a le nombre de tick ( signé ) par unité de temps  = vitesse
  speed_moy = (speed_n_1 + speed) / 2;
  speed_n_1 = speed;

  // CALCUL DU PID SI MODE 3//
  if (mode == 3) {
    erreur = consigne - speed_moy ;
    somme_erreur += erreur;
    delta_erreur = erreur-erreur_precedente;
    erreur_precedente = erreur;
    // CALCUL CONSIGNE
    cmd = kp * erreur + ki * somme_erreur + kd * delta_erreur;
    if (cmd < 0) cmd = 0;
    else if (cmd > 255) cmd = 255;
    analogWrite (IN2, cmd);
    analogWrite (IN1, 0);

  }



  myEnc.write(0); // On remet le compteur de tick à 0
  toggleLed();
  if (nb < nb_max) {
    tableau[nb] = speed; // stocke en mémoire les valeurs
    nb ++ ;
  }
  if (serieContinu == 1) {
    String mess;
    mess += "MS,";    // Elapsed time (ms)
    mess += String(millis()-millis0);
    mess += ",ERR,";  // Error
    mess += String(erreur);
    mess += ",SP,";   // SetPoint
    mess += String(consigne * (mode == 3));
    mess += ",COM,";  // Command
    mess += String(commande * (1 - (mode == 0)));
    mess += ",CMD,";  // Cmd
    mess += String(cmd);
    mess += ",KP,";   // Kp gain
    mess += String(kp,3);
    mess += ",KI,";   // Ki gain
    mess += String(ki,3);
    mess += ",KD,";   // Kd gain
    mess += String(kd,3);
    mess += ",SPE,";  // Speed
    mess += String(speed, 3);
    mess += ",SPM,";  // Av. speed
    mess += String(speed_moy,3);
    Serial.println(mess);
  }
  //Serial.print("> vitesse :"); Serial.print(millis());
  //Serial.print("   :"); Serial.println(speed);
}

// LED
void toggleLed() {
  static bool ledState = false;
  ledState = !ledState;
  digitalWrite(PINLED, ledState);
}

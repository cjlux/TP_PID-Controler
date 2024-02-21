#include <Encoder.h>
#include <EEPROM.h>

// Fonction RESET de la carte
void(* resetFunc) (void) = 0; //declare reset function @ address 0

/*-----------------------------------------------
 * paramètres de réglage des constantes du système
 * Unités en tr/min sortie d'arbre ou sortie moteur
 * Unités en tr/min en consigne (setpoint)
 */

float vitesse_max = 260 ;                   // tr/min en sortie d'arbre
float facteur_reduction = 34;               // sortie d'arbre = 1:34 sortie moteur
float nb_imp_par_tour_moteur = 2000;        // 2000 imp/tr moteur (sampling front up/down sur 2 fils)
float Te = 30;                               // période d'échantillonnage en ms
int nb_tourmin_max_mot_12V = vitesse_max*34;        // 8000;          // 8840 tr/min max à 12V (PWM à 255)



// PRAMAETRES PID POUR TP - 20ms
//float kp = 0.128; // 0.08 //0.01 // entre 0.2 et 0.5 (avec D)
//float ki = 0.03; // 0.02 //0.01 // 0.03
//float kd = 0.0; // 0.02 //0.1 //


// PRAMAETRES PID POUR ROUE ET PILE 9V
/*
#define Tau 34
#define Tretard 0.5
#define Kgain 1
float kp = (Tau+0.4*Tretard)/(1.2*Kgain*Tretard); // 0.08 //0.01 // entre 0.2 et 0.5 (avec D)
float ki = 0.8/(Kgain*Tretard); // 0.02 //0.01 // 0.03
float kd = Kgain/(0.35*Tau); // 0.02 //0.1 
*/

// paramètres à la fin
//float kp = 3.6; // 0.08 //0.01 // entre 0.2 et 0.5 (avec D)
//float ki = 1.6; // 0.02 //0.01 // 0.03
//float kd = 0.006; // 0.02 //0.1 //

// PRAMAETRES PID POUR MASSE RONDE ET 9V
float kp = 1; // entre 0.2 et 0.5 (avec D)
float ki = 0.00; // 0.03
float kd = 0.00; //

// EEPROM
unsigned int TeAddress = 0; //EEPROM Sampling frequency adress
uint32_t valTimer = 1; // valeur de la période d'échantillonnage (en ms)

int consigne  = 150; // consigne en tours/min

long erreur = 0 ; // consigne - mesure
long erreur_precedente = 0 ; //
float cmd_trminute = 0; // sortie du calcul PID
float cmd_trminute_precedente=0; // commande précédente
float cmd = 0 ; // commande PWM de 0 à 255
long somme_erreur = 0 ; // pour PI
float delta_erreur = 0 ; // pour PID

// GPIO
const byte IN1 = 0;
const byte IN2 = 1 ;
const byte PINLED = 13;
const byte ENCODEURA = 6;
const byte ENCODEURB = 7;

// Encoder
volatile long nb_imp = 0; // nb impulsions par Te ms
volatile float speed = 0; // vitesse de l'arbre moteur en sortir
volatile float speed_n_1 = 0; // vitesse du moteur n-1
volatile float speed_moy = 0; // vitesse du moteur moyen

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
  analogWriteResolution(8);

  // Fréquence des PWM utilisées pour piloter le moteur (en Hz)
  analogWriteFrequency(IN1, 4750);
  analogWriteFrequency(IN2, 4750);
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

  //EEPROM
  valTimer = EEPROM.read(TeAddress); // valeur de l'EEPROM à l'adresse
  Serial.println("Timer value (ms) : " + String(valTimer));
  if (valTimer == (uint32_t) 0) {valTimer=1;};
  if (valTimer > (uint32_t) 100) {valTimer = 100;};
  // INITIALIATION DU TIMER à la période Te (en ms)
  myTimer.begin(timerIsr, valTimer*1000);   // 100000 => 0.1s period  
                                      // change this value to a lower one
                                      // for more interrupt / seconds
  Te=valTimer;

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
        case 'c': // PID-Control
          forward(0); // en avant vitesse
          mode = 3; // PI
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état bas en marche avant
          break;

        case 'x': // Stop Motor
          stopMotor();
          mode = 0;
          somme_erreur = 0 ;
          break;

        case 'P': // Kp*1.1
          kp = kp * 1.1;
          break;
        case 'p': // Kp/1.1
          kp = kp / 1.1;
          break;
        case 'I': // Ki*1.1
          ki = ki * 1.1;
          break;
        case 'i': // Ki/1.1
          ki = ki / 1.1;
          break;
        case 'D': // Kd*1.1
          kd = kd * 1.1;
          break;
        case 'd': // Kd/1.1
          kd = kd / 1.1;
          break;

        case 'f': // OL-Forward
          commande = (consigne * 255) / (nb_tourmin_max_mot_12V / facteur_reduction);
          if (commande > 255) commande = 255;
          if (commande < 0) commande = 0;
          forward (commande); // en avant vitesse
          mode = 1;
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état bas en marche avant
          break;

        case 'b': // OL-Backward
          commande = (consigne * 255) / (nb_tourmin_max_mot_12V / facteur_reduction);
          if (commande > 255) commande = 255;
          if (commande < 0) commande = 0;
          backward (commande); // en arrière vitesse
          mode = 2;
          nb = 0 ; // RAZ pour tableau mémoire
          // le driver fonctionne à l'état haut en marche arrière
          break;

        case 's': // Start Data flow
          serieContinu = 1;
          millis0 = millis();
          break;

        case 'S': // Stop Data flow
          serieContinu = 0;
          break;

        case '+': // Accelerates
          //commande += 10;
          consigne += 10;
          commande = (consigne * 255) / (nb_tourmin_max_mot_12V / facteur_reduction);
          if (commande > 255) commande = 255;
          if (mode == 1) {
            forward (commande); // en avant vitesse
          } else if (mode == 2) {
            backward (commande); // en arrière vitesse
          } else if (mode == 3) {
            consigne += 10;
          }
          break;

        case '-': // Decelerates
          consigne  -= 10;
          commande = (consigne * 255) / (nb_tourmin_max_mot_12V / facteur_reduction);
          // commande -= 10;
          if (commande < 0) commande = 0;

          if (mode == 1) {
            forward (commande); // en avant vitesse
          } else if (mode == 2) {
            backward (commande); // en arrière vitesse
          } else if (mode ==3) {
            consigne -= 10;
          }
          break;

	      case 'X': // Stop Motor
          stopMotor();
          mode = 0;
          somme_erreur = 0 ;
          break;

        case 'A': // Send Data
          for (int i = 0; i < nb ; i++) {
            Serial.println(tableau[i]);
          }
          nb = 0 ; // RAZ pour tableau mémoire
          break;

        case 't': // Sampling 1ms
      	  Serial.println("Sampling 1ms");
      	  valTimer = 1;
      	  //One simple call, with the address first and the object second.
      	  EEPROM.put( TeAddress, valTimer );
      	  Serial.println("Mise en EEPROM: " + String(valTimer));      
      	  delay(1000);
      	  resetFunc();
      	break;

        case 'T': // Sampling 10ms
          Serial.println("Sampling 10ms");     
          valTimer = 10;
          //One simple call, with the address first and the object second.
          EEPROM.put( TeAddress, valTimer ); 
          Serial.println("Mise en EEPROM: " + String(valTimer));   
          delay(1000);   
          resetFunc();
        break;

        case 'u': // Sampling 30ms
          Serial.println("Sampling 30ms");     
          valTimer = 30;
          //One simple call, with the address first and the object second.
          EEPROM.put( TeAddress, valTimer ); 
          Serial.println("Mise en EEPROM: " + String(valTimer));   
          delay(1000);   
          resetFunc();
        break;

        case 'V': // Sampling 50ms
          Serial.println("Sampling 50ms");     
          valTimer = 50;
          //One simple call, with the address first and the object second.
          EEPROM.put( TeAddress, valTimer ); 
          Serial.println("Mise en EEPROM: " + String(valTimer));   
          delay(1000);   
          resetFunc();
        break;

        case 'w': // Sampling 100ms
          Serial.println("Sampling 100ms");     
          valTimer = 100;
          //One simple call, with the address first and the object second.
          EEPROM.put( TeAddress, valTimer ); 
          Serial.println("Mise en EEPROM: " + String(valTimer));   
          delay(1000);   
          resetFunc();
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

  // code with interrupts blocked (consecutive atomic operations will not get interrupted)
  
  nb_imp = myEnc.read(); // on a le nombre de tick ( signé ) par unité de temps  = vitesse
  
  /* 
   conversion impulsions en tours par minutes sortie de l'arbre
   nb_impulsions (impl en Te(ms)) * 60 (s/min) * 1000 (ms/s) / (reducteur-34 * nb_im_par_tour (2000 impl/tr) * Te (ms))
  */
  speed = 60 * nb_imp * 1000 / (facteur_reduction * nb_imp_par_tour_moteur * Te); 
  //speed_moy = (speed_n_1 + speed) / 2;
  //speed_n_1 = speed;
  myEnc.write(0); // On remet le compteur de tick à 0
  toggleLed();
 
  // CALCUL DU PID SI MODE 3//
  if (mode == 3) {
    // CALCUL CONSIGNE PID avec approximation standard
    erreur = consigne - speed ; //en tr/minute sortie arbre
    somme_erreur += erreur;
    delta_erreur = erreur - erreur_precedente;
    cmd_trminute = kp * erreur + ki * somme_erreur + kd * delta_erreur;
    //
    // CALCULS CATHERINE
    //cmd_trminute = cmd_trminute_precedente + 5.37 * erreur - 3.83 * erreur_precedente;

    
    // 
    cmd_trminute_precedente=cmd_trminute;
    erreur_precedente = erreur;
    
    /*
     Conversion du calcul du PID en tr/min en valeur PWM (0-255)
     cmd = cmd_trminute (tr/min) * PWM_MAX (255 code) / (nb_tourmin_max_mot_12V (tr/min) * reducteur (34)))
    */
    
    cmd = (cmd_trminute * 255) / (nb_tourmin_max_mot_12V / facteur_reduction);
    
    if (cmd < 0) cmd = 0;
    else if (cmd > 255) cmd = 255;
    analogWrite (IN1, cmd);
    analogWrite (IN2, 0);

  }



  if (nb < nb_max) {
    tableau[nb] = speed; // stocke en mémoire les valeurs
    nb ++ ;
  }
  if (serieContinu == 1) {
    String mess;
    mess += "MS,";    // Elapsed time (ms)
    mess += String(millis() - millis0);
    mess += ",ERR,";  // Error
    mess += String(erreur);
    mess += ",SP,";   // SetPoint
    mess += String(consigne);
    mess += ",Cmd_BO,";  // Command
    mess += String(commande* (1 - (mode == 0)));
    mess += ",CMD,";  // Cmd
    mess += String(cmd);
    mess += ",KP,";   // Kp gain
    mess += String(kp, 3);
    mess += ",KI,";   // Ki gain
    mess += String(ki, 3);
    mess += ",KD,";   // Kd gain
    mess += String(kd, 3);
    mess += ",SPE,";  // Speed
    mess += String(speed, 2);
    mess += ",Te,";  // Av. speed
    mess += String(Te);
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

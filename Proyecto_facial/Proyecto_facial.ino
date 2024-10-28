#include <ESP32Servo.h>
#include <NewPing.h>

Servo torniquete;

const int gPin = 12;  // LED verde conectado al pin 2
const int rPin = 13;  // LED rojo conectado al pin 4
const int TRIGGER_PIN = 4;  // Pin para el trigger del sensor ultrasónico
const int ECHO_PIN = 16;     // Pin para el echo del sensor ultrasónico
const int TORNIQUETE = 26; //Pin para el PWM del Servo
const int MAX_DISTANCE = 20; // Distancia máxima a medir en cm

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

unsigned long lastDetectionTime = 0;
const unsigned long detectionCooldown = 1000; // 1 segundo de espera entre detecciones

void setup() {
  Serial.begin(115200);  // Iniciar comunicación serial
  pinMode(gPin, OUTPUT);  // Configurar el pin del LED verde como salida
  pinMode(rPin, OUTPUT);  // Configurar el pin del LED rojo como salida
  digitalWrite(gPin, LOW);  // Inicialmente, LED verde apagado
  digitalWrite(rPin, LOW);  // Inicialmente, LED rojo apagado
  torniquete.attach(TORNIQUETE);     // Conectar el servo al pin 9
}

void loop() {
  // Medir la distancia con el sensor ultrasónico
  int distance = sonar.ping_cm();
  
  // Si se detecta un objeto a 30 cm y ha pasado el tiempo de espera
  if (distance > 0 && distance <= 30 && (millis() - lastDetectionTime > detectionCooldown)) {
    Serial.write('q');  // Enviar 'q' para activar la captura y comparación de imágenes
    lastDetectionTime = millis();  // Actualizar el tiempo de la última detección
  }
  
  if (Serial.available() > 0) {  // Si hay datos disponibles
    char estado = Serial.read();  // Leer el byte recibido
    
    if (estado == '1') {
      digitalWrite(rPin, LOW);  // Apagar el LED rojo
      digitalWrite(gPin, HIGH);  // Encender el LED verde
      torniquete.write(90);
      delay(3000);
      digitalWrite(gPin, LOW);
      torniquete.write(0);
    } 
    else if (estado == '0') {
      digitalWrite(gPin, LOW);  // Apagar el LED verde
      digitalWrite(rPin, HIGH);  // Encender el LED rojo
      delay(3000);
      digitalWrite(rPin, LOW);
    }
  }
}
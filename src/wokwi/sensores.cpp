#include "DHTesp.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <array>

#define I2C_ADDR    0x27
#define LCD_COLUMNS 20
#define LCD_LINES   4
#define I2C_SDA     21
#define I2C_SCL     22


LiquidCrystal_I2C lcd(I2C_ADDR, LCD_COLUMNS, LCD_LINES);

//FIAP - FASE 4
//Variáveis com tipos modificados para minimizar uso de memória
const unsigned char RELE_PIN = 19;
const unsigned char DHT_PIN = 23;
const unsigned char BUTTON_PINS[] = {34, 35};
const unsigned char LDR_DO_PIN = 32;
const unsigned char LDR_AO_PIN = 33;
const float GAMMA = 0.7;
const float RL10 = 50;

DHTesp dhtSensor;

void setup() {
  Serial.begin(115200);
  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);
  pinMode(BUTTON_PINS[0], INPUT_PULLUP);
  pinMode(BUTTON_PINS[1], INPUT_PULLUP);
  pinMode(LDR_AO_PIN, INPUT);
  pinMode(LDR_DO_PIN, INPUT);
  pinMode(RELE_PIN, OUTPUT);

  Wire.begin(I2C_SDA, I2C_SCL);
  lcd.begin(LCD_COLUMNS, LCD_LINES);
  lcd.backlight();
}

void loop() {
  TempAndHumidity data = getTempAndHumidityFromSensor();
  float analogValue = analogRead(LDR_AO_PIN);
  float pHConverted = analogValue / 288;
  float roundedPhConverted = floorf(pHConverted * 100) / 100;

  // Dados para o Serial Plotter - DEVE ser a primeira saída serial
  Serial.print("Temp:");
  Serial.print(data.temperature);
  Serial.print(" Umid:");
  Serial.print(data.humidity);
  Serial.print(" pH:");
  Serial.println(roundedPhConverted);

  // Marca separadora entre dados do plotter e JSON
  Serial.println("---");

  //Imprimindo Temperatura e Umidade no visor LCD
  lcd.setCursor(0,0);
  lcd.print("Tp: " + String(data.temperature, 2));
  lcd.setCursor(10,0);
  lcd.print("/ Um: " + String(data.humidity, 1));

  //Imprimindo Temperatura e Umidade no Monitor Serial em formato JSON
  Serial.println("{");
  Serial.println("\t\"temp\":" + String(data.temperature, 2) + ",");
  Serial.println("\t\"hum\": " + String(data.humidity, 1) + ",");

  //Lendo estado dos botões que representam P e K
  std::array<bool, 2> states = {false, false};
  states[0] = (digitalRead(BUTTON_PINS[0]) == LOW);
  states[1] = (digitalRead(BUTTON_PINS[1]) == LOW);

  //Imprimindo o estado dos botões no visor LCD:
  lcd.setCursor(0, 1);
  if (states[0]) {
    lcd.print("P: SIM");
  } else {
    lcd.print("P: NAO");
  }
  lcd.setCursor(7, 1);
  if (states[1]) {
    lcd.print(" / K: SIM");
  } else {
    lcd.print(" / K: NAO");
  }

  //Imprimindo estado de P e K no Monitor Serial:
  for(size_t i = 0; i < states.size(); i++) {
      if (i == 0) {
        Serial.print("\t\"P\": ");
      } else {
        Serial.print("\t\"K\": ");
      }
      Serial.print(states[i] ? "\"presente\",\n" : "\"não-presente\",\n");
  }

  Serial.printf("\t\"pH\": %.2f,\n", roundedPhConverted);
  lcd.setCursor(0,2);
  lcd.print("pH: " + String(roundedPhConverted));

  // Decisão por ligar ou não a bomba de água da irrigação:
  Serial.printf("\t\"irrigacao\": {\n");
  // Cenário 1: Solo seco - Liga a bomba
  if (data.humidity < 55) {
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo seco, pouca humidade.\"\n");
    digitalWrite(RELE_PIN, HIGH);
    lcd.setCursor(0,3);
    lcd.print("B Irrig LIGADA");
  } else if ((data.humidity >= 55 && data.humidity <= 70) && data.temperature > 35) {
    // Cenário 2: Solo úmido e temperatura alta - Liga a bomba
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo úmido com temperatura alta.\"\n");
    digitalWrite(RELE_PIN, HIGH);
    lcd.setCursor(0,3);
    lcd.print("B Irrig LIGADA");
  } else if (pHConverted > 7.5 && (!states[0] || !states[1])) {
    // Cenário 3: pH básico e falta de nutrientes - Liga a bomba
    Serial.printf("\t\t\"estado\": \"ligada\",\n");
    Serial.printf("\t\t\"motivo\": \"pH básico e nutrientes ausentes no solo.\"\n");
    digitalWrite(RELE_PIN, HIGH);
    lcd.setCursor(0,3);
    lcd.print("B Irrig LIGADA");
  } else {
    // Cenário 4: Solo já úmido e irrigado
    Serial.printf("\t\t\"estado\": \"desligada\",\n");
    Serial.printf("\t\t\"motivo\": \"Solo suficientemente úmido com nutrientes e temperatura adequada.\"\n");
    digitalWrite(RELE_PIN, LOW);
    lcd.setCursor(0,3);
    lcd.print("B Irrig DESLIGADA");
  }
  Serial.printf("\t}\n");

  Serial.println("},");

  delay(1000);
}

TempAndHumidity getTempAndHumidityFromSensor() {
  return dhtSensor.getTempAndHumidity();
}
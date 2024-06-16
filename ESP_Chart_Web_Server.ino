#include <Wire.h>
#include <Adafruit_AHT10.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// Substitua pelos pinos que você está usando para o AHT10
Adafruit_AHT10 aht;

// Substitua com as credenciais da sua rede
const char* ssid = "JHONATAN";
const char* password = "lcs102223";

// Credenciais do Supabase
String API_URL = "https://puhilvgiiyeqyorktlpx.supabase.co";
String API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB1aGlsdmdpaXllcXlvcmt0bHB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTgzMjg1NDMsImV4cCI6MjAzMzkwNDU0M30.ITl1Xzykgy7_Um-2BPYUCn3GcpmjqQIbK6u2qpGHMso";
String TableName = "maintable";
const int httpsPort = 443;

// Intervalo de envio dos pacotes em segundos
int sendinginterval = 1200; // 
//int sendinginterval = 120; // 2 minutos

HTTPClient https;
WiFiClientSecure client;

float h;
float t;
int m;

// Defina o pino do LED embutido manualmente
const int LED_PIN = 2;

void setup() {
  // O LED embutido é usado para indicar quando uma mensagem está sendo enviada
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // O LED embutido é invertido, HIGH o desliga

  // HTTPS é usado sem verificação de credenciais
  client.setInsecure();

  // Conectar ao Wi-Fi
  Serial.begin(115200);
  if (!aht.begin()) {
    Serial.println("Não foi possível encontrar o AHT10! Verifique a conexão.");
    while (1) delay(10);
  }

  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Imprimir endereço IP local
  Serial.println("");
  Serial.println("WiFi conectado.");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Se conectado à internet, liga o LED embutido e tenta enviar uma mensagem para o banco de dados
  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_PIN, LOW); // LOW acende o LED

    // Ler todos os sensores
    sensors_event_t humidity, temp;
    aht.getEvent(&humidity, &temp); // Atualiza e obtém leituras

    h = humidity.relative_humidity;
    t = temp.temperature;
    m = analogRead(34); // Pino ADC do ESP32, assegure-se de que está correto

    // Imprimir leituras dos sensores na serial
    Serial.print("Temperatura: ");
    Serial.print(t);
    Serial.println(" °C");
    
    Serial.print("Umidade: ");
    Serial.print(h);
    Serial.println(" %");
    
    Serial.print("Umidade do solo (sensor analógico): ");
    Serial.print(4095 - m);
    Serial.println();

    // Enviar a requisição POST para o servidor
    https.begin(client, API_URL + "/rest/v1/" + TableName);
    https.addHeader("Content-Type", "application/json");
    https.addHeader("Prefer", "return=representation");
    https.addHeader("apikey", API_KEY);
    https.addHeader("Authorization", "Bearer " + API_KEY);
    int httpCode = https.POST("{\"temperature\":" + String(t) + ",\"humidity\":" + String(h) + ",\"moisture\":" + String(4095 - m) + "}" );   // Envia a requisição
    String payload = https.getString(); 
    Serial.print("Código HTTP: ");
    Serial.println(httpCode);   // Imprime o código de retorno HTTP
    Serial.print("Resposta do servidor: ");
    Serial.println(payload);    // Imprime a resposta da requisição
    https.end();

    digitalWrite(LED_PIN, HIGH); // HIGH apaga o LED
  } else {
    Serial.println("Erro na conexão WiFi");
  }
  delay(1000 * sendinginterval);  // Aguarda para enviar a próxima requisição
}

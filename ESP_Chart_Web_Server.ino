#include <Wire.h>
#include <Adafruit_AHT10.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

Adafruit_AHT10 aht;

// Credenciais da minha rede criada pelo ESP
const char* ssid = "JHONATAN";
const char* password = "lcs102223";

// Configurações para enviar dados para o Supabase via nuvem
String API_URL = "https://puhilvgiiyeqyorktlpx.supabase.co"; // URL da API do Supabase para acesso ao banco de dados
String API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB1aGlsdmdpaXllcXlvcmt0bHB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTgzMjg1NDMsImV4cCI6MjAzMzkwNDU0M30.ITl1Xzykgy7_Um-2BPYUCn3GcpmjqQIbK6u2qpGHMso"; 
// Chave de API para autenticação no Supabase
String TableName = "maintable"; // Nome da tabela principal onde os dados serão armazenados
const int httpsPort = 443; // Porta padrão para conexões HTTPS


// Intervalo de envio dos pacotes em segundos
int sendinginterval = 20; // 
//int sendinginterval = 120; // 2 minutos



HTTPClient https; // Objeto para realizar requisições HTTP para enviar dados ao Supabase
WiFiClientSecure client; // Cliente WiFi seguro para conexão HTTPS com o Supabase

float h; // Variável para armazenar a leitura da umidade relativa
float t; // Variável para armazenar a leitura da temperatura
int m;   // Variável para armazenar a leitura da umidade do solo (ADC)


// pino do LED embutido manualmente
const int LED_PIN = 2;



/*
   Este programa utiliza RTOS (Real-Time Operating System) no ESP32 para organizar as tarefas em unidades independentes.
   A tarefa sendSensorDataTask é criada como uma tarefa RTOS para enviar dados do sensor para um servidor via HTTPS.
   Isso permite que ela execute de forma concorrente com outras tarefas, como a gestão da conexão WiFi e outras operações do sistema.
   A utilização de tarefas separadas melhora a eficiência e responsividade do sistema, permitindo operações simultâneas e independentes.
   
   Este código é configurado para funcionar com o sensor AHT10, enviando leituras de temperatura, umidade e umidade do solo (ADC) para um servidor.
   Certifique-se de ajustar as credenciais de rede WiFi e API de acordo com suas configurações.
*/

void sendSensorData(void * parameter) {
  for (;;) {
    // Se conectado à internet, liga o LED embutido e tenta enviar uma mensagem para o banco de dados
    if (WiFi.status() == WL_CONNECTED) {
      digitalWrite(LED_PIN, LOW); // LOW acende o LED

      // Ler todos os sensores
      sensors_event_t humidity, temp;
      aht.getEvent(&humidity, &temp); // Atualiza e obtém leituras

      h = humidity.relative_humidity;
      t = temp.temperature;
      m = analogRead(33); // Pino ADC do ESP32

      // Enviar uma requisição POST com dados dos sensores para o servidor Supabase
      https.begin(client, API_URL + "/rest/v1/" + TableName); // Inicia a conexão HTTPS com a URL do Supabase e a tabela específica
      https.addHeader("Content-Type", "application/json"); // Define o tipo de conteúdo da requisição como JSON
      https.addHeader("Prefer", "return=representation"); // Preferência para retorno da representação após a requisição
      https.addHeader("apikey", API_KEY); // Chave de API para autenticação no Supabase
      https.addHeader("Authorization", "Bearer " + API_KEY); // Autorização usando a chave de API
      int httpCode = https.POST("{\"temperature\":" + String(t) + ",\"humidity\":" + String(h) + ",\"moisture\":" + String(4095 - m) + "}"); 
      // Envia os dados de temperatura, umidade e umidade do solo em formato JSON
      String payload = https.getString(); // Obtém a resposta da requisição do servidor
      Serial.print("Código HTTP: ");
      Serial.println(httpCode); // Imprime o código de retorno HTTP da requisição
      Serial.print("Resposta do servidor: ");
      Serial.println(payload); // Imprime a resposta recebida do servidor
      https.end(); // Finaliza a conexão HTTPS


      digitalWrite(LED_PIN, HIGH); // HIGH apaga o LED
    } else {
      Serial.println("Erro na conexão WiFi");
    }
    vTaskDelay(pdMS_TO_TICKS(1000 * sendinginterval));  // Aguarda para enviar a próxima requisição
  }
}

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


// Inicia a conexão WiFi com as credenciais fornecidas
Serial.print("Conectando a ");
Serial.println(ssid); // Imprime o nome da rede WiFi sendo conectada
WiFi.begin(ssid, password); // Inicia o processo de conexão WiFi com o SSID e a senha fornecidos

// Aguarda até que o dispositivo esteja conectado à rede WiFi
while (WiFi.status() != WL_CONNECTED) {
  delay(500); // Aguarda meio segundo
  Serial.print("."); // Exibe um ponto para indicar o processo de conexão em andamento
}


  // Imprimir endereço IP local
  Serial.println("");
  Serial.println("WiFi conectado.");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());

  // Inicia a tarefa para enviar dados do sensor
  //RTOS
  xTaskCreatePinnedToCore(
    sendSensorData,     // Função que implementa a tarefa
    "sendSensorData",   // Nome da tarefa
    10000,              // Tamanho da pilha da tarefa
    NULL,               // Parâmetro passado para a tarefa
    1,                  // Prioridade da tarefa
    NULL,               // Identificador da tarefa, opcional
    0);                 // Núcleo onde a tarefa deve ser executada (0 ou 1)
}

void loop() {
  // Não precisa de código aqui porque as tarefas estão rodando no RTOS
  vTaskDelete(NULL);
}
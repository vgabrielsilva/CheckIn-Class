#include <Keypad.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <vector>
#include <sstream>
#include <algorithm>


const char* ssid = "SERGIO SILVA";
const char* senha_wifi = "palio5910";

const char* servidor_mqtt = "63bd50c65ab64331beb93ad88527a44d.s1.eu.hivemq.cloud";
const int porta_mqtt = 8883;
const char* usuario_mqtt = "teste";
const char* senha_mqtt = "Teste123";

WiFiClientSecure cliente_esp;
PubSubClient cliente_mqtt(cliente_esp);

LiquidCrystal_I2C lcd(0x27, 20, 4); // Endereço I2C, colunas, linhas


const int vermelho = 33; 
const int amarelo = 23;
const int verde = 27;

int estadovermelho = 0;
int estadoamarelo = 0;
int estadoverde = 0;

const uint8_t LINHAS = 4;
const uint8_t COLUNAS = 3;
char teclas[LINHAS][COLUNAS] = {
    { '1', '2', '3' },
    { '4', '5', '6' },
    { '7', '8', '9' },
    { '*', '0', '#' }
};
uint8_t pinos_colunas[COLUNAS] = { 16, 4, 32 };
uint8_t pinos_linhas[LINHAS] = { 19, 18, 5, 17 };
Keypad teclado = Keypad(makeKeymap(teclas), pinos_linhas, pinos_colunas, LINHAS, COLUNAS);

struct Aluno {
    String matricula;
    String nome;
};

std::vector<Aluno> lista_alunos = {
    {"202300128715", "ADILSON ARMANDO MIGUEL"},
    {"202100007142", "ALAN FERNANDES BISPO DO NASCIMENTO"},
    {"202200007495", "AMANDA DE JESUS MELO"},
    {"202200007501", "ANA MARIA DE CARVALHO MENDONCA"},
    {"202300072422", "BRUNO ANTONIO CARVALHO GOES"},
    {"202200007539", "CASSIANO MENEZES SILVA SANTOS"},
    {"201500431828", "CLOVIJAN BISPO ROCHA"},
    {"202200007575", "DIEGO DIAS INOCENCIO"},
    {"202300016479", "GABRIEL VINICIUS SOUZA DA SILVA"},
    {"202000060915", "JADSON TAVARES SANTOS"},
    {"202300016521", "JORGE EDUARDO FREIRE DO NASCIMENTO SANTOS"},
    {"202000007990", "LUCAS SILVEIRA RIBEIRO LIMA"},
    {"202200007717", "LUIZ AUGUSTO FARIAS HORA"},
    {"202300072351", "MATHEUS SANTOS DE JESUS"},
    {"202300016648", "PABLO RAFAEL DOS SANTOS"},
    {"202100075536", "RAFAEL PESSOA DA SILVA SANTOS"},
    {"202300016675", "RIQUELME JOSE ALMEIDA FERREIRA"},
    {"202200071629", "SAVIO LOURENCO DE OLIVEIRA LIRA"},
    {"202000008138", "VERENILSON DA SILVA SOUZA"},
    {"202000008183", "VITOR OLIVEIRA SANTOS"}
};


std::vector<Aluno> todos_participantes;

String matricula_digitada = "";
bool matricula_valida = false;
std::vector<int> votosPergunta1; 

String mensagem_recebida = "";
bool sistema_iniciado = false;

struct Pergunta {
    int numero;
    String texto;
};

std::vector<int> votosSim;
std::vector<int> votosNao;
std::vector<int> votosNa;

std::vector<String> nomes_participantes;

std::vector<Pergunta> perguntas;

void enviarParticipantesEResultados() {
    String lista_participantes = "Participantes: ";

    for (const String& nome : nomes_participantes) {
        lista_participantes += nome + "; ";
    }
    
    lista_participantes += "\nResultados:\n";
    for (size_t j = 0; j < perguntas.size(); ++j) {
        lista_participantes += "Pergunta " + String(perguntas[j].numero) + ": ";
        lista_participantes += "\"Sim\": " + String(votosSim[j]) + " | ";
        lista_participantes += "\"Nao\": " + String(votosNao[j]) + " | ";
        lista_participantes += "\"N/A\": " + String(votosNa[j]) + ";\n";
    }
    
    delay(1000);
    Serial.println(lista_participantes.c_str());
    Serial.println("teste01");
    cliente_mqtt.publish("esp_enviar", lista_participantes.c_str());

}

void callback(char* topic, byte* payload, unsigned int length) {
    mensagem_recebida = "";
    for (unsigned int i = 0; i < length; i++) {
        mensagem_recebida += (char)payload[i];
    }

    if (mensagem_recebida == "comando_iniciar") {
        sistema_iniciado = true;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Sistema Iniciado");
        delay(2000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Aguardando perguntas...");
    } else if (mensagem_recebida.startsWith("comando_enviar")) {
        perguntas.clear();
        String perguntas_str = mensagem_recebida.substring(strlen("comando_enviar"));
        std::istringstream iss(perguntas_str.c_str());
        std::string pergunta;

        while (std::getline(iss, pergunta, ';')) {
            int numero;
            String texto;
            size_t pos = pergunta.find('-');
            if (pos != std::string::npos) {
                numero = atoi(pergunta.substr(0, pos).c_str());
                texto = pergunta.substr(pos + 1).c_str();
                perguntas.push_back({numero, texto});
            }
        }

        std::sort(perguntas.begin(), perguntas.end(), [](const Pergunta &a, const Pergunta &b) {
            return a.numero < b.numero;
        });

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Perguntas");
        lcd.setCursor(0, 1);
        lcd.print("atualizadas");
        delay(2000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Digite sua Matricula");
    } else if (mensagem_recebida == "comando_encerrar") {
        enviarParticipantesEResultados();  // Chama a função para enviar participantes e resultados

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Sistema Encerrado");
        delay(2000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Digite sua Matricula");
    }
}



void setup() {
    Serial.begin(115200);

    pinMode(vermelho, INPUT_PULLUP);
    pinMode(verde, INPUT_PULLUP);
    pinMode(amarelo, INPUT_PULLUP);

    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Iniciando...");

    WiFi.begin(ssid, senha_wifi);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Conectado à rede Wi-Fi");

    cliente_esp.setInsecure();
    cliente_mqtt.setServer(servidor_mqtt, porta_mqtt);
    cliente_mqtt.setCallback(callback);

    while (!cliente_mqtt.connected()) {
        Serial.print("Conectando ao broker MQTT...");
        if (cliente_mqtt.connect("ESP32Client", usuario_mqtt, senha_mqtt)) {
            Serial.println("Conectado!");
            cliente_mqtt.subscribe("py_enviar");
            //cliente_mqtt.subscribe("esp_enviar");
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Aguardando iniciacao");
            lcd.setCursor(0, 1);
            lcd.print("remota");
        } else {
            Serial.print("Falha na conexão, rc=");
            Serial.println(cliente_mqtt.state());
            delay(5000);
        }
    }
}




void exibirResultados() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Participantes: ");
    lcd.print(nomes_participantes.size());

    Serial.println("Participantes:");
    for (const String& nome : nomes_participantes) {
        Serial.println(nome);
    }

    Serial.println("Votos por pergunta:");
    for (size_t j = 0; j < perguntas.size(); ++j) {
        Serial.print("Pergunta ");
        Serial.print(perguntas[j].numero);
        Serial.print(": \"Sim\" ");
        Serial.print(votosSim[j]); 
        Serial.print(" | \"Nao\" ");
        Serial.print(votosNao[j]);  
        Serial.print(" | \"N/A\" ");
        Serial.print(votosNa[j]);   
        Serial.println();
    }
}









void exibirPerguntas() {
    if (!perguntas.empty()) {
        votosSim.resize(perguntas.size(), 0);
        votosNao.resize(perguntas.size(), 0);
        votosNa.resize(perguntas.size(), 0);

        for (size_t i = 0; i < perguntas.size(); ++i) {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print(perguntas[i].texto);

            lcd.setCursor(0, 3);
            lcd.print("1-Sim  2-N/A  3-Nao");

            bool voto_registrado = false;
            while (!voto_registrado) {

                estadoverde = digitalRead(verde);
                estadovermelho = digitalRead(vermelho);
                estadoamarelo = digitalRead(amarelo); 

                if (estadoverde == LOW) {
                    Serial.println("verde");
                    votosSim[i]++;
                    voto_registrado = true;
                    delay(1000);
                } else if (estadovermelho == LOW) {
                    Serial.println("vermelho");
                    votosNao[i]++;
                    voto_registrado = true;
                    delay(1000);
                } else if (estadoamarelo == LOW) { 
                    Serial.println("amarelo");
                    votosNa[i]++;
                    voto_registrado = true;
                    delay(1000);
                }
                cliente_mqtt.loop();  
            }
        }

        exibirResultados();

        todos_participantes.clear();
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Digite sua Matricula");
    }
}


void loop() {

    if (!cliente_mqtt.connected()) {
        Serial.println("Desconectado do broker MQTT, tentando reconectar...");
        while (!cliente_mqtt.connected()) {
            Serial.print("Tentando reconectar ao broker MQTT...");
            if (cliente_mqtt.connect("ESP32Client", usuario_mqtt, senha_mqtt)) {
                Serial.println("Conectado!");
                cliente_mqtt.subscribe("py_enviar");
            } else {
                Serial.print("Falha na conexão, rc=");
                Serial.println(cliente_mqtt.state());
                delay(5000); 
            }
        }
    } else {
        cliente_mqtt.loop();
    }

    if (sistema_iniciado) {
        char tecla = teclado.getKey();
        if (tecla) {
            if (tecla == '#') {
                if (!matricula_digitada.isEmpty()) {
                    auto it = std::find_if(lista_alunos.begin(), lista_alunos.end(), [&](const Aluno& aluno) {
                        return aluno.matricula == matricula_digitada;
                    });

                    if (it != lista_alunos.end()) {
                        auto participante_it = std::find_if(nomes_participantes.begin(), nomes_participantes.end(), [&](const String& nome) {
                            return nome == it->nome;
                        });

                        if (participante_it == nomes_participantes.end()) {
                            lcd.clear();
                            lcd.setCursor(0, 0);
                            lcd.print("Matricula valida");
                            lcd.setCursor(0, 1);
                            lcd.print(it->nome);
                            matricula_valida = true;

                      
                            nomes_participantes.push_back(it->nome);

                            delay(2000);
                            lcd.clear();
                            matricula_digitada = "";                           
                            exibirPerguntas(); 
                        } else {
                            lcd.clear();
                            lcd.setCursor(0, 0);
                            lcd.print("Ja participou");
                            delay(2000);
                            lcd.clear();
                            lcd.setCursor(0, 0);
                            lcd.print("Digite sua Matricula"); 
                            matricula_digitada = ""; 
                        }
                    } else {
                        lcd.clear();
                        lcd.setCursor(0, 0);
                        lcd.print("Matricula invalida");
                        delay(2000);
                        lcd.clear();
                        lcd.setCursor(0, 0);
                        lcd.print("Digite sua Matricula"); 
                        matricula_digitada = ""; 
                    }
                }
            } else if (tecla == '*') {
                if (matricula_digitada.length() > 0) {
                    matricula_digitada.remove(matricula_digitada.length() - 1); 
                    lcd.setCursor(0, 1);
                    lcd.print(matricula_digitada + " ");
                }
            } else {
                matricula_digitada += tecla;
                lcd.setCursor(0, 1);
                lcd.print(matricula_digitada);
            }
        }
    }
}
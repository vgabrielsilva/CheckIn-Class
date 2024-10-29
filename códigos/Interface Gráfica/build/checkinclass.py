

'''
    Esse é o sistema do CheckIn Class destinado ao professor!

    Pontos importantes:
        1. Utilizamos a lib Tkinter para o desenvolvimento da interface gráfica.
        2. Os botões funcionam a partir de comando enviados ao mqtt, exemplo: [Botão Iniciar Sistema] = ao ser acionado, envie "comando_iniciar" ao tópico do mqtt.
            2.1 O sistema do esp reconhece cada comando e executa as respectivas funções
        3. Os botões do sistemas são imagens personalizadas sobrepostas aos botões padrões da biblioteca.
            3.1 Note que nesse repositório há um diretório destinado ao armazenamento de imagens. Além disso, por meio de testes, adicionamos futilmente uma segunda opção de armazenamento de imagens através de decodificação
            3.2 Alguns ícones e imagens foram codificados e armazenados em "banco_de_imagens.py". Assim que chamados, são decodificados pelo sistema e transformados imagens gráficas.

    ATENÇÃO:
        A tipografia da interface foi criada a partir da família de fontes "Poppins". Para execução completa e funcional do programa, instale-as no computador antes de inicializar.
        Link para instalação via Google Fonts: https://fonts.google.com/specimen/Poppins

'''



from pathlib import Path
from tkinter import *
from tkinter import messagebox
import sys
import requests
from bs4 import BeautifulSoup
import time
import paho.mqtt.client as mqtt
import base64
from banco_de_imagens import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#configuração do servidor mqtt (hivemq)
MQTT_SERVIDOR = "63bd50c65ab64331beb93ad88527a44d.s1.eu.hivemq.cloud"
MQTT_PORTA = 8883
MQTT_USUARIO = "teste"
MQTT_SENHA = "Teste123"
MQTT_TOPICO_RECEBER = "esp_enviar" 
MQTT_TOPICO_ENVIAR = "py_enviar"    

#chamada quando conecta ao servidor
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT. Código de resultado: {rc}")
    client.subscribe(MQTT_TOPICO_RECEBER)
    print(f"Inscrito no tópico: {MQTT_TOPICO_RECEBER}")

#chamada quando recebe dados do tópico que inscrevemos
def on_message(client, userdata, msg):
    print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")

# criação do nosso cliente no mqtt
client = mqtt.Client()
client.username_pw_set(MQTT_USUARIO, MQTT_SENHA)

#config. do callback
client.on_connect = on_connect
client.on_message = on_message

def mqtt_init():
    try:
        print("Inicializando cliente MQTT...")
        client.tls_set()
        client.connect(MQTT_SERVIDOR, MQTT_PORTA, 60)
    except Exception as e:
        print(f"Erro ao inicializar: {e}")

mqtt_init()

def enviar_mensagem_mqtt(mensagem):
    try:
        print("Conectando ao broker...")
        if not client.is_connected():
            client.reconnect()
        print(f"Enviando: {mensagem}")
        client.publish(MQTT_TOPICO_ENVIAR, mensagem)
    except Exception as e:
        print(f"Erro ao conectar: {e}")



# função criada para buscar e retirar a lista de alunos matriculados no DSI (usamos uma partição do sigaa de domínio público)
def atualizar():
    url = 'https://www.sigaa.ufs.br/sigaa/public/curso/alunos.jsf?lc=pt_BR&id=320196'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tds = soup.find_all('td')

        alunos = []
        matricula = ""

        alunos.append("comando_atualizar")
        for td in tds:
            if 'colMatricula' in td.get('class', []):
                matricula = td.text.strip()
            elif matricula:
                nome = td.text.strip()
                
                alunos.append(f"{matricula} {nome}")
                matricula = ""

        dados_alunos = "\n".join(alunos)

        enviar_mensagem_mqtt(dados_alunos)

    else:
        print(f"Falha ao acessar a página. Status code: {response.status_code}")

# configuração da interface gráfica (usando o Tkinter)
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"  # Caminho relativo para a pasta frame0

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def on_drag(event):
    x = window.winfo_pointerx() - window._offsetx
    y = window.winfo_pointery() - window._offsety
    window.geometry(f"+{x}+{y}")

def on_drag_start(event):
    window._offsetx = event.x
    window._offsety = event.y

window = Tk()
window.geometry("1075x651")
window.configure(bg="#F0F0F0")
window.overrideredirect(True)

canvas = Canvas(
    window,
    bg="#F0F0F0",
    height=651,
    width=1075,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

barra_titulo = canvas.create_rectangle(
    0.0,
    0.0,
    1075.0,
    44.0,
    fill="#250C6B",
    outline=""
)

canvas.tag_bind(barra_titulo, "<ButtonPress-1>", on_drag_start)
canvas.tag_bind(barra_titulo, "<B1-Motion>", on_drag)


canvas.create_rectangle(
    23.0,
    135.0,
    1051.0,
    627.0,
    fill="#250C6B",
    outline="")

canvas.create_rectangle(
    590.0,
    164.0,
    1026.0,
    598.0,
    fill="#F0F0F0",
    outline="")

canvas.create_rectangle(
    49.0,
    164.0,
    485.0,
    598.0,
    fill="#F0F0F0",
    outline="")

canvas.create_text(
    447.0,
    7.0,
    anchor="nw",
    text="Área do Professor",
    fill="#F0F0F0",
    font=("Poppins Bold", 20 * -1)
)

canvas.create_text(
    54.0,
    77.0,
    anchor="nw",
    text="Atualizar lista de alunos",
    fill="#250C6B",
    font=("Poppins Bold", 16 * -1)
)





def limitador_de_caractere(event):
    char_count = len(entry_1.get())
    
    if char_count == 0:
        label_counter.config(text="")

    elif char_count > 0 and char_count < 40:
        label_counter.config(text=f"{char_count}", fg="#250C6B")

    else:
        if event.keysym not in ["Delete"]:
            entry_1.delete(len(entry_1.get()) - 1)
            label_counter.config(text=f"{40}", fg="#FF0000")

    '''
    elif char_count > 40 and char_count <= 50:
        label_counter.config(text=f"{char_count}", fg="#FF0000")
    
    else:  # char_count > 50
        if event.keysym not in ["BackSpace", "Delete"]:
            entry_1.delete(len(entry_1.get()) - 1) 
            label_counter.config(text=f"{40}", fg="#FF0000")
    '''
            
entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    228.0,
    270.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#CACACA",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=105.0,
    y=258.0,
    width=246.0,
    height=23.0
)

label_counter = Label(window, text="", font=("Poppins", 10 * -1), fg="#250C6B")
label_counter.place(x=75.0, y=260.0)


#deixa o evento de tecla do entry_1 vinculado nessa função
entry_1.bind("<KeyRelease>", limitador_de_caractere)



entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    267.0,
    446.0,
    image=entry_image_2
)

entry_2 = Text(
    bd=0,
    bg="#CACACA",
    fg="#000716",
    highlightthickness=0,
    font=("Poppins Light", 16 * -1),
    wrap='word',
    state=DISABLED
)

# scroll vertical
scrollbar = Scrollbar(window, orient="vertical", command=entry_2.yview)
entry_2.configure(yscrollcommand=scrollbar.set)

entry_2.place(
    x=105.0,
    y=330.0,
    width=304.0,
    height=230.0
)

#posicionamento do scroll
scrollbar.place(
    x=412.0,  # 105 (posição x do entry_2) + 304 (largura do entry_2)
    y=330.0,
    height=232.0
)

assuntos = []
assunto_count = 1

def assuntos_formatados(assuntos):
    formatado = "comando_enviar" + ";".join([f"{idx+1}-{assunto}?" for idx, assunto in enumerate(assuntos)])
    return formatado



def atualizar_conteudo():

    entry_2.config(state=NORMAL)
    entry_2.delete("1.0", "end") 
    for i, assunto in enumerate(assuntos, start=1):
        entry_2.insert("end", f"ASSUNTO 0{i}:\n{assunto}\n\n")
    entry_2.config(state=DISABLED)
    assuntos_formatados(assuntos)

def comando():
    global assunto_count
    assunto = entry_1.get()

    if len(assunto) > 40:
        messagebox.showwarning("Limite de caracteres", "O assunto excede o limite de 40 caracteres.")
    elif assunto and len(assuntos) < 5:
        assuntos.append(assunto)
        atualizar_conteudo()

        entry_1.delete(0, 'end')
        assunto_count += 1
        label_counter.config(text="")
    elif assunto and len(assuntos) == 5:
        messagebox.showwarning("Erro", "O limite de 5 assuntos foi excedido.")
    else:
        messagebox.showwarning("Erro", "Nenhum assunto foi digitado")


def apagar_primeiro_assunto():
    if len(assuntos) >= 1:
        assuntos.pop(0)
        atualizar_conteudo()

def apagar_segundo_assunto():
    if len(assuntos) >= 2:
        assuntos.pop(1)
        atualizar_conteudo()

def apagar_terceiro_assunto():
    if len(assuntos) >= 3:
        assuntos.pop(2)
        atualizar_conteudo()

def apagar_quarto_assunto():
    if len(assuntos) >= 4:
        assuntos.pop(3)
        atualizar_conteudo()

def apagar_quinto_assunto():
    if len(assuntos) >= 5:
        assuntos.pop(4)
        atualizar_conteudo()

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    808.0,
    322.5,
    image=entry_image_3
)


entry_3 = Text(
    bd=0,
    bg="#CACACA",
    fg="#000716",
    highlightthickness=0,
    font=("Poppins Light", 16 * -1),
    wrap='word',
    state=NORMAL
)
entry_3.place(
    x=646.0,
    y=250.0,
    width=324.0,
    height=143.0
)


# scroll vertical 2
scrollbar_dois = Scrollbar(window, orient="vertical", command=entry_3.yview)
entry_3.configure(yscrollcommand=scrollbar_dois.set)

scrollbar_dois.place(
    x=970.0,
    y=250.0,
    height=143.0
)




# Função para criar e exibir gráficos com rolagem e scroll do mouse apenas no Canvas
def plotar_com_rolagem(widget_pai):
    largura, altura = 324, 143

    # Canvas com barra de rolagem, sem bordas
    canvas = Canvas(widget_pai, width=largura, height=altura, highlightthickness=0)
    barra_rolagem = Scrollbar(widget_pai, orient="vertical", command=canvas.yview)
    quadro_rolavel = Frame(canvas)

    # Configurar o Canvas para a barra de rolagem
    quadro_rolavel.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=quadro_rolavel, anchor="nw")
    canvas.configure(yscrollcommand=barra_rolagem.set)

    # Posicionamento do Canvas e Barra de Rolagem
    canvas.place(x=646, y=417)  
    barra_rolagem.place(x=660 + largura - 15, y=417, height=altura)

    # Função para criar gráfico circular (pizza)
    def criar_grafico_pizza(pai, dados, rotulos, titulo, posicao_y):
        titulo_label = Label(pai, text=titulo, font=("Poppins Bold", 14 * -1), fg='#250C6B', bg="#F0F0F0") 
        titulo_label.pack(pady=(posicao_y, 1))

        figura = Figure(figsize=(largura / 100, altura / 100), dpi=100)
        eixo = figura.add_subplot(111)

        # Função para customizar o texto das porcentagens
        def calcular_porcentagem(valores):
            def autopct(pct):
                total = sum(valores)
                val = int(round(pct * total / 100.0))
                return f'{pct:.1f}%'
            return autopct

        cores = ['#9ACD32', '#FFD700', '#FF6347']
        
        eixo.pie(dados, labels=rotulos, autopct=calcular_porcentagem(dados), startangle=90,
                 textprops={'fontsize': 8}, colors=cores)
        eixo.axis('equal')
        figura.patch.set_facecolor('none')

        # Canvas para a figura
        grafico_canvas = FigureCanvasTkAgg(figura, master=pai)
        grafico_canvas.draw()
        widget_grafico = grafico_canvas.get_tk_widget()
        widget_grafico.pack(pady=(0, 10))

    rotulo = ['sim', 'neutro', 'não']

    valores1 = [53, 22, 25]
    criar_grafico_pizza(quadro_rolavel, valores1, rotulo, titulo="Pergunta 1", posicao_y=0)

    valores2 = [10, 50, 40]
    criar_grafico_pizza(quadro_rolavel, valores2, rotulo, titulo="Pergunta 2", posicao_y=0)

    valores3 = [10, 82, 8]
    criar_grafico_pizza(quadro_rolavel, valores3, rotulo, titulo="Pergunta 3", posicao_y=0)

    valores4 = [100, 40, 0]
    criar_grafico_pizza(quadro_rolavel, valores4, rotulo, titulo="Pergunta 4", posicao_y=0)

    valores5 = [10, 40, 40]
    criar_grafico_pizza(quadro_rolavel, valores5, rotulo, titulo="Pergunta 5", posicao_y=0)

# Configuração e exibição dos gráficos no Canvas
plotar_com_rolagem(widget_pai=canvas)  # Substitua 'canvas' pelo widget pai adequado, se necessário
 




canvas.create_text(
    105.0,
    192.0,
    anchor="nw",
    text="Adicionar assuntos",
    fill="#250C6B",
    font=("Poppins Bold", 16 * -1)
)

canvas.create_text(
    105.0,
    210.0,
    anchor="nw",
    text="abordados",
    fill="#250C6B",
    font=("Poppins Bold", 16 * -1)
)

canvas.create_text(
    646.0,
    191.0,
    anchor="nw",
    text="Presença e",
    fill="#250C6B",
    font=("Poppins Bold", 16 * -1)
)

canvas.create_text(
    646.0,
    209.0,
    anchor="nw",
    text="Feedback",
    fill="#250C6B",
    font=("Poppins Bold", 16 * -1)
)

canvas.create_text(
    105.0,
    297.0,
    anchor="nw",
    text="Deseja apagar algum?",
    fill="#250C6B",
    font=("Poppins Regular", 14 * -1)
)

canvas.create_text(
    105.0,
    245.0,
    anchor="nw",
    text="max assuntos: 5",
    fill="#250C6B",
    font=("Poppins Regular", 10 * -1)
)

canvas.create_text(
    254.0,
    245.0,
    anchor="nw",
    text="max caracteres: 40",
    fill="#250C6B",
    font=("Poppins Regular", 10 * -1)
)


canvas.create_text(
    689.0,
    572.0,
    anchor="nw",
    text="Encerre o sistema para obter os resultados",
    fill="#250C6B",
    font=("Poppins Regular", 11 * -1)
)


def enviar_assunto():
    formatados = assuntos_formatados(assuntos)
    msg = (formatados)
    enviar_mensagem_mqtt(msg)

button_enviar_assunto = PhotoImage(
    file=relative_to_assets("button_enviar.png"))
button_enviar = Button(
    image=button_enviar_assunto,
    borderwidth=0,
    highlightthickness=0,
    command=enviar_assunto,
    relief="flat"
)
button_enviar.place(
    x=363.0,
    y=200.0,
    width=66.0,
    height=25.0
)





# botão pra adicionar assunto
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=comando,
    relief="flat"
)
button_1.place(
    x=363.0,
    y=258.0,
    width=66.0,
    height=25.0
)



def encerrar_programa():
    msg = "comando_encerrar"
    enviar_mensagem_mqtt(msg)
    

# botão pra encerrar e colher dados
button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=encerrar_programa,
    relief="flat"
)
button_2.place(
    x=812.0,
    y=202.0,
    width=158.0,
    height=25.0
)



def iniciar():
    comando = "comando_iniciar"
    enviar_mensagem_mqtt(comando)

# botão pra iniciar o sistema
button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=iniciar,
    relief="flat"
)
button_3.place(
    x=955.0,
    y=78.0,
    width=96.0,
    height=22.0
)




#criação e configuração da janela criada quando aciona o botao de wifi
def atualizar_wifi():
    
    def centralizar_janela(janela):
        janela.update_idletasks()
        
        largura = janela.winfo_width()
        altura = janela.winfo_height()
        
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        
        janela.geometry(f"{largura}x{altura}+{x}+{y}")
    

    

    # decodigica a string base64
    icone_bytes = base64.b64decode(icone_wifi_base64)
    icone_imagem = PhotoImage(data=icone_bytes)


    icone_conectar_format = base64.b64decode(botao_conectar_conf)
    icone_conectar_formatado = PhotoImage(data=icone_conectar_format)


    janela2 = Toplevel()
    janela2.title('WIFI')
    janela2.geometry('250x250') 
    janela2.resizable(False, False)
    janela2.configure(bg='#f0f0f0') 
    janela2.iconphoto(False, icone_imagem)
    centralizar_janela(janela2)
    janela2.grab_set()

    label_titulo = Label(janela2, text="Conecte o ESP32", font=("Poppins Bold", 14), fg='#250C6B', bg='#f0f0f0')
    label_titulo.pack(pady=10)

    label_usuario = Label(
        janela2,
        text="Rede",
        font=("Poppins Regular", 8),
        fg='#250C6B',
        bg='#f0f0f0'
    )

    label_usuario.place(
        x = 30.5,
        y = 58.0
    )

    label_senha = Label(
        janela2,
        text="Senha",
        font=("Poppins Regular", 8),
        fg='#250C6B',
        bg='#f0f0f0'
    )

    label_senha.place(
        x = 30.5,
        y = 110.0
    )

    entrada_nome = Entry(
        janela2,
        bd=0,
        bg='#CACACA',
        fg='#000716',
        highlightthickness=0,
        font=("Popping Regular", 12)
    )
 
    entrada_nome.pack(pady=15)

    entrada_senha = Entry(
        janela2,
        bd=0,
        bg='#CACACA',
        fg='#000716',
        highlightthickness=0,
        font=("Popping Regular", 12)
    )
 
    entrada_senha.pack(pady=17)


    def comando_login(): #desativado para funcionamento do protótipo

        rede = entrada_nome.get()
        senha = entrada_senha.get()

        login_enviar = (f"comando_wifi{rede}+{senha}")
        enviar_mensagem_mqtt(login_enviar)
        label_resposta.config(text=f"{login_enviar}")





    button_exibir = Button(
        janela2,
        image=icone_conectar_formatado,
        borderwidth=0,
        highlightthickness=0,
        #command=comando_login, #desativado para funcionamento do protótipo
        relief="flat"
    )
    button_exibir.image = icone_conectar_formatado

    button_exibir.pack(pady=12)

    label_resposta = Label(janela2, text="", font=("Poppins Regular", 12), bg='#f0f0f0')
    label_resposta.pack(pady=10)




icone_botao_wifi_format = base64.b64decode(botao_wifi_png)
icone_botao_wifi_formatado = PhotoImage(data=icone_botao_wifi_format)

button_wifi = Button(
    image=icone_botao_wifi_formatado,
    borderwidth=0,
    highlightthickness=0,
    command=atualizar_wifi,
    relief="flat"
)
button_wifi.place(
    x=925.0,
    y=78.0,
    width=25.0,
    height=25.0
)


# botão pra apagar o primeiro assunto
button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=apagar_primeiro_assunto,
    relief="flat"
)
button_4.place(
    x=284.0,
    y=294.0,
    width=25.0,
    height=25.0
)

# botão pra apagar o segundo assunto
button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=apagar_segundo_assunto,
    relief="flat"
)
button_5.place(
    x=314.0,
    y=294.0,
    width=25.0,
    height=25.0
)

# botão pra apagar o terceiro assunto
button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=apagar_terceiro_assunto,
    relief="flat"
)
button_6.place(
    x=344.0,
    y=294.0,
    width=25.0,
    height=25.0
)

# botão pra apagar o quarto assunto
button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=apagar_quarto_assunto,
    relief="flat"
)
button_7.place(
    x=374.0,
    y=294.0,
    width=25.0,
    height=25.0
)

# botão pra apagar o quinto assunto
button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=apagar_quinto_assunto,
    relief="flat"
)
button_8.place(
    x=404.0,
    y=294.0,
    width=25.0,
    height=25.0
)


# Botão para atualizar lista de alunos
button_image_9 = PhotoImage(file=relative_to_assets("button_9.png"))
button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=atualizar,
    relief="flat"
)
button_9.place(x=23.0, y=78.0, width=22.0, height=22.0)

def destruir():
    window.destroy()
    sys.exit()

# Botão para fechar o programa
button_image_10 = PhotoImage(file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=destruir,
    relief="flat"
)
button_10.place(x=1043.0, y=15.0, width=15.0, height=14.0)

def atualizar_relogio():
    agora = time.localtime()
    hora_str = time.strftime("%H:%M:%S", agora)
    canvas.itemconfig(texto_relogio, text=hora_str)
    window.after(1000, atualizar_relogio)

agora = time.localtime()
hora_str = time.strftime("%H:%M:%S", agora)

texto_relogio = canvas.create_text(
    470.0,
    62.0,
    anchor="nw",
    text=hora_str,
    fill="#250C6B",
    font=("Poppins Bold", 36 * -1)
)

atualizar_relogio()

window.update_idletasks()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = window.winfo_width()
window_height = window.winfo_height()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"+{x}+{y}")

window.resizable(False, False)
window.mainloop()
* CheckIn Class

O CheckIn Class é um sistema de presença e feedback desenvolvido para melhorar a interação em salas de aula.
O projeto busca automatizar o registro de presença e permitir que os alunos forneçam feedback sobre as aulas, promovendo um ambiente educacional mais engajado.
Esse sistema foi idealizado para simplificar o acompanhamento da frequência dos alunos e personalizar o ensino com base no retorno deles.

Objetivos:<br>

1 - Monitorar a frequência dos alunos;<br>
2 - Facilitar a comunicação entre alunos e professores;<br>
3 - Aumentar a participação em sala de aula;<br>
4 - Personalizar a metodologia de ensino com base no feedback.<br>

Componentes:<br>

1 - ESP32: Microcontrolador central que gerencia a comunicação via Wi-Fi com o sistema Python do professor.<br>
2 - Teclado matricial (4x3): Para inserção das matrículas.<br>
3 - Teclado colorido (3 botões): Para votação dos alunos (verde, amarelo, e vermelho para “sim”, “neutro” e “não”).<br>
4 - Display LCD 20x4: Exibe instruções e feedback.<br>

Funcionamento:<br>
Os alunos inserem suas matrículas no teclado matricial, que são validadas e mostradas no display LCD. Em seguida, respondem a tópicos discutidos em sala usando o teclado colorido.
Os dados coletados são enviados em tempo real ao sistema Python do professor via protocolo MQTT, que permite o controle completo do sistema.
No final, o professor recebe um relatório detalhado da presença e das respostas dos alunos.

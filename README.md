# PMR3402 - Monitoramento de Plantas

Este projeto foi desenvolvido como parte da disciplina PMR3402 - Sistemas Embarcados (2024), para monitoramento de temperatura de plantas utilizando Streamlit e Supabase.

## Sobre o Projeto

O projeto consiste em uma aplicação web para monitoramento de temperatura, umidade e umidade do solo de plantas. Os dados são coletados por um dispositivo embarcado e armazenados no banco de dados Supabase. A interface gráfica é desenvolvida em Streamlit, permitindo visualizar gráficos e alertas com base nos dados coletados.

## Funcionalidades

- **Inserção de Detalhes da Planta:** O usuário pode inserir o nome da planta, temperatura mínima e máxima suportadas, e escolher entre gráficos de barras ou linhas.
  
- **Busca de Dados:** Ao pressionar o botão "Buscar Dados", a aplicação faz uma consulta ao banco de dados Supabase para obter os dados coletados da planta específica.

- **Visualização de Dados Agregados:** Após a busca, os dados são processados para calcular as grandezas médias diárias de temperatura, umidade e umidade do solo.

- **Gráficos Interativos:** Os dados processados são exibidos em gráficos de barras ou linhas, conforme escolhido pelo usuário. Os gráficos mostram a variação da temperatura ao longo dos dias, com destaque para temperaturas muito altas ou baixas.

- **Alertas de Temperatura:** A aplicação também exibe alertas de temperatura, indicando se os valores coletados estão abaixo da mínima, acima da máxima ou dentro dos limites ideais para a planta.

## Tecnologias Utilizadas

- **Streamlit:** Framework de código aberto para criar aplicativos da web de maneira simples e eficiente utilizando Python.

- **Supabase:** Plataforma open-source que fornece bancos de dados PostgreSQL como serviço, com APIs para consultas e manipulação de dados.

- **Matplotlib e Pandas:** Bibliotecas Python amplamente utilizadas para visualização de dados e manipulação de estruturas de dados, respectivamente.

## Pré-Requisitos

- Python 3.6 ou superior
- Bibliotecas necessárias (instaladas via pip):


## Como Executar

1. Clone o repositório para sua máquina local.
2. Configure as variáveis de ambiente no arquivo `.env` com as credenciais do Supabase.
3. Abra um terminal na pasta do projeto e execute o comando:


Substitua `nome_do_arquivo.py` pelo nome do seu script principal.

## Autor

- Grupo D

## Licença

© 2024 - Todos os direitos reservados - Grupo D
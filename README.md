# Fluig Oracle

Esse projeto visa coletar dados de sites, forums e documentações encontradas sobre o Fluig com objetivo de auxiliar no desenvolvimento de funcionalidades e aplicações dos desenvolvedores na empresa em que trabalho, com o fim único e exclusivo de melhorar o desenvolvimento, tornando a consulta mais rápida e fácil, trazendo assim, maior agilidade.

Até o momento foi coletado apenas informações do site https://style.fluig.com/ que contém informações em sua maioria para o desenvolvimento em front-end. Inicialmente a aplicação será utilizada também como um dos projetos de disciplina de Pós-Graduação em IA e Machine Learning da Infnet.

A ideia é que com o passar do tempo essa aplicação se desenvolva e passe a coletar e receber dados, após análise, de novas documentações e informações de fontes on-line e do usuário através de arquivos em PDF. 

## Principais conceitos e tecnologias utilizadas
- Scraping (utilizando Scrapy)
- Armazenamento em SQLite
- Langchain + LLM (GPT-4o-mini - OpenAI) + RAG
- Streamlit

## Instruções para uso
Após clonar o repositório ou baixar ele em seu computador, siga os seguintes passos:

1. Crie um arquivo *.env* e adicione a sua chave da OpenAI conforme o *.env-sample* indica (OPENAI_API_KEY)

2. Instale as libs com:
```shell
pip install .
```
Ou você pode também utilizar um ambiente virtual para isso, no projeto foi utilizado venv, opcionalmente você pode antes de instalar as libs ativar o ambiente colocando no terminal:
```
.\.venv\Scripts\activate 
```

3. Execute no CMD os comandos:
```shell
cd scraper_app
scrapy crawl fluig_dev_spider
```
Isso irá popular a tabela que está no arquivo de banco *content_data.db* 

4. Em seguida execute:
```shell
cd ..
streamlit run src/app.py
```
Na primeira vez que executar o streamlit ele irá pedir um e-mail, mas você pode apenas seguir apertando enter.

A aplicação rodará localmente na porta *8501*, você pode acompanhar em http://localhost:8501
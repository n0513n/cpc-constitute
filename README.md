🇧🇷 CPC-CONSTITUTE
---

### Sobre o projeto

<img align="center" src="img/cpc.jpg" width="50%" heigth="50%" />

Este projeto visa a criação de uma plataforma de código aberto que disponibilize **informações constitucionais sobre o funcionamento dos sistemas de governo** em democracias a nível global, por via da interação com a API do **[Project Constitute](https://www.constituteproject.org/)**, além de redes de notícias, enciclopédias e citações acadêmicas.

O **[Centro de Política Comparada (CPC)](http://www.cpc.ufes.br)** é um núcleo de pesquisas vinculado ao Departamento de Ciências Sociais (DCSO) da Universidade Federal do Espírito Santo (Ufes), fundado e registrado no Diretório dos Grupos de Pesquisa no Brasil, do CNPq, em 2016.

### Requisitos

* **Python 2.7+/3.6+**
* community==1.0.0b1
* matplotlib==3.1.1
* networkx==2.3
* news-please==1.4.21
* newsapi-python==0.2.5
* newspaper3k==0.2.8
* numpy==1.16.2
* pandas==0.25.0
* seaborn=0.9.0
* wikipedia==1.4.0

### Instruções de uso

O projeto encontra-se com o código para obtenção de dados e interação com API já desenvolvido, podendo ser importado ou executado localmente utilizando [Jupyter](https://jupyter.org/) ou plataformas virtuais como o [Colab](https://colab.research.google.com/). 

Funções desenvolvidas:

* Interagir com a API do Constitute Project para realizar buscas e demais ações;
* Disponibilizar o acesso a dados sobre o modo de organização dos sistemas de governo;
* Comparar características entre sistemas presidencialistas, parlamentaristas e híbridos;
* Possibilitar pesquisas de excertos e temáticas presentes nos textos constitucionais;
* Buscar publicações associadas às constituições pesquisadas e a artigos acadêmicos;
* Capturar notícias recentes do conceito ou país pesquisado pelo MediaCloud/News API;
* Coletar dados de tweets publicados a priori na última semana com "política" atualmente;
* Pesquisar correlações entre páginas da Wikipédia sobre os termos de busca utilizados.

### Exemplos de uso

### Importar código fonte

```
import src as cpc
```

### Interação com a API do Constitute

* Buscar constituições da África:

`cpc.constitute_query('constitutions', '?region=Africa')`

* Buscar constituições da África e Europa:

`cpc.constitute_query('constitutions', '?region=Africa&region=Europe')`

* Buscar constituições da Ucrânia:

`cpc.constitute_query('constitutions', '?country=Ukraine')`

* Buscar constituições de 1954 a 2000:

`cpc.constitute_query('constitutions', '?from_year=1954&to_year=2000')`

* Buscar constituições europeias desde 1960:

`cpc.constitute_query('constitutions', '?region=Europe&from_year=1960')`

* Buscar constituições em língua inglesa:

`cpc.constitute_query('constitutions', '?lang=en')`

* Listar todas as constituições em vigor:

`cpc.constitute_query('constitutions', '?historic=false')`

* Tópicos disponíveis para busca em inglês:

`cpc.constitute_query('topics', '?lang=en')`

* Regiões disponíveis para busca em espanhol:

`cpc.constitute_query('locations', '?lang=es')`

* Busca por emendas na Ucrânia entre 1954 e 2000:

`cpc.constitute_query('constopicsearch', '?key=amend&country=Ukraine&from_year=1954&to_year=2000')`

* Busca por emendas de antigas constituições da África e da Europa:

`cpc.constitute_query('constopicsearch', '?key=amend&region=Africa&region=Europe&historic=true')`

* Conteúdo da constituição da Austrália de 1985 em inglês:

`cpc.constitute_query('html', '?cons_id=Australia_1985&lang=en')`

## Outras funções de busca e integração

* Buscar apenas os artigos mais vistos sobre democracia no MediaCloud:

`cpc.news_search('democracy', method='mediacloud')`

* Buscar notícias de política em português nos últimos 7 dias na News API:

`cpc.news_search('política', lang='pt', days=7, method='newsapi')`

* Buscar o PDF da constituição do Brasil no Google:

`cpc.google_search('Constituição+Brasil+filetype:pdf')`

* Conteúdo do artigo de Democracia na Wikipédia:

`cpc.wiki_page("Democracia", lang='pt')`

* Relações com demais verbetes da Wikipédia (hyperlinks):

`cpc.wiki_graph("Democracia", lang='pt')`

* Tópicos em tendência na rede do Twitter no Brasil:

`cpc.trending_topics('BR')`

* Tweets publicados com democracia na última semana:

`cpc.twitter_search('democracia', days=7)`

* Tweets publicados ao vivo com "política" na rede:

`cpc.twitter_search('política', method='stream')`

**Nota:** a interação com as APIs do News API, MediaCloud e Twitter requer o uso de credenciais de usuário.

### Futuras atualizações

Sugestões de futuras atualizações incluem a revisão e reestruturação dos arquivos do repositório, focado no desenvolvimento de um webaplicativo que vise integrar os resultados do código desenvolvido em uma interface de usuário.

### Referências

* [Comparative Constitutions Project](https://comparativeconstitutionsproject.org/)

* [Constitute API Documentation](https://docs.google.com/document/d/1wATS_IAcOpNZKzMrvO8SMmjCgOZfgH97gmPedVxpMfw/pub)

* [Constitute Project](https://www.constituteproject.org)

* [constviz @ GitHub](https://github.com/thequbit/constviz/blob/master/README.md)

* [Google Search API @ GitHub](https://github.com/abenassi/Google-Search-API)

* [Glossary of constitutional terms](https://www.infoplease.com/chemistry/glossary/glossary-constitutional-terms)

* [Scraping Constitute](https://sites.psu.edu/bdssblog/author/rbm166/)

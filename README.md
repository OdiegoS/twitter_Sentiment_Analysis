# twitter_Sentiment_Analysis
Projeto 1 da Disciplina Programação Paralela e Concorrente da Universidade Federal de Sergipe (UFS)


## TwitterApi_Key.txt
Como as keys são de uso privado para um usuário dev, foi criado um arquivo _TwitterApi_Key_ para guardar essas informações **_LOCALMENTE_**, o programa principal irá ler esse arquivo e carregar as keys.
As keys devem ser adicionadas no TwitterApi_key **manualmente** nessa ordem: consumer_key, consumer_secret, access_token, access_token_secret.
**Obs:** Não adicione esse arquivo para commit.

## Original_twitterSentimentAnalysis
É o código disponibilizado no site do [Geeks for Geeks](https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/) modificado para conter uma busca maior do que 100 tweets. O arquivo com o final Paralelo, é o mesmo código com a funcionalidade de de executa-lo com multithreading ou multiprocesso.

## Teste nas versões paralelas
- Mudar a variável global control para definir que tipo de execução será utilizado (N para sequencial, P para multiprocesso, e T para multithreading)
- Deixa uma quantidade de tweests razoáveis, acho que 200 é bom, mas pode ser 1000 também...qt maior, mais demorado não só para pegar como por causa do block (comento mais embaixo).
- Se estiver utilizando alguma versão paralela "control = P or T", coloca a quantidade de threads/processo em qt_multi, nesse momento utiliza um valor divisível para quantidade de tweets, pois eu ainda não tratei o caso de uma divisão não inteira.
- Apenas ao usar a versão multithreadings: existem dois métodos de multithreading, o primeiro método basta deixa-lo descomentado e executa-lo, o segundo método é necessário além da chamada dele descomentar em dois momentos a lista resultados[]. Lembre-se de comentar o que não for utilizado para aquele método.
- Sobre o block: a api do twitter permite apenas uma quantidade fixa de requests a cada 15min (se n me engano), n lembro a quantidade, mas é mais que 1000. Então ao ver uma mensagem com algo do tipo "limit exceeded" é porque ele bloquiou e só vai continuar a execução passado o tempo em segundos que ele dá logo depois da mensagem. Caso isso ocorra, ignore esse teste que foi bloqueado já que o tempo esperando vai contar no tempo de execução.


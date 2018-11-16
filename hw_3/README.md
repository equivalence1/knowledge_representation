# Used libraries
- [dbpedia/spotlight-rusian](https://github.com/dbpedia-spotlight/spotlight-docker)
- [pymystem3](https://github.com/nlpub/pymystem3)
- [deepmipt/ner](https://github.com/deepmipt/ner)
- [wikipedia-python-api](https://github.com/goldsmith/Wikipedia)
- [sparqlwrapper](https://rdflib.github.io/sparqlwrapper/)


# Solution Description

Сначала я использовал просто библиотеку DBpedia Spotlight,
которая работает с русским языком (см. [репозиторий](https://github.com/dbpedia-spotlight/spotlight-docker)).

Она в целом неплохо работает в плане того, что узнает много названий
организаций, мест и людей. Но у нее есть пара проблем: 

Первая -- она
выдает uri вида `ru.dbpedia.org`. Я что-то не смог найти дамп троек
с таким доменом, просто сайт dbpedia о них не знает, там на русские
uri даже не проставленно `dbo:sameAs`. Но можно заметить, что на самом
деле эти uri тривиальным образом сгенерированы из русской википедии,
поэтому эти uri тривиальным образом преобразуются в url на русскую
википедию, так что эти uri все равно полезны.

Вторая -- она фигово работает с категорией Person. Иногда она, например,
фамилию или имя человека считает за название местности. Многих фамилий она
вообще не понимает, особенно если там использованны склонения. Вообще,
эта библиотека в целом довольно странно работает со склонениями. Она 
их использует для поиска, и иногда это хорошо, иногда не очень. Поэтому
не получается просто все застемить.

Для борьбы со второй проблемой я делаю следующее. Я нашел библиотеку
`pymystem3`, написанную Яндексом. Она довольно хорошо умеет определять
русские имена и фамилии, чуть хуже зарубежные, но с использованием
небольших эвристик можно довольно неплохо определять и их.

Использую я эту библиотеку так -- перед запускам `ru-dbpedia-spotlight`,
я использую `pymystem3`, чтобы задать набор ограничений вида "эта
подстрока title'a является упоминанием Person'a, поэтому если 
`ru-dbpedia-spotlight` аннотирует ее как Organization или Place, то игнорируй
это". Затем, уже после отработки `ru-dbpedia-spotlight`, я тех Person,
что еще не проаннотированны ищу в википедии и, если там что-то нашлось,
использую `dbo:sameAs` для поиска uri в dbpedia.

К сожалению, api поиска по википедии довольно кривое. Т.к. нам надо
получить английскую страничку, чтобы взять из нее pageid, то нам приходится
отправлять запрос на русском языке в английскую версию wikipedia, которая
с русским языком фигово работает (основная проблема -- склонения), поэтому 
иногда образуются всякие странные результаты (например, запрос "Павел Дуров"
выдает страничку про Павла Дурова, а "Павла Дурова" про Alex Neff). Можно
было бы искать на русском, брать точный заголовок, и потом запрашивать
такую страницу в английской версии (и это работает хорошо), но это работает
в 2 раза дольше, т.к. приходится делать 2 запроса, вместо одного.

Затем, после этих манипуляций я еще скармливаю запрос в NER (библиотека для
Named Entity Recognition, основанная на методах ML и натренированная именно
на поиск Organization/Person/Place). Она тоже немного иногда помогает, особенно
когда `ru-dbpedia-spotlight` не смог в склонения.

Из wikipedia я всегда везде беру первый результат. Если еще доставать всякие
abstract, то, во-первых, это не сильно помогает, т.к. новость к этому abstract 
часто не относится, во-вторых, это работало бы еще дольше, а у меня и так все
это за несколько часов считается (если использовать только `ru-dbpedia-spotlight`,
то работало бы 10 минут. А так очень много времени уходит на работу с сетью при
обращении к wikipedia. + мне кажется, у них есть лимиты на запросы с одного IP).

# Results

"В качестве метрик используйте микроусредненные точность и полноту."

Честно говоря, я не очень понимаю, как это делать. Я могу, наверно,
проанализировав сам все эти 100 заголовков понять, какие из тех, что
предложил мой аннотатор нерелевантны (т.е. я могу оценить precision,
хоть это и займет много времени), но вот я вообще не понимаю, как оценивать
recall. Надо ручками попытаться найти все возможные сущности в русской
и английской версии dbpedia и понять, кто из них может быть связан, а кто нет (
"попытаться понять" потому, что я не знаю многих из фамилий и многих названий
организаций. Поэтому мне сложно понять, действительно ли эти 2 фамилии в заголовки
связаны. Например, первый же заголовок "Виктория Скрипаль не верит в подлинность обращения Юлии" --
я не знаю, кто такая Юлия (Тимошенко? О_о), и вполне возможно, что это известная личность,
про которую что-то написано в википедии).

В общем, я не знаю, как считать precision и recall не потрартив на это несколько недель
и не разобравшись досконально в политической ситуации в России и мире, поэтому
я это не сделал.
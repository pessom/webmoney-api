Потребовалось мне как то реализовать поддержку Webmoney API (<a href="https://wiki.webmoney.ru/projects/webmoney/wiki/XML-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B">Документация</a>) в проекте. Библиотеке на питоне я не нашел, поэтому решил написать свою. 


<a href="https://bitbucket.org/sallyruthstruik/python-webmoney-api">Ссылка на репозиторий</a>

Итак, есть два варианта запроса к апи вебманей.

<ul>
    <li> Keeper Classic - каждый запрос подписывается с помощью проги WMSign </li>
    <li> Keeper Light - запросы отправляются через защищенное HTTPS соединение с клиентским сертификатом. </li>
</ul>

Я рассматриваю только второй вариант. Для запроса потребуется сертификат. Как его получить написано <a href="https://wiki.webmoney.ru/projects/webmoney/wiki/%D0%9F%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D1%81%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82">Здесь</a>. У меня получилось получить сертификат только из Firefox'а, Chrome вообще не поддерживает такую возможность, а Explorer (Windows 8) выдал ошибку. После получения сертификат нужно экспортировать в файл. Какк это сделать написано <a href="https://wiki.webmoney.ru/projects/webmoney/wiki/%D0%AD%D0%BA%D1%81%D0%BF%D0%BE%D1%80%D1%82_%D0%BA%D0%BB%D1%8E%D1%87%D0%B0_Keeper_Light">Тут</a>

Сертификат экспортируется в pkcs12 файл. Нужно из него получить публичный и приватный ключи. Делается это командами:
<source lang="bash">
    openssl pkcs12 -in path.p12 -out crt.pem -clcerts -nokeys
    openssl pkcs12 -in path.p12 -out key.pem -nocerts -nodes
</source>

<h4>Работа с API</h4>

Пакет можно установить через pip:

<source lang="bash">
pip install webmoney-api
</source>

После установки импортируем библиотеки

<source lang="python">
from webmoney_api import ApiInterface, WMLightAuthInterface
</source>

<b>WMLightAuthInterface</b> - класс, описывающий аутентификацию через Keeper Light.
<b>ApiInterface</b> - класс апи.

Подключаем:

<source lang="python">
>>> api = ApiInterface(WMLightAuthInterface("/home/stas/wmcerts/crt.pem", "/home/stas/wmcerts/key.pem"))
</source>

При инициализации WMLightAuthInterface, передаем в него пути до наших сгенеренных публичного и приватного ключа
После подключения доступны следующие методы:

x1 - x10 - соответствуют аналогичным интерфейсам вебманей. Параметры передаются поименно в вызываемый метод. 
Дополнительно можно передать параметр <b>reqn</b> - номер запроса. 

Метод делает запрос и возвращает данные в формате:
<source>
{"retval": <retval>,     
"retdesc": <retdesc>, 
"response": <response}
</source>

где

<ul>
    <li>retval - код ответа, возвращаемый вебманями. 0 если запрос успешен. Коды можно посмотреть <a href="https://wiki.webmoney.ru/projects/webmoney/wiki/%D0%98%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81_X2">тут</a></li>
    <li>retdesc - если retval != 0, тут лежит описание ошибки</li>
    <li>response - распарсенный в OrderedDict ответ запроса. Тут лежат только данные, касающиеся запроса. Например, для запроса
        <source>
            <w3s.response>
                <reqn></reqn>
                <retval></retval>
                <retdesc></retdesc>
                <operation id="n1" ts="n2">
                    <tranid></tranid>
                    <pursesrc></pursesrc>
                    <pursedest></pursedest>
                    <amount></amount>
                    <comiss></comiss>
                    <opertype></opertype>
                    <period></period>
                    <wminvid></wminvid>
                    <orderid></orderid>
                    <desc></desc>
                    <datecrt></dateupd>
                    <dateupd></dateupd>
                </operation>
            </w3s.response>
        </source>
        в response будет лежать распарсенный 
        <source>
            <operation id="n1" ts="n2">
                <tranid></tranid>
                <pursesrc></pursesrc>
                <pursedest></pursedest>
                <amount></amount>
                <comiss></comiss>
                <opertype></opertype>
                <period></period>
                <wminvid></wminvid>
                <orderid></orderid>
                <desc></desc>
                <datecrt></dateupd>
                <dateupd></dateupd>
            </operation>
        </source>
        Парсинг осуществляется с помощью библиотеки https://github.com/martinblech/xmltodict
        </li>
</ul>

<h4>Пример: поиск ID юзера по кошельку</h4>

 <source lang="python">
>>> api.x8(purse="R328079907035", reqn=int(time.time()))["response"]
OrderedDict([(u'wmid', OrderedDict([(u'@available', u'0'), (u'@themselfcorrstate', u'0'), (u'@newattst', u'110'), ('#text', u'407414370132')])), (u'purse', OrderedDict([(u'@merchant_active_mode', u'-1'), (u'@merchant_allow_cashier', u'-1'), ('#text', u'R328079907035')]))])

>>> api.x8(purse="R328079907035", reqn=int(time.time()))["response"]["wmid"]["#text"]
u'407414370132'

>>> api.x8(purse="R328079907035", reqn=int(time.time()))["response"]["wmid"]["@available"]
u'0'
 </source>

<h4>Пример: получение истории всех выписанных счетов по кошельку</h4>

<source lang="python">
>>> api.x4(purse="R328079907035", datestart="20100101 00:00:00", datefinish="20140501 00:00:00")
ValueError: Error while requesting API. retval = -4, retdesc = wrong w3s.request/reqn step=2
Request data: {'cert': ('/home/stas/wmcerts/crt.pem', '/home/stas/wmcerts/key.pem'),
 'data': '<w3s.request><reqn></reqn><getoutinvoices><datestart>20100101 00:00:00</datestart><datefinish>20140501 00:00:00</datefinish><purse>R328079907035</purse></getoutinvoices></w3s.request>',
 'url': 'https://w3s.wmtransfer.com/asp/XMLOutInvoicesCert.asp',
 'verify': False}
</source>

Ошибка, т.к. не передан параметр reqn. Передадим его:
<source lang="python">
>>> api.x4(purse="R328079907035", datestart="20100101 00:00:00", datefinish="20140501 00:00:00", reqn=int(time.time())) 
{'response': OrderedDict([(u'@cnt', u'0'), (u'@cntA', u'0')]),
 'retdesc': None,
 'retval': u'0'}
</source>

<h4>Пример: получение списка счетов на оплату</h4>

<source lang="python">
>>> for order in api.x10(wmid="407414370132", datestart="20100101 00:00:00", datefinish="20140501 00:00:00", reqn=int(time.time()))["response"]["ininvoice"]:
>>>     print order["orderid"], order["amount"], order["state"]

4640849 122.40 2
24 1.00 2
27 0.40 2
</source>

<h4>Ссылки</h4>

<ul>
    <li>Ссылка на репозиторий: https://bitbucket.org/sallyruthstruik/python-webmoney-api</li>
    <li>Документация Webmoney: https://wiki.webmoney.ru/projects/webmoney/wiki/XML-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B</li>
    <li>Документация xmltodict: https://github.com/martinblech/xmltodict</li>
</ul> 

Буду рад замечаниям и помощи)
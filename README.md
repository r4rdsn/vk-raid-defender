# о программе
**vk-raid-defender** может быть использован для добавления пользователей в беседы [вк](https://vk.com) в случае их исключения оттуда

# инструкция по установке и запуску на gnu/linux
* установи [python](https://www.python.org/downloads) версии не менее 3.6.0
* клонируй этот репозиторий:  
```$ git clone https://github.com/r4rdsn/vk-raid-defender.git```
* установи *vk-raid-defender* через скрипт установки:  
```# python vk-raid-defender/setup.py install```
* запусти программу:  
```$ vk-raid-defender```

# инструкция по установке и запуску на windows
* установи [python](https://www.python.org/downloads) версии не менее 3.6.0 (чекбокс "*Add Python to PATH*" при этом должен быть активирован)
* скачай [архив с этим репозиторием](https://github.com/r4rdsn/vk-raid-defender/archive/master.zip)
* в командной строке перейди в директорию со скачанным архивом:  
```> cd <директория>```
* распакуй архив в папку *vk-raid-defender*
* установи *vk-raid-defender* через скрипт установки:  
```> python vk-raid-defender/setup.py install```
* запусти программу:  
```> python -m vk_raid_defender```

# дополнительные зависимости
для работы протокола прокси socks5 (в частности, для выполнения запросов через tor) необходимо установить зависимость [PySocks](https://github.com/Anorov/PySocks):  
```python -m pip install PySocks```

# лицензия
данное программное обеспечение опубликовано под лицензией MIT (см. [LICENSE](https://raw.github.com/r4rdsn/vk-raid-defender/master/LICENSE))

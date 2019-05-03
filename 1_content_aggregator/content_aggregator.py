# plan:
# FIX   1. какие ресурсы и тематику хотим просматривать (сайты, с которых получать контент)
# https://www.finam.ru боковик события и рынки
# 2. использовать в фоне (обратить внимание на библиотеки Celery или Apscheduler)
# Выполняется по запросу, можно использовать Cron
# FIX   3. подумайте о БД, в которой будет храниться собранная информация
# подойдет самая легкая sqlite
from datetime import datetime, timedelta

import notify2
import peewee
import requests
from bs4 import BeautifulSoup

sqlite_db = peewee.SqliteDatabase('my_apps.db', timeout=1)


class BaseModel(peewee.Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = sqlite_db


class New(BaseModel):
    """New"""

    link = peewee.TextField(
        verbose_name='Ссылка на новость',
    )
    title = peewee.TextField(
        verbose_name='Заголовок новости',
    )
    add_date = peewee.DateTimeField(
        verbose_name='Дата добавления записи',
        default=datetime.today(),
    )
    is_sent = peewee.BooleanField(
        verbose_name='Отправлено',
        default=False,
    )

    def __repr__(self):
        return '{0}: {1} {2}'.format(
            self.__class__.__name__,
            self.add_date,
            self.title,
        )


class Parser(object):
    """News parser"""

    now = datetime.today()
    day = str(now.day).rjust(2, '0')
    month = str(now.month).rjust(2, '0')
    resource = 'https://www.finam.ru/analysis/united/rqdate{0}{1}7E3/'.format(day, month)

    def _get_page(self):
        """request resource"""
        response = requests.get(url=self.resource)
        if response.status_code == 200:
            result = response.text
        else:
            raise ConnectionError('Ресурс недоступен')
        return result

    def parse(self):
        """parse 1 page (30 notes)"""
        parse_list = []
        soup = BeautifulSoup(self._get_page(), features = "html.parser" )
        news_list = soup.find_all("div", "news-belt-sidebar-item")
        try:
            for n in news_list:
                info = n.contents[3].contents[0]
                parse_list.append([
                    (info.text or n.contents[3].text or '').replace('\n', ''),
                    'https://www.finam.ru{}'.format(info.attrs['href'])
                ])
        except:
            raise Exception('Ошибка парсинга страницы')
        return parse_list

    def __repr__(self):
        return self.__class__.__name__


if __name__ == "__main__":
    p = Parser()
    now = datetime.now()
    news = p.parse()
    sqlite_db.connect()
    # sqlite_db.create_tables([New])
    if news:
        old_new_titles = New.select().where(New.add_date > now-timedelta(days=2))
        old_titles = [a.title for a in old_new_titles]
        for new in news:
            if new[0] not in old_titles:
                New().insert(
                    title=new[0],
                    link=new[1],
                    add_date=now,
                    is_sent=False
                ).execute()

    # send notifications
    notify2.init("Notes")
    ids = []
    my_not_send_news = New.select().where(New.is_sent==False)
    for not_send_new in my_not_send_news:
        note = notify2.Notification(
            summary=not_send_new.title,
            message=not_send_new.link,
        )
        note.set_timeout(1000)
        note.show()
        ids.append(not_send_new.id)

    # update news as is_sent=True
    up = New.update(is_sent=True).where(New.id.in_(ids))
    up.execute()
    sqlite_db.close()

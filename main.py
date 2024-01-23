from kivy.uix.button import Button
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty
import data_manage
import datetime
import os

#################
# параметры БД  #
#################
dir_path = os.path.dirname(os.path.realpath(__file__))
db_file = dir_path + "./notes.db"
data_manage.initialize_note_table(db_file)

########################################
# класс с зметками о покупках (кнопка) #
########################################
class Note_card(Button):
    note_id = NumericProperty()
    note_title = StringProperty()
    note_content = StringProperty()
    note_date = StringProperty()

    def __init__(self, **kwargs):
        super(Note_card, self).__init__(**kwargs)
        self.text = str(self.note_title)  # надпись на кнопке - товар
        self.background_color = (0, 1, 0, .8)  # цвет кнопки до удаления товара

    # функция обработки события касания кнопки с товаром
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # print('нажата кнопка с товаром из БД')  # -------------------------------
            # Касание произошло внутри области виджетов
            notes_screen = self.parent.parent.parent.parent.parent.get_screen('notes')
            notes_screen.note_id = self.note_id
            iden = notes_screen.ids
            iden.note_title.text = self.note_title
            iden.note_content.text = self.note_content
            iden.note_content.scroll_y = 0
            self.parent.parent.parent.parent.manager.current = 'notes'


#############################################
# класс для загрузки заметок из БД          #
# для их просмотра (область со скроллингом) #
#############################################
class Note_view(ScrollView):
    def __init__(self, **kwargs):
        super(Note_view, self).__init__(**kwargs)
        self.update_scroll()

    def update_scroll(self):
        for c in list(self.children):
            if isinstance(c, GridLayout):
                self.remove_widget(c)
        layout = GridLayout(cols=2,
                            spacing=10,
                            size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        entry_list = []
        # подключиться к БД и загрузить список введенных товаров
        with data_manage.connect_to_db(db_file) as conn:
            entry_list = data_manage.query_notes(conn)

        # создать кнопки с названием загруженных товаров
        for i in entry_list:
            btn = Note_card(note_id=str(i[0]),
                            note_title=str(i[1]),
                            note_content=str(i[2]),
                            note_date=str(i[3]),
                            size_hint_y=None, height=40)
            layout.add_widget(btn)
        self.add_widget(layout)
        # print('Список введенных товаров сформирован')  # --------------


########################################
# класс для удаления заметки о товаре  #
########################################
class Delete_card(Button):
    note_id = NumericProperty()
    note_title = StringProperty()
    note_content = StringProperty()
    note_date = StringProperty()
    deletion_status = BooleanProperty()

    def __init__(self, **kwargs):
        super(Delete_card, self).__init__(**kwargs)
        self.text = str(self.note_title)
        self.background_color = (0, 1, 0, .8)
        self.deletion_status = False

    # функция обработки нажатия кнопки с заметкой о товаре
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # касание произошло внутри области виджета
            queue = []
            del_screen = self.parent.parent.parent.parent

            # отметить товар для удаления
            if self.deletion_status == False:
                queue.append(self.note_id)
                del_screen.items_to_delete.append(self.note_id)
                self.deletion_status = True
                self.background_color = (0, 1, 0, .3)
            # снять отметку товар об удалении
            else:
                self.deletion_status = False
                self.background_color = (0, 1, 0, .8)
                # print("Button id is: " + str(self.note_id)) # ---------------
                del_screen.items_to_delete.remove(self.note_id)


############################################
# класс для удаления заметок о товаре      #
# (область со скроллингом)                 #
############################################
class Delete_scroll(ScrollView):
    def __init__(self, **kwargs):
        super(Delete_scroll, self).__init__(**kwargs)
        self.update_scroll()

    def update_scroll(self):
        for c in list(self.children):
            if isinstance(c, GridLayout):
                self.remove_widget(c)
        layout = GridLayout(cols=2,
                            spacing=10,
                            size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        entry_list = []
        with data_manage.connect_to_db(db_file) as conn:
            entry_list = data_manage.query_notes(conn)

        # добавление кнопок с названиями товаров
        for i in entry_list:
            btn = Delete_card(note_id=str(i[0]),
                              note_title=str(i[1]),
                              note_content=str(i[2]),
                              note_date=str(i[3]),
                              size_hint_y=None,
                              height=40)
            layout.add_widget(btn)
        self.add_widget(layout)


#################################################
# класс экрана для перехода к зметкам о товарах #
#################################################
class Home(Screen):
    # функция формирования новой заметке о товаре
    def make_new_note(self):
        new_note = self.manager.get_screen('notes')
        new_note.ids.note_title.text = ''
        new_note.ids.note_content.text = ''
        self.manager.current = 'notes'  # перейти к окну заметки о товарах
        # print('Нажата кнопка - Новая заметка о товаре')  # -------------


#################################
# класс экрана удаления товара  #
#################################
class Delete_screen(Screen):
    items_to_delete = ListProperty()

    # выход из окна удаления
    def cancel_delete(self):
        self.items_to_delete = []
        self.manager.current = 'home'  # перейти к главному окну 'home'
        # print('Отмена удаления')  # --------------------------------

    # удалить отмеченные товары
    def complete_deletion(self):
        for item in self.items_to_delete:
            data_manage.delete_entry_by_id(db_file, item)
        self.ids.delete_view.update_scroll()
        # print('Товар удален')  # ----------------------


#########################################
# класс для экрана с заметками о товаре #
#########################################
class Note(Screen):
    note_id = NumericProperty()

    def delete_self(self):
        current_id = self.note_id
        # удалить сведения о введенном товавре
        data_manage.delete_entry_by_id(db_file, current_id)
        # print('Удалено, направлено к главному экрану')  # ----------------
        self.manager.current = 'home'  # перейти к главному окну


########################################
# класс для создания менеджера экранов #
########################################
class ScreenManagement(ScreenManager):
    transition = RiseInTransition()
    pass


# строковая переменная для загрузки кода на языке KV
presentation = Builder.load_file("NotePad.kv")

# цвет фона приложения
Window.clearcolor = (0, 199 / 255, 254 / 255, 1)


############################
# базовый класс приложения #
############################
class NotePadApp(App):
    # загрузчик кода приложения на языке KV
    def build(self):
        return presentation

    # получение сведений о товаре
    def get_note_info(self):
        note_screen = self.root.get_screen('notes')
        iden = note_screen.ids
        n_title = iden.note_title.text
        n_content = iden.note_content.text
        n_id = note_screen.note_id
        if (n_title or n_content) == '':
            n_title = 'none'
            n_content = 'none'
        date_of_submission = datetime.date.today()
        entry = [n_title, n_content, date_of_submission]
        # print('получение сведений о товаре')  # ---------------
        return entry

    # функция сохранить запись о товаре в БД
    def submit(self):
        entry = self.get_note_info()
        note_screen = self.root.get_screen('notes')
        old_id = note_screen.note_id  # запомнить ID текущего товара
        # print('Текущий ID', old_id)  # --------------------------

        if old_id != 0:
            # если в БД есть запись о товаре, то обновить ее
            # print('Сведения о товаре обновлены')
            new_date = datetime.date.today()
            new_entry = [entry[0], entry[1], new_date, old_id]
            data_manage.update_tasks_table(db_file, new_entry)
            note_screen.note_id = 0    # обнулить ID текущего товара
            self.root.current = 'home'  # перейти к главному окну
        elif (entry[1] or entry[0]) != 'none':
            # если в БД нет записи о товаре, то добавить ее
            with data_manage.connect_to_db(db_file) as conn:
                data_manage.insert_entry_to_notes(conn, entry)
                self.root.current = 'home'  # перейти к главному окну
                # print('Товар добавлен в БД')  # -----------------------
        else:
            # print('Нет сведений о товаре')  # ---------------------------
            # если пользователь не добавил товар, но нажал кнопку сохранить
            note_screen = self.root.get_screen('notes')
            iden = note_screen.ids
            iden.note_title.hint_text = 'Товар'
            iden.note_content.hint_text = 'Подрорбные сведения о товаре'


NotePadApp().run()
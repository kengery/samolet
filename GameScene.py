import random
import MenuLevel
import Pogoda
import Tyrbylentnost
import airplane
import Class
import pygame
import Figyrs
from Image import Image
import board
import math
import new_game_file
import queue
import Zona
import point
import time
import MyMicrophone
command_queue = queue.Queue()  # очередь для передачи голосовых команд
VISOTA_SBLIGENIA_AIRPLANE = 305  # метры: столкновение и интервал, если разница высот меньше этого
INTERVAL_PIKSEL = 100  # ближе этого между центрами в одном слое — нарушение
INTERVAL_SHTRAF = 200  # баллы, когда пара впервые вошла в интервал
INTERVAL_KADROV = 80  # 8 секунд прямой при паузе кадра 100 мс
CVET_INTERVAL = (255, 210, 0)  # линия нарушения интервала
CVET_SBLIZHENIE = (230, 160, 40)  # линия предупреждения о сближении
REAL_ZHIVYH = 5  # своих в воздухе на реальной карте
REAL_CHUZHIH = 2  # чужих одновременно на экране
REAL_PAUZA = 8  # секунды между появлениями
REAL_LUCH = 400  # пиксели входа, которые не должны пересечь запретную зону
REAL_OKNO = 160  # длина проёма вдоль рамки
REAL_VYSOTY = (610, 1220, 1830, 2440, 3040)  # слои высоты новых рейсов, метры
POLOSA_DLINA = 150  # длина прямоугольника полосы вдоль курса, пиксели
POLOSA_SHIRINA = 40  # ширина прямоугольника полосы, пиксели
POLOSA_VIS_MIN = 600  # нижняя высота посадки, метры
POLOSA_VIS_MAX = 900  # верхняя высота посадки, метры
POSADKA_DALI = 400  # пиксели до центра аэропорта: здесь высота сильно падает
POSADKA_SKOROST = 75  # пиксели до центра аэропорта: здесь скорость идёт к минимуму
VETER_PIKSEL = 0.2  # снос встречного ветра, пиксели за кадр
VTOROY_NAD = 300  # метры набора над коридором посадки на втором круге
OZHID_SDVIG = 220  # пиксели центра овала влево или вправо от аэропорта
OZHID_A = 120  # полуось овала по X, пиксели
OZHID_B = 60  # полуось овала по Y, пиксели

# Сцена симуляции: самолёты, зоны, кнопки, счёт и голос.
class GameScene(Class.Scene):
    # Создаёт кнопки, поле и поля раунда. Самолёты появятся при загрузке карты.
    def __init__(self, gameEngine, display):
        super().__init__(gameEngine)
        self.display = display  # окно pygame
        self.kn_w = gameEngine.screenx * 0.08  # ширина обычной кнопки
        self.kn_bolshaya = gameEngine.screenx * 0.105  # ширина «Изменить маршрут», «Высота» и «Маршрут»
        self.kn_h = gameEngine.screeny * 0.09  # высота всех кнопок
        self.button_izmenit = Image(gameEngine.screenx * 0.125, gameEngine.screeny * 0, gameEngine.screenx * 0.105, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # ввод маршрута точками
        self.button_reduce = Image(gameEngine.screenx * 0.23, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\reduse.png')  # медленнее
        self.button_increase = Image(gameEngine.screenx * 0.31, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\increase.png')  # быстрее
        self.button_levo = Image(gameEngine.screenx * 0.39, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\levo.png')  # поворот влево
        self.button_pravo = Image(gameEngine.screenx * 0.47, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\pravo.png')  # поворот вправо
        self.button_kurs = Image(gameEngine.screenx * 0.55, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # ввод курса
        self.button_skorost = Image(gameEngine.screenx * 0.63, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # ввод скорости
        self.button_visota = Image(gameEngine.screenx * 0.71, gameEngine.screeny * 0, gameEngine.screenx * 0.105, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # ввод высоты
        self.button_marshrut = Image(gameEngine.screenx * 0.815, gameEngine.screeny * 0, gameEngine.screenx * 0.105, gameEngine.screeny * 0.09, self.display, 'image\\button1.png')  # возврат на маршрут к своей цели
        self.button_exit = Image(gameEngine.screenx * 0.92, gameEngine.screeny * 0, gameEngine.screenx * 0.08, gameEngine.screeny * 0.09, self.display, 'image\\bsxod.PNG')  # выход в меню
        self.button_ozhidanie = Image(gameEngine.screenx * 0.815, gameEngine.screeny * 0.09, gameEngine.screenx * 0.105, gameEngine.screeny * 0.045, self.display, 'image\\button1.png')  # увод на овал, под «Маршрут»
        self.risuet_marshrut = False  # идёт ли расстановка точек
        self.chernovik = []  # точки до правого клика
        self.vvod = ""  # какая плашка открыта: visota, kurs, skorost или пусто
        self.vvod_text = ""  # набранные цифры
        self.pole_x = 260  # левый край поля, справа от табличек
        self.pole_y = 100  # верхний край поля
        self.pole_x2 = 1820  # правый край поля
        self.pole_y2 = 965  # нижний край поля
        self.fon_cvet = (6, 16, 28)  # цвет фона за полем
        self.pole_cvet = (10, 28, 46)  # заливка поля
        self.ramka_cvet = (0, 210, 220)  # цвет рамки поля
        self.polosa_kurs = 270  # курс носа при посадке, градусы
        self.gameEngine=gameEngine  # движок сцен
        self.display=display  # окно pygame
        self.click_airplane = None  # выбранный самолёт
        self.circle_x=0  # центр аэропорта X
        self.circle_y=0  # центр аэропорта Y
        self.circle_radiusx = 0  # половина ширины аэропорта
        self.circle_radiusy = 0  # половина высоты аэропорта
        self.end_game=False  # все самолёты уже имеют исход
        self.airplanes_stolk=0  # сколько столкнулись
        self.airplanes_finish=0  # сколько сели в аэропорт
        self.airplanes_granica=0  # сколько ушли через свой проём
        self.airplanes_poteryan=0  # сколько потеряны
        self.v_hody = []  # проёмы на рамке этой карты
        self.ball = 0  # сумма расхода и штрафов
        self.shtraf_interval = 0  # баллы за входы пар в интервал
        self.narusheniya_interval = 0  # сколько раз пара впервые сблизилась
        self.pary_interval = set()  # пары, которые сейчас в нарушении
        self.linii_interval = []  # отрезки нарушения этого кадра
        self.linii_sblizhenie = []  # отрезки предупреждения этого кадра
        self.rezhim = ""  # "" обычная карта, "real" — задания до лимита
        self.zadach = 0  # сколько заданий закрыть на реальной карте
        self.vypolneno = 0  # сели, ушли в проём или разбились
        self.ball_proshlyh = 0  # баллы уже снятых с экрана бортов
        self.stolk_vsego = 0  # разбитые за весь реальный раунд
        self.finish_vsego = 0  # севшие в аэропорт за весь реальный раунд
        self.granica_vsego = 0  # ушедшие в проём за весь реальный раунд
        self.poteryan_vsego = 0  # потерянные за весь реальный раунд
        self.real_konec = False  # задания уже закрыты, экран пуст
        self.sled_nash = 0  # когда можно выпустить следующего своего
        self.sled_chuzhoy = 0  # когда можно выпустить следующего чужого
        self.nomer_reisa = 1  # номер следующего своего имени
        self.nomer_borta = 1  # номер следующего чужого имени
        self.nomer_okna = 1  # номер следующего проёма
        #self.points=[point.point(200, 300), point.point(700, 200), point.point(700, 800), point.point(500, 400)]
        self.n_zona=[]  # запретные многоугольники карты
        self.my_microphone = MyMicrophone.MyMicrophone()  # запись голоса по пробелу

    # Клики, клавиши, голос и кнопки курса, скорости, высоты и маршрута.
    def handle_events(self, events):
        self.__process_voice_commands()
        for event in events:
            if self.vvod != "" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__zakryt_vvod()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.__apply_vvod()
                elif event.key == pygame.K_BACKSPACE:
                    self.vvod_text = self.vvod_text[:-1]
                elif event.unicode.isdigit() and len(self.vvod_text) < self.__vvod_predel():
                    self.vvod_text += event.unicode
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if getattr(event, "repeat", 0) == 0:
                    self.my_microphone.space_pressed()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.my_microphone.space_released()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.risuet_marshrut = False
                self.chernovik = []

            mouse_x, mouse_y = pygame.mouse.get_pos()  # координаты курсора

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.__zakonchit_marshrut()
                    continue
                if event.button != 1:
                    continue
                if self.button_exit.click(mouse_x, mouse_y):
                    self.gameEngine.change_scene("menu")
                    continue
                na_knopke = False  # клик пришёлся на кнопку, точку не ставим
                if self.click_airplane is not None:
                    if self.button_pravo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(-15)
                        na_knopke = True
                    if self.button_levo.click(mouse_x, mouse_y):
                        self.click_airplane.add_angle(15)
                        na_knopke = True
                    if self.button_increase.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(1)
                        na_knopke = True
                    if self.button_reduce.click(mouse_x, mouse_y):
                        self.click_airplane.add_speed(-1)
                        na_knopke = True
                    if self.button_kurs.click(mouse_x, mouse_y):
                        self.__otkryt_vvod("kurs")
                        na_knopke = True
                    if self.button_skorost.click(mouse_x, mouse_y):
                        self.__otkryt_vvod("skorost")
                        na_knopke = True
                    if self.button_visota.click(mouse_x, mouse_y):
                        self.__otkryt_vvod("visota")
                        na_knopke = True
                    if self.button_ozhidanie.click(mouse_x, mouse_y):
                        ox, oy = self.__centr_ozhidaniya()  # центр овала сбоку от аэропорта
                        self.click_airplane.nachat_ozhidanie(ox, oy, OZHID_A, OZHID_B)
                        na_knopke = True
                    if self.button_marshrut.click(mouse_x, mouse_y):
                        self.click_airplane.na_marshrut()
                        na_knopke = True
                    if self.button_izmenit.click(mouse_x, mouse_y):
                        self.risuet_marshrut = True
                        self.chernovik = []
                        na_knopke = True
                vybral = False  # клик выбрал самолёт
                if getattr(self, "airplanes", None):
                    vybral = self.__select_airplane(mouse_x, mouse_y)
                if na_knopke == False and vybral == False and self.risuet_marshrut == True and self.click_airplane is not None:
                    if self.pole_x <= mouse_x <= self.pole_x2 and self.pole_y <= mouse_y <= self.pole_y2:
                        self.__dobavit_tochku(mouse_x, mouse_y)


    # Движение, столкновения, посадка, проём на рамке, поле, запретные зоны и конец раунда.
    def update(self):

        self.__update_tyrbylentnost()
        self.__update_move_airplanes()

        game_end = 0  # сколько своих самолётов уже с исходом
        svoih = 0  # сколько своих самолётов на карте
        self.airplanes_stolk = 0
        self.airplanes_finish = 0
        self.airplanes_granica = 0
        self.airplanes_poteryan = 0
        kto_na_cherte = self.__kto_na_cherte()  # кто держит полосу в этом кадре
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].nash == False:
                if self.airplanes[i].ushel == False:
                    if self.rezhim == "real":
                        if self.__za_oknom(self.airplanes[i]):
                            self.airplanes[i].ushel = True
                    elif self.airplanes[i].x < self.pole_x or self.airplanes[i].x + self.airplanes[i].dx > self.pole_x2 or \
                            self.airplanes[i].y < self.pole_y or self.airplanes[i].y + self.airplanes[i].dy > self.pole_y2:
                        self.airplanes[i].ushel = True
                continue
            if self.rezhim == "real" and self.airplanes[i].voshel == False:
                if self.__polnostyu_v_pole(self.airplanes[i]):
                    self.airplanes[i].voshel = True
                    if self.airplanes[i].okno_zhdet == True:
                        self.__otkryt_svoy_vyhod(self.airplanes[i])
                        self.airplanes[i].okno_zhdet = False
                elif self.__za_oknom(self.airplanes[i]):
                    self.airplanes[i].poteryan = True
            svoih = svoih + 1
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(i + 1, len(self.airplanes)):
                    if self.airplanes[j].nash == False:
                        continue
                    if self.airplanes[j].stolk == False and self.airplanes[j].finish == False:
                        x_2 = self.airplanes[i].x + self.airplanes[i].dx / 2  # центр первого по X
                        x_1 = self.airplanes[j].x + self.airplanes[j].dx / 2  # центр второго по X
                        y_2 = self.airplanes[i].y + self.airplanes[i].dy / 2  # центр первого по Y
                        y_1 = self.airplanes[j].y + self.airplanes[j].dy / 2  # центр второго по Y

                        # находим растояние между центром самолётов
                        d = math.sqrt((x_2 - x_1) * (x_2 - x_1) + (y_2 - y_1) * (y_2 - y_1))  # расстояние между центрами
                        stolk_airplane = self.airplanes[i].dx / 2 + self.airplanes[j].dx / 2 >= d or self.airplanes[i].dy / 2 + \
                                self.airplanes[j].dy / 2 >= d  # близко на карте
                        min_na_stolk_visota = math.fabs(self.airplanes[i].visota_airplane - self.airplanes[j].visota_airplane) < VISOTA_SBLIGENIA_AIRPLANE  # разница высот меньше 305 м
                        if stolk_airplane and min_na_stolk_visota:
                            self.airplanes[i].stolk = True
                            self.airplanes[j].stolk = True

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False and self.airplanes[i].na_v_hod == False:
                x1 = self.airplanes[i].x + self.airplanes[i].dx / 2  # центр самолёта X
                y1 = self.airplanes[i].y + self.airplanes[i].dy / 2  # центр самолёта Y
                if self.airplanes[i].vtoroy == False and self.airplanes[i].ozhidanie == False:
                    if math.hypot(x1 - self.circle_x, y1 - self.circle_y) <= POSADKA_DALI:
                        self.airplanes[i].silno_snizit(POLOSA_VIS_MAX)
                    if math.hypot(x1 - self.circle_x, y1 - self.circle_y) <= POSADKA_SKOROST:
                        self.airplanes[i].k_minimum_skorosti()
                if self.airplanes[i].nad_polosoy(x1, y1) == True and self.airplanes[i].vtoroy == False and self.airplanes[i].ozhidanie == False:
                    if kto_na_cherte is not None and self.airplanes[i] is not kto_na_cherte:
                        self.airplanes[i].nachat_vtoroy((self.polosa_kurs + 90) % 360, POLOSA_VIS_MAX + VTOROY_NAD)
                    elif self.airplanes[i].skorost_minimalnaya() == True and self.__polosa_prinimaet(self.airplanes[i]) == True:
                        self.airplanes[i].finish = True
                        self.airplanes[i].kruzhit = False
                    else:
                        self.airplanes[i].nachat_krug(POLOSA_VIS_MIN, POLOSA_VIS_MAX)

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                ishod = self.__ishod_ramki(self.airplanes[i])  # успех в проёме, ещё летит или потеря
                if ishod == "uspeh":
                    self.airplanes[i].finish = True
                    self.airplanes[i].cherez_granicu = True
                elif ishod == "poteryan":
                    self.airplanes[i].poteryan = True
            """
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(0, len(self.Pogoda)):
                    if self.Pogoda[j].select(self.airplanes[i].x, self.airplanes[i].y, self.airplanes[i].dx,self.airplanes[i].dy) == True:
                        self.airplanes[i].stolk=True
            """

            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                for j in range(0, len(self.n_zona)):
                    if self.n_zona[j].select(self.airplanes[i].x+self.airplanes[i].dx/2,self.airplanes[i].y+self.airplanes[i].dy/2)==True:
                        self.airplanes[i].poteryan = True

            if self.airplanes[i].stolk == True:
                self.airplanes_stolk = self.airplanes_stolk + 1
            if self.airplanes[i].finish == True and self.airplanes[i].cherez_granicu == False:
                self.airplanes_finish = self.airplanes_finish + 1
            if self.airplanes[i].cherez_granicu == True:
                self.airplanes_granica = self.airplanes_granica + 1
            if self.airplanes[i].poteryan == True:
                self.airplanes_poteryan = self.airplanes_poteryan + 1

            if self.airplanes[i].stolk == True or self.airplanes[i].finish == True or self.airplanes[
                i].poteryan == True:
                game_end = game_end + 1

        self.__interval()
        self.__calc_balls()

        if self.rezhim == "real":
            self.__real_kadr()
        elif svoih > 0 and game_end == svoih:
            self.end_game = True

    # Курс полосы: нос к ближайшему краю, черта захода от него внутрь поля.
    def __kurs_polosy(self):
        kraya = [  # расстояние центра аэропорта до стороны и курс носа к ней
            (self.circle_y - self.pole_y, 90),
            (self.pole_y2 - self.circle_y, 270),
            (self.circle_x - self.pole_x, 180),
            (self.pole_x2 - self.circle_x, 0),
        ]
        blizhe = kraya[0]  # ближайший край
        for kray in kraya:
            if kray[0] < blizhe[0]:
                blizhe = kray
        return blizhe[1]

    # Аэропорт принимает борт с любой стороны: высота 600–900 м.
    def __polosa_prinimaet(self, plane):
        if plane.visota_airplane < POLOSA_VIS_MIN or plane.visota_airplane > POLOSA_VIS_MAX:
            return False
        return True

    # Свой ещё летит и не ушёл на второй круг или ожидание. тоесть можем ли использовать самолёт
    def __mozhet_na_chert(self, plane):
        if plane.nash == False or plane.na_v_hod == True:
            return False
        if plane.stolk == True or plane.finish == True or plane.poteryan == True:
            return False
        if plane.vtoroy == True or plane.ozhidanie == True:
            return False
        return True

    # Кто держит черт: сначала тот, кто уже кружит, иначе первый в списке над полосой.
    def __kto_na_cherte(self):
        if getattr(self, "airplanes", None) is None:
            return None
        for plane in self.airplanes:
            if self.__mozhet_na_chert(plane) == True and plane.kruzhit == True:
                return plane
        for plane in self.airplanes:
            if self.__mozhet_na_chert(plane) == False:
                continue
            x = plane.x + plane.dx / 2  # центр по X
            y = plane.y + plane.dy / 2  # центр по Y
            if plane.nad_polosoy(x, y) == True:
                return plane
        return None

    # Центр овала: 220 пикселей левее аэропорта, если точка ещё в поле, иначе правее.
    def __centr_ozhidaniya(self):
        x = self.circle_x - OZHID_SDVIG  # левее аэропорта
        if self.pole_x < x < self.pole_x2 and self.pole_y < self.circle_y < self.pole_y2:
            return x, self.circle_y
        return self.circle_x + OZHID_SDVIG, self.circle_y

    # Четыре угла прямоугольника полосы: длинная сторона по курсу носа.
    def __ugoly_polosy(self):
        rad = math.radians(self.polosa_kurs)  # курс полосы в радианах
        fx = math.cos(rad)  # вперёд по носу, X
        fy = -math.sin(rad)  # вперёд по носу, Y экрана
        px = math.sin(rad)  # поперёк полосы, X
        py = math.cos(rad)  # поперёк полосы, Y экрана
        dl = POLOSA_DLINA / 2  # половина длины
        sh = POLOSA_SHIRINA / 2  # половина ширины
        ugoly = []  # углы по часовой от носа
        for vdol, poperek in ((dl, sh), (dl, -sh), (-dl, -sh), (-dl, sh)):
            ugoly.append((self.circle_x + vdol * fx + poperek * px, self.circle_y + vdol * fy + poperek * py))
        return ugoly

    # Прямоугольник полосы вместо картинки аэропорта.
    def __render_polosa(self):
        ugoly = self.__ugoly_polosy()  # углы прямоугольника
        pygame.draw.polygon(self.display, (28, 64, 72), ugoly)  # заливка полосы
        pygame.draw.polygon(self.display, self.ramka_cvet, ugoly, 2)  # рамка цветом поля

    # Центр аэропорта и прямоугольник полосы для линии курса и посадки.
    def __privyazat_aeroport(self, plane):
        plane.set_aeroport(self.circle_x, self.circle_y, self.circle_radiusx, self.circle_radiusy)
        plane.set_polosa(self.polosa_kurs, POLOSA_DLINA, POLOSA_SHIRINA)

    # Встречный ветер полосы своему борту. Чужой его не получает.
    def __dat_veter(self, plane):
        if plane.nash == False:
            plane.veter_sila = 0
            return
        plane.veter_ugol = (self.polosa_kurs + 180) % 360
        plane.veter_sila = VETER_PIKSEL

    # True, если свой борт ещё летит: не сел, не разбился и не потерян.
    def __eshche_letit(self, plane):
        return plane.nash == True and plane.stolk == False and plane.finish == False and plane.poteryan == False

    # Центр спрайта на экране.
    def __centr(self, plane):
        return plane.x + plane.dx / 2, plane.y + plane.dy / 2

    # Сдвиг центра за кадр по текущим курсу и скорости. Снос и доворот не входят.
    def __skorost_ekrana(self, plane):
        shag = plane.piksel_kadra()  # пиксели за кадр
        rad = math.radians(plane.angle)  # курс в радианах
        return shag * math.cos(rad), -shag * math.sin(rad)

    # Ближайшее расстояние центров за INTERVAL_KADROV кадров прямой.
    def __blizhe_vperedi(self, a, b):
        ax, ay = self.__centr(a)  # центр первого
        bx, by = self.__centr(b)  # центр второго
        avx, avy = self.__skorost_ekrana(a)  # шаг первого за кадр
        bvx, bvy = self.__skorost_ekrana(b)  # шаг второго за кадр
        rx = bx - ax  # разница центров по X
        ry = by - ay  # разница центров по Y
        vx = bvx - avx  # относительный шаг по X
        vy = bvy - avy  # относительный шаг по Y
        vv = vx * vx + vy * vy  # квадрат относительной скорости
        if vv < 1e-8:
            return math.hypot(rx, ry)
        t = -(rx * vx + ry * vy) / vv  # кадр наибольшего сближения
        if t < 0:
            t = 0
        elif t > INTERVAL_KADROV:
            t = INTERVAL_KADROV
        return math.hypot(rx + vx * t, ry + vy * t)

    # Нарушение интервала и предупреждение за 8 секунд. Чужие не входят.
    def __interval(self):
        for plane in self.airplanes:
            plane.interval = False
            plane.sblizhenie = False
        zhivye = []  # свои, которые ещё летят
        for plane in self.airplanes:
            if self.__eshche_letit(plane):
                zhivye.append(plane)
        seychas = set()  # пары в нарушении в этом кадре
        self.linii_interval = []
        self.linii_sblizhenie = []
        for i in range(0, len(zhivye)):
            for j in range(i + 1, len(zhivye)):
                a = zhivye[i]  # первый борт пары
                b = zhivye[j]  # второй борт пары
                if math.fabs(a.visota_airplane - b.visota_airplane) >= VISOTA_SBLIGENIA_AIRPLANE:
                    continue
                ax, ay = self.__centr(a)
                bx, by = self.__centr(b)
                d = math.hypot(bx - ax, by - ay)  # расстояние между центрами
                key = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))  # пара без порядка
                if d < INTERVAL_PIKSEL:
                    seychas.add(key)
                    a.interval = True
                    b.interval = True
                    self.linii_interval.append((ax, ay, bx, by))
                    if key not in self.pary_interval:
                        self.shtraf_interval = self.shtraf_interval + INTERVAL_SHTRAF
                        self.narusheniya_interval = self.narusheniya_interval + 1
                elif self.__blizhe_vperedi(a, b) < INTERVAL_PIKSEL:
                    a.sblizhenie = True
                    b.sblizhenie = True
                    self.linii_sblizhenie.append((ax, ay, bx, by))
        for plane in zhivye:
            if plane.interval == True:
                plane.sblizhenie = False
        self.pary_interval = seychas

    # Линии между парами: жёлтая при нарушении, янтарная при предупреждении.
    def __render_interval_linii(self):
        for ax, ay, bx, by in self.linii_sblizhenie:
            pygame.draw.line(self.display, CVET_SBLIZHENIE, (ax, ay), (bx, by), 2)
        for ax, ay, bx, by in self.linii_interval:
            pygame.draw.line(self.display, CVET_INTERVAL, (ax, ay), (bx, by), 2)

    # Рисует тёмный фон окна и прямоугольник поля с рамкой.
    def __render_pole(self):
        self.display.fill(self.fon_cvet)
        pole = (self.pole_x, self.pole_y, self.pole_x2 - self.pole_x, self.pole_y2 - self.pole_y)  # прямоугольник поля
        pygame.draw.rect(self.display, self.pole_cvet, pole)  # заливка поля
        pygame.draw.rect(self.display, self.ramka_cvet, pole, 2)  # рамка поля толщиной 2
        self.__render_proemy()

    # Рисует разрыв рамки на каждом проёме и засечки по концам.
    def __render_proemy(self):
        for v_hod in self.v_hody:
            self.__render_proem(v_hod)

    # Закрашивает отрезок рамки целиком цветом поля и ставит короткие засечки.
    def __render_proem(self, v_hod):
        a = v_hod.a  # начало проёма вдоль рамки
        b = v_hod.b  # конец проёма вдоль рамки
        tol = 8  # толщина закраски, больше линии рамки в 2 пикселя
        if v_hod.storona == "verh" or v_hod.storona == "niz":
            y = self.pole_y if v_hod.storona == "verh" else self.pole_y2  # сторона рамки
            pygame.draw.rect(self.display, self.pole_cvet, (a, y - tol / 2, b - a, tol))  # разрыв на всю толщину рамки
            pygame.draw.line(self.display, self.ramka_cvet, (a, y - 8), (a, y + 8), 2)  # засечка в начале
            pygame.draw.line(self.display, self.ramka_cvet, (b, y - 8), (b, y + 8), 2)  # засечка в конце
        else:
            x = self.pole_x if v_hod.storona == "levo" else self.pole_x2  # сторона рамки
            pygame.draw.rect(self.display, self.pole_cvet, (x - tol / 2, a, tol, b - a))  # разрыв на всю толщину рамки
            pygame.draw.line(self.display, self.ramka_cvet, (x - 8, a), (x + 8, a), 2)  # засечка в начале
            pygame.draw.line(self.display, self.ramka_cvet, (x - 8, b), (x + 8, b), 2)  # засечка в конце

    # True, если край спрайта вышел за прямоугольник поля.
    def __za_polem(self, plane):
        return plane.x < self.pole_x or plane.x + plane.dx > self.pole_x2 or plane.y < self.pole_y or plane.y + plane.dy > self.pole_y2

    # True, если центр самолёта уже за этой стороной рамки.
    def __centr_za(self, plane, storona):
        cx = plane.x + plane.dx / 2  # центр по X
        cy = plane.y + plane.dy / 2  # центр по Y
        if storona == "verh":
            return cy <= self.pole_y
        if storona == "niz":
            return cy >= self.pole_y2
        if storona == "levo":
            return cx <= self.pole_x
        if storona == "pravo":
            return cx >= self.pole_x2
        return False

    # True, если координата центра вдоль рамки лежит в отрезке своего проёма.
    def __vdol_proema(self, plane):
        cx = plane.x + plane.dx / 2  # центр по X
        cy = plane.y + plane.dy / 2  # центр по Y
        if plane.granica_storona == "verh" or plane.granica_storona == "niz":
            return plane.granica_a <= cx <= plane.granica_b
        return plane.granica_a <= cy <= plane.granica_b

    # None, пока спрайт в поле. Иначе uspeh, letit или poteryan.
    def __ishod_ramki(self, plane):
        if self.rezhim == "real" and plane.voshel == False:
            return None
        if self.__za_polem(plane) == False:
            return None
        if plane.na_v_hod == False:
            return "poteryan"
        vdol = self.__vdol_proema(plane)  # центр вдоль рамки в своём отрезке
        svoya = self.__centr_za(plane, plane.granica_storona)  # центр пересёк сторону проёма
        drugaya = False  # центр пересёк другую сторону
        for storona in ("verh", "niz", "levo", "pravo"):
            if storona != plane.granica_storona and self.__centr_za(plane, storona) == True:
                drugaya = True
        if svoya == True and vdol == True and drugaya == False:
            return "uspeh"
        v_proem = False  # край спрайта вышел в сторону своего проёма
        if plane.granica_storona == "levo" and plane.x < self.pole_x:
            v_proem = True
        elif plane.granica_storona == "pravo" and plane.x + plane.dx > self.pole_x2:
            v_proem = True
        elif plane.granica_storona == "verh" and plane.y < self.pole_y:
            v_proem = True
        elif plane.granica_storona == "niz" and plane.y + plane.dy > self.pole_y2:
            v_proem = True
        if vdol == True and drugaya == False and svoya == False and v_proem == True:
            return "letit"
        return "poteryan"

    # Рисует поле, зоны, кнопки, аэропорт, самолёты и итог раунда.
    def render(self):
        self.__render_pole()
        self.__render_tyrbylentnost()
        self.__render_polosa()
        self.__render_airplanes()
        self.display.set_clip(None)

        self.__render_button_airplanes()

        self.button_exit.render()
        self.button_pravo.render()
        self.button_levo.render()
        self.button_increase.render()
        self.button_reduce.render()
        self.button_kurs.render()
        self.button_skorost.render()
        self.button_visota.render()
        self.button_marshrut.render()
        self.button_ozhidanie.render()
        self.button_izmenit.render()
        self.__render_chernovik()
        podpis_y = self.kn_h / 2  # середина подписи на кнопке
        Figyrs.print_text(self.display, self.button_kurs.x + self.kn_w / 2, podpis_y, 22, (0, 0, 0), "Курс")
        Figyrs.print_text(self.display, self.button_skorost.x + self.kn_w / 2, podpis_y, 22, (0, 0, 0), "Скорость")
        Figyrs.print_text(self.display, self.button_visota.x + self.kn_bolshaya / 2, podpis_y, 22, (0, 0, 0), "Высота")
        Figyrs.print_text(self.display, self.button_marshrut.x + self.kn_bolshaya / 2, podpis_y, 22, (0, 0, 0), "Маршрут")
        Figyrs.print_text(self.display, self.button_izmenit.x + self.kn_bolshaya / 2, podpis_y, 22, (0, 0, 0), "Изменить маршрут")
        Figyrs.print_text(self.display, self.button_ozhidanie.x + self.kn_bolshaya / 2, self.button_ozhidanie.y + self.gameEngine.screeny * 0.0225, 18, (0, 0, 0), "Ожидание")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.45, self.gameEngine.screeny * 0.12, 20, (0, 0, 0), f"Столкновение, если разница высот < {VISOTA_SBLIGENIA_AIRPLANE} м")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.45, self.gameEngine.screeny * 0.15, 20, (0, 0, 0), f"Ветер, если разница высот < {Tyrbylentnost.VISOTA_SLOIA} м")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.45, self.gameEngine.screeny * 0.18, 20, (0, 0, 0), f"Интервал {INTERVAL_PIKSEL} пикселей, если разница высот < {VISOTA_SBLIGENIA_AIRPLANE} м")
        if self.rezhim == "real":
            Figyrs.print_text(self.display, 480, 130, 22, (220, 230, 235), f"Выполнено {self.vypolneno} из {self.zadach}")
        self.__render_vvod()

        if self.end_game == True:
            self.__render_end_game()

    # Рисует турбулентность и запретные зоны.
    def __render_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].render()
        for i in range(0, len(self.n_zona)):
            self.n_zona[i].render()
        #for i in range(0, len(self.Pogoda)):
        #    self.Pogoda[i].render()

    # Рисует летящие самолёты: свой ромбом, чужой тусклым квадратом.
    def __render_airplanes(self):
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].ushel == True:
                continue
            if self.airplanes[i].stolk == False and self.airplanes[i].finish == False and self.airplanes[
                i].poteryan == False:
                self.airplanes[i].render()
        self.__render_interval_linii()

    # Показывает итоговое окно: баллы, столкнулись, потеряны, сели и ушли через границу.
    def __render_end_game(self):
        if self.rezhim == "real":
            stolk = self.stolk_vsego  # разбитые за раунд
            poteryan = self.poteryan_vsego  # потерянные за раунд
            finish = self.finish_vsego  # севшие в аэропорт
            granica = self.granica_vsego  # ушедшие в проём
        else:
            stolk = self.airplanes_stolk
            poteryan = self.airplanes_poteryan
            finish = self.airplanes_finish
            granica = self.airplanes_granica
        Figyrs.kvadr_poly(self.gameEngine.screenx*0.25,self.gameEngine.screeny*0.25,self.gameEngine.screenx*0.5,self.gameEngine.screeny*0.48,200,self.display)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.505, self.gameEngine.screeny * 0.35,80, (0, 0, 0),f"Баллы = {int(self.ball)}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.4,self.gameEngine.screeny * 0.45,40,(0,0,0),f"Столкнулись = {stolk}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.5, 40, (0, 0, 0),f"Потерянны = {poteryan}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.62, self.gameEngine.screeny * 0.45,40, (0, 0, 0),f"Прилетели в аэропорт = {finish}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.56, 40, (0, 0, 0), f"Ушли через границу = {granica}")
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.62, 32, (0, 0, 0), f"Нарушения интервала = {self.narusheniya_interval}")
        if self.rezhim == "real":
            Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, self.gameEngine.screeny * 0.68, 32, (0, 0, 0), f"Выполнено = {self.vypolneno}")


    # Рисует таблички слева: обычная, красная или зелёная.
    def __render_button_airplanes(self):
        if self.button_airplane is None:
            return
        for i in range(0, len(self.button_airplane)):
            if self.airplanes[i].nash == False:
                continue
            if self.airplanes[i].stolk != True:
                self.button_airplane[i].render_poloska()
            else:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].poteryan == True:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].benzin <= 0:
                self.button_stolk[i].render_poloska()
            if self.airplanes[i].finish == True:
                self.button_finish[i].render_poloska()

    # Сдвигает зоны ветра по их курсу и по высоте слоя.
    def __update_tyrbylentnost(self):
        for i in range(0, len(self.Tyrbylentnost)):
            self.Tyrbylentnost[i].move()

    # Двигает самолёты: доклад зоны при входе, снос и множитель топлива.
    def __update_move_airplanes(self):
        for i in range(0,len(self.airplanes)):
            if self.airplanes[i].nash == False:
                self.airplanes[i].move()
                continue
            zona = None  # зона, в которой самолёт в этом кадре
            for j in range(0, len(self.Tyrbylentnost)):
                popal = self.Tyrbylentnost[j].select(self.airplanes[i].x,self.airplanes[i].y,self.airplanes[i].dx,self.airplanes[i].dy,self.airplanes[i].visota_airplane)  # самолёт в турбулентной зоне
                if popal == True:
                    if self.airplanes[i].turb_vnutri == False:
                        self.Tyrbylentnost[j].doklad()
                    zona = self.Tyrbylentnost[j]
                    break
            self.airplanes[i].turb_zahod(zona)
            self.airplanes[i].ymn_koef_ball(self.airplanes[i].turb_koef())
            self.airplanes[i].move()

    # Считает баллы: топливо, полный бак за разбитых и потерянных, штраф интервала.
    def __calc_balls(self):
        self.ball=self.ball_proshlyh + self.shtraf_interval
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].nash == False:
                continue
            if self.airplanes[i].stolk == False and self.airplanes[i].poteryan == False:
                self.ball = self.ball + self.airplanes[i].ball_benz
            else:
                self.ball = self.ball + self.airplanes[i].izn_benzin

    # Закрывает плашку ввода и стирает набранные цифры.
    def __zakryt_vvod(self):
        self.vvod = ""
        self.vvod_text = ""

    # Открывает одну плашку и закрывает остальные.
    def __otkryt_vvod(self, kakoy):
        self.vvod = kakoy
        self.vvod_text = ""

    # Сколько цифр можно набрать в открытой плашке.
    def __vvod_predel(self):
        if self.vvod == "kurs":
            return 3
        if self.vvod == "skorost":
            return 4
        return 7

    # Enter в открытой плашке: высота, курс или скорость.
    def __apply_vvod(self):
        if self.vvod == "visota":
            self.__apply_visota_input()
        elif self.vvod == "kurs":
            self.__apply_kurs_input()
        elif self.vvod == "skorost":
            self.__apply_skorost_input()

    # Записывает набранную высоту выбранному самолёту.
    def __apply_visota_input(self):
        if self.vvod_text == "" or self.click_airplane is None:
            return
        self.click_airplane.set_zadana_visota(int(self.vvod_text))
        self.__zakryt_vvod()

    # Записывает курс 0–359. Если команда уже висит, плашка остаётся.
    def __apply_kurs_input(self):
        if self.vvod_text == "" or self.click_airplane is None:
            return
        grad = int(self.vvod_text)  # набранные градусы
        if grad > 359:
            return
        if self.click_airplane.zadat_kurs(grad) == True:
            self.__zakryt_vvod()

    # Записывает скорость в км/ч выбранному самолёту.
    def __apply_skorost_input(self):
        if self.vvod_text == "" or self.click_airplane is None:
            return
        self.click_airplane.zadat_skorost_kmch(int(self.vvod_text))
        self.__zakryt_vvod()

    # Рисует плашку ввода высоты, курса или скорости.
    def __render_vvod(self):
        if self.vvod == "":
            return
        if self.vvod == "kurs":
            zagolovok = "Курс, градусы"  # подпись плашки
        elif self.vvod == "skorost":
            zagolovok = "Скорость, км/ч"
        else:
            zagolovok = "Высота, метры"
        x = self.gameEngine.screenx * 0.35  # левый край плашки
        y = self.gameEngine.screeny * 0.35  # верхний край плашки
        Figyrs.kvadr_poly(x, y, self.gameEngine.screenx * 0.3, self.gameEngine.screeny * 0.18, 220, self.display)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.04, 32, (0, 0, 0), zagolovok)
        if self.vvod_text != "":
            shown = self.vvod_text  # набранные цифры
        else:
            shown = "_"  # подчёркивание, пока ничего не введено
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.09, 36, (0, 0, 0), shown)
        Figyrs.print_text(self.display, self.gameEngine.screenx * 0.5, y + self.gameEngine.screeny * 0.14, 22, (0, 0, 0), "Enter — записать, Escape — отмена")

    # Берёт голосовые команды и применяет поворот, курс или скорость к самолёту.
    def __process_voice_commands(self):
        if not getattr(self, "airplanes", None):
            while self.my_microphone.pop_command() is not None:
                pass
            return

        while True:
            cmd = self.my_microphone.pop_command()  # одна распознанная команда

            if cmd is None:
                break
            print(f"ищем {cmd["name"]} ")
            plane = None  # найденный самолёт по имени
            for p in self.airplanes:
                if p.nash == False:
                    continue
                if MyMicrophone.MyMicrophone.same_plane_name(p.name.lower(), cmd["name"]):
                    plane = p
                    break
            if plane is None:
                print(f"{cmd["name"]} не найден")
                continue
            if cmd["type"] == "turn":
                plane.add_angle(cmd["value"]/100)
            elif cmd["type"] == "speed":
                plane.add_speed(cmd["value"]/100)
            elif cmd["type"] == "kurs":
                plane.zadat_kurs(cmd["value"])
            elif cmd["type"] == "speed_abs":
                plane.zadat_skorost_kmch(cmd["value"])

    # Ставит выбранным этот борт. Чужой самолёт сбрасывает незаписанные точки.
    def __vzyat_samolet(self, plane):
        if self.click_airplane is not None and self.click_airplane is not plane:
            self.risuet_marshrut = False
            self.chernovik = []
            self.__zakryt_vvod()
        if self.click_airplane is not None:
            self.click_airplane.click_camolet = False
        self.click_airplane = plane
        self.click_airplane.click_camolet = True

    # Правый клик записывает точки. Без точек ввод просто закрывается.
    def __zakonchit_marshrut(self):
        if self.risuet_marshrut == False or self.click_airplane is None:
            return
        if len(self.chernovik) > 0:
            self.click_airplane.zadat_tochki(self.chernovik)
        self.risuet_marshrut = False
        self.chernovik = []

    # Добавляет точку черновика, если она не вплотную к предыдущей.
    def __dobavit_tochku(self, x, y):
        if len(self.chernovik) > 0:
            px, py = self.chernovik[-1]  # предыдущая точка
            if math.hypot(x - px, y - py) < 8:  # расстояние до предыдущей точки меньше 8 пикселей
                return
        self.chernovik.append((x, y))

    # Рисует ещё не записанный маршрут: прямые по точкам и линия до курсора.
    def __render_chernovik(self):
        if self.risuet_marshrut == False or self.click_airplane is None:
            return
        plane = self.click_airplane  # борт, которому рисуем маршрут
        cx = plane.x + plane.dx / 2  # центр борта по X
        cy = plane.y + plane.dy / 2  # центр борта по Y
        pts = [(cx, cy)]  # линия с борта
        for t in self.chernovik:
            pts.append(t)
        mx, my = pygame.mouse.get_pos()  # курсор, конец черновика
        pts.append((mx, my))
        if len(pts) > 1:
            pygame.draw.lines(self.display, (180, 255, 255), False, pts, 2)  # черновик прямыми
        for tx, ty in self.chernovik:
            pygame.draw.circle(self.display, (180, 255, 255), (tx, ty), 4)  # точка клика

    # Выбирает самолёт кликом по табличке или по спрайту. True, если клик попал в борт.
    def __select_airplane(self, mouse_x, mouse_y):
        # Выбор таблички самолета
        for i in range(0, len(self.button_airplane)):
            if self.button_airplane[i].airplane.nash == False:
                continue
            if self.button_airplane[i].click(mouse_x, mouse_y):
                self.__vzyat_samolet(self.button_airplane[i].airplane)
                return True

        # выбор самолета
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].click(mouse_x, mouse_y):
                self.__vzyat_samolet(self.airplanes[i])
                return True
        return False


    # True, если спрайт целиком вышел за окно.
    def __za_oknom(self, plane):
        return plane.x + plane.dx < 0 or plane.x > self.gameEngine.screenx or plane.y + plane.dy < 0 or plane.y > self.gameEngine.screeny

    # True, если спрайт целиком внутри прямоугольника поля.
    def __polnostyu_v_pole(self, plane):
        return plane.x >= self.pole_x and plane.x + plane.dx <= self.pole_x2 and plane.y >= self.pole_y and plane.y + plane.dy <= self.pole_y2

    # Сторона рамки, к которой центр ближе всего. Ей открывается окно входа.
    def __storona_u_ramki(self, plane):
        cx = plane.x + plane.dx / 2  # центр по X
        cy = plane.y + plane.dy / 2  # центр по Y
        rasst = {  # расстояние центра до каждой стороны
            "levo": cx - self.pole_x,
            "pravo": self.pole_x2 - cx,
            "verh": cy - self.pole_y,
            "niz": self.pole_y2 - cy,
        }
        blizhe = "levo"  # сторона с наименьшим зазором
        for storona in rasst:
            if rasst[storona] < rasst[blizhe]:
                blizhe = storona
        return blizhe

    # True, если отрезок пересекает уже открытый проём на той же стороне.
    def __okno_zanayto(self, storona, a, b):
        for okno in self.v_hody:
            if okno.storona != storona:
                continue
            if a < okno.b and b > okno.a:
                return True
        return False

    # Случайный проём на стороне. Старается не лечь на уже открытый.
    def __sluchainoe_okno(self, storona):
        if storona == "verh" or storona == "niz":
            lo = self.pole_x + 24  # левый допустимый край отрезка
            hi = self.pole_x2 - 24 - REAL_OKNO  # правый допустимый край начала
        else:
            lo = self.pole_y + 24
            hi = self.pole_y2 - 24 - REAL_OKNO
        if hi < lo:
            hi = lo
        a = lo  # начало отрезка
        b = lo + REAL_OKNO  # конец отрезка
        for _ in range(25):
            a = random.uniform(lo, hi)
            b = a + REAL_OKNO
            if self.__okno_zanayto(storona, a, b) == False:
                break
        okno = new_game_file.v_hod(f"okno{self.nomer_okna}", storona, a, b)  # новый проём
        self.nomer_okna = self.nomer_okna + 1
        return okno

    # Добавляет проём на сторону и оставляет его на рамке.
    def __otkryt_okno(self, storona):
        if storona not in ("verh", "niz", "levo", "pravo"):
            return
        self.v_hody.append(self.__sluchainoe_okno(storona))

    # Двум стартовым рейсам выдаёт случайные проёмы, не аэропорт.
    def __real_nachalo(self):
        self.nomer_reisa = 1
        for plane in self.airplanes:
            if plane.nash == False:
                continue
            self.nomer_reisa = self.nomer_reisa + 1
            plane.voshel = True
            plane.okno_zhdet = False
            storona = random.choice(("verh", "niz", "levo", "pravo"))  # сторона проёма этого рейса
            okno = self.__sluchainoe_okno(storona)  # проём, уже открытый на старте
            self.v_hody.append(okno)
            plane.svoy_vyhod = okno
            plane.set_v_hod(okno.storona, okno.a, okno.b, self.pole_x, self.pole_y, self.pole_x2, self.pole_y2)
        self.sled_nash = time.time() + REAL_PAUZA
        self.sled_chuzhoy = time.time() + REAL_PAUZA
        self.real_konec = False

    # Снимает борт с поля и с табличек. Если это был выбранный — выбор гаснет.
    def __vykinut(self, i):
        if self.click_airplane is self.airplanes[i]:
            self.click_airplane = None
            self.risuet_marshrut = False
            self.chernovik = []
            self.__zakryt_vvod()
        self.airplanes.pop(i)
        self.button_airplane.pop(i)
        self.button_finish.pop(i)
        self.button_stolk.pop(i)

    # Убирает с рамки проём этого борта: линия рамки снова сплошная.
    def __zakryt_vyhod(self, plane):
        okno = plane.svoy_vyhod  # проём, который рисовался только ему
        if okno is None:
            return
        if okno in self.v_hody:
            self.v_hody.remove(okno)
        plane.svoy_vyhod = None

    # Пишет исход в счёт заданий и в баллы снятых бортов.
    def __zapisat_ishod(self, plane):
        if plane.finish == True:
            self.__zakryt_vyhod(plane)
        if plane.stolk == True:
            self.stolk_vsego = self.stolk_vsego + 1
            self.vypolneno = self.vypolneno + 1
            self.ball_proshlyh = self.ball_proshlyh + plane.izn_benzin
            return
        if plane.finish == True and plane.cherez_granicu == True:
            self.granica_vsego = self.granica_vsego + 1
            self.vypolneno = self.vypolneno + 1
            self.ball_proshlyh = self.ball_proshlyh + plane.ball_benz
            return
        if plane.finish == True:
            self.finish_vsego = self.finish_vsego + 1
            self.vypolneno = self.vypolneno + 1
            self.ball_proshlyh = self.ball_proshlyh + plane.ball_benz
            return
        if plane.poteryan == True:
            self.poteryan_vsego = self.poteryan_vsego + 1
            self.ball_proshlyh = self.ball_proshlyh + plane.izn_benzin

    # Убирает своих с исходом и чужих, ушедших за окно. Таблички живых сдвигает вверх.
    def __snyat_s_ishodom(self):
        i = len(self.airplanes) - 1
        while i >= 0:
            plane = self.airplanes[i]  # борт, который, может быть, уже закончил
            if plane.nash == False:
                if plane.ushel == True:
                    self.__vykinut(i)
                i = i - 1
                continue
            if plane.stolk == True or plane.finish == True or plane.poteryan == True:
                self.__zapisat_ishod(plane)
                self.__vykinut(i)
            i = i - 1
        self.__uplotnit_tablichki()

    # Ставит таблички живых своих подряд сверху, без пустых мест.
    def __uplotnit_tablichki(self):
        n = 0  # сколько живых своих уже разложено
        for i in range(0, len(self.airplanes)):
            if self.airplanes[i].nash == False:
                continue
            y = 12 + n * 110  # верх таблички
            for knopka in (self.button_airplane[i], self.button_finish[i], self.button_stolk[i]):
                knopka.y = y
                knopka.image.set_x_y(knopka.x, y)
            n = n + 1

    # Снимает всех, кто ещё на экране. У летящих своих в баллы идёт уже сожжённое топливо.
    def __ubrat_vseh(self):
        for plane in self.airplanes:
            if plane.nash == True and plane.stolk == False and plane.finish == False and plane.poteryan == False:
                self.ball_proshlyh = self.ball_proshlyh + plane.ball_benz
        self.airplanes = []
        self.button_airplane = []
        self.button_finish = []
        self.button_stolk = []
        self.click_airplane = None
        self.risuet_marshrut = False
        self.chernovik = []
        self.__zakryt_vvod()

    # Сколько своих ещё летит.
    def __zhivyh(self):
        n = 0
        for plane in self.airplanes:
            if plane.nash == True and plane.stolk == False and plane.finish == False and plane.poteryan == False:
                n = n + 1
        return n

    # Сколько чужих ещё на экране.
    def __chuzhih(self):
        n = 0
        for plane in self.airplanes:
            if plane.nash == False and plane.ushel == False:
                n = n + 1
        return n

    # Высота из свободного слоя: разница с летящими своими не меньше 305 м.
    def __svobodnaya_visota(self):
        zanyato = []  # высоты тех, кто ещё летит
        for plane in self.airplanes:
            if plane.nash == True and plane.stolk == False and plane.finish == False and plane.poteryan == False:
                zanyato.append(plane.visota_airplane)
        svobodnye = []  # слои, которые ещё не заняты
        for visota in REAL_VYSOTY:
            godna = True  # слой далеко от всех летящих
            for est in zanyato:
                if abs(visota - est) < VISOTA_SBLIGENIA_AIRPLANE:
                    godna = False
            if godna == True:
                svobodnye.append(visota)
        if len(svobodnye) == 0:
            return None
        return random.choice(svobodnye)

    # True, если прямая внутрь на REAL_LUCH пикселей задевает запретную зону или рядом уже есть борт.
    def __vhoda_meshaet(self, x, y, angle):
        cx = x + 16.15  # центр спрайта по X
        cy = y + 16.15  # центр спрайта по Y
        rad = math.radians(angle)  # курс входа
        shag = 16  # шаг проверки луча, пиксели
        n = int(REAL_LUCH / shag)
        for k in range(0, n + 1):
            px = cx + math.cos(rad) * shag * k  # точка луча по X
            py = cy - math.sin(rad) * shag * k  # точка луча по Y, ось экрана вниз
            for zona in self.n_zona:
                if zona.select(px, py) == True:
                    return True
        for plane in self.airplanes:
            if plane.ushel == True:
                continue
            px = plane.x + plane.dx / 2
            py = plane.y + plane.dy / 2
            if math.hypot(px - cx, py - cy) < 80:
                return True
        return False

    # Число от a до b. Если отрезок вырожден, возвращает a.
    def __mezhdu(self, a, b):
        if b <= a:
            return a
        return random.uniform(a, b)

    # Случайная точка за рамкой на этой стороне и курс внутрь поля.
    def __tochka_vhoda(self, storona):
        dx = 32.3  # ширина спрайта
        dy = 32.3  # высота спрайта
        if storona == "levo":
            x = self.__mezhdu(246, self.pole_x - dx - 8)
            y = self.__mezhdu(self.pole_y + 8, self.pole_y2 - dy - 8)
            return x, y, 0
        if storona == "pravo":
            x = self.__mezhdu(self.pole_x2 + 8, self.gameEngine.screenx - dx - 4)
            y = self.__mezhdu(self.pole_y + 8, self.pole_y2 - dy - 8)
            return x, y, 180
        if storona == "verh":
            x = self.__mezhdu(1180, self.pole_x2 - dx - 8)
            y = self.__mezhdu(104, self.pole_y - dy - 6)
            return x, y, 270
        x = self.__mezhdu(self.pole_x + 8, self.pole_x2 - dx - 8)
        y = self.__mezhdu(self.pole_y2 + 8, self.gameEngine.screeny - dy - 4)
        return x, y, 90

    # Ищет сторону и точку, откуда борт входит мимо запретных зон. None, если места нет.
    def __mesto_vhoda(self):
        storony = ["verh", "niz", "levo", "pravo"]  # все четыре стороны рамки
        random.shuffle(storony)
        for storona in storony:
            for _ in range(12):
                x, y, angle = self.__tochka_vhoda(storona)  # кандидат за рамкой
                if self.__vhoda_meshaet(x, y, angle) == True:
                    continue
                return storona, x, y, angle
        return None

    # Цель нового своего: аэропорт или свой новый проём, не общий с другим бортом.
    def __naznachit_cel(self, plane):
        storony = []  # стороны, кроме той, откуда он заходит
        for storona in ("verh", "niz", "levo", "pravo"):
            if storona != plane.storona_vhoda:
                storony.append(storona)
        if len(storony) == 0:
            storony = ["verh", "niz", "levo", "pravo"]
        okno = self.__sluchainoe_okno(random.choice(storony))  # проём только этого борта
        self.v_hody.append(okno)
        plane.svoy_vyhod = okno
        if random.random() < 0.5:
            plane.na_v_hod = False
            plane.v_hod = None
            plane.cel_x = self.circle_x
            plane.cel_y = self.circle_y
            return
        plane.set_v_hod(okno.storona, okno.a, okno.b, self.pole_x, self.pole_y, self.pole_x2, self.pole_y2)

    # Открывает этому борту свой проём, если его ещё нет.
    def __otkryt_svoy_vyhod(self, plane):
        if plane.svoy_vyhod is not None:
            return
        storona = plane.storona_vhoda  # сторона, с которой его выпустили
        if storona is None:
            storona = self.__storona_u_ramki(plane)
        if storona not in ("verh", "niz", "levo", "pravo"):
            return
        okno = self.__sluchainoe_okno(storona)  # проём только этого борта
        self.v_hody.append(okno)
        plane.svoy_vyhod = okno

    # Вешает три таблички на новый борт, в конец списков.
    def __dobavit_tablichku(self, plane):
        y = 12  # верх, потом таблички уплотняются
        a = board.board(12, y, 220, 96, self.display, 'image\\button1.png', plane, (0, 210, 220))
        s = board.board(12, y, 220, 96, self.display, 'image\\button_green.png', plane, (0, 255, 0))
        d = board.board(12, y, 220, 96, self.display, 'image\\button_red.png', plane, (255, 0, 0))
        self.button_airplane.append(a)
        self.button_finish.append(s)
        self.button_stolk.append(d)

    # Ставит борт за рамкой. Свой получает цель, чужой летит прямо.
    def __postavit_bort(self, nash, imya, visota):
        mesto = self.__mesto_vhoda()  # сторона, точка и курс
        if mesto is None:
            return False
        storona, x, y, angle = mesto
        speed = random.uniform(1.75, 2.25)  # скорость около оптимальной
        plane = airplane.airplane(x, y, 32.3, 32.3, self.display, 'image\\camolet2.png', imya, speed, 0.5, 4, angle, 1500, visota, 305, 3048, nash, None)
        self.__privyazat_aeroport(plane)
        plane.voshel = False
        plane.storona_vhoda = storona
        plane.okno_zhdet = False
        plane.svoy_vyhod = None
        if nash == True:
            self.__naznachit_cel(plane)
        self.__dat_veter(plane)
        self.airplanes.append(plane)
        self.__dobavit_tablichku(plane)
        self.__uplotnit_tablichki()
        return True

    # Выпускает своего, если живых меньше пяти, и чужого, если их меньше двух.
    def __rozhdenie(self):
        seychas = time.time()  # секунды
        if seychas >= self.sled_nash and self.__zhivyh() < REAL_ZHIVYH and self.vypolneno < self.zadach:
            visota = self.__svobodnaya_visota()  # свободный слой
            if visota is not None and self.__postavit_bort(True, f"Рейс{self.nomer_reisa}", visota) == True:
                self.nomer_reisa = self.nomer_reisa + 1
                self.sled_nash = seychas + REAL_PAUZA
        if seychas >= self.sled_chuzhoy and self.__chuzhih() < REAL_CHUZHIH:
            visota = random.choice(REAL_VYSOTY)  # высота чужого, на столкновения не влияет
            if self.__postavit_bort(False, f"Борт{self.nomer_borta}", visota) == True:
                self.nomer_borta = self.nomer_borta + 1
                self.sled_chuzhoy = seychas + REAL_PAUZA

    # Снимает закончивших, на 20 заданиях очищает экран, иначе выпускает следующих.
    def __real_kadr(self):
        if self.real_konec == True:
            return
        self.__snyat_s_ishodom()
        if self.vypolneno >= self.zadach:
            self.__ubrat_vseh()
            self.real_konec = True
            self.end_game = True
            self.__calc_balls()
            return
        self.__rozhdenie()
        self.__calc_balls()

    # Начинает раунд: грузит карту из JSON.
    def init_new_game(self, level):
        self.__zakryt_vvod()
        self.risuet_marshrut = False
        self.chernovik = []
        self.__new_game_from_file(level)

        #self.__init_airplanes()
        #self.__init_tyrbylentnost()

    # Читает JSON карты и создаёт самолёты, таблички, зоны и аэропорт.
    def __new_game_from_file(self, file :str):

        with open(file, 'r', encoding='utf-8') as filef:
            file_text = filef.read()  # текст файла уровня

        n=new_game_file.new_game_file([],[],[],0,0,0,0)  # пустая карта, чтобы вызвать from_json
        nn=n.from_json( self.display,file_text)  # загруженная карта
        self.pole_x = 260
        self.pole_y = 100
        self.pole_x2 = 1820
        self.pole_y2 = 965
        if nn.pole is not None:
            self.pole_x = nn.pole["x"]
            self.pole_y = nn.pole["y"]
            self.pole_x2 = nn.pole["x2"]
            self.pole_y2 = nn.pole["y2"]
        self.rezhim = nn.rezhim
        self.zadach = nn.zadach
        self.vypolneno = 0
        self.ball_proshlyh = 0
        self.shtraf_interval = 0
        self.narusheniya_interval = 0
        self.pary_interval = set()
        self.linii_interval = []
        self.linii_sblizhenie = []
        self.stolk_vsego = 0
        self.finish_vsego = 0
        self.granica_vsego = 0
        self.poteryan_vsego = 0
        self.real_konec = False
        self.end_game = False
        self.nomer_okna = 1
        self.nomer_borta = 1
        self.click_airplane = None
        self.circle_x = nn.finish_x
        self.circle_y = nn.finish_y
        self.circle_radiusx = nn.finish_rx
        self.circle_radiusy = nn.finish_ry
        self.polosa_kurs = self.__kurs_polosy()


        self.airplanes=[]  # самолёты этого раунда
        for i in nn.airplanes:
            s = airplane.airplane(i.x, i.y, i.dx,i.dy,  # копия самолёта с карты
                                  self.display, i.file, i.name,
                                  i.speed,
                                  i.speed_min, i.speed_max, i.angle,
                                  i.benzin, i.visota_airplane, i.visota_min, i.visota_max, i.nash, i.v_hod)
            self.__privyazat_aeroport(s)
            if s.v_hod is not None:
                for j in nn.v_hody:
                    if j.id == s.v_hod:
                        s.set_v_hod(j.storona, j.a, j.b, self.pole_x, self.pole_y, self.pole_x2, self.pole_y2)
            self.__dat_veter(s)
            self.airplanes.append(s)

        self.v_hody = nn.v_hody

        self.button_finish = []  # зелёные таблички (сел)
        self.button_airplane = []  # обычные таблички
        self.button_stolk = []  # красные таблички (разбит или потерян)

        for i in range(0, len(self.airplanes)):
            tab_y = 12 + i * 110  # верх таблички
            a = board.board(12, tab_y, 220, 96, self.display, 'image\\button1.png', self.airplanes[i], (0, 210, 220))  # летит, бирюзовая рамка
            s = board.board(12, tab_y, 220, 96, self.display, 'image\\button_green.png', self.airplanes[i], (0, 255, 0))  # сел или ушёл через проём
            d = board.board(12, tab_y, 220, 96, self.display, 'image\\button_red.png', self.airplanes[i], (255, 0, 0))  # потерян, красная рамка
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

        self.Tyrbylentnost = []  # турбулентные зоны карты
        for i in nn.tyrbylentnosts:
            s = Tyrbylentnost.Tyrbylentnost(self.display, i.x,i.y, i.dx,i.dy,i.file)
            self.Tyrbylentnost.append(s)
        if len(self.Tyrbylentnost) > 0:
            self.Tyrbylentnost[0].doklad()  # на старте карты известен один доклад

        self.n_zona = []  # запретные зоны карты
        for i in nn.zona:
            s = Zona.zona(self.display, i.points,i.color)
            self.n_zona.append(s)
        if self.rezhim == "real":
            self.__real_nachalo()

    # Случайные самолёты без JSON. На карты сейчас не влияет.
    def __init_airplanes(self):
        self.airplanes = []
        n = 0  # номер рейса
        for i in range(0, 2):
            n = n + 1
            self.scx = random.randint(200, 1600)  # случайный X
            self.scy = random.randint(200, 800)  # случайный Y
            self.speed_min = random.randint(2, 6)  # нижний предел скорости
            self.speed_min = self.speed_min / 10
            self.speed_max = random.randint(3, 5)  # верхний предел скорости
            self.angle = random.randint(0, 360)  # случайный курс
            s = airplane.airplane(self.scx, self.scy, self.gameEngine.screenx * 0.017,
                                  self.gameEngine.screeny * 0.03,
                                  self.display, 'image\\camolet2.png', f"Рейс{n}",
                                  (self.speed_min + self.speed_max) / 2,
                                  self.speed_min, self.speed_max, self.angle,
                                  1500, 914, 305, 3048)
            self.airplanes.append(s)


        self.button_finish = []  # зелёные таблички
        self.button_airplane = []  # обычные таблички
        self.button_stolk = []  # красные таблички

        for i in range(0, len(self.airplanes)):
            tab_y = 12 + i * 110  # верх таблички
            a = board.board(12, tab_y, 220, 96, self.display, 'image\\button1.png', self.airplanes[i], (0, 210, 220))  # летит, бирюзовая рамка
            s = board.board(12, tab_y, 220, 96, self.display, 'image\\button_green.png', self.airplanes[i], (70, 190, 120))  # сел, зелёная рамка
            d = board.board(12, tab_y, 220, 96, self.display, 'image\\button_red.png', self.airplanes[i], (190, 70, 80))  # потерян, красная рамка
            self.button_airplane.append(a)
            self.button_finish.append(s)
            self.button_stolk.append(d)

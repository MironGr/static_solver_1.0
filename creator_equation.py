import math

# Парсинг входных данный с фронта (строк) и получение коэффициентов линейной системы уравнений

# Пример входных данных (не измененных)
# lines,KL-1.714,id-line_1,x1-125,y1-88.488,x2-209.533,y2-65.838,id-line_2,x1-209.533,y1-65.838,x2-209.533,y2-153.353
# nodes_1,id-node_1-1,x1-209.533,y1-153.353,alfa-45,line_id-line_2,id-node_1-2,x1-181.35510199573588,y1-73.38806198521975,alfa-45,line_id-line_1
# nodes_2,id-node2_1,cx-125,cy-88.488,id-node2_2,cx-209.533,cy-65.838
# forces_point,id-fp-1,fa-45,fd-50,fm-1000,ob-line_2,id-fp-2,fa-80,fd-50,fm-1000,ob-line_1

# Пример входных данных (измененных)
# lines,KL-1.714,id-line_1,x1-125,y1-88.488,x2-209.533,y2-65.838{;}id-line_2,x1-209.533,y1-65.838,x2-209.533,y2-153.353
# - nodes_1,id-{node1_1},{x}-209.533,{y}-153.353,{angle}-45,{ob}-line_2,id-{node1_2},x-181.35510199573588,y-73.38806198521975,alfa-45,{ob}-line_1
# - nodes_2,id-node2_1,{x}-125,{y}-88.488,{ob-line_1}{;}id-node2_2,cx-209.533,cy-65.838,{line_id-line_1};id-node2_3,cx-209.533,cy-65.838,{line_id-line_2}
# - forces_point,id-{fp_1},{fp_x-80.111,fp_y-112.222},fa-45,fd-50,fm-1000,{fdirect-0},ob-line_2,id-fp-2,{fp_x-102.123,fp_y-90.321},fa-80,fd-50,fm-1000,ob-line_1

# Допущения для v_1.0
# 1. Все элементы конструкции - прямые отрезки
# 2. Все элементы конструкции соединяются между собой неподвижными шарнирами (все шарниры есть в исходных данных)
# 3. Система координат относительно экрана, ось Х слева направо, Y - сверху вниз
# 4. Все углы с фронта со знаком "+" против ЧС, со знаком "-" по ЧС
# 5. Начало системы координат - верхний левый угол SVG.x = 0, SVG.y = 0
# 6. ? Неподвижные шарниры в местах соединения линий нужно ставить N раз, где N - число линий в узле
# 7. Неизвестные переменные - реакции опор (внутренние / внешние)
# 8. Все нагрузки и реакции (силы) приложены к отрезкам line
# 9. Решенать систему линейных уравнений условий равновесия будем сразу для всех элементов (число
#    неизвестых равно числу уравнений)

# Примем в v_1.0
# 1. Каждая линия это экземпляр класса Line;
# 2. Класс Line парсит строку и информацией о линии в dict с инфой о нагрузках на линию
# 3. Принадлежность нагрузки к линии определяются с фронта в ob
# 4. fdirect - 0 / 1, где 0 - положительное направление по оси Х, 1 - отрицательное направление
# 5. Угол наклона нагрузки относитльно Х 0...180
# 6. Условимся, что отрезки конструкции соединены между собой (система едина)
# 7. Связь 2 рода (неподвижный шарнир) может принадлежать или одному или двум отрезкам
# 8. Все force известны и являются коэффициентами В уравнений системы равновесия
# 9. KL = [м] / [px]

# Протестить numpy.linalg.solve(M2, v2) где М2 = numpy.array(список списков коэффициентов каждого ур-я)
# V2 = numpy.array(список свободных коэффициентов)


class ForcePoint:
    # каждая сила принадлежит отрезку Line
    def __init__(self, describe_str):
        """
        Разбор строки описания силы на словарь типа {'id': 'fp-1', 'fp_x': 80, ...}
        :param describe_str: str
        :return создание атрибута describe_dict
        """
        self.describe_str = describe_str
        # список describe_list не упорядочен, чтобы избежать ошибки:
        # param_list = ['id', 'fp_x', 'fp_y', 'fa', 'fm', 'fdirect', 'ob']
        self.force_dict = dict()
        describe_list = describe_str.split(',')
        for force_str in describe_list:
            force_list = force_str.split('-')
            self.force_dict.update({force_list[0] : force_list[1]})

    def get_line(self):
        line = self.force_dict.get('ob')
        return line

    def get_px(self): # projection
        """
        Получить модуль проекции на ось Х
        :return: float
        """
        module = float(self.force_dict.get('fm'))
        angle = float(self.force_dict.get('fa'))
        f_x = module * math.fabs(math.cos(angle * math.pi / 180))
        f_x = round(f_x, 3)
        return f_x

    def get_py(self): # projection
        """
        получить модуль проекции на ось у
        :return: float
        """
        module = float(self.force_dict.get('fm'))
        angle = float(self.force_dict.get('fa'))
        f_y = module * math.fabs(math.sin(angle * math.pi / 180))
        f_y = round(f_y, 3)
        return f_y

    def get_m(self, KL):
        mx = self.get_ma_y(KL) * self.get_px()
        my = self.get_ma_x(KL) * self.get_py()
        direct_x = self.get_dx()
        direct_y = self.get_dy()
        if direct_x == 1:
            mx *= -1
        if direct_y == 1:
            my *= -1
        m = mx + my
        m = round(m, 3)
        return m

    def get_ma_x(self, KL): # moment_arm - плечо силы
        ma_x = float(self.force_dict.get('fp_x')) * KL
        return ma_x

    def get_ma_y(self, KL): # moment_arm - плечо силы
        ma_y = float(self.force_dict.get('fp_y')) * KL
        return ma_y

    def get_dx(self): # direction
        """
        :return: 0 / 1, где 0 - по оси X, 1 - против оси Х
        """
        direct = self.force_dict.get('fdirect')
        return direct

    def get_dy(self):
        """
        :return: 0 / 1, где 0 - по оси Y, 1 - против оси Y
        """
        angle = float(self.force_dict.get('fa'))
        direct_x = self.force_dict.get('fdirect')
        if angle < 180 and direct_x == 0:
            direct_y = 1  # direct_y = 1 - против оси Y, 0 - по оси Y
            return direct_y
        elif angle < 180 and direct_x == 1:
            direct_y = 0
            return direct_y


class Line:
    # число уравнений равновесия = 3 * Число отрезков Line
    def __init__(self, describe_str):
        """
        Разбор строки описания силы на словарь типа {'id': 'fp-1', 'fp_x': 80, ...}
        :param describe_str: str
        :return создание атрибута describe_dict
        """
        self.describe_str = describe_str
        # список describe_list не упорядочен, чтобы избежать ошибки:
        # param_list = ['id', 'fp_x', 'fp_y', 'fa', 'fm', 'fdirect', 'ob']
        self.line_dict = dict()
        describe_list = describe_str.split(',')
        for line_str in describe_list:
            line_list = line_str.split('-')
            self.line_dict.update({line_list[0]: line_list[1]})

    def get_xy(self):
        xy = {}
        xy.update({'x1': self.line_dict.get('x1')})
        xy.update({'y1': self.line_dict.get('y1')})
        xy.update({'x2': self.line_dict.get('x2')})
        xy.update({'y2': self.line_dict.get('y2')})
        return xy

    def id(self):
        return self.line_dict.get('id')


class Node1:
    # Направление реакция опоры известно, принадлежит одному отрезку
    def __init__(self, describe_str):
        """
        Разбор строки описания силы на словарь типа {'id': 'fp-1', 'fp_x': 80, ...}
        :param describe_str: str
        :return создание атрибута describe_dict
        """
        self.describe_str = describe_str
        # список describe_list не упорядочен, чтобы избежать ошибки:
        # param_list = ['id', 'fp_x', 'fp_y', 'fa', 'fm', 'fdirect', 'ob']
        self.node_1_dict = dict()
        describe_list = describe_str.split(',')
        for node1_str in describe_list:
            node1_list = node1_str.split('-')
            self.node_1_dict.update({node1_list[0]: node1_list[1]})

    def get_line(self):
        return self.node_1_dict.get('ob')

    def id(self):
        return self.node_1_dict.get('id')

    def get_py(self): # projection y
        """
        получить известный множитель проекции на ось у для системы линейных уравнений
        :return: float
        """
        angle = float(self.node_1_dict.get('angle'))
        f_y = math.fabs(math.sin(angle * math.pi / 180))
        f_y = round(f_y, 3)
        return f_y

    def get_px(self): # projection x
        """
        получить известный множитель проекции на ось x для системы линейных уравнений
        :return: float
        """
        angle = float(self.node_1_dict.get('angle'))
        f_x = math.fabs(math.cos(angle * math.pi / 180))
        f_x = round(f_x, 3)
        return f_x

    def get_zm(self, KL):
        """
        Сумма моментов проекции реакции на ось Х и Y.
        Направление не имеет значения
        :return: float
        """
        mx = self.get_ma_y(KL) * self.get_px()
        my = self.get_ma_x(KL) * self.get_py()
        m = my + mx
        return round(m, 3)

    def get_ma_x(self, KL): # moment_arm - плечо силы, с учетом коэффициента масштаба Kl
        # KL = [м] / [px]
        ma_x = float(self.node_1_dict.get('x')) * KL
        return ma_x

    def get_ma_y(self, KL): # moment_arm - плечо силы, с учетом коэффициента масштаба Kl
        # KL = [м] / [px]
        ma_y = float(self.node_1_dict.get('y')) * KL
        return ma_y

class Node2:
    # Неизвестно направление и модуль
    def __init__(self, describe_str):
        """
        Разбор строки описания связи на словарь типа {'id': 'fp-1', 'fp_x': 80, ...}
        :param describe_str: str
        :return создание атрибута describe_dict
        """
        self.describe_str = describe_str
        # список describe_list не упорядочен, чтобы избежать ошибки:
        # param_list = ['id', 'fp_x', 'fp_y', 'fa', 'fm', 'fdirect', 'ob']
        self.node_2_dict = dict()
        describe_list = describe_str.split(',')
        for node2_str in describe_list:
            node2_list = node2_str.split('-')
            self.node_2_dict.update({node2_list[0]: node2_list[1]})

    def _point_on_line(self, points):
        """
        Определяет принадлежность точки отрезку (лижит ли точка внутри на отрезке или на концах)
        :param points: словарь с координатами точек (объект Line).
        Необходимая точка (объект Node2).
        :return: bool
        С v1.1 вынести в отдельный модуль математики
        """
        x1 = float(points.get('x1'))
        x2 = float(points.get('x2'))
        y1 = float(points.get('y1'))
        y2 = float(points.get('y2'))
        # Уравнение прямой по двум точкам Ax + By + C = 0
        A = y1 - y2
        B = x2 - x1
        C = x1 * y2 - x2 * y1
        x = float(self.node_2_dict.get('x'))
        y = float(self.node_2_dict.get('y'))
        result = A * x + B * y + C
        # Принадлежность точки попадает в математическую погрешность (переработать v1.1,
        # определение точки внутри отрезка)
        if round(result, 3) == 0:
            return True
        else:
            return False

    def get_lines(self, lines):
        """
        Принимает список объектов line, возвращает список id линий к которым принадлежит связь
        :param lines: список объектов [<obj>, <obj>, ...]
        :return: список id линий
        """
        # Примем, что связь 2 рода может принадлежать одному или двум отрезкам (v1.0)
        # Необходимо спроектировать класс Line
        line_id_list = []
        line_parent = self.node_2_dict.get('ob')
        line_id_list.append(line_parent)
        for line in lines:
            xy = line.get_xy()
            if self._point_on_line(xy) and len(line_id_list) < 2 and self.node_2_dict.get('ob') != line.id():
                line_id_list.append(line.id())
        return line_id_list

    def get_mzx(self, KL):
        """
        Получить коэффицнт А равный значению плеча проекции рекции 2-го рода на ось Х
        с учетом масштаба KL = [м] / [px]
        :return: float
        """
        A = float(self.node_2_dict.get('y')) * KL
        return round(A, 3)

    def get_mzy(self, KL):
        """
        Получить коэффицнт А равный значению плеча проекции рекции 2-го рода на ось Y
        с учетом масштаба KL = [м] / [px]
        :return: float
        """
        A = float(self.node_2_dict.get('x')) * KL
        return round(A, 3)

    def id(self):
        return self.node_2_dict.get('id')


class EquationsEquilibrium:
    """
    Входные данные - словари с распеределением по отрезкам нагрузок, связей 1 и 2 рода, (моментов с v.1.1).
    В уравнениях равновесия для каждого из тел участвуют все реакции, если реакция не принадлежит
    текущему телу то коэффициент этой рекции Аi = 0.
    Знак у коэффициентов примем '+', т.к при решении общей системы уравнений неизвестные реакции получат знак
    """
    def __init__(self,
                 line_id,
                 forces_list,
                 node1_list,
                 node2_list):
        self.line_id = line_id          # str
        self.forces_list = forces_list
        self.node1_list = node1_list
        self.node2_list = node2_list

    def coefficients_b(self, KL):
        """
        Возвращает list[float] со свобоными коэффициентами B уравнения равновесия на ось Х, Y, Moments
        KL = [м] / [px]
        :return: list
        """
        # Получение свободного члена уравнения на ось Х, Y, M
        B_list = []
        Bx = 0
        By = 0
        Bmz = 0
        for force in self.forces_list:
            if force.get_line() == self.line_id:
                Bx += force.get_px()
                By += force.get_py()
                Bmz += force.get_m(KL)
        B_list.append(Bx * (-1))
        B_list.append(By * (-1))
        B_list.append(Bmz * (-1))
        return B_list  # [Bx, By, Bmz]

    def coefficients_a(self, KL, lines):
        """
        Возвращает dict('Ax':<list>, 'Ay':<list>, 'Am':<list>), где <list> это сипсок Ai коэффициетов каждого
        уравнения равновесия.
        KL = [м] / [px]
        :return: dict
        """
        A_dict = dict() # {'Ax' : [1, 2, 3, 0, 0, 0...], 'Ay' : [4, 5, 6, 0, 0, 0...], 'Amz' : [...]}
        # Сначала рассматриваются реакции 1-го рода, затем 2-го, последние 3-го рода
        Ax = []
        Ay = []
        Amz = []
        # Добавление реакций 1-го рода в список коэффициентов
        for node1 in self.node1_list:
            node1_Ax = 0
            node1_Ay = 0
            node1_Amz = 0
            if node1.get_line() == self.line_id:
                node1_Ax = node1.get_px()
                node1_Ay = node1.get_py()
                node1_Amz = node1.get_zm(KL)
            Ax.append(node1_Ax)
            Ay.append(node1_Ay)
            Amz.append(node1_Amz)
        # Добавление реакций 2-го рода в список коэффициентов
        # Сортировка списков node2 по алфавиту во избежание повторения
        node2_lines_list = []
        for node2 in self.node2_list:
            node2_lines = sorted(node2.get_lines(lines))
            if node2_lines not in node2_lines_list:
                node2_lines_list.append(node2_lines)
        # Добавление реакций 2-го рода в список коэффициентов
        lines_list_check = []
        for node2 in self.node2_list:
            lines_list = sorted(node2.get_lines(lines))
            lines_list_check.append(lines_list)
            if self.line_id not in lines_list:
                for i in [0, 0]:
                    Ax.append(i)  # Сначала проекция на Х, затем на Y
                    Ay.append(i)
                    Amz.append(i)
            # Проверка существования в списке узла2
            # if lines_list_check == node2_lines_list:
                # for line in lines_list:
            if self.line_id in lines_list and lines_list.index(self.line_id) == 0:
                Ax.append(1)
                Ax.append(0)
                Ay.append(0)
                Ay.append(1)
                Amz.append(node2.get_mzx(KL))
                Amz.append(node2.get_mzy(KL))
            elif self.line_id in lines_list and lines_list.index(self.line_id) == 1:
                Ax.append(-1)
                Ax.append(0)
                Ay.append(0)
                Ay.append(-1)
                Amz.append(node2.get_mzx(KL))
                Amz.append(node2.get_mzy(KL))
        # Добавление реакций 3-го рода в список коэффициентов (с v.1.1)
        A_dict.update({'Ax' : Ax, 'Ay' : Ay, 'Amz' : Amz})
        return A_dict




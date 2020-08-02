import math

import numpy

from app.static_solver.services.creator_equation import (ForcePoint,
                                                         EquationsEquilibrium,
                                                         Node1,
                                                         Node2,
                                                         Line)

# Сформировать списки объектов классов Line(), ForcePoint(), Node1(), Node2()

# Парсер строки forces_point
# forces_point = 'forces_point,id-fp_1,fp_x-80.111,fp_y-112.222,fa-45,fd-50,fm-1000,fdirect-0,ob-line_2;id-fp_2,fp_x-102.123,fp_y-90.321,fa-80,fd-50,fm-1000,fdirect-0,ob-line_1'
# forces_point = 'forces_point,id-fp_1,fa-45,fd-50,fm-1000,fp_x-80.111,fp_y-112.222,fdirect-0,ob-line_1;id-fp_1,fa-60,fd-50,fm-1000,fp_x-102.123,fp_y-90.321,fdirect-0,ob-line_2'
forces_point = 'forces_point,id-fp_1,fa-90,fd-60,fm-1000,fp_x-180,fp_y-120,fdirect-0,ob-line_1'
forces_point = forces_point[13:]
forces_desc_list = forces_point.split(';')

force_list = []
for force_str in forces_desc_list:
    force = ForcePoint(force_str)
    force_list.append(force)

print('force_list - ', force_list)

# nodes1_str = 'nodes_1,id-node1_1,x-209.533,y-153.353,angle-45,ob-line_2;id-node1_2,x-181.355,y-73.388,angle-45,ob-line_1'
# nodes1_str = 'nodes_1,id-node1_1,x-120,y-142,angle-90,ob-line_1;id-node1_2,x-204.533,y-119.35,angle-0,ob-line_2'
nodes1_str = 'nodes_1,id-node1_1,x-240,y-240,angle-45,ob-line_2;id-node1_2,x-240,y-200,angle-60,ob-line_2'
nodes1_str = nodes1_str[8:]
node1_desc_list = nodes1_str.split(';')

node1_list = []
for node1_str in node1_desc_list:
    node1 = Node1(node1_str)
    node1_list.append(node1)

print('node1_list - ', node1_list)

# nodes2_str = 'nodes_2,id-node2_1,x-125,y-88.488,ob-line_1;id-node2_2,x-209.533,y-65.838,ob-line_1;id-node2_3,x-209.533,y-65.838,ob-line_2'
# nodes2_str = 'nodes_2,id-node2_1,x-204.533,y-148.522,ob-line_2;id-node2_2,x-204.533,y-119.35,ob-line_1'
nodes2_str = 'nodes_2,id-node2_1,x-120,y-120,ob-line_1;id-node2_2,x-240,y-120,ob-line_2'
nodes2_str = nodes2_str[8:]
node2_desc_list = nodes2_str.split(';')

node2_list = []
for node2_str in node2_desc_list:
    node2 = Node2(node2_str)
    node2_list.append(node2)

print('node2_list - ', node2_list)

# lines_str = 'lines,KL-1.714,id-line_1,x1-125,y1-88.488,x2-209.533,y2-65.838;id-line_2,x1-209.533,y1-65.838,x2-209.533,y2-153.353'
# lines_str = 'lines,KL-1.714,id-line_1,x1-120,y1-142,x2-204.533,y2-119.35;id-line_2,x1-204.533,y1-148.522,x2-204.533,y2-61.007'
lines_str = 'lines,KL-1.714,id-line_1,x1-120,y1-120,x2-240,y2-120;id-line_2,x1-240,y1-120,x2-240,y2-240'
kl = float(lines_str[9:14])
lines_str = lines_str[15:]
lines_desc_list = lines_str.split(';')

lines_list = []
for line_str in lines_desc_list:
    line = Line(line_str)
    lines_list.append(line)

print('lines_list - ', lines_list)


# Получение списка объектов уравнений EquationsEquilibrium для каждого из объектов line
equations_list = []
for line in lines_list:
    equations = EquationsEquilibrium(line.id(), force_list, node1_list, node2_list)
    equations_list.append(equations)

print('eq_list - ', equations_list)
for eq in equations_list:
    print('B - ', eq.coefficients_b(kl))
    dict_A = eq.coefficients_a(kl, lines_list)
    print('Ax - ', dict_A.get('Ax'), ' - ', len(dict_A.get('Ax')))
    print('Ay - ', dict_A.get('Ay'), ' - ', len(dict_A.get('Ay')))
    print('Amz - ', dict_A.get('Amz'), ' - ', len(dict_A.get('Amz')))

for node2 in node2_list:
    print('node2 lines - ', node2.get_lines(lines_list))

# Расчет системы уравнений по списку equations_list объектов уравнений для каждого тела
# numpy.linalg.solve(M2, v2)
a_list = []
b_list = []
for eq in equations_list:
    a_dict = eq.coefficients_a(kl, lines_list)
    ax = a_dict.get('Ax')
    ay = a_dict.get('Ay')
    am = a_dict.get('Amz')
    a_list.append(ax)
    a_list.append(ay)
    a_list.append(am)
    b_eq = eq.coefficients_b(kl)
    for b in b_eq:
        b_list.append(b)

a_array = numpy.array(a_list)
b_array = numpy.array(b_list)
x_array = numpy.linalg.solve(a_array, b_array)
print('a - ', a_list)
print('b_list - ', b_list)
print('x_arr - ', x_array)
for x in x_array:
    print('x - ', x)


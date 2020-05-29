import sys
try:
    from msvcrt import *
    PLAT='win' #В Windows и Linux различаются коды клавиш и команда очистки консоли
    RESET='cls'
    SPEC=224
    ENT=13
    UP=72
    DOWN=80
    LEFT=75
    RIGHT=77
except ImportError:
    try:
        '''
Реализация функций из msvcrt под Linux честно сперта отсюда:
http://code.activestate.com/recipes/572182-how-to-implement-kbhit-on-linux/
'''
        import termios
        from select import select
        fd = sys.stdin.fileno()
        new_term = termios.tcgetattr(fd)
        old_term = termios.tcgetattr(fd)
        new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
        def set_normal_term():
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)
        def set_curses_term():
            termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)
        def getch():
            return sys.stdin.read(1)
        def kbhit():
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr!=[]
        PLAT='lin'  
        RESET='tput reset'
        SPEC=27
        ENT=10
        UP=65
        DOWN=66
        LEFT=68
        RIGHT=67
    except:
        print("Какая-то проблема!")
from random import randint
from os import system
from time import sleep

class Snake:
    """
    Snake

    Змейка в консоли.
    "@" -- тело самой змейки
    Черный прямоугольник (или что угодно другое, кроме нижеперечисленного) -- непроходимая стена
    Звездочка -- "еда" для змейки, увеличивает счет и длину змейки на один сегмент
    Точка -- "проходимая стена". Если змейка войдет в эту стену, игра не закончится, просто "голова" змейки выйдет с другой стороны
    Пробел -- "свободное место", по которому змейка перемещается.
    """
    def __init__(self, field="""
██████████████████████
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█         @          █
█         @          █
█         @          █
█         @          █
█         @          █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
██████████████████████
""", speed=0.5):
        self.speed=speed #Если быть точным, время задержки между перемещениями змейки
        self.score=0 
        self.field=field
        self.leng=self.field[1:].find('\n')+1 #Так как используется строка, длина нам понадобится чтобы двигаться вверх и вниз
        self.dir=-self.leng #В начале игры движемся вверх
        self.snake=[self.field.find('@')] #Начальное положение змейки задается полем
        for i in range (1,5): #чтобы не усложнять, начальная длина змейки == 5 и расположена она вертикально
            self.snake.append(self.snake[0]+i*self.leng) #Змейка будет задаваться списком координат всех ее частей
        self.food=0
        self.newfood()
    def newfood(self): #Генерирует новую "еду" в случайном пустом месте поля
        self.food=randint(0, len(self.field)-1)
        while (self.field[self.food]!=' '):
            self.food=randint(0, len(self.field))
        self.field=self.field[:self.food]+'*'+self.field[self.food+1:]
    def move(self): #Двигает змейку, обрабатывая все, что может с ней случиться
        if self.crash(): #Если врезались, игра закончена
            return False 
        system(RESET)
        if self.through():
            if self.dir==1:
                self.snake.insert(0, self.snake[0]-self.leng+4)
            elif self.dir==-1:
                self.snake.insert(0, self.snake[0]+self.leng-4)
            elif self.dir>0:
                self.snake.insert(0, self.snake[0]-len(self.field)+3*self.dir+1)
            else:
                self.snake.insert(0, len(self.field)+3*self.dir+self.snake[0]-1)
                
        else:
            self.snake.insert(0, self.snake[0]+self.dir)
        if self.ate():
            self.score+=int(10/self.speed)
            self.newfood()
        else:
            self.field=self.field[:self.snake[-1]]+" "+self.field[self.snake[-1]+1:]
            self.snake.pop()
        self.field=self.field[:self.snake[0]]+"@"+self.field[self.snake[0]+1:] #Изменили поле
        sys.stdout.write("%d\n" % self.score) #Вывели его в очищенный терминал
        sys.stdout.write(self.field)
        return True
    def crash(self): #Если после движения змейка врежется в стену
        return not (self.field[self.snake[0]+self.dir] in " *.") #Тут строка "безопасных" элементов.
    def through(self): #Определяет, не вошла ли змейка в "безопасную стену"
        return self.field[self.snake[0]+self.dir]=='.'
    def ate(self): #Проверяет, не наткнулись ли мы на еду при перемещении
        return self.snake[0]==self.food
    def __call__(self): #Основной цикл
        system(RESET) #Очищает терминал
        if PLAT=='lin':
            set_curses_term() #Терминал не выводит символы при нажатии клавиши
        while True:
            if kbhit(): #Если было нажатие
                c=ord(getch()) #Считать один символ из потока ввода
                if c==SPEC: #Одна из системных кнопок нажата
                    if PLAT=='lin':
                        ord(getch()) #всегда будет '['
                    k=ord(getch()) #Проверяем, нажата ли какая-то стрелка или какая-то другая кнопка
                    if k==UP: 
                        if abs(self.dir)==1:
                            self.dir=-self.leng #...и изменяем направление движения соответственно
                    if k==DOWN:
                        if abs(self.dir)==1:
                            self.dir=self.leng
                    if k==LEFT:
                        if abs(self.dir)==self.leng:
                            self.dir=-1
                    if k==RIGHT:
                        if abs(self.dir)==self.leng:
                            self.dir=1
                elif c==ord('q'): #Хоткей экстренного выхода
                    if PLAT=='lin':
                        set_normal_term() #Возвращает терминал в нормальное состояние
                    system(RESET)
                    exit()
            if not self.move():
                return 0 #Если игра окончена, из цикла выходим
            sleep(self.speed) #Пауза между движениями
    def __str__(self):
        return self.field

if __name__=='__main__':
    yn=['\r     да      ', '\r     нет     '] 
    fields=["""
██████████████████████
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█         @          █
█         @          █
█         @          █
█         @          █
█         @          █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
██████████████████████
""", """
......................
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.         @          .
.         @          .
.         @          .
.         @          .
.         @          .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
......................
""", """
██████..........██████
█                    █
█                    █
█                    █
█                    █
█                    █
.                    .
.                    .
.                    .
.         @          .
.         @          .
.         @          .
.         @          .
.         @          .
.                    .
.                    .
█                    █
█                    █
█                    █
█                    █
█                    █
██████..........██████
""", """
█....................█
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█         @          █
█         @          █
█         @          █
█         @          █
█         @          █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█                    █
█....................█
""", """
██████████████████████
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.         @          .
.         @          .
.         @          .
.         @          .
.         @          .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
.                    .
██████████████████████
""", """
█████████████.....████
█                    █
█                    █
█                    █
█                    |
.       █            .
.       █            .
.       █            .
.       █            .
.       █ @          .
█       █ @          █
█       █ @          █
█       █ @          █
█       █ @          █
█       █            █
███   ███████     ████
█                    █
█                    █
█                    █
█                    █
█                    █
█████████████.....████
""", """
....................................................
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                        @                         .
.                        @                         .
.                        @                         .
.                        @                         .
.                        @                         .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
.                                                  .
....................................................
"""] 
#█████████
    speeds=[1, 0.9, 0.75, 0.66, 0.5, 0.33, 0.25, 0.1, 0.05, 0.025, 0.01]
    spd=speeds[4]
    leng=fields[0][1:].find('\n')+1
    n=0
    if PLAT=='lin':
        set_curses_term()
    system(RESET)
    sys.stdout.write("Выберите уровень")
    sys.stdout.write(fields[0])
    c=ord(getch())
    while c!=ENT:
        if c==SPEC:
            if PLAT=='lin':
                ord(getch())
            c=ord(getch())
            if c==LEFT:
                n-=1
            elif c==RIGHT:
                n+=1
        system(RESET)
        sys.stdout.write("Выберите уровень")
        sys.stdout.write(fields[n%len(fields)])
        c=ord(getch())
    n=n%len(fields)
    m=4
    spdbar='['+'█'*m+' '*(10-m)+']'
    system(RESET)
    sys.stdout.write("Выберите скорость")
    sys.stdout.write(spdbar)
    sys.stdout.write('\n%d' % m)
    c=ord(getch())
    while c!=ENT:
        if c==SPEC:
            if PLAT=='lin':
                ord(getch())
            c=ord(getch())
            if c==LEFT and m>0:
                m-=1
            elif c==RIGHT and m<10:
                m+=1
        spdbar='['+'█'*m+' '*(10-m)+']'
        system(RESET)
        sys.stdout.write("Выберите скорость")
        sys.stdout.write(spdbar)
        sys.stdout.write('\n%d' % m )
        c=ord(getch())
    c=''
    spd=speeds[m]
#    field=Field()
#    field()
    while True:
        field1=Snake(fields[n],spd)
        field1() #Объявляем и запускаем игру
        sys.stdout.write("Вы проиграли!\n")
        sleep(1)
        if PLAT=='lin':
            set_normal_term()
        try:
            f=open('scores') #Файл со списком лучших результатов
        except: #Если его нет, создаем новый и записываем новый результат в него
            f=open('scores', mode='w')
            sys.stdout.write("Введите ваше имя:\n")
            name=sys.stdin.readline()[:-1]
            rec=name+' '+str(field1.score)
            system(RESET)
            sys.stdout.write('%s\n' % rec)
            f.write('%s\n' % rec)
        else: #Если есть, считываем его...
            recs=f.read().split('\n')
            f.close()
            i=0
            while i<10: #...смотрим первые десять строк...
                rec=recs[i]
                if rec=='': #Если рекордов < 10 и прошедшая игра была хуже остальных, записываем результат в конец файла
                    sys.stdout.write("Введите ваше имя:\n")
                    name=sys.stdin.readline()[:-1]
                    recs.insert(i, name+' '+str(field1.score))
                    break
                if int(rec.split()[-1])<field1.score: #Иначе вставляем его в нужное место в таблице рекордов.
                    sys.stdout.write("Введите ваше имя:\n")
                    name=sys.stdin.readline()[:-1]
                    recs.insert(i, name+' '+str(field1.score))
                    i+=1
                    break
                i+=1
            if len(recs)>11: recs.pop(-2)
            f=open('scores', mode='w')
            system(RESET) #Очищаем терминал и выводим новую таблицу рекордов, одновременно записывая ее в файл
            for i in recs[:-1]:
                sys.stdout.write('%s\n' % i)
                f.write('%s\n' % i)
        finally:
            f.close()
            if PLAT=='lin':
                set_curses_term()
            sleep(3)
            sys.stdout.write("Начать сначала?\n") 
            i=0
            sys.stdout.write('%s' % yn[0]) #Тут выводится строка, в которой по нажатию стрелочек меняются "да" и "нет"
            c=ord(getch())
            while(c!=ENT): #До нажатия на enter будет считывать другие нажатия; если стрелочки -- менять да и нет
                if (c==SPEC):
                    if PLAT=='lin':
                        getch()
                    c=ord(getch())
                    if c==UP or c==LEFT or c==RIGHT or c==UP:
                        i+=1
                        sys.stdout.write('%s' % yn[i%2])
                c=ord(getch())
            if (i%2): #"да" на четном месте, так что это уловие будет, если выбрали "нет"
                break #Завершаем программу, если не хотят играть заново, иначе повторится цикл
    if PLAT=='lin':
        set_normal_term()
    system(RESET)

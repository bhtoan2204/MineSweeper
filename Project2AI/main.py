from tkinter import *
from tkinter import filedialog, messagebox
import math
import numpy
from time import sleep, perf_counter
from itertools import combinations
from pysat.solvers import Glucose3

global matrix, colorMatrix, sqsize, list_cnf, numberedMatrix, time_delay
time_delay = 0.5

xNeighbor = [0, 0, 0, 1, 1, 1, -1, -1, -1]
yNeighbor = [0, 1, -1, 0, 1, -1, 0, 1, -1]

height = 500
width = 500

size = 0

sqsize = 0

list_cnf =[]

def setNumber():
    sqsize = height / len(matrix[0])
    for i in range(size):
        for j in range(size):
            if matrix[i][j] == -1: continue
            canvas.create_text(sqsize*j + sqsize/2, sqsize*i+sqsize/2, text=str(int(matrix[i][j])))

def testResult(input,m, n, result):
    for row in range(m):
        for col in range(n):
            if (input[row][col] >= 0 and input[row][col] <= 9):
                count_green, right_green = 0, int(input[row][col])
                for i in range(row - 1, row + 2):
                    if (i >= 0 and i < m):
                        for j in range(col - 1, col + 2):
                            if (j >= 0 and j < n):
                                if(result[i][j] == 1):
                                    count_green += 1
                if (right_green != count_green):
                    return False
    return True

def BFAssignment(row, col, input, m, n, result):
    if (row == m):
        return testResult(input, m, n, result)
    for color in range(2):
        if color == 0:
            fillRedWD(col, row)
        if color == 1:
            fillGreenWD(col, row)
        result[row][col] = color
        next_row, next_col = row, col + 1
        if (next_col == n):
            next_row += 1
            next_col = 0
        if (BFAssignment(next_row, next_col, input, m, n, result)):
            return True
    return False

def BTAssignment(indexCell, posCell, redAdjIndex, redAdj, green, input, m, n, result):
    for adj in range(redAdjIndex, redAdj[1]):
        result[redAdj[2][adj][0]][redAdj[2][adj][1]] = 1
        fillGreenWD(redAdj[2][adj][1], redAdj[2][adj][0])
        conflict = 0
        for i in range(0, indexCell):
            temp = checkRedAdjCell(posCell[i], m, n, result)
            temp2 = int(posCell[i][0]) - (temp[0] - temp[1])
            if (temp2 != 0):
                conflict = 1
                break
        if (conflict == 0):
            green -= 1
            if (green > 0):
                if(BTAssignment(indexCell, posCell, adj+1, redAdj, green, input, m, n, result)):
                    return True
            elif(green == 0):
                if (solveBTCells(indexCell+1, posCell, input, m, n, result)):
                    return True
            green += 1
        result[redAdj[2][adj][0]][redAdj[2][adj][1]] = 0
        fillRedWD(redAdj[2][adj][1], redAdj[2][adj][0])
    return False

def showNoti(time):
    Tk().wm_withdraw()
    messagebox.showinfo('Notification', 'Time execute: ' + str(abs(round(time, 3))))

def Pysat():
    start = perf_counter()
    generateCNF(matrix)
    for i in range(size):
        for j in range(size):
            if colorMatrix[j][i] == False:
                fillRedWD(i, j)
            if colorMatrix[j][i] == True:
                fillGreenWD(i, j)
    end = perf_counter()
    setNumber()
    showNoti(end - start)
def A_start():
    for i in range(size):
        for j in range(size):
            fillRedWD(i, j)

def Brute_Force():
    start = perf_counter()
    for i in range(size):
        for j in range(size):
            fillRedWD(i, j)
    result = [[0 for i in range(size)] for j in range(size)]
    if (not BFAssignment(0, 0, matrix, size, size, result)):
        for row in range(size):
            for col in range(size): result[row][col] = -1
    print(result)
    setNumber()
    end = perf_counter()
    showNoti(end - start)

def getPosCells():
    posCells=[]
    for row in range(size):
        for col in range(size):
            if matrix[row][col] >= 0 and matrix[row][col] <= 9: posCells.append((matrix[row][col], row, col))
    return posCells

def checkRedAdjCell(checkCell, m, n, result):
    redAdjList = []
    countRedAdjCells, totalAdjCell = 0, 0
    for i in range(checkCell[1]-1, checkCell[1]+2):
        if (i >= 0 and i < m):
            for j in range(checkCell[2]-1, checkCell[2]+2):
                if (j >= 0 and j < n):
                    if (result[i][j] == 0):
                        countRedAdjCells += 1
                        redAdjList.append((i, j))
                    totalAdjCell += 1

    return (totalAdjCell, countRedAdjCells, redAdjList)

def solveBTCells(index, posCell, input, m, n, result):
    if (index < len(posCell)):
        redAdj = checkRedAdjCell(posCell[index], m, n, result)
        green = int(posCell[index][0]) - (redAdj[0] - redAdj[1])
        if (green > 0):
            return BTAssignment(index, posCell, 0, redAdj, green, input, m, n, result)
        elif (green == 0):
            return solveBTCells(index+1, posCell, input, m, n, result)
        else: return False
    return True

def Backtracking():
    start = perf_counter()
    result = [[0 for i in range(size)] for j in range(size)]
    cell_with_unnega_value = getPosCells()
    for i in range(size):
        for j in range(size):
            fillRedWD(i, j)
    if (not solveBTCells(0, cell_with_unnega_value, matrix, size, size, result)):
        for row in range(size):
            for col in range(size):
                result[row][col]=-1
    end = perf_counter()
    setNumber()
    showNoti(start - end)

def generateCNF(matrix):
    global g
    g = Glucose3()
    U = list()
    L = list()
    for x in range(size):
        for y in range(size):
            if matrix[x][y]== -1: continue
            adjacents = list()
            for z in range(9):
                iNew = xNeighbor[z] + x
                jNew = yNeighbor[z] + y
                if iNew > -1 and jNew > -1 and iNew < size and jNew < size:
                    adjacents.append(1 + (x + xNeighbor[z]) * size + y + yNeighbor[z])
            k = int(matrix[x][y])
            n = len(adjacents)
            for combination in combinations(adjacents, k + 1):
                U.append({i * -1 for i in combination})  # element-wise multiplication with -1

            for combination in combinations(adjacents, n - k + 1):
                L.append(set(combination))
    for clause in numpy.unique(U):
        list_cnf.append(clause)
        g.add_clause(clause)

    for clause in numpy.unique(L):
        list_cnf.append(clause)
        g.add_clause(clause)

    if not g.solve():
        print('No solutions!')
    else:
        model = g.get_model()
        assignColor(model)

def assignColor(arr):
    index = 0
    print(arr)
    global colorMatrix
    for i in range(size):
        for j in range(size):
            if (arr[index] > 0):
                colorMatrix[i][j] = True
            if (arr[index] < 0):
                colorMatrix[i][j] = False
            index = index + 1

def takeUpdate():
    time_delay = entry1.get()

def loadString(string):
    str = string.split()
    global size
    global matrix, colorMatrix, numberedMatrix
    size = int(math.sqrt(len(str)))
    matrix = numpy.full((size, size), -1, dtype=int)
    colorMatrix = numpy.full((size, size), False, dtype=bool)
    numberedMatrix = numpy.full((size,size), None)
    for i in range(size):
        for j in range(size):
            numberedMatrix[i][j] = size*i+j+1
    matrix = numpy.loadtxt(filepath, usecols=range(size))
    drawBoard()

def openFile():
    global filepath
    filepath = filedialog.askopenfilename()
    label1.config(text = str(filepath))
    file = open(filepath, 'r')
    string = str(file.read())
    loadString(string)
    file.close()

def drawBoard():
    sqsize = height / len(matrix[0])
    for i in range(size):
        canvas.create_line(0, sqsize*i, 500, sqsize*i)
    for i in range(size):
        canvas.create_line(sqsize*i, 0, sqsize*i, 500)

def fillGreen(x, y):
    sqsize = height / len(matrix[0])
    canvas.create_rectangle(sqsize*x, sqsize*y, sqsize*(x+1), sqsize*(y+1), fill='blue')
    canvas.update()
    sleep(time_delay)

def fillRed(x, y):
    sqsize = height / len(matrix[0])
    canvas.create_rectangle(sqsize * x, sqsize * y, sqsize * (x + 1), sqsize * (y + 1), fill='red')
    canvas.update()
    sleep(time_delay)

def fillGreenWD(x, y): #without delay
    sqsize = height / len(matrix[0])
    canvas.create_rectangle(sqsize*x, sqsize*y, sqsize*(x+1), sqsize*(y+1), fill='blue')

def fillRedWD(x, y):
    sqsize = height / len(matrix[0])
    canvas.create_rectangle(sqsize * x, sqsize * y, sqsize * (x + 1), sqsize * (y + 1), fill='red')

def returnClicked():
    takeUpdate()
    command = clicked.get()
    if command == "Pysat":
        Pysat()
    if command == "A Star":
        A_start()
    if command == "Brute Force":
        Brute_Force()
    if command == "Backtracking":
        Backtracking()

def stop():
    time_delay = 1000000

global root, canvas
root = Tk()
root.geometry("500x600+150+100")
root.title("Puzzle")

canvas = Canvas()
canvas.config(bg='white')
canvas.config(width="500", height="500")
canvas.place(x = "0", y = "100")

button1 = Button(text="Browse", command=openFile)
button1.place(x="10", y="70")

button2 = Button(text="Update", command=takeUpdate)
button2.place(x="10", y="40")

button3 = Button(text ="Start", command=returnClicked)
button3.place(x="250", y="10", width=50, height=60)

button4 = Button(text ="Stop", command=stop)
button4.place(x="300", y="10", width=50, height=60)

button5 = Label(text="Heuristic", bg='white')
button5.place(x="10", y="10")

global entry1, entry2
entry1 = Entry(root, bd = 5)
entry1.insert(END, str(time_delay))
entry1.place(x = "90", y="40")

entry2 = Label(root, bd = 5, bg='white')
entry2.place(x = "90", y="10")

global label1
label1 = Label(root, text ="", bg='white')
label1.place(x="90", y="70")

global clicked

options = ["Pysat", "A Star", "Brute Force", "Backtracking"]
clicked = StringVar()
clicked.set("Pysat")
drop = OptionMenu( root , clicked , *options )
drop.place(x = "370", y = "10")

root.mainloop()

import random as rd
import keyboard as kb

bc = "🞩" #bomb char
sc = "▣" #square char
fc = "⚑" #flagged char

# Por algun motivo, los nombres de algunas teclas cambian segun el idioma
keys = {
    "left": ["a", "left", "flecha izquierda"],
    "right": ["d", "right", "flecha derecha"],
    "up": ["w", "up", "flecha arriba"],
    "down": ["s", "down", "flecha abajo"],
    "shift": ["shift", "mayusculas"],
}

# Diccionario de colores básicos
colors = {
    "negro": "\033[30m",
    "rojo": "\033[31m",
    "verde": "\033[32m",
    "amarillo": "\033[33m",
    "azul": "\033[34m",
    "magenta": "\033[35m",
    "cian": "\033[36m",
    "blanco": "\033[37m",
    "reset": "\033[0m"  # Para resetear el color
}


conf = {"width": 10, "height": 10, "bombs": 10}
rd.seed(15)

class Cell():
    def __init__(self) -> None:
        self.is_visible = False
        self.is_flagged = False
        self.content = 0   # -1 si es bomba
        
    def __str__(self) -> str:
        if self.is_flagged:
            return fc
        if self.is_visible:
            if self.content == 0:
                return " "
            if self.content == -1:
                return bc
            return str(self.content)
        return sc

class Board():
    def __init__(self, width: int, height: int, bombs: int) -> None:
        self.height = height
        self.width = width
        self.bombs = bombs
        self.current_bombs = bombs
        self.board = []
        self.lose = False
        self.win = False
        self.numeric_cells = width*height-bombs
        self.first_cell = []
        self.current_cell = (0,0)

    def clear_board(self) -> None:
        self.board = []
        self.first_cell = []
        self.lose = False
        self.win = False
        self.numeric_cells = self.width*self.height-self.bombs
        self.current_bombs = self.bombs

    # Crea el tablero   
    def create_board(self) -> None:
        if self.board != []:
            self.clear_board()
        self.board = [[Cell() for _ in range(self.width)] for _ in range(self.height)]

    # Asigna el contenido de cada celda
    def assign_content(self):
        self.assign_bombs()
        self.assign_numbers()
        print(f"numeric cells: {self.numeric_cells}")

    # Asigna los bombas
    def assign_bombs(self) -> None:
        bombs = self.bombs
        while (bombs > 0):
            x = rd.randint(0,self.width-1)
            y = rd.randint(0,self.height-1)
            if self.cell_has_bomb((x, y)) or self.first_cell == (x, y) or (x, y) in self.first_cell_perimeter():
                continue
            self.board[y][x].content = -1 
            bombs -= 1

    def first_cell_perimeter(self) -> list:
        coords = self.where_there_is_something_in_perimeter(0, self.first_cell)
        return coords

    # Asigna los numeros a cada celda
    def assign_numbers(self) -> None:
        for y in range(0, self.height):
            for x in range(0, self.width):
                if not self.cell_has_bomb((x, y)):
                    bombs = self.bombs_in_perimeter((x, y))
                    self.board[y][x].content = bombs

    # Retorna la cantidad de bombas que rodea a la celda 
    def bombs_in_perimeter(self, coord: tuple[int, int]) -> int:
        coords = self.where_there_is_something_in_perimeter(-1, coord)
        return len(coords)

    # retorna una lista de coordenadas donde está(n) something rodeando a la celda (x,y). No incluye la celda (x,y)
    def where_there_is_something_in_perimeter(self, something, coord: tuple[int, int]) -> list:
        x, y= coord
        i = x-1
        j = y-1
        coords = []
        while i <= x+1 and j <= y+1:
            if self.validate_cell((i, j)):
                if self.cell_has_something(something, (i, j)):
                    coords.append((i,j))
            if i == x+1:
                i = x-1
                j += 1
                continue
            i += 1
        return coords
    
    # Comprueba si la celda (x,y) tiene ceros
    def cell_has_zero(self, coord: tuple[int, int]) -> bool:
        return self.cell_has_something(0, coord)
    
    # Comprueba si la celda (x,y) tiene bombas
    def cell_has_bomb(self, coord: tuple[int, int]) -> bool:
        return self.cell_has_something(-1, coord)

    # Comprueba si la celda (x,y) tiene algo
    def cell_has_something(self, something, coord: tuple[int, int]) -> bool:
        x, y = coord
        if self.get_content(coord) == something:
            return True
        elif something == fc:
            return self.board[y][x].is_flagged
        return False
    
    def cell_has_flag(self, coord: tuple[int, int]) -> bool:
        return self.cell_has_something(fc, coord)

    def flags_in_perimeter(self, coord: tuple[int, int]) -> int:
        coords = self.where_there_is_something_in_perimeter(fc, coord)
        return len(coords)

    def get_content(self, coord: tuple[int, int]) -> int:
        x, y = coord
        return self.board[y][x].content

    # Define el comportamiento al seleccionar una celda
    def select_cell(self, coord: tuple[int, int], read_flag: bool = True) -> None:
        if self.first_cell == []:
            self.first_cell = coord
            self.assign_content()
        if not self.validate_cell(coord):
            return
        self.make_cell_visible(coord)
        if self.cell_has_zero(coord): 
            coords0 = self.find_group_of_zeros(coord)
            for coord in coords0:
                self.make_cell_visible(coord)
                self.make_perimeter_visible(coord)
        elif self.cell_has_flag(coord):
            pass
        elif self.cell_has_bomb(coord):
            self.lose_game()
        elif read_flag and self.flags_in_perimeter(coord) == int(self.get_content(coord)):
            self.select_perimeter(coord)

        if self.all_numeric_cells_are_visible():
            self.win_game()
        
    def all_numeric_cells_are_visible(self) -> bool:
        print(f"numeric_cells: {self.numeric_cells}")
        if self.numeric_cells == 0:
            return True
        return False

    def lose_game(self) -> None:
        self.lose = True
        self.make_board_visible()

    def win_game(self) -> None:
        self.win = True

    def select_perimeter(self, coord: tuple[int, int]) -> None:
        x, y = coord
        self.select_cell((x-1, y-1), False)
        self.select_cell((x-1, y), False)
        self.select_cell((x-1, y+1), False)
        self.select_cell((x, y-1), False)
        self.select_cell((x, y+1), False)
        self.select_cell((x+1, y-1), False)
        self.select_cell((x+1, y), False)
        self.select_cell((x+1, y+1), False)
        
    # Hace visible el tablero
    def make_board_visible(self) -> None:
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.make_cell_visible((x, y))

    # Busca un grupo de ceros desde la celda (x,y), incluyendo la misma
    def find_group_of_zeros(self, coord: tuple[int, int]) -> None:
        x, y = coord

        def union(l1,l2):
            for i in l2:
                if i not in l1:
                    l1.append(i)
            return l1
        
        if not self.cell_has_zero(coord):
            return []
        coords0 = []
        coords0.extend(self.where_there_is_something_in_perimeter(0, coord))
        if len(coords0) > 0:
            k = 0
            i, j = coords0[0]#[0], coords0[1][1]
            while True:
                tmp = self.where_there_is_something_in_perimeter(0, (i, j))
                
                coords0 = union(coords0, tmp)
                k += 1
                if k == len(coords0):
                    break
                i, j = coords0[k]
        #print(f"coords0: {coords0}")
        return coords0
    
    # Quita la bandera de una celda
    def take_flag(self, coord: tuple[int, int]) -> None:
        x, y = coord
        if not self.board[y][x].is_visible:
            self.current_bombs += 1
            self.board[y][x].is_flagged = False
    
    # Coloca la bandera en una celda
    def put_flag(self, coord: tuple[int, int]) -> None:
        x, y = coord
        if not self.board[y][x].is_visible:
            self.current_bombs -= 1
            self.board[y][x].is_flagged = True

    def set_current_cell(self, coord: tuple[int, int]) -> None:
        if self.validate_cell(coord):
            self.current_cell = coord
            print(f"current_cell: {self.current_cell}")

    # Hace visible una celda
    def make_cell_visible(self, coord: tuple[int, int]) -> None:
        x, y = coord
        if not self.validate_cell(coord):
            return
        if not self.board[y][x].is_visible and not self.board[y][x].is_flagged:
            self.numeric_cells -= 1
            self.board[y][x].is_visible = True

    def validate_cell(self, coord: tuple[int, int]) -> bool:
        x, y = coord
        if x in range(0, self.width) and y in range(0, self.height):
            return True
        return False

    def validate_cell_perimeter(self, coord: tuple[int, int]) -> bool:
        x, y = coord
        if x in range(0+1, self.width-1) and y in range(0+1, self.height-1):
        #if int(x)-1 >= 0 and int(x)+1 < self.width and int(y)-1 >= 0 and int(y)+1 < self.height:
            return True
        return False

    # Hace visible la zona que rodea a la celda (x,y). No incluye la celda (x,y)
    def make_perimeter_visible(self, coord: tuple[int, int]) -> None:
        x, y = coord
        #if self.validate_cell_perimeter(x, y):
        self.make_cell_visible((x-1, y-1))
        self.make_cell_visible((x-1, y))
        self.make_cell_visible((x-1, y+1))
        self.make_cell_visible((x, y-1))
        self.make_cell_visible((x, y+1))
        self.make_cell_visible((x+1, y-1))
        self.make_cell_visible((x+1, y))
        self.make_cell_visible((x+1, y+1))

    def __str__(self) -> str:
        string = ""

        up = " "+" "*len(str(self.height)) + "  "
        for x in range(97, 97+self.width):
            up += chr(x) + " "
        up += "\n " + " "*len(str(self.height)) + "  "
        for x in range(0, self.width):
           up+= "| "
        string += up + "\n"
        
        for y in range(0, self.height):
            left = str(y+1) + " "*(1+len(str(self.height))-len(str(y+1))) + "- "
            string += left
            for x in range(0, self.width):
                if (x,y) == self.current_cell:
                    string += colors["azul"] 
                string += str(self.board[y][x]) + " "
                if (x,y) == self.current_cell:
                    string += colors["reset"] 
            right = "-" + " "*(1+len(str(self.height))-len(str(y+1))) + str(y+1)
            string += right + "\n"

        down = " "+" "*len(str(self.height)) + "  "
        for x in range(0, self.width):
           down += "| "
        down += "\n " + " "*len(str(self.height)) + "  "
        for x in range(97, 97+self.width):
            down += chr(x) + " "
        string += down + "\n"
        
        string += f"\n\tbombas restantes: {self.current_bombs}\n"
        return string
    


class View():
    def __init__(self) -> None:
        pass
    
    def input(self) -> str:
        return input("Selecciona una celda, con formato [letra][numero] (ej: a3)\nSi marcas/desmarcas una flag, el formato es f [letra][numero] (ej: f a3): ")

    def error(self) -> None:
        print("Error: selecciona una celda válida")

    def print_board(self, board: Board) -> None:
        print(board)

    def lose(self) -> None:
        print("Perdiste! :P")

    def win(self) -> None:
        print("Ganaste! :D")

    def play_again(self) -> None:
        return input("¿Quieres jugar de nuevo? (s/n): ")


class Controller():
    def __init__(self, board: Board, view: View) -> None:
        self.board = board
        self.view = view
        
    def init_board(self) -> None:
        self.board.create_board()

    def main(self) -> None:
        self.init_board()
        while not (self.board.lose or self.board.win):
            self.view.print_board(self.board)
            input = kb.read_hotkey(False)
            print(f"input: {input}")
            if input in keys["up"]:
                self.board.current_cell = (self.board.current_cell[0], self.board.current_cell[1]-1)
            elif input in keys["down"]:
                self.board.current_cell = (self.board.current_cell[0], self.board.current_cell[1]+1)
            elif input in keys["left"]:
                self.board.current_cell = (self.board.current_cell[0]-1, self.board.current_cell[1])
            elif input in keys["right"]:
                self.board.current_cell = (self.board.current_cell[0]+1, self.board.current_cell[1])
            elif input in keys["shift"]:
                if self.board.cell_has_flag(self.board.current_cell):
                    self.board.take_flag(self.board.current_cell)
                else:
                    self.board.put_flag(self.board.current_cell)
            elif input == "enter":
                self.board.select_cell(self.board.current_cell)
        if self.board.lose:
            self.view.lose()
        if self.board.win:
            self.view.win()
        play_again = self.view.play_again()
        if play_again == "s":
            self.main()
        else:
            print("Adiós!")

    
    # def main1(self) -> None:
    #     self.init_board()
    #     while not self.board.lose and not self.board.win:
    #         self.view.print_board(self.board, self.board.height, self.board.width)
    #         user_input = self.view.input()
    #         try:
    #             flag, x, y = self.parse_input(user_input)
    #         except:
    #             self.view.error()
    #             continue
    #         if not self.validate_coord((x, y)):
    #             self.view.error()
    #             continue
    #         if flag:
    #             if self.board.cell_has_flag((x, y)):
    #                 self.board.take_flag((x, y))
    #             else:
    #                 self.board.put_flag((x, y))
    #         elif not flag:
    #             self.board.select_cell((x, y))
    #     self.view.print_board(self.board)
    #     if self.board.win:
    #         self.view.win()
    #     elif self.board.lose:    
    #         self.view.lose()
    #     play_again = self.view.play_again()
    #     if play_again == "s":
    #         self.main()
    #     else:
    #         print("Adiós!")

    def validate_coord(self, coord: tuple[int, int]) -> bool:
        x, y = coord
        if int(x) >= 0 and int(x) < self.board.width and int(y) >= 0 and int(y) < self.board.height:
            return True
        return False
        
    def parse_input(self, string) -> None:
        l = string.split(" ")
        flag = False
        if len(l) == 2:
            if l[0] == "f":
                flag = True 
            l.pop(0)
        xstr, ystr = "", ""
        for char in l[0]: 
            if char.isalpha():
                xstr += char
            elif char.isdigit():
                break
        for char in l[0][len(xstr):]:
            if char.isdigit():
                ystr += char
            elif char.isalpha():
                break
        xstr = ord(xstr[0])-97
        ystr = int(ystr)-1
        return flag, xstr, ystr

a = Board(conf["width"], conf["height"], conf["bombs"])
v = View()
c = Controller(a, v)
c.init_board()
c.main()
# a.select_cell(9,9)
# #a.assign_content()
# # # print(a.board[4][0])
# print(a.where_there_is_something_in_perimeter("0", 9, 9))
# print(a.where_there_is_something_in_perimeter("0", 8, 9))
# print(a.where_there_is_something_in_perimeter("0", 7, 9))
# print(a.find_group_of_zeros(9, 9))
# print(a)
#c.main()
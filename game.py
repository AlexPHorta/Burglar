import pilasengine
import random


screen_ancho, screen_alto = 1200, 1400

fps = 15

pilas = pilasengine.iniciar(ancho = screen_ancho, alto = screen_alto)

pilas.widget.fps.frecuencia = 1000 / fps


class WhiteStone(pilasengine.actores.Actor):

    def iniciar(self, x = 0, y = 0, z = 0, tag = None):
        self.imagen = "images/grid.png"
        self.x = x
        self.y = y
        self.z = z
        self.tag = str(tag)


class PauseButton(pilasengine.actores.Actor):

    def iniciar(self, x = 0, y = 0, z = 0, tag = None):
        self.imagen = "images/pause.png"
        self.x = x
        self.y = y
        self.z = z
        self.tag = str(tag)

        pilas.eventos.click_de_mouse.conectar(self.cuando_hace_click)

    def cuando_hace_click(x, y):
        pause_menu = GamePauseMenu(pilas, z = -10)
        pause_menu.transparencia = 20


class CloseButton(pilasengine.actores.Actor):
    
    def iniciar(self, x = 0, y = 0, z = 0, tag = None):
        self.imagen = "images/close.png"
        self.x = x
        self.y = y
        self.z = z
        self.tag = str(tag)

        pilas.eventos.click_de_mouse.conectar(self.cuando_hace_click)

    def cuando_hace_click(x, y):
        return True
        XXXXX

class Score(pilasengine.actores.Texto):

    def iniciar(self, texto = "", x = 0, y = 0, fuente = None, tag = None, anchor = 1):
        self.texto = str(texto)
        self.x = x
        self.y = y
        self.fuente = fuente
        self.tag = tag
        self.anchor = anchor
        self.ancho_ = None

    def update_score(self, texto):
        print "update_score in"
        self.texto = str(texto)
        if self.anchor == len(str(texto)):
            pass
        else:
            self.anchor = len(str(texto))
            self.ancho_ = self.obtener_ancho()
            if self.anchor > 1:
                self.x -= (self.ancho_) + (3 * self.anchor) # sloppy solution, research a better one, please.
        print self.anchor, self.ancho_, self.x
        print "update_score out"
        return


class MainMenu(pilasengine.escenas.Escena):

    def iniciar(self):
        nome = pilas.actores.Texto("Burglar", y = 100, magnitud = 48)
        version = pilas.actores.Texto("v. 0.1", magnitud = 24)
        autor = pilas.actores.Texto("Buey Studios", y = -30, magnitud = 24)
        menu = pilas.actores.Menu([('easy', self.facil), ('normal', self.normal), ('hard', self.hard), ('options', self.options), ('help', self.help)],y = -120)
        pass

    def facil(self):
        pilas.escenas.GameScreen()

    def normal(self):
        pilas.escenas.GameScreen()

    def hard(self):
        pilas.escenas.GameScreen()

    def options(self):
        pilas.escenas.OptionsScreen()

    def help(self):
        pilas.escenas.HelpScreen()

    def ejecutar(self):
        pass


class GamePauseMenu(pilasengine.actores.Actor):

    def iniciar(self, x = 0, y = 0, z = 0, tag = None):
        self.x = x
        self.y = y
        self.z = z
        self.tag = tag
        imagen_ = pilas.imagenes.cargar_superficie(screen_ancho, screen_alto)
        imagen_.pintar(pilas.colores.Color(0, 0, 0))
        self.imagen = imagen_
        self.close_button = CloseButton(pilas, x = -408, y = 550)
        self.close_button.escala = 0.7
        self.close_button.z = -11

    def atualizar(self):
        if self.close_button.quando_hace_click():
            self.eliminar()

    def ejecutar(self):
        pass


class GameScreen(pilasengine.escenas.Escena):

    def iniciar(self):
        self.game = GameEngine()

        # Generates the groups.
        self.inner_ring = pilas.actores.Grupo()
        self.middle_ring = pilas.actores.Grupo()
        self.outer_ring = pilas.actores.Grupo()

        # Each stone in its group
        self.inner_ring.agregar(WhiteStone(pilas, x = 70, y = 70, tag = "i0"))
        self.inner_ring.agregar(WhiteStone(pilas, x = 70, y = -70, tag = "i1"))
        self.inner_ring.agregar(WhiteStone(pilas, x = -70, y = -70, tag = "i2"))
        self.inner_ring.agregar(WhiteStone(pilas, x = -70, y = 70, tag = "i3"))
        self.middle_ring.agregar(WhiteStone(pilas, x = 99, y = 224, tag = "m0"))
        self.middle_ring.agregar(WhiteStone(pilas, x = 229, y = 95, tag = "m1"))
        self.middle_ring.agregar(WhiteStone(pilas, x = 229, y = -95, tag = "m2"))
        self.middle_ring.agregar(WhiteStone(pilas, x = 99, y = -224, tag = "m3"))
        self.middle_ring.agregar(WhiteStone(pilas, x = -99, y = -224, tag = "m4"))
        self.middle_ring.agregar(WhiteStone(pilas, x = -229, y = -95, tag = "m5"))
        self.middle_ring.agregar(WhiteStone(pilas, x = -229, y = 95, tag = "m6"))
        self.middle_ring.agregar(WhiteStone(pilas, x = -99, y = 224, tag = "m7"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 85, y = 396, tag = "o0"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 230, y = 338, tag = "o1"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 338, y = 230, tag = "o2"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 396, y = 85, tag = "o3"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 396, y = -85, tag = "o4"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 338, y = -230, tag = "o5"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 230, y = -338, tag = "o6"))
        self.outer_ring.agregar(WhiteStone(pilas, x = 85, y = -396, tag = "o7"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -85, y = -396, tag = "o8"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -230, y = -338, tag = "o9"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -338, y = -230, tag = "o10"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -396, y = -85, tag = "o11"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -396, y = 85, tag = "o12"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -338, y = 230, tag = "o13"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -230, y = 338, tag = "o14"))
        self.outer_ring.agregar(WhiteStone(pilas, x = -85, y = 396, tag = "o15"))
        
        self.game.bag()
        self.game.insert_stone()

        self.fill_rings(self.game.outer, self.outer_ring)
        self.fill_rings(self.game.middle, self.middle_ring)
        self.fill_rings(self.game.inner, self.inner_ring)

        pause_button = PauseButton(pilas, x = -408, y = 550)
        pause_button.escala = 0.7

        guia = pilas.imagenes.cargar_superficie(screen_ancho, screen_alto)
        guia.linea(0, 185, 1500, 185, pilas.colores.rojo, 2)
        guia.linea(1048, 0, 1048, 1500, pilas.colores.rojo, 2)
        guia_ = pilas.actores.Actor(imagen = guia)

        self.score_x = 395
        self.score_y = 544
        # self.score_sup = pilas.imagenes.cargar_superficie(500, 120)
        # self.score_sup.texto(str(self.game.points), magnitud = 72, color = pilas.colores.blanco)
        # self.score = pilas.actores.Actor(imagen = self.score_sup, x = self.score_x, y = self.score_y)
        # self.score.z = 0
        self.score = Score(pilas, str(self.game.points), fuente = "fonts/Multicolore.otf", x = self.score_x, y = self.score_y, magnitud = 78)
        self.score.update_score(self.game.points)

        pilas.eventos.pulsa_tecla.conectar(self.al_pulsar_tecla)

    def actualizar(self):
        pass

    def fill_rings(self, engine_ring, screen_ring):
        for indice, hole in enumerate(engine_ring):
            if engine_ring[indice] == 0:
                screen_ring[indice].imagen = "images/grid.png"
            elif engine_ring[indice] == 1:
                screen_ring[indice].imagen = "images/red_stone.png"
            elif engine_ring[indice] == 2:
                screen_ring[indice].imagen = "images/blue_stone.png"
            elif engine_ring[indice] == 3:
                screen_ring[indice].imagen = "images/green_stone.png"
            else:
                continue
        return

    def al_pulsar_tecla(self, tecla):
        if (tecla.codigo == 1) or (tecla.codigo == 2):
            self.game.where_to_turn(tecla.codigo)
            self.game.new_round()
            
            if self.game.current_bag == []:
                self.game.bag()
            
            self.game.insert_stone()
            
            self.fill_rings(self.game.outer, self.outer_ring)
            self.fill_rings(self.game.middle, self.middle_ring)
            self.fill_rings(self.game.inner, self.inner_ring)
            
            self.score.update_score(self.game.points)
            
            if self.game.game_over:
                self.game_over()
        else:
            pass
        return

    # def print_score(self):
    #     anchor = len(str(self.game.points))
    #     ancho_ = self.score.obtener_ancho()
    #     if anchor > 1:
    #         self.score.x -= (ancho_ * anchor) / 2
    #     self.score.definir_texto(str(self.game.points))
    #     return

    def game_over(self):
        over = pilas.actores.Texto("Game Over", y = 100, magnitud = 64)

    def ejecutar(self):
        pass


class GameEngine:

    def __init__(self):
        self.inner = [0, 0, 0, 0]
        self.middle = [0, 0, 0, 0, 0, 0, 0, 0]
        self.outer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._bag = []
        self._turn = None
        self._points = 0
        self.no_trades = False
        self.one_place_to_insert = False
        self.game_over = False

    def __str__(self):
        return "%s(direction: %r; inner: %r;middle: %r;outer: %r)" % (self.__class__, self._turn, self.inner, self.middle, self.outer)

    @property
    def inner(self):
        return self.inner

    @property
    def middle(self):
        return self.middle

    @property
    def outer(self):
        return self.outer

    @property
    def current_bag(self):
        return self._bag

    @property
    def points(self):
        return self._points

    def bag(self):
        colors = (1, 2, 3)
        self._bag = random.sample(colors, len(colors))
        return self.current_bag

    def insert_stone(self):
        ok = False
        where_to_insert = None
           
        while not ok:
            if self.inner.count(0) == 0:
                ok = True
            else:
                where_to_insert = random.randrange(4)
                if self.inner[where_to_insert] != 0:
                    continue
                else:
                    self.inner[where_to_insert] = self._bag.pop()
                    ok = True
        
        if max(self.inner.count(0), self.middle.count(0), self.outer.count(0)) == 0:
            self.game_over = True
        
        return where_to_insert

    def where_to_turn(self, direction):
        self._turn = direction
        return

    def turn(self, which_ring, turn_choice):
        if turn_choice == 1:
            retrieved = which_ring.pop(0)
            which_ring.append(retrieved)
        elif turn_choice == 2:
            retrieved = which_ring.pop()
            which_ring.insert(0, retrieved)
        return which_ring
    
    def trade_stones(self, external, internal, turn_direction):
        no_trades = True
        for place in enumerate(internal):
            if place[1] == 0:
                continue
            else:
                if turn_direction == 1:
                    if external[place[0] * 2] == 0:
                        external[place[0] * 2] = internal[place[0]]
                        internal[place[0]] = 0
                        no_trades = False
                    else:
                        continue
                elif turn_direction == 2:
                    if external[(place[0] * 2) + 1] == 0:
                        external[(place[0] * 2) + 1] = internal[place[0]]
                        internal[place[0]] = 0
                        no_trades = False
                    else:
                        continue
        return external, internal, no_trades

    def mark_for_clearing(self, ring):
        pick = 0
        stone = 0
        count = 0
        marked = []
        for index, stone_ in enumerate(ring * 2):
            if (ring.count(stone_) == len(ring)) and (stone_ != 0):
                marked.append((0, stone_, len(ring)))
                break
            if count >= 3 and stone_ != stone:
                marked.append((pick, stone, count))
            if stone_ == stone and stone_ != 0:
                count += 1
            elif stone_ != 0:
                pick, stone, count = index, stone_, 1
            elif stone_ == 0:
                pick, stone, count = 0, 0, 0
        marked = filter(lambda x: x[0] < len(ring), marked)
        if len(marked) != 0:
            first, last = marked[0], marked[-1]
            lgt = last[0] + last[2]
            diff = lgt - len(ring)
            if lgt - 1 >= len(ring):
                if first[0] == 0:
                    last = (last[0], last[1], (diff - 2))
                    marked.pop()
                    marked.append(last)
                else:
                    marked.insert(0, (0, last[1], (diff)))
                    marked.pop()
                    last = (last[0], last[1], last[2] - diff)
                    marked.append(last)
        else:
            pass
        return marked

    def clear_stones(self, ring):
        ring_intern = ring
        marked_for_clearing = self.mark_for_clearing(ring_intern)
        for index, color, lgt in marked_for_clearing:
            for _ in range(index, index + lgt):
                ring[_] = 0
        self._points += self.calc_points(marked_for_clearing)
        return ring

    def calc_points(self, mapping):
        points = 0
        for item in mapping:
            points += item[2] * 10
        return points
    
    def new_round(self):
        turn_choice = self._turn
        self.outer, self.middle, _ = self.trade_stones(self.outer, self.middle, turn_choice)
        self.outer = self.turn(self.outer, turn_choice)
        self.outer = self.clear_stones(self.outer)
        self.middle, self.inner, self.no_trades = self.trade_stones(self.middle, self.inner, turn_choice)
        self.middle = self.turn(self.middle, turn_choice)
        self.middle = self.clear_stones(self.middle)
        self.inner = self.turn(self.inner, turn_choice)
        return


class OptionsScreen(pilasengine.escenas.Escena):

    def iniciar(self):
        nome = pilas.actores.Texto("Options", y = 100, magnitud = 48)
        pass

    def ejecutar(self):
        pass


class HelpScreen(pilasengine.escenas.Escena):

    def iniciar(self):
        nome = pilas.actores.Texto("Help", y = 100, magnitud = 48)
        pass

    def ejecutar(self):
        pass


pilas.escenas.vincular(MainMenu)
pilas.escenas.vincular(GameScreen)
pilas.escenas.vincular(OptionsScreen)
pilas.escenas.vincular(HelpScreen)

pilas.escenas.MainMenu()

if __name__ == "__main__":
    pilas.ejecutar()


# Para testar
# antes __main__.GameEngine(direction: 1; inner: [2, 3, 1, 3];middle: [0, 3, 1, 1, 3, 2, 1, 2];outer: [0, 3, 1, 1, 3, 3, 2, 3, 2, 1, 1, 2, 1, 2, 3, 3]) 1
# antes __main__.GameEngine(direction: 1; inner: [3, 1, 2, 1];middle: [1, 1, 0, 1, 3, 1, 2, 3];outer: [2, 1, 3, 3, 0, 0, 0, 3, 3, 2, 2, 1, 1, 2, 2, 3]) 1
# antes __main__.GameEngine(direction: 1; inner: [0, 0, 2, 0];middle: [0, 0, 0, 0, 0, 0, 0, 3];outer: [0, 2, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 2, 3, 3, 0]) exception
# antes __main__.GameEngine(direction: 2; inner: [3, 2, 1, 2];middle: [2, 3, 1, 2, 1, 0, 1, 1];outer: [2, 2, 1, 2, 2, 1, 2, 3, 3, 1, 2, 1, 2, 1, 3, 1]) 1 exception
# antes __main__.GameEngine(direction: 2; inner: [1, 0, 0, 0];middle: [0, 3, 1, 0, 0, 0, 2, 0];outer: [3, 3, 1, 1, 0, 2, 3, 0, 0, 1, 1, 3, 2, 0, 2, 2]) 1 exception
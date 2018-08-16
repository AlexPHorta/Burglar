import pilasengine
import random

pilas = pilasengine.iniciar(ancho = 1200, alto = 1600)


class WhiteStone(pilasengine.actores.Actor):

    def iniciar(self, x = 0, y = 0, z = 0, tag = None):
        self.imagen = "images/grid.png"
        self.x = x
        self.y = y
        self.z = -1000
        self.tag = str(tag)


class RedStone(pilasengine.actores.Actor):
    
    def iniciar(self):
        self.imagen = "images/red_stone.png"
        self.z = -1000


class BlueStone(pilasengine.actores.Actor):
    
    def iniciar(self):
        self.imagen = "images/blue_stone.png"
        self.z = -1000


class GreenStone(pilasengine.actores.Actor):
    
    def iniciar(self):
        self.imagen = "images/green_stone.png"
        self.z = -1000


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


class GameScreen(pilasengine.escenas.Escena):

    def iniciar(self):
        self.game = GameEngine()

        # Generates the groups.
        self.inner_ring = pilas.actores.Grupo()
        self.middle_ring = pilas.actores.Grupo()
        self.outer_ring = pilas.actores.Grupo()

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

        pilas.eventos.pulsa_tecla.conectar(self.al_pulsar_tecla)

        #print "############################################"
        #for element in self.outer_ring:
            #print element.tag + " - " + str(element.imagen)
        #print "---"
        #for element in self.middle_ring:
            #print element.tag + " - " + str(element.imagen)
        #print "---"
        #for element in self.inner_ring:
            #print element.tag + " - " + str(element.imagen)
        #print "----------------------------"
        #print self.game.outer
        #print self.game.middle
        #print self.game.inner
        #print "+++++++++++++++++++++++++++++++++++++++++++"

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
            print str(tecla.codigo)
            self.game.where_to_turn(tecla.codigo)
            print "new round bf " + str(self.game.one_place_to_insert) + " - " + str(self.game.no_trades) + " - " + str(self.game.game_over)
            self.game.new_round()
            print "new round af " + str(self.game.one_place_to_insert) + " - " + str(self.game.no_trades) + " - " + str(self.game.game_over)
            
            if self.game.current_bag == []:
                self.game.bag()
            
            print "insert bf " + str(self.game.one_place_to_insert) + " - " + str(self.game.no_trades) + " - " + str(self.game.game_over)
            self.game.insert_stone()
            print "insert af " + str(self.game.one_place_to_insert) + " - " + str(self.game.no_trades) + " - " + str(self.game.game_over)
            
            self.fill_rings(self.game.outer, self.outer_ring)
            self.fill_rings(self.game.middle, self.middle_ring)
            self.fill_rings(self.game.inner, self.inner_ring)
            
            if self.game.game_over:
                self.game_over()
            
            #print "############################################"
            #for element in self.outer_ring:
                #print element.tag + " - " + str(element.imagen)
            #print "---"
            #for element in self.middle_ring:
                #print element.tag + " - " + str(element.imagen)
            #print "---"
            #for element in self.inner_ring:
                #print element.tag + " - " + str(element.imagen)
            #print "----------------------------"
            #print self.game.outer
            #print self.game.middle
            #print self.game.inner
            #print "+++++++++++++++++++++++++++++++++++++++++++"
        else:
            pass

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
        self.user_action = False
        self.refresh_rings = False
        self.no_trades = False
        self.one_place_to_insert = False
        self.game_over = False

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
    def ready_to_user_action(self):
        return self.user_action

    @property
    def ready_to_refresh_rings(self):
        return self.refresh_rings

    def bag(self):
        colors = (1, 2, 3)
        self._bag = random.sample(colors, len(colors))
        return self.current_bag

    def insert_stone(self):
        
        ok = False
        where_to_insert = None
        
        #if self.inner.count(0) == 1:
            #self.one_place_to_insert = True
        #else:
            #self.one_place_to_insert = False
        
        while not ok:
            where_to_insert = random.randrange(4)
            if self.inner[where_to_insert] != 0:
                continue
            else:
                self.inner[where_to_insert] = self._bag.pop()
                ok = True
        
        if max(self.inner.count(0), self.middle.count(0), self.outer.count(0)) == 0:
            self.game_over = True
        #if self.no_trades and self.one_place_to_insert:
            #self.game_over = True
        #else:
            #pass
        
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

    def clear_stones(self, ring):
        ring_intern = ring
        marked_for_clearing = self.mark_for_clearing(ring_intern)
        #print "marked_for_clearing" + str(marked_for_clearing)
        for index, color in sorted(marked_for_clearing.keys()):
            if index > 15:
                continue
            elif (index + marked_for_clearing[(index, color)]) > len(ring):
                count = marked_for_clearing[(index, color)]
                for _ in range(index, len(ring)):
                    ring[_] = 0
                    count -= 1
                for _ in range(0, count):
                    ring[_] = 0
            else:
                for _ in range(index, (index + marked_for_clearing[(index, color)])):
                    ring[_] = 0
        return ring

    def mark_for_clearing(self, ring):
        counter = 0
        pick = (None, None)
        clearing = {}
        for place, stone in enumerate(ring * 2):
            #print "clearing" + str(clearing)
            #print str(pick) + " - " + str(counter)
            if stone == 0:
                counter = 0
                pick = (None, None)
            elif pick[1] == None:
                pick = (place, stone)
                counter += 1
            elif stone == pick[1]:
                counter += 1
            elif stone != pick[1]:
                pick = (place, stone)
                counter = 1
            if counter >= 3:
                clearing[pick] = counter
        return clearing
    
    def new_round(self):
        
        turn_choice = self._turn
        self.outer = self.turn(self.outer, turn_choice)
        self.outer, self.middle, _ = self.trade_stones(self.outer, self.middle, turn_choice)
        self.outer = self.clear_stones(self.outer)
        self.middle = self.turn(self.middle, turn_choice)
        self.middle, self.inner, self.no_trades = self.trade_stones(self.middle, self.inner, turn_choice)
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


pilas.actores.vincular(RedStone)
pilas.actores.vincular(BlueStone)
pilas.actores.vincular(GreenStone)

pilas.escenas.vincular(MainMenu)
pilas.escenas.vincular(GameScreen)
pilas.escenas.vincular(OptionsScreen)
pilas.escenas.vincular(HelpScreen)

pilas.escenas.MainMenu()

if __name__ == "__main__":
    pilas.ejecutar()

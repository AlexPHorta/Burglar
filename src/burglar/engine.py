#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import random


class GameEngine_Easy:
    """Define the game logic in the easy mode."""

    def __init__(self,
        inner = None,
        middle = None,
        outer = None,
        big_outer = None,
        bag = [],
        points = 0,
        no_trades = False,
        one_place_to_insert = False,
        game_over = False
        ):
        """Initialize the game engine.

        Keyword arguments:
            inner -- The inner ring. A List with four integers.
            middle -- The middle ring. A List with eight integers.
            outer -- The small outer ring. A List with sixteen integers.
            big_outer -- The big outer ring. A List with thirty two integers.
            bag -- The bag with the stones from a specific round. A List with integers.
            points -- The number of points. An integer.
            no_trades -- Whether there are trades to be made or not. A boolean.
            one_place_to_insert -- Whether there's only one place to insert a stone
                in the inner ring. A boolean.
            game_over -- Whether the game is over or not. A boolean.
        """
        if inner is None:
            self.inner_ring = [0] * 4
        else:
            self.inner_ring = inner
        if middle is None:
            self.middle_ring = [0] * 8
        else:
            self.middle_ring = middle
        if outer is None:
            self.outer_ring = [0] * 16
        else:
            self.outer_ring = outer
        if big_outer is None:
            self.big_outer_ring = [0] * 32
        else:
            self.big_outer_ring = outer
        self._bag = bag
        self.colors = {1, 2, 3}
        self.matches = (3, 3, 3)
        self._turn = None
        self.points = points
        self.no_trades = no_trades
        self.one_place_to_insert = one_place_to_insert
        self.game_over = game_over
        self.blanks = sum(map(len, (
            self.inner_ring,
            self.middle_ring,
            self.outer_ring,
            self.big_outer_ring,)))

    def __str__(self):
        return "%s(direction: %r; inner: %r;middle: %r;outer: %r)" % (self.__class__,
            self._turn, self.inner, self.middle, self.outer)

    def get_state(self):
        return "inner = %r, middle = %r, outer = %r, bag = %r, points = %r, \
        no_trades = %r, one_place_to_insert = %r, game_over = %r" % (self.inner, \
            self.middle, self.outer, self._bag, self.points, self.no_trades, \
            self.one_place_to_insert, self.game_over)

    @property
    def inner(self):
        return self.inner_ring

    @property
    def middle(self):
        return self.middle_ring

    @property
    def outer(self):
        return self.outer_ring

    @property
    def big_outer(self):
        return self.big_outer_ring

    def bag(self):
        """Pick a stone from the bag and return it."""
        try:
            assert len(self._bag) > 0
        except AssertionError:
            self._bag = random.sample(self.colors, len(self.colors))
        finally:
            return self._bag.pop()

    def check_game_over(self):
        """Check if the game is over."""
        done = True if self.blanks == 0 else False
        self.game_over = done

    def insert_stone(self):
        """Insert a stone in an empty place in the inner ring."""
        done = False
        where_to_insert = None

        while not done:
            if self.inner.count(0) == 0:
                done = True
            else:
                where_to_insert = self.place_to_insert()
                if self.inner[where_to_insert] != 0:
                    continue
                else:
                    self.inner[where_to_insert] = self.bag()
                    self.blanks -= 1
                    done = True

        self.check_game_over()

        return where_to_insert

    def place_to_insert(self):
        """Pick a random place to insert a stone in the inner ring.

        Called by insert_stone."""
        return random.randrange(len(self.inner))

    def where_to_turn(self, direction):
        """Change the direction to turn the rings.

        Positional arguments:
        direction -- The direction to turn the ring (clockwise or
            counter-clockwise). An integer.
        """
        self._turn = direction

    def turn(self, which_ring, turn_choice):
        """Shift the position of the stones in one ring.

        Positional arguments:
        which_ring -- Which of the rings to turn. A list (one of the ring
            attributes).
        turn_choice -- The direction to turn the ring (clockwise or
            counter-clockwise). An integer.
        """
        if turn_choice == 1:
            retrieved = which_ring.pop(0)
            which_ring.append(retrieved)
        elif turn_choice == 2:
            retrieved = which_ring.pop()
            which_ring.insert(0, retrieved)
        return which_ring

    def trade_stones(self, external, internal, turn_direction):
        """Trade the stones from an internal to an external ring, at the end of
        the round.

        Positional arguments:
        external -- The external ring (where the stones will be placed). A list
            (one of the ring attributes).
        internal -- The internal ring (from where the stones are retrieved).
            A list (one of the ring attributes).
        turn_direction -- The direction to turn the ring (clockwise or
            counter-clockwise). An integer.
        """
        external_ = external
        internal_ = internal
        no_trades = True
        for index, stone in enumerate(internal):
            if stone == 0:
                continue
            else:
                if turn_direction == 1:
                    if external_[index * 2] == 0:
                        external_[index * 2] = internal_[index]
                        internal_[index] = 0
                        no_trades = False
                    else:
                        continue
                elif turn_direction == 2:
                    if external_[(index * 2) + 1] == 0:
                        external_[(index * 2) + 1] = internal_[index]
                        internal_[index] = 0
                        no_trades = False
                    else:
                        continue
        return external_, internal_, no_trades

    def mark_for_clearing(self, ring):
        pick = 0
        stone = 0
        count = 0
        marked = []
        for index, stone_ in enumerate(ring * 2):
            if (ring.count(stone_) == len(ring)) and (stone_ != 0):
                marked.append((0, stone_, len(ring)))
                break
            if self.mark_matches(count, stone_, stone):
                marked.append((pick, stone, count))
            if stone_ == stone and stone_ != 0:
                count += 1
            elif stone_ != 0:
                pick, stone, count = index, stone_, 1
            elif stone_ == 0:
                pick, stone, count = 0, 0, 0

        marked = list(filter(lambda x: x[0] < len(ring), marked))

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

    def mark_matches(self, count, actual, ref):
        if actual == ref: return False
        return count >= 3 and actual != ref

    def clear_stones(self, ring):
        ring_intern = ring
        marked_for_clearing = self.mark_for_clearing(ring_intern)
        for index, color, lgt in marked_for_clearing:
            for _ in range(index, index + lgt):
                ring[_] = 0
        self.points += self.calc_points(marked_for_clearing)
        return ring

    def calc_points(self, mapping):
        multiplier = 10
        points = 0
        for item in mapping:
            clearedStones = item[2]
            points += clearedStones * multiplier
            self.blanks += clearedStones
        return points

    def new_round(self):
        turn_choice = self._turn
        self.big_outer_ring, self.outer_ring, dummy_ = self.trade_stones(
            self.big_outer, self.outer, turn_choice)
        self.big_outer_ring = self.turn(self.big_outer, turn_choice)
        self.big_outer_ring = self.clear_stones(self.big_outer)
        self.outer_ring, self.middle_ring, self.no_trades = self.trade_stones(
            self.outer, self.middle, turn_choice)
        self.outer_ring = self.turn(self.outer, turn_choice)
        self.outer_ring = self.clear_stones(self.outer)
        self.middle_ring, self.inner_ring, self.no_trades = self.trade_stones(
            self.middle, self.inner, turn_choice)
        self.middle_ring = self.turn(self.middle, turn_choice)
        self.middle_ring = self.clear_stones(self.middle)
        self.inner_ring = self.turn(self.inner, turn_choice)
        return


class GameEngine_Normal(GameEngine_Easy):

    def __init__(self):
        super().__init__()
        self.colors = {1, 2, 5}

    def mark_matches(self, count, actual, ref):
        # print(f'Count: {count}, Actual: {actual}, Ref: {ref}')
        if actual == ref: return False
        if ref == 5:
            return count >= 4 and actual != ref
        else:
            return count >= 3 and actual != ref


class GameEngine_Hard(GameEngine_Easy):

    def __init__(self):
        super().__init__()
        colors1_4 = (1, 2, 3, 4)
        colors3_4 = (1, 2, 3)
        self.colors = colors1_4 + colors3_4 + colors3_4 + colors3_4

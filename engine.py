#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Burglar: a game of stones
#
#    Copyright 2018 - Alexandre Paloschi Horta
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Website - http://www.buey.net.br/burglar


import random

from collections import deque
from itertools import chain, repeat


class GameEngine_Easy:

    def __init__(self, inner = None, middle = None, outer = None, bag = None,
        points = 0, no_trades = False, one_place_to_insert = False, game_over = False):
        if not inner:
            self.inner_ring = deque([0, 0, 0, 0])
        else:
            self.inner_ring = inner
        if not middle:
            self.middle_ring = deque([0, 0, 0, 0, 0, 0, 0, 0])
        else:
            self.middle_ring = middle
        if not outer:
            self.outer_ring = deque([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        else:
            self.outer_ring = outer
        if not outer:
            self.big_outer_ring = deque([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        else:
            self.big_outer_ring = outer
        if bag == None:
            self._bag = []
        else: self._bag = bag
        self._turn = None
        self._points = points
        self.no_trades = no_trades
        self.one_place_to_insert = one_place_to_insert
        self.game_over = game_over

    def __str__(self):
        return "%s(direction: %r; inner: %r;middle: %r;outer: %r)" % (self.__class__,
            self._turn, self.inner, self.middle, self.outer)

    def get_state(self):
        return "inner = %r, middle = %r, outer = %r, bag = %r, points = %r, \
        no_trades = %r, one_place_to_insert = %r, game_over = %r" % (self.inner, \
            self.middle, self.outer, self._bag, self._points, self.no_trades, \
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

        if max(self.inner.count(0), self.middle.count(0), self.outer.count(0), \
            self.big_outer.count(0)) == 0:
            self.game_over = True

        return where_to_insert

    def where_to_turn(self, direction):
        self._turn = direction
        return

    def turn(self, which_ring, turn_choice):
        if turn_choice == 1:
            which_ring.rotate(-1)
            # retrieved = which_ring.popleft()
            # which_ring.append(retrieved)
        elif turn_choice == 2:
            which_ring.rotate(1)
            # retrieved = which_ring.pop()
            # which_ring.appendleft(retrieved)
        return which_ring

    def trade_stones(self, external, internal, turn_direction):
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
        # times = 1 if ring[0] == 0 or ring[-1] == 0 or ring[0] == ring[1] else 2
        for index, stone_ in enumerate(chain.from_iterable(repeat(tuple(ring), 2))):
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
            points += (item[2] ** 2) * 5
        return points

    def new_round(self):
        turn_choice = self._turn
        self.big_outer_ring, self.outer_ring, dummy_ = self.trade_stones(self.big_outer, self.outer, turn_choice)
        self.big_outer_ring = self.turn(self.big_outer, turn_choice)
        self.big_outer_ring = self.clear_stones(self.big_outer)
        self.outer_ring, self.middle_ring, self.no_trades = self.trade_stones(self.outer, self.middle, turn_choice)
        self.outer_ring = self.turn(self.outer, turn_choice)
        self.outer_ring = self.clear_stones(self.outer)
        self.middle_ring, self.inner_ring, self.no_trades = self.trade_stones(self.middle, self.inner, turn_choice)
        self.middle_ring = self.turn(self.middle, turn_choice)
        self.middle_ring = self.clear_stones(self.middle)
        self.inner_ring = self.turn(self.inner, turn_choice)
        return


class GameEngine_Normal(GameEngine_Easy):

    def __init__(self):
        super().__init__()

    def bag(self):
        colors = (1, 2, 5)
        self._bag = random.sample(colors, len(colors))
        return self.current_bag

    def mark_for_clearing(self, ring):
        pick = 0
        stone = 0
        count = 0
        marked = []
        times = 1 if ring[0] == 0 or ring[-1] == 0 or ring[0] == ring[1] else 2
        for index, stone_ in enumerate(chain.from_iterable(repeat(tuple(ring), times))):
            if (ring.count(stone_) == len(ring)) and (stone_ != 0):
                marked.append((0, stone_, len(ring)))
                break
            if stone == 5:
                if count >= 4 and stone_ != stone:
                    marked.append((pick, stone, count))
            else:
                if count >= 3 and stone_ != stone:
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


class GameEngine_Hard(GameEngine_Easy):

    def __init__(self):
        super().__init__()

    def bag(self):
        colors3 = (1, 2, 3)
        colors1 = (1, 2, 3, 4)
        for b in (colors3, colors3, colors3, colors1):
            self._bag.extend(random.sample(b, len(b)))
        return self.current_bag
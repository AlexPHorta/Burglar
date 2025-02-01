import pytest

from src.burglar.engine import GameEngine_Easy


class TestGameEngine_Easy:

    @pytest.fixture(scope = 'function')
    def easy(self):
        return GameEngine_Easy()

    def testInstantiationNoParams(self, easy):
        assert easy._bag == []
        assert easy._turn is None
        assert easy._points == 0
        assert easy.no_trades is False
        assert easy.one_place_to_insert is False
        assert easy.game_over is False
        assert easy.inner_ring == [0] * 4
        assert easy.middle_ring == [0] * 8
        assert easy.outer_ring == [0] * 16
        assert easy.big_outer_ring == [0] * 32
        assert easy._start_places == 4
        assert easy.colors == {1, 2, 3}
        assert easy.matches == (3, 3, 3)
        assert easy.blanks == 60
        assert easy.inner == easy.inner_ring
        assert easy.middle == easy.middle_ring
        assert easy.outer == easy.outer_ring
        assert easy.big_outer == easy.big_outer_ring

    def test__str__(self, easy):
        assert str(easy) == "<class 'src.burglar.engine.GameEngine_Easy'>(direction: None; inner: [0, 0, 0, 0];middle: [0, 0, 0, 0, 0, 0, 0, 0];outer: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];big_outer: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])"

    def test_get_state_empy_engine(self, easy):
        assert easy.get_state() == ('inner = [0, 0, 0, 0], '
                                    'middle = [0, 0, 0, 0, 0, 0, 0, 0], '
                                    'outer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '
                                    '0, 0, 0, 0, 0], big_outer = [0, 0, 0, 0, '
                                    '0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '
                                    '0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
                                    'bag = [], points = 0, no_trades = False, '
                                    'one_place_to_insert = False, game_over = False')

    def test_bag(self, easy):
        raffle = []
        assert len(easy._bag) == 0
        for i in range(len(easy.colors)):
            raffle.append(easy.bag())
        assert sorted(raffle) == sorted(easy.colors)
        assert len(easy._bag) == 0

    def test_check_game_over(self, easy):
        assert easy.game_over is False
        easy.blanks = 0
        assert easy.game_over is False
        easy.check_game_over()
        assert easy.game_over is True

    def test_place_to_insert(self, easy):
        p = easy._start_places
        assert 0 <= easy.place_to_insert(p) <= p

    def test_place_to_insert_wrong(self, easy):
        cases = (3, 5, "4", [4])
        for case in cases:
            with pytest.raises(ValueError):
                easy.place_to_insert(case)

    def test_insert_stone_empty(self, easy, monkeypatch):
        easy.inner_ring = [0, 0, 0, 0]
        monkeypatch.setattr("random.choice", lambda x: 2)
        monkeypatch.setattr(easy, "bag", lambda: 1)
        assert easy.blanks == 60
        assert easy.bag() == 1
        assert easy.insert_stone() == 2
        assert easy.inner_ring == [0, 0, 1, 0]
        assert easy.blanks == 59

    def test_insert_stone_full(self, easy, monkeypatch):
        monkeypatch.setattr(easy, "inner_ring", [0, 3, 2, 1])
        monkeypatch.setattr(easy, "blanks", 1) 
        monkeypatch.setattr("random.choice", lambda x: 0)
        monkeypatch.setattr(easy, "bag", lambda: 3)
        assert easy.bag() == 3
        assert easy.insert_stone() == 0
        assert easy.inner_ring == [3, 3, 2, 1]
        assert easy.game_over is True

    def test_where_to_turn(self, easy):
        easy.where_to_turn(1)
        assert easy._turn == 1
        easy.where_to_turn(2)
        assert easy._turn == 2
        with pytest.raises(ValueError):
            easy.where_to_turn(3)

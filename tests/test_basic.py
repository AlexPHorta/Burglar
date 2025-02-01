import pytest

from src.burglar.engine import GameEngine_Easy


class TestGameEngine_Easy:

    @pytest.fixture(scope = 'class')
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

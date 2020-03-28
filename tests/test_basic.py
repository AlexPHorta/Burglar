import pytest

from ..engine import GameEngine_Easy


class TestGameEngine_Easy:

    @pytest.fixture(scope = 'class')
    def easy(self):
        return GameEngine_Easy()

    def testInstantiation(self, easy):
        assert easy._bag is None
        assert easy._turn is None
        assert easy._points == 0
        assert easy.no_trades is False
        assert easy.one_place_to_insert is False
        assert easy.game_over is False
        assert easy.inner_ring == [0] * 4
        assert easy.middle_ring == [0] * 8
        assert easy.outer_ring == [0] * 16
        assert easy.big_outer_ring == [0] * 32
        assert easy.blanks == 60

    # def testBag(self, easy):
    #     bag = easy.bag()
    #     assert bag.sort() is None
    #     assert sorted(easy.current_bag) == [1, 2, 3]

    @pytest.fixture()
    def insertStoneInitial(self):
        pass

    def testInsertStoneInitial(self, easy):
        easy.inner_ring = [0, 0, 0, 0]
        easy._bag = [2, 1, 3]

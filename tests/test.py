from datetime import datetime, timedelta

import pytest

from src import main


class TestIsNotAliveIndex:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, monkeypatch):
        monkeypatch.setenv("MAX_INDEX_AGE_DAYS", "30")
        main.now = datetime.now()

    def test_not_alive(self):
        """ 寿命を1日超えた場合
        """
        epoch_millsec_31day = str(
            int((main.now - timedelta(days=31)).timestamp()) * 1000)
        property = {"aliases": {"test": {}}, "settings": {
            "index": {"creation_date": epoch_millsec_31day}}}

        assert main.is_not_alive_index(property)

    def test_alive(self):
        """ 寿命の日だった場合
        """
        epoch_millsec_30day = str(
            int((main.now - timedelta(days=30)).timestamp()) * 1000)
        property = {"aliases": {"test": {}}, "settings": {
            "index": {"creation_date": epoch_millsec_30day}}}

        assert not main.is_not_alive_index(property)


class TestIsDeletableIndex:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, monkeypatch):
        monkeypatch.setenv("MAX_INDEX_AGE_DAYS", "30")
        main.now = datetime.now()
        self.epoch_millsec_100day: str = str(
            int((main.now - timedelta(days=100)).timestamp()) * 1000)

    def test_has_default_index(self):
        """ defaultのindexだった場合
        """
        property = {"aliases": {}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert not main.is_deletable_index(".test", property)
        assert main.is_deletable_index("t.est", property)
        assert main.is_deletable_index("test.", property)

    def test_has_alias(self):
        """ aliasと紐づくindexだった場合
        """
        property = {"aliases": {"test": {}}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert not main.is_deletable_index("test", property)

    def test_without_alias(self):
        """ aliasを持たないindexだった場合
        """
        property = {"aliases": {}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert main.is_deletable_index("test", property)

    def test_has_index_excluded(self):
        """ 除外indexがある場合
        """
        main.excluded_indicies = ["test1"]
        property = {"aliases": {}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert not main.is_deletable_index("test1", property)
        assert main.is_deletable_index("test2", property)

    def test_have_indicies_excluded(self):
        """ 除外indexが複数ある場合
        """
        main.excluded_indicies = ["test1", "test2"]
        property = {"aliases": {}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert not main.is_deletable_index("test1", property)
        assert not main.is_deletable_index("test2", property)
        assert main.is_deletable_index("test3", property)

    def test_without_excluded_indicies(self):
        """ 除外indexがない場合
        """
        main.excluded_indicies = []
        property = {"aliases": {}, "settings": {
            "index": {"creation_date": self.epoch_millsec_100day}}}

        assert main.is_deletable_index("test1", property)
        assert main.is_deletable_index("test2", property)

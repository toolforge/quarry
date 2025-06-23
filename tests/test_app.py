from mock_alchemy.mocking import UnifiedAlchemyMagicMock

from quarry.web.models.query import Query
from quarry.web.models.queryrevision import QueryRevision
from quarry.web.models.queryrun import QueryRun
from quarry.web.models.user import User


class TestApp:
    def test_frontpage(self, mocker, client):
        self.db_session = UnifiedAlchemyMagicMock()

        # Homepage shows statistics
        for user_id in range(5):
            self.db_session.add(User(id=user_id))
            for query_id in range(3):
                self.db_session.add(Query(id=query_id, user_id=user_id))
                for queryrev_id in range(3):
                    self.db_session.add(
                        QueryRevision(id=queryrev_id, query_id=query_id)
                    )
                    for queryrun_id in range(3):
                        self.db_session.add(
                            QueryRun(id=queryrun_id, query_rev_id=queryrev_id)
                        )

        mocker.patch(
            "quarry.web.connections.Connections.session",
            new_callable=mocker.PropertyMock(return_value=self.db_session),
        )

        response = client.get("/")
        print(response.__dict__)
        assert response.status_code == 200
        assert response.data
        assert "5 users" in response.data.decode("utf8")
        assert f"{5 * 3 * 3 * 3} queries" in response.data.decode("utf8")

    def test_robots_txt(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
        assert "User-Agent: *" in response.data.decode("utf8")

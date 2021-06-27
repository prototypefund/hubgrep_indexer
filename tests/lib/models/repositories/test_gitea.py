import pytest

from hubgrep_indexer.models.repositories.gitea import GiteaRepository
from hubgrep_indexer import db

gitea_results = [
    {
        "id": 2,
        "owner": {
            "id": 5,
            "login": "codi.cooperatiu",
            "full_name": "",
            "email": "",
            "avatar_url": "http://gitea.codi.coop/avatars/a89a876bb0456b115c77dbee684d409b",
            "username": "codi.cooperatiu",
        },
        "name": "codi-theme",
        "full_name": "codi.cooperatiu/codi-theme",
        "description": "",
        "empty": False,
        "private": False,
        "fork": False,
        "parent": None,
        "mirror": False,
        "size": 5188,
        "html_url": "http://gitea.codi.coop/codi.cooperatiu/codi-theme",
        "ssh_url": "root@gitea.codi.coop:codi.cooperatiu/codi-theme.git",
        "clone_url": "http://gitea.codi.coop/codi.cooperatiu/codi-theme.git",
        "website": "",
        "stars_count": 0,
        "forks_count": 0,
        "watchers_count": 3,
        "open_issues_count": 0,
        "default_branch": "master",
        "created_at": "2018-01-25T18:52:35Z",
        "updated_at": "2019-05-20T18:55:46Z",
        "permissions": {"admin": False, "push": False, "pull": True},
    },
    {
        "id": 3,
        "owner": {
            "username": "tester",
        },
        "name": "testrepo",
        "description": "",
        "empty": False,
        "private": False,
        "fork": False,
        "parent": None,
        "mirror": False,
        "size": 5188,
        "website": "",
        "stars_count": 0,
        "forks_count": 0,
        "watchers_count": 3,
        "open_issues_count": 0,
        "default_branch": "master",
        "created_at": "2018-01-25T18:52:35Z",
        "updated_at": "2019-05-20T18:55:46Z",
    },
]


class TestGiteaRepository:
    def test_add_from_dict(self, test_app, test_client, hosting_service):
        with test_app.app_context():
            repo = GiteaRepository.from_dict(hosting_service.id, gitea_results[0])
            db.session.add(repo)
            db.session.commit()

            assert GiteaRepository.query.count() == 1
            assert repo.gitea_id == 2

    def test__get_repo_list_chunks(self, test_app, test_client, hosting_service):
        with test_app.app_context():
            repo_0 = GiteaRepository.from_dict(hosting_service.id, gitea_results[0])
            repo_1 = GiteaRepository.from_dict(hosting_service.id, gitea_results[1])
            db.session.add(repo_0)
            db.session.add(repo_1)
            db.session.commit()

            generator = GiteaRepository._yield_repo_list(chunk_size=1)
            item = next(generator)
            print(item)
            assert item['hosting_service_id'] == hosting_service.id
            item_1_id = item["gitea_id"]

            item = next(generator)
            item_2_id = item["gitea_id"]
            assert item_1_id != item_2_id

            # iterator ends after two repos
            with pytest.raises(StopIteration):
                item = next(generator)

    def test_export_to_file(self, test_app, test_client, hosting_service):
        import tempfile
        import os
        import shutil
        import pathlib

        with test_app.app_context():
            repo = GiteaRepository.from_dict(hosting_service.id, gitea_results[0])
            db.session.add(repo)
            db.session.commit()
            filename = "testfile"
            with tempfile.TemporaryDirectory() as tempdir:
                GiteaRepository.export_json_gz(
                    hosting_service.id, filename, results_base_path=tempdir
                )
                filepath = pathlib.Path(tempdir).joinpath(filename)
                assert filepath.stat().st_size != 0

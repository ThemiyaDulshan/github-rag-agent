from app.repository_tools import (
    get_repository_structure,
    get_file,
)

from app.code_search import search_code

from app.definition_lookup import find_definitions

from app.reference_lookup import find_references


class RepositoryTools:
    def __init__(self, repository_path: str):
        self.repository_path = repository_path

    def repository_structure(
        self,
        max_depth: int = 4
    ) -> str:
        return get_repository_structure(
            self.repository_path,
            max_depth
        )

    def file_lookup(
        self,
        file_path: str
    ) -> dict:
        return get_file(
            self.repository_path,
            file_path
        )

    def code_search(
        self,
        query: str,
        max_results: int = 50
    ) -> list[dict]:
        return search_code(
            self.repository_path,
            query,
            max_results
        )

    def definition_lookup(
        self,
        name: str,
        definition_type: str | None = None
    ) -> list[dict]:
        return find_definitions(
            self.repository_path,
            name,
            definition_type
        )

    def reference_lookup(
        self,
        name: str,
        max_results: int = 50
    ) -> list[dict]:
        return find_references(
            self.repository_path,
            name,
            max_results
        )
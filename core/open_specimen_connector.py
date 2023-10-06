import os
from dataclasses import dataclass, fields
from typing import List

import requests


@dataclass
class ParsedRow:
    participant_ppid: str
    participant_date_of_birth: str
    participant_gender: str
    specimen_type: str
    specimen_collection_status: str
    specimen_creation_time: str
    specimen_id: str

    def has_no_empty_fields(self):
        field_names = [field.name for field in fields(self)]
        return all(
            getattr(self, field_name) is not None and getattr(self, field_name) != ""
            for field_name in field_names
        )


class OpenSpecimenConnector:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        query_id: str,
        query_mapping: dict,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.query_id = query_id
        self.query_mapping = query_mapping

    def get_parsed_rows(self) -> List[ParsedRow]:
        token = self._get_auth_token()
        result = self._query_result(auth_token=token, query_id=self.query_id)
        return result

    def _get_auth_token(self) -> str:
        # TODO: Ideally we should point to UCY certificate instead, instead of using verify=False
        r = requests.post(
            url=self._url("/rest/ng/sessions"),
            json={
                "loginName": self.username,
                "password": self.password,
                "domainName": "openspecimen",
            },
            verify=False,
        )
        response_json = r.json()
        if "token" not in response_json:
            raise Exception("Could not get auth token for OpenSpecimen API")
        return response_json["token"]

    def _query_result(self, auth_token: str, query_id: str) -> List[ParsedRow]:
        r = requests.post(
            url=self._url(f"/rest/ng/query/{query_id}"),
            headers={"X-OS-API-TOKEN": auth_token},
            json={"startAt": 0, "maxResults": 100000},
            verify=False,
        )
        response_json = r.json()
        cleaned_rows = list(
            map(
                lambda row: ParsedRow(
                    participant_ppid=row[self.query_mapping["participant_ppid"]],
                    participant_gender=row[self.query_mapping["participant_gender"]],
                    participant_date_of_birth=row[
                        self.query_mapping["participant_date_of_birth"]
                    ],
                    specimen_type=row[self.query_mapping["specimen_type"]],
                    specimen_id=row[self.query_mapping["specimen_id"]],
                    specimen_collection_status=row[
                        self.query_mapping["specimen_collection_status"]
                    ],
                    specimen_creation_time=row[
                        self.query_mapping["specimen_creation_time"]
                    ],
                ),
                response_json["rows"],
            )
        )
        cleaned_rows = list(filter(lambda x: x.has_no_empty_fields(), cleaned_rows))
        return cleaned_rows

    def _url(self, path: str) -> str:
        return f"{self.host}{path}"

import datetime
import json
from dataclasses import dataclass, asdict

import requests
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference
from fhir.resources.specimen import Specimen, SpecimenCollection

from core.models import EtlConfiguration
from core.open_specimen_connector import OpenSpecimenConnector


@dataclass
class RunnerResults:
    patient_count: int
    specimen_count: int

    def to_dict(self):
        return asdict(self)


# Note: Useful code samples: https://community.intersystems.com/post/simple-example-fhir-client-python
class EtlRunner:
    def __init__(self, config: EtlConfiguration):
        self.config = config
        self.mapping_config = json.loads(config.mapping_config)
        self.extractor = OpenSpecimenConnector(
            host=config.open_specimen_host,
            username=config.open_specimen_user,
            password=config.open_specimen_pass,
            query_id=config.open_specimen_query_id,
            query_mapping=self.mapping_config["query_mapping"],
        )

    def run(self):
        specimen_type_mapping = self.mapping_config["specimen_type_mapping"]

        parsed_rows = self.extractor.get_parsed_rows()
        parsed_rows = list(
            filter(
                lambda x: x.specimen_type in specimen_type_mapping.keys(), parsed_rows
            )
        )
        parsed_rows = list(
            filter(lambda x: x.specimen_collection_status == "Collected", parsed_rows)
        )

        data = {
            "id": self.mapping_config["organization_id"],
            "active": True,
            "name": self.mapping_config["organization_name"],
        }
        org = Organization(**data)

        # Organization
        res = self._make_request(resource_name="Organization", resource=org)

        # Patients
        added_ids = set()
        patient_count = 0
        for parsed_row in parsed_rows:
            if parsed_row.participant_ppid in added_ids:
                continue

            p = Patient()
            p.id = parsed_row.participant_ppid
            p.birthDate = datetime.datetime.strptime(
                parsed_row.participant_date_of_birth, "%Y/%m/%d"
            ).date()
            # TODO: Check for valid gender values
            p.gender = parsed_row.participant_gender.lower()
            res = self._make_request(resource_name="Patient", resource=p)
            added_ids.add(p.id)
            print(res)
            if res.status_code == 200:
                patient_count += 1

        # Specimens
        added_ids = set()
        specimen_count = 0
        for parsed_row in parsed_rows:
            if parsed_row.specimen_id in added_ids:
                continue

            s = Specimen()

            reference = Reference()
            reference.reference = f"Patient/{parsed_row.participant_ppid}"
            s.subject = reference

            s.id = parsed_row.specimen_id
            coding = Coding()
            coding.system = "https://fhir.bbmri.de/CodeSystem/SampleMaterialType"
            coding.code = self.mapping_config["specimen_type_mapping"][
                parsed_row.specimen_type
            ]
            code = CodeableConcept()
            code.coding = [coding]
            s.type = code

            sc = SpecimenCollection()
            sc.collectedDateTime = datetime.datetime.strptime(
                parsed_row.specimen_creation_time, "%Y/%m/%d %H:%M"
            ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            s.collection = sc

            res = self._make_request(resource_name="Specimen", resource=s)
            added_ids.add(parsed_row.specimen_id)
            print(res)
            if res.status_code == 200:
                specimen_count += 1

        return RunnerResults(
            patient_count=patient_count,
            specimen_count=specimen_count,
        ).to_dict()

    def _make_request(self, resource_name: str, resource):
        # TODO: Handle error
        return requests.put(
            url=f"{self.config.bridgehead_host}/{resource_name}/{resource.id}",
            auth=(self.config.bridgehead_user, self.config.bridgehead_pass),
            data=resource.json(),
            headers={"Content-type": "application/json"},
            verify=False,
        )

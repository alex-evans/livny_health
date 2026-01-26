"""
Practitioner mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.practitioner import PractitionerORM
from resources.practitioner import Practitioner
from resources.core import HumanName, Gender, Identifier, ContactPoint, CodeableConcept


class PractitionerMapper(Mapper[Practitioner, PractitionerORM]):
    """Mapper for Practitioner <-> PractitionerORM conversion."""

    def to_orm(self, domain: Practitioner) -> PractitionerORM:
        """Convert Practitioner domain model to ORM."""
        return PractitionerORM(
            id=domain.id,
            name_family=domain.name.family,
            name_given=domain.name.given,
            name_prefix=domain.name.prefix,
            name_suffix=domain.name.suffix,
            gender=domain.gender.value,
            active=domain.active,
            identifiers=[
                {"system": i.system, "value": i.value} for i in domain.identifiers
            ],
            telecom=[
                {"system": t.system, "value": t.value, "use": t.use}
                for t in domain.telecom
            ],
            qualifications=[
                {"code": q.code, "display": q.display, "system": q.system}
                for q in domain.qualifications
            ],
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: PractitionerORM) -> Practitioner:
        """Convert PractitionerORM to Practitioner domain model."""
        return Practitioner(
            id=orm.id,
            name=HumanName(
                family=orm.name_family,
                given=orm.name_given or [],
                prefix=orm.name_prefix or [],
                suffix=orm.name_suffix or [],
            ),
            gender=Gender(orm.gender) if orm.gender else Gender.UNKNOWN,
            active=orm.active,
            identifiers=[
                Identifier(system=i["system"], value=i["value"])
                for i in (orm.identifiers or [])
            ],
            telecom=[
                ContactPoint(system=t["system"], value=t["value"], use=t.get("use"))
                for t in (orm.telecom or [])
            ],
            qualifications=[
                CodeableConcept(
                    code=q["code"], display=q["display"], system=q.get("system")
                )
                for q in (orm.qualifications or [])
            ],
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )

"""FastAPI service: ingest profiles, segment the workforce, analyse skill gaps."""

from __future__ import annotations

import os
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import __version__
from .extraction import SkillExtractor
from .gaps import analyse_gap, best_fit_roles, load_roles, segment_gap
from .privacy import pseudonymise
from .segmentation import segment_workforce
from .store import ProfileStore
from .taxonomy import Taxonomy


class ProfileIn(BaseModel):
    employee_ref: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=20_000)


class SegmentIn(BaseModel):
    k: int | None = Field(default=None, ge=2, le=12)


def create_app(store: ProfileStore | None = None, salt: str | None = None) -> FastAPI:
    app = FastAPI(title="Workforce Skill Intelligence", version=__version__)
    taxonomy = Taxonomy.from_csv()
    extractor = SkillExtractor(taxonomy)
    roles = load_roles()
    db = store or ProfileStore()
    secret = salt or os.getenv("SKILLINTEL_SALT", "change-me-in-production")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "version": __version__, "employees": len(db.all())}

    @app.get("/roles")
    def list_roles() -> dict[str, list[str]]:
        return roles

    @app.post("/profiles", status_code=201)
    def add_profile(body: ProfileIn) -> dict:
        employee_id = pseudonymise(body.employee_ref, secret)
        skills = extractor.skill_set(body.text)
        db.upsert(employee_id, skills)
        return {"employee_id": employee_id, "skills": sorted(skills)}

    @app.get("/employees/{employee_id}/fit")
    def fit(employee_id: str, role: str | None = None) -> dict:
        skills = db.get(employee_id)
        if skills is None:
            raise HTTPException(404, "employee not found")
        if role:
            if role not in roles:
                raise HTTPException(404, f"unknown role: {role}")
            return asdict(analyse_gap(skills, role, roles))
        return {"best_fit": [asdict(r) for r in best_fit_roles(skills, roles)]}

    @app.post("/segments")
    def segment(body: SegmentIn) -> dict:
        profiles = db.all()
        if len(profiles) < 3:
            raise HTTPException(422, "need at least 3 profiles to segment")
        segments = segment_workforce(profiles, taxonomy, k=body.k)
        return {
            "segments": [
                {"id": s.segment_id, "label": s.label, "size": s.size, "top_skills": s.top_skills}
                for s in segments
            ]
        }

    @app.get("/segments/gaps")
    def segment_gaps(role: str, k: int | None = None) -> dict:
        if role not in roles:
            raise HTTPException(404, f"unknown role: {role}")
        profiles = db.all()
        if len(profiles) < 3:
            raise HTTPException(422, "need at least 3 profiles to segment")
        out = []
        for s in segment_workforce(profiles, taxonomy, k=k):
            gaps = segment_gap([profiles[m] for m in s.members], role, roles)
            out.append({"label": s.label, "size": s.size, "missing_share": gaps})
        return {"role": role, "segments": out}

    return app


app = create_app()

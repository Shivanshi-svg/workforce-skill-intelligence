"""Segment employees into skill clusters (K-Means), choosing k by silhouette score."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .taxonomy import Taxonomy


@dataclass
class Segment:
    segment_id: int
    size: int
    top_skills: list[str]
    members: list[str]

    @property
    def label(self) -> str:
        return " / ".join(self.top_skills[:3]) or "general"


def build_matrix(
    profiles: dict[str, set[str]], taxonomy: Taxonomy
) -> tuple[list[str], list[str], np.ndarray]:
    employees = sorted(profiles)
    skills = sorted(taxonomy.skills)
    index = {s: i for i, s in enumerate(skills)}
    matrix = np.zeros((len(employees), len(skills)))
    for row, emp in enumerate(employees):
        for skill in profiles[emp]:
            if skill in index:
                matrix[row, index[skill]] = 1.0
    return employees, skills, matrix


def choose_k(matrix: np.ndarray, k_min: int = 2, k_max: int = 8, seed: int = 0) -> int:
    upper = min(k_max, len(matrix) - 1)
    if upper < k_min:
        return max(1, min(len(matrix), k_min))
    best_k, best_score = k_min, -1.0
    for k in range(k_min, upper + 1):
        labels = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(matrix)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(matrix, labels)
        if score > best_score:
            best_k, best_score = k, score
    return best_k


def segment_workforce(
    profiles: dict[str, set[str]],
    taxonomy: Taxonomy,
    k: int | None = None,
    seed: int = 0,
    top_n: int = 5,
) -> list[Segment]:
    if len(profiles) < 2:
        raise ValueError("need at least two employees to segment")
    employees, skills, matrix = build_matrix(profiles, taxonomy)
    k = k or choose_k(matrix, seed=seed)
    model = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(matrix)
    overall = matrix.mean(axis=0)

    segments = []
    for cluster in range(k):
        member_idx = np.where(model.labels_ == cluster)[0]
        if len(member_idx) == 0:
            continue
        # Rank skills by how much more common they are inside the segment than overall.
        lift = matrix[member_idx].mean(axis=0) - overall
        coverage = matrix[member_idx].mean(axis=0)
        ranked = np.argsort(-(lift + 0.01 * coverage))
        top = [skills[i] for i in ranked[:top_n] if coverage[i] > 0.3]
        segments.append(
            Segment(cluster, len(member_idx), top, [employees[i] for i in member_idx])
        )
    return sorted(segments, key=lambda s: -s.size)

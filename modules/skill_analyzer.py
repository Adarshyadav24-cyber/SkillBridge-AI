"""Job description analyzer and skill taxonomy parser for SkillBridge AI.

Uses a transparent, deterministic keyword and synonym matching algorithm
derived from an editable skill taxonomy JSON.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from config import TAXONOMY_FILE


class SkillAnalyzer:
    """Analyzes job descriptions and maps required skills against student profiles."""

    def __init__(self, taxonomy_path: Optional[Path] = None):
        self.taxonomy_path = taxonomy_path or TAXONOMY_FILE
        self.skills: List[Dict[str, Any]] = []
        self._skill_map_by_name: Dict[str, Dict[str, Any]] = {}
        self._skill_map_by_id: Dict[str, Dict[str, Any]] = {}
        self.load_taxonomy()

    def load_taxonomy(self) -> None:
        """Loads skill taxonomy from disk or initializes defaults if missing."""
        if self.taxonomy_path.exists():
            try:
                with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills = data.get("skills", [])
            except Exception as e:
                # Fallback to empty if corrupt
                self.skills = []
        else:
            self.skills = []

        self._skill_map_by_name = {s["name"].lower(): s for s in self.skills}
        self._skill_map_by_id = {s["id"]: s for s in self.skills}

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Returns all skills defined in taxonomy."""
        return self.skills

    def get_skill_names(self) -> List[str]:
        """Returns ordered list of canonical skill names."""
        return [s["name"] for s in self.skills]

    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up skill dict by canonical name (case-insensitive)."""
        return self._skill_map_by_name.get(name.strip().lower())

    def get_skill_by_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Look up skill dict by unique ID."""
        return self._skill_map_by_id.get(skill_id.strip().lower())

    def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """Extracts skills from unstructured job description text.

        Uses explicit regex word boundaries and synonym dictionary mapping.
        Returns extracted skills, match counts, and exact matching evidence.
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "detected_skills": [],
                "evidence": {},
                "match_count": 0,
                "status": "empty_input",
                "explanation": "No text provided. Paste a valid job description to extract required skills.",
            }

        cleaned_text = text.lower()
        detected_skills: List[str] = []
        evidence: Dict[str, List[str]] = {}

        for skill in self.skills:
            canonical_name = skill["name"]
            matched_terms: Set[str] = set()

            # Check canonical name
            escaped_name = re.escape(canonical_name.lower())
            pattern = rf"\b{escaped_name}\b"
            if re.search(pattern, cleaned_text):
                matched_terms.add(canonical_name.lower())

            # Check synonyms
            for syn in skill.get("synonyms", []):
                syn_lower = syn.lower()
                escaped_syn = re.escape(syn_lower)
                # Word boundary matching
                pattern = rf"\b{escaped_syn}\b"
                if re.search(pattern, cleaned_text):
                    matched_terms.add(syn_lower)

            if matched_terms:
                detected_skills.append(canonical_name)
                evidence[canonical_name] = sorted(list(matched_terms))

        # Sort detected skills deterministically
        detected_skills.sort()

        if not detected_skills:
            explanation = (
                "No skills from the current taxonomy were identified in this text. "
                "The text may be too short, or uses specialized terms not yet present in the taxonomy."
            )
        else:
            explanation = (
                f"Identified {len(detected_skills)} relevant skill(s) based on keyword and synonym occurrences "
                f"across our transparent taxonomy."
            )

        return {
            "detected_skills": detected_skills,
            "evidence": evidence,
            "match_count": len(detected_skills),
            "status": "success" if detected_skills else "no_matches",
            "explanation": explanation,
        }

    def analyze_skill_gap(
        self, required_skills: List[str], student_skills: List[str]
    ) -> Dict[str, Any]:
        """Compares required skills against self-reported student skills.

        Deduplicates inputs and computes set intersections/differences.
        """
        # Canonicalize inputs to match taxonomy names if possible
        def canonicalize_list(items: List[str]) -> List[str]:
            seen: Set[str] = set()
            res: List[str] = []
            for item in items or []:
                if not item or not isinstance(item, str):
                    continue
                cleaned = item.strip()
                matched_skill = self.get_skill_by_name(cleaned)
                name = matched_skill["name"] if matched_skill else cleaned
                if name.lower() not in seen:
                    seen.add(name.lower())
                    res.append(name)
            return sorted(res)

        clean_req = canonicalize_list(required_skills)
        clean_stu = canonicalize_list(student_skills)

        req_set = set(clean_req)
        stu_set = set(clean_stu)

        matched = sorted(list(req_set.intersection(stu_set)))
        missing = sorted(list(req_set.difference(stu_set)))
        additional = sorted(list(stu_set.difference(req_set)))

        total_req = len(clean_req)
        match_count = len(matched)
        match_percentage = round((match_count / total_req * 100), 1) if total_req > 0 else 0.0

        if total_req == 0:
            summary = "No job requirements analyzed yet."
        elif match_count == total_req:
            summary = f"All {total_req} required skills are present in the student's profile (100% match)."
        elif match_count == 0:
            summary = f"0 of {total_req} required skills matched. All {total_req} are identified as learning gaps."
        else:
            summary = (
                f"Matched {match_count} of {total_req} required skills ({match_percentage}% match). "
                f"{len(missing)} skill gap(s) identified for focused study."
            )

        return {
            "required_skills": clean_req,
            "student_skills": clean_stu,
            "matched_skills": matched,
            "missing_skills": missing,
            "additional_skills": additional,
            "total_required": total_req,
            "match_count": match_count,
            "missing_count": len(missing),
            "match_percentage": match_percentage,
            "summary": summary,
        }

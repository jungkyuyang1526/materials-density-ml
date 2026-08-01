"""Secure Materials Project data collection for the density benchmark."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from mp_api.client import MPRester

CHEMICAL_SYSTEM_QUERIES = ["Si-O", "Al-O-Si"]
REQUESTED_FIELDS = [
    "material_id",
    "formula_pretty",
    "chemsys",
    "density",
    "volume",
    "nsites",
    "nelements",
    "composition",
    "symmetry",
]


def _stringify_enum(value: Any) -> str | None:
    if value is None:
        return None
    return str(getattr(value, "value", value))


def _display_chemical_system(composition: Any, api_chemsys: Any) -> str | None:
    if composition is not None:
        symbols = {str(element) for element in composition.elements}
        if symbols == {"Si", "O"}:
            return "Si-O"
        if symbols == {"Si", "Al", "O"}:
            return "Si-Al-O"
    return str(api_chemsys) if api_chemsys is not None else None


def _document_to_record(document: Any) -> dict[str, Any]:
    composition = getattr(document, "composition", None)
    symmetry = getattr(document, "symmetry", None)
    volume = getattr(document, "volume", None)
    number_of_sites = getattr(document, "nsites", None)

    formula = getattr(document, "formula_pretty", None)
    if not formula and composition is not None:
        formula = composition.reduced_formula

    mean_atomic_mass = None
    if composition is not None and composition.num_atoms:
        mean_atomic_mass = float(composition.weight / composition.num_atoms)

    volume_per_atom = None
    if volume is not None and number_of_sites:
        volume_per_atom = float(volume / number_of_sites)

    return {
        "Material ID": str(document.material_id),
        "Formula": str(formula) if formula is not None else None,
        "Chemical System": _display_chemical_system(
            composition, getattr(document, "chemsys", None)
        ),
        "Density": float(document.density) if document.density is not None else None,
        "Volume": float(volume) if volume is not None else None,
        "Number of Sites": int(number_of_sites) if number_of_sites is not None else None,
        "Number of Elements": (
            int(document.nelements) if document.nelements is not None else None
        ),
        "Crystal System": (
            _stringify_enum(getattr(symmetry, "crystal_system", None))
            if symmetry is not None
            else None
        ),
        "Space Group Number": (
            int(symmetry.number)
            if symmetry is not None and symmetry.number is not None
            else None
        ),
        "Mean Atomic Mass": mean_atomic_mass,
        "Volume per Atom": volume_per_atom,
    }


def collect_materials(
    output_csv: str | Path = "data/materials_snapshot.csv",
    metadata_json: str | Path = "data/materials_snapshot_metadata.json",
) -> pd.DataFrame:
    """Retrieve the defined chemical systems and save a credential-free snapshot."""
    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "MP_API_KEY is not set. Add the Materials Project API key "
            "as an environment variable before running this script."
        )

    output_csv = Path(output_csv)
    metadata_json = Path(metadata_json)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    metadata_json.parent.mkdir(parents=True, exist_ok=True)

    database_version = "Unavailable from client"
    with MPRester(api_key) as mpr:
        try:
            database_version = str(mpr.get_database_version())
        except Exception as exc:
            print(
                "Materials Project database version could not be recorded: "
                f"{type(exc).__name__}: {exc}"
            )

        documents = mpr.materials.summary.search(
            chemsys=CHEMICAL_SYSTEM_QUERIES,
            deprecated=False,
            include_gnome=False,
            fields=REQUESTED_FIELDS,
        )

    dataframe = pd.DataFrame(_document_to_record(doc) for doc in documents)
    dataframe.to_csv(output_csv, index=False)

    metadata_record = {
        "data_retrieval_date": date.today().isoformat(),
        "materials_project_database_version": database_version,
        "source": "Materials Project summary API",
        "chemical_system_queries": CHEMICAL_SYSTEM_QUERIES,
        "include_gnome": False,
        "deprecated": False,
    }
    metadata_json.write_text(
        json.dumps(metadata_record, indent=2),
        encoding="utf-8",
    )
    return dataframe


if __name__ == "__main__":
    collected = collect_materials()
    print(f"Saved {len(collected):,} records.")

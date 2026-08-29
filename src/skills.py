from __future__ import annotations

from pathlib import Path


def load_skills_index(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for line in lines:
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "items": []}
            sections.append(current)
            continue

        if not current:
            continue

        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue

        skill_id = cells[0].strip("`")
        purpose = cells[1]
        link_cell = cells[2]
        if skill_id in {"Skill", "---"}:
            continue
        link_target = link_cell
        if link_cell.startswith("[") and "](" in link_cell and link_cell.endswith(")"):
            link_target = link_cell[link_cell.find("(") + 1 : -1]
        link_target = link_target.strip("`")

        items = current.setdefault("items", [])
        items.append(
            {
                "id": skill_id,
                "purpose": purpose,
                "label": Path(link_target).name,
                "path": link_target,
            }
        )

    return sections

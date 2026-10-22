"""Export installed runtime distribution metadata and full license files."""

import importlib.metadata as metadata
import json
import shutil
import sys
import sysconfig
from pathlib import Path

from packaging.requirements import Requirement


def export(destination: Path) -> None:
    pending = [Requirement("markitdown[pdf,docx,pptx,xlsx]"), Requirement("psutil")]
    seen = set()
    inventory = []
    destination.mkdir(parents=True, exist_ok=True)
    candidates = [
        Path(sysconfig.get_path("stdlib")) / "LICENSE.txt",
        Path(sys.base_prefix) / "LICENSE.txt",
        Path(sys.base_prefix) / "LICENSE",
    ]
    python_license = next((path for path in candidates if path.is_file()), None)
    if python_license is None:
        raise FileNotFoundError("The Python runtime license must accompany redistributed builds")
    (destination / "Python").mkdir(exist_ok=True)
    shutil.copy2(python_license, destination / "Python/LICENSE.txt")
    while pending:
        requirement = pending.pop()
        distribution = metadata.distribution(requirement.name)
        name = distribution.metadata["Name"]
        if name in seen:
            continue
        seen.add(name)
        inventory.append(
            {
                "name": name,
                "version": distribution.version,
                "license": distribution.metadata.get("License-Expression")
                or distribution.metadata.get("License", "See bundled notices"),
                "homepage": distribution.metadata.get("Home-page", ""),
            }
        )
        for file in distribution.files or []:
            if any(
                part.lower().startswith(("license", "copying", "notice")) for part in file.parts
            ):
                source = Path(distribution.locate_file(file))
                if source.is_file():
                    relative = Path(*(part for part in file.parts if part not in ("..", ".")))
                    target = destination / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
        for dependency in distribution.requires or []:
            dependency = Requirement(dependency)
            if dependency.marker is None or any(
                dependency.marker.evaluate({"extra": extra}) for extra in {"", *requirement.extras}
            ):
                pending.append(dependency)
    (destination / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export(Path("dist/licenses"))

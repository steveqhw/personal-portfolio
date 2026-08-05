#!/usr/bin/env python3
"""Validate portfolio source contracts using only the Python standard library."""

from __future__ import annotations

import html.parser
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
Reporter = Callable[[str], None]

REQUIRED_FILES = (
    "_config.yml",
    "Gemfile",
    "_data/ui.yml",
    "_data/projects.yml",
    "_data/site.yml",
    "_layouts/default.html",
    "_layouts/project.html",
    "_includes/head.html",
    "_includes/header.html",
    "_includes/footer.html",
    "_includes/sections/contact.html",
    "_includes/sections/projects.html",
    "assets/css/style.css",
    "assets/images/progetto-posizionatore.jpeg",
    "index.html",
    "it/index.html",
    "privacy/index.html",
    "it/privacy/index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
)

PROJECT_ROUTES = {
    "hydroponic-frame": (
        "/work/hydroponic-living-frame-controller/",
        "/it/work/controller-quadro-idroponico/",
    ),
    "positioning-machine": (
        "/work/industrial-positioning-machine-controller/",
        "/it/work/controller-macchina-posizionamento-industriale/",
    ),
    "3d-enclosures": (
        "/work/3d-printed-electronic-enclosures/",
        "/it/work/enclosure-elettroniche-stampate-3d/",
    ),
}

GENERIC_EMPLOYERS = {
    ("Academic development phase", "Fase di sviluppo accademico"),
    ("Medical robotics R&D organization", "Organizzazione R&D di robotica medicale"),
    ("Airfield ground-lighting organization", "Organizzazione per l'illuminazione aeroportuale"),
}

PUBLIC_SUFFIXES = {".html", ".xml", ".txt", ".css", ".js", ".yml", ".yaml"}
SKIP_PARTS = {".git", ".agents", "_site", ".jekyll-cache", "vendor"}
ALLOWED_NAVIGATION_HOSTS = {"formspree.io", "github.com", "www.linkedin.com"}
FORM_ACTION = "https://formspree.io/f/{{ site.data.site.formspree_id }}"
PRIVATE_FILE_TOKEN = re.compile(r"(?:cv|resume|curriculum(?:vitae)?)", re.IGNORECASE)
REMOTE_URL = re.compile(r"^(?:https?:)?//", re.IGNORECASE)


def fail(message: str) -> None:
    ERRORS.append(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(relative_path: str | Path) -> str:
    path = ROOT / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(f"cannot read {path.relative_to(ROOT)} as UTF-8: {exc}")
        return ""


def scalar(value: str, context: str, report: Reporter = fail) -> str:
    value = value.strip()
    if not value:
        return ""
    if value[0] in "\"'" or value[-1] in "\"'":
        if len(value) < 2 or value[0] != value[-1] or value[0] not in "\"'":
            report(f"{context} has a malformed quoted scalar")
            return value
        return value[1:-1]
    return value


def parse_front_matter_text(
    text: str, label: str, report: Reporter = fail
) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report(f"{label} is missing opening front matter")
        return {}
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        report(f"{label} is missing closing front matter")
        return {}

    result: dict[str, str] = {}
    for number, line in enumerate(lines[1:closing], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*", line)
        if not match:
            report(f"{label}:{number} has malformed front matter")
            continue
        key = match.group(1)
        if key in result:
            report(f"{label}:{number} duplicates front matter key {key}")
            continue
        result[key] = scalar(match.group(2), f"{label}:{number} {key}", report)
    return result


def parse_front_matter(path: Path) -> dict[str, str]:
    return parse_front_matter_text(read(path.relative_to(ROOT)), rel(path))


def parse_ui_text(
    text: str, label: str = "_data/ui.yml", report: Reporter = fail
) -> dict[str, dict[str, str]]:
    locales: dict[str, dict[str, str]] = {}
    current: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        locale_match = re.fullmatch(r"(en|it):\s*", line)
        if locale_match:
            current = locale_match.group(1)
            if current in locales:
                report(f"{label}:{number} duplicates locale {current}")
            else:
                locales[current] = {}
            continue
        key_match = re.fullmatch(r"  ([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*", line)
        if current is None or not key_match:
            report(f"{label}:{number} has malformed UI scalar structure")
            continue
        key = key_match.group(1)
        values = locales[current]
        if key in values:
            report(f"{label}:{number} duplicates {current}.{key}")
            continue
        value = scalar(key_match.group(2), f"{label}:{number} {current}.{key}", report)
        if not value:
            report(f"{label}:{number} has an empty {current}.{key} value")
        values[key] = value
    return locales


def parse_record_text(
    text: str, label: str, report: Reporter = fail
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    list_key: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        id_match = re.fullmatch(r"- id:\s*(.*?)\s*", line)
        if id_match:
            identifier = scalar(id_match.group(1), f"{label}:{number} id", report)
            if not identifier:
                report(f"{label}:{number} has an empty project/record id")
            current = {"id": identifier}
            records.append(current)
            list_key = None
            continue
        field_match = re.fullmatch(r"  ([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*", line)
        if field_match and current is not None:
            key = field_match.group(1)
            if key in current:
                report(f"{label}:{number} duplicates scalar/list key {key}")
                list_key = None
                continue
            value = scalar(field_match.group(2), f"{label}:{number} {key}", report)
            current[key] = value
            list_key = key if not value else None
            continue
        if re.fullmatch(r"    -\s+.+", line) and current is not None and list_key:
            continue
        report(f"{label}:{number} has malformed record scalar/list structure")
    return records


def parse_flat_yaml_text(
    text: str, label: str, report: Reporter = fail
) -> dict[str, str]:
    result: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*", line)
        if not match:
            report(f"{label}:{number} has malformed scalar structure")
            continue
        key = match.group(1)
        if key in result:
            report(f"{label}:{number} duplicates scalar key {key}")
            continue
        result[key] = scalar(match.group(2), f"{label}:{number} {key}", report)
    return result


def validate_ui() -> None:
    locales = parse_ui_text(read("_data/ui.yml"))
    for locale in ("en", "it"):
        if not locales.get(locale):
            fail(f"_data/ui.yml must define a non-empty {locale} mapping")
    en_keys = set(locales.get("en", {}))
    it_keys = set(locales.get("it", {}))
    if en_keys - it_keys:
        fail(f"_data/ui.yml keys missing from it: {', '.join(sorted(en_keys - it_keys))}")
    if it_keys - en_keys:
        fail(f"_data/ui.yml keys missing from en: {', '.join(sorted(it_keys - en_keys))}")

    template_keys: set[str] = set()
    template_paths = list((ROOT / "_layouts").rglob("*.html")) + list(
        (ROOT / "_includes").rglob("*.html")
    )
    for path in template_paths:
        template_keys.update(re.findall(r"\bt\.([A-Za-z_][A-Za-z0-9_]*)", read(path.relative_to(ROOT))))
    for locale in ("en", "it"):
        missing = sorted(template_keys - set(locales.get(locale, {})))
        if missing:
            fail(f"template t.* keys missing from {locale}: {', '.join(missing)}")


def route_file(route: str) -> Path:
    clean = route.strip("/")
    return ROOT / clean / "index.html" if clean else ROOT / "index.html"


def validate_project_page(
    path: Path,
    project: dict[str, str],
    lang: str,
    permalink: str,
    counterpart: str,
) -> None:
    if not path.is_file():
        fail(f"missing project page {rel(path)}")
        return
    front = parse_front_matter(path)
    expected = {
        "layout": "project",
        "lang": lang,
        "project_id": project.get("id", ""),
        "permalink": permalink,
        "counterpart_url": counterpart,
        "alternate_en": project.get("path_en", ""),
        "alternate_it": project.get("path_it", ""),
    }
    for key, value in expected.items():
        if front.get(key) != value:
            fail(f"{rel(path)} front matter {key} must be {value!r}, found {front.get(key)!r}")


def validate_projects() -> None:
    projects = parse_record_text(read("_data/projects.yml"), "_data/projects.yml")
    ids = [project.get("id", "") for project in projects]
    if len(projects) != 3:
        fail(f"_data/projects.yml must contain exactly 3 projects, found {len(projects)}")
    if len(ids) != len(set(ids)):
        fail("_data/projects.yml contains duplicate project IDs")
    if set(ids) != set(PROJECT_ROUTES):
        fail(f"project IDs must be exactly {sorted(PROJECT_ROUTES)}, found {sorted(ids)}")

    expected_pages: set[Path] = set()
    for project in projects:
        project_id = project.get("id", "<missing-id>")
        for key in (
            "slug_en", "slug_it", "path_en", "path_it", "title_en", "title_it",
            "summary_en", "summary_it", "seo_title_en", "seo_title_it",
            "seo_description_en", "seo_description_it",
        ):
            if not project.get(key):
                fail(f"project {project_id} is missing {key}")
        for key in tuple(project):
            if key.endswith("_en") and key[:-3] + "_it" not in project:
                fail(f"project {project_id} has {key} without its Italian counterpart")
            if key.endswith("_it") and key[:-3] + "_en" not in project:
                fail(f"project {project_id} has {key} without its English counterpart")

        path_en = project.get("path_en", "")
        path_it = project.get("path_it", "")
        expected_routes = PROJECT_ROUTES.get(project_id)
        if expected_routes and (path_en, path_it) != expected_routes:
            fail(
                f"project {project_id} routes must be exactly {expected_routes}, "
                f"found {(path_en, path_it)}"
            )
        if path_en and path_en.strip("/").split("/")[-1] != project.get("slug_en"):
            fail(f"project {project_id} path_en does not match slug_en")
        if path_it and path_it.strip("/").split("/")[-1] != project.get("slug_it"):
            fail(f"project {project_id} path_it does not match slug_it")
        if path_en and path_it:
            en_file, it_file = route_file(path_en), route_file(path_it)
            expected_pages.update((en_file, it_file))
            validate_project_page(en_file, project, "en", path_en, path_it)
            validate_project_page(it_file, project, "it", path_it, path_en)

        image = project.get("image", "")
        if image:
            image_path = ROOT / "assets" / "images" / image
            if not image_path.is_file():
                fail(f"project {project_id} references missing asset {rel(image_path)}")
            for alt_key in ("image_alt_en", "image_alt_it"):
                if not project.get(alt_key):
                    fail(f"project {project_id} image requires non-empty {alt_key}")
            if project.get("media_status") != "public_image_available":
                fail(f"project {project_id} image requires media_status public_image_available")
        elif project.get("media_status") != "not_publicly_available":
            fail(f"project {project_id} without an image must declare not_publicly_available")

    actual_pages = set((ROOT / "work").glob("*/index.html")) | set(
        (ROOT / "it" / "work").glob("*/index.html")
    )
    if actual_pages != expected_pages:
        missing = sorted(rel(path) for path in expected_pages - actual_pages)
        extra = sorted(rel(path) for path in actual_pages - expected_pages)
        if missing:
            fail(f"project pages missing: {', '.join(missing)}")
        if extra:
            fail(f"project pages not represented in project data: {', '.join(extra)}")


def validate_page_counterparts() -> None:
    pairs = (
        ("index.html", "it/index.html", "/", "/it/"),
        ("privacy/index.html", "it/privacy/index.html", "/privacy/", "/it/privacy/"),
    )
    for en_name, it_name, en_route, it_route in pairs:
        en = parse_front_matter(ROOT / en_name)
        it = parse_front_matter(ROOT / it_name)
        for key, value in {
            "lang": "en", "permalink": en_route, "counterpart_url": it_route,
            "alternate_en": en_route, "alternate_it": it_route,
        }.items():
            if en.get(key) != value:
                fail(f"{en_name} front matter {key} must be {value!r}")
        for key, value in {
            "lang": "it", "permalink": it_route, "counterpart_url": en_route,
            "alternate_en": en_route, "alternate_it": it_route,
        }.items():
            if it.get(key) != value:
                fail(f"{it_name} front matter {key} must be {value!r}")


class FormParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, str]] = []
        self.fields: list[dict[str, str]] = []
        self.in_form = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value if value is not None else "" for key, value in attrs}
        if tag == "form":
            self.forms.append(attributes)
            self.in_form = True
        elif self.in_form and tag in {"input", "textarea"}:
            attributes["_tag"] = tag
            self.fields.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self.in_form = False


def validate_form_source(source: str, formspree_id: str, report: Reporter = fail) -> None:
    if not re.fullmatch(r"[A-Za-z0-9]{8,32}", formspree_id):
        report("_data/site.yml formspree_id must be 8-32 ASCII alphanumeric characters")
    parser = FormParser()
    parser.feed(source)
    if len(parser.forms) != 1:
        report(f"contact include must contain exactly one form, found {len(parser.forms)}")
        return
    if parser.forms[0].get("action") != FORM_ACTION:
        report("contact form action no longer uses the approved Formspree endpoint contract")
    if parser.forms[0].get("method", "").upper() != "POST":
        report("contact form method must be POST")

    named_fields = [field for field in parser.fields if field.get("name")]
    unnamed_count = len(parser.fields) - len(named_fields)
    if unnamed_count:
        report(f"contact form has {unnamed_count} unnamed input/textarea field(s)")
    names = [field["name"] for field in named_fields]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        report(f"contact form has duplicate field name(s): {', '.join(duplicates)}")
    expected_names = {"name", "email", "message", "_language", "_gotcha"}
    if set(names) != expected_names:
        report(f"contact form fields must be exactly {sorted(expected_names)}, found {sorted(set(names))}")
    fields = {field["name"]: field for field in named_fields}
    contracts = {
        "name": {"_tag": "input", "type": "text", "required": "", "maxlength": "120"},
        "email": {"_tag": "input", "type": "email", "required": "", "maxlength": "254"},
        "message": {"_tag": "textarea", "required": "", "maxlength": "5000"},
        "_language": {"_tag": "input", "type": "hidden", "value": "{{ lang }}"},
        "_gotcha": {
            "_tag": "input", "type": "text", "tabindex": "-1",
            "autocomplete": "off", "aria-hidden": "true",
        },
    }
    for name, contract in contracts.items():
        field = fields.get(name)
        if not field:
            continue
        for attribute, expected in contract.items():
            if field.get(attribute) != expected:
                report(
                    f"contact form field {name} requires {attribute}={expected!r}, "
                    f"found {field.get(attribute)!r}"
                )
    for fragment in ("t.contact_privacy_notice", "t.contact_privacy_link", "privacy_url | relative_url"):
        if fragment not in source:
            report(f"contact form is missing privacy contract fragment {fragment!r}")


def validate_form() -> None:
    site_data = parse_flat_yaml_text(read("_data/site.yml"), "_data/site.yml")
    formspree_id = site_data.get("formspree_id", "")
    if not formspree_id:
        fail("_data/site.yml formspree_id must not be empty")
    validate_form_source(read("_includes/sections/contact.html"), formspree_id)
    configured_hosts = {
        "linkedin": "www.linkedin.com",
        "github": "github.com",
    }
    for key, expected_host in configured_hosts.items():
        value = site_data.get(key, "")
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.hostname != expected_host:
            fail(f"_data/site.yml {key} must be an HTTPS URL on {expected_host}")


def public_source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in PUBLIC_SUFFIXES:
            files.append(path)
    return files


def remote_host(value: str) -> str:
    candidate = "https:" + value if value.startswith("//") else value
    return (urlparse(candidate).hostname or "").lower()


class ResourcePolicyParser(html.parser.HTMLParser):
    RESOURCE_ATTRIBUTES = {"src", "srcset", "poster", "data"}
    RESOURCE_TAGS = {"iframe", "video", "audio", "source", "object", "embed", "script", "link"}

    def __init__(self, label: str, report: Reporter = fail) -> None:
        super().__init__()
        self.label = label
        self.report = report

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        for name, value in attributes.items():
            candidates = [part.strip().split()[0] for part in value.split(",") if part.strip()] if name == "srcset" else [value.strip()]
            for candidate in candidates:
                if not REMOTE_URL.match(candidate):
                    continue
                if tag == "a" and name == "href":
                    if not candidate.startswith("https://") or remote_host(candidate) not in ALLOWED_NAVIGATION_HOSTS:
                        self.report(f"{self.label} has an unapproved remote navigation link: {candidate}")
                elif tag == "form" and name == "action" and candidate == FORM_ACTION:
                    continue
                else:
                    self.report(f"{self.label} loads a forbidden remote resource in {tag}[{name}]: {candidate}")

        for name in self.RESOURCE_ATTRIBUTES:
            value = attributes.get(name, "")
            if re.search(r"(?:https?:)?//", value, re.IGNORECASE) and not REMOTE_URL.match(value.strip()):
                self.report(f"{self.label} hides a remote URL inside {tag}[{name}]")
            if "{{" in value and "relative_url" not in value and "absolute_url" not in value:
                self.report(f"{self.label} has an unfiltered dynamic resource in {tag}[{name}]")
        if tag in self.RESOURCE_TAGS:
            for name, value in attributes.items():
                if "{{" in value and name in self.RESOURCE_ATTRIBUTES and "relative_url" not in value and "absolute_url" not in value:
                    self.report(f"{self.label} has an unsafe dynamic resource in {tag}[{name}]")


def validate_urls_and_assets() -> None:
    attribute_pattern = re.compile(
        r"\b(?:href|src|action|poster|srcset|data)\s*=\s*([\"'])(.*?)\1", re.IGNORECASE
    )
    asset_pattern = re.compile(r"[\"'](/assets/[^\"'{}\s|?#,]+)")
    image_pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)

    for path in public_source_files():
        source = read(path.relative_to(ROOT))
        if path.suffix.lower() == ".html":
            ResourcePolicyParser(rel(path)).feed(source)
            if re.search(r"(?:url\(|@import)[^;>]*(?:https?:)?//", source, re.IGNORECASE):
                fail(f"{rel(path)} contains a forbidden remote inline-style resource")
        for match in attribute_pattern.finditer(source):
            value = match.group(2).strip()
            if value.startswith(("mailto:", "tel:")):
                fail(f"{rel(path)} publishes a direct private contact URL: {value}")
            if value.startswith("/") and not value.startswith("//"):
                fail(f"{rel(path)} has a root-relative URL without a Jekyll URL filter: {value}")
            if "{{" in value and not value.startswith(("http://", "https://")):
                if "relative_url" not in value and "absolute_url" not in value:
                    allowed_navigation = (
                        match.group(0).lower().startswith("href"),
                        "site.data.site.linkedin" in value or "site.data.site.github" in value,
                    )
                    if not all(allowed_navigation):
                        fail(f"{rel(path)} has an unfiltered Liquid URL attribute: {value}")
        for match in asset_pattern.finditer(source):
            asset_path = ROOT / match.group(1).lstrip("/")
            exists = asset_path.is_dir() if match.group(1).endswith("/") else asset_path.is_file()
            if not exists:
                fail(f"{rel(path)} references missing asset {match.group(1)}")
        for image_tag in image_pattern.findall(source):
            for attribute in ("alt", "width", "height"):
                if not re.search(rf"\b{attribute}\s*=", image_tag, re.IGNORECASE):
                    fail(f"{rel(path)} has an <img> without {attribute}")

    css = read("assets/css/style.css")
    for pattern, label in (
        (r"@import\b", "CSS @import"),
        (r"url\(\s*['\"]?(?:https?:)?//", "remote CSS asset"),
        (r"fonts\.(?:googleapis|gstatic)\.com", "third-party font"),
    ):
        if re.search(pattern, css, re.IGNORECASE):
            fail(f"assets/css/style.css contains forbidden {label}")
    for forbidden in ("package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
        if (ROOT / forbidden).exists():
            fail(f"forbidden frontend dependency manifest found: {forbidden}")


def repository_candidates() -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"cannot inspect tracked and non-ignored files with git: {exc}")
        return set()
    try:
        return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}
    except UnicodeDecodeError as exc:
        fail(f"git returned a non-UTF-8 repository path: {exc}")
        return set()


def is_private_filename(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", Path(name).stem.lower())
    return bool(PRIVATE_FILE_TOKEN.search(normalized))


def validate_private_exclusions() -> None:
    candidates = repository_candidates()
    secret_suffixes = {".env", ".key", ".pem", ".p12", ".pfx"}
    for name in sorted(candidates):
        path = Path(name)
        if path.parts and path.parts[0] == ".agents":
            fail(f"internal agent artifact is publishable: {name}")
        if is_private_filename(path.name):
            fail(f"private CV/resume/curriculum-like file is publishable: {name}")
        if path.suffix.lower() in secret_suffixes or path.name.lower().startswith(".env"):
            fail(f"credential/private key-like file is publishable: {name}")

    experiences = parse_record_text(read("_data/experience.yml"), "_data/experience.yml")
    actual_employers: set[tuple[str, str]] = set()
    for record in experiences:
        employer_pair = (record.get("employer_en", ""), record.get("employer_it", ""))
        if not all(employer_pair):
            fail(f"experience {record.get('id', '<missing-id>')} lacks a paired generic employer label")
        else:
            actual_employers.add(employer_pair)
        if employer_pair not in GENERIC_EMPLOYERS:
            fail(f"experience {record.get('id', '<missing-id>')} has a non-allowlisted employer label")
    if actual_employers != GENERIC_EMPLOYERS:
        fail("experience employer labels must exactly match the approved generic EN/IT allowlist")

    config = read("_config.yml")
    for fragment in ("- .agents", "- handoff.md", "- README.md", "- Gemfile", "- Gemfile.lock", "- vendor"):
        if fragment not in config:
            fail(f"_config.yml exclusion is missing {fragment}")
    if "_data/*CV*" not in config or "_data/*cv*" not in config:
        fail("_config.yml must exclude case variants of private CV data")

    public_text = "\n".join(read(path.relative_to(ROOT)) for path in public_source_files())
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", public_text, re.IGNORECASE):
        fail("public source contains a direct email address; keep it private")
    if re.search(r"\+\d[\d\s().-]{7,}\d", public_text):
        fail("public source contains a phone-number-like value; keep it private")


def validate_required_files() -> None:
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            fail(f"required file is missing: {relative_path}")


def validate_metadata_contract() -> None:
    head = read("_includes/head.html")
    for fragment in (
        "{{ page.url | absolute_url }}",
        "{{ include.alternate_en | absolute_url }}",
        "{{ include.alternate_it | absolute_url }}",
        "{{ '/assets/css/style.css' | relative_url }}",
    ):
        if fragment not in head:
            fail(f"localized metadata/baseurl contract is missing {fragment}")
    if "{{ '/sitemap.xml' | absolute_url }}" not in read("robots.txt"):
        fail("robots.txt sitemap URL must use absolute_url")
    sitemap = read("sitemap.xml")
    for fragment in ("project.path_en | absolute_url", "project.path_it | absolute_url"):
        if fragment not in sitemap:
            fail(f"sitemap.xml is missing {fragment}")


def run_self_tests() -> int:
    failures: list[str] = []

    def expect(condition: bool, label: str) -> None:
        if not condition:
            failures.append(label)

    for private_name in ("StefanoCV2027.pdf", "resume2026.docx", "curriculumvitae.md"):
        expect(is_private_filename(private_name), f"private filename not detected: {private_name}")
    expect(not is_private_filename("index.html"), "ordinary filename classified as private")

    parser_errors: list[str] = []
    parse_front_matter_text("---\nlang: en\nlang: it\nmalformed\n---\n", "fixture", parser_errors.append)
    expect(len(parser_errors) >= 2, "duplicate/malformed front matter was not rejected")
    parser_errors.clear()
    parse_ui_text("en:\n  key: one\n  key: two\ninvalid\nit:\n  key: uno\n", "fixture", parser_errors.append)
    expect(len(parser_errors) >= 2, "duplicate/malformed UI data was not rejected")
    parser_errors.clear()
    parse_record_text("- id: one\n  path_en: /one/\n  path_en: /two/\n  invalid value\n", "fixture", parser_errors.append)
    expect(len(parser_errors) >= 2, "duplicate/malformed project scalars were not rejected")

    for snippet in (
        '<img src="https://github.com/remote.png" alt="x">',
        '<script src="https://github.com/remote.js"></script>',
        '<source srcset="https://github.com/remote.webp 1x">',
        '<iframe src="https://github.com/"></iframe>',
    ):
        policy_errors: list[str] = []
        ResourcePolicyParser("fixture", policy_errors.append).feed(snippet)
        expect(bool(policy_errors), f"remote resource was not rejected: {snippet}")
    policy_errors = []
    ResourcePolicyParser("fixture", policy_errors.append).feed('<a href="https://evil.example/">x</a>')
    expect(bool(policy_errors), "non-allowlisted navigation host was not rejected")
    policy_errors.clear()
    ResourcePolicyParser("fixture", policy_errors.append).feed('<a href="https://github.com/steveqhw">x</a>')
    expect(not policy_errors, "allowlisted HTTPS navigation link was rejected")

    valid_form = f'''<form action="{FORM_ACTION}" method="POST">
<input type="hidden" name="_language" value="{{{{ lang }}}}">
<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="text" name="name" required maxlength="120">
<input type="email" name="email" required maxlength="254">
<textarea name="message" required maxlength="5000"></textarea>
</form> t.contact_privacy_notice t.contact_privacy_link privacy_url | relative_url'''
    form_errors: list[str] = []
    validate_form_source(valid_form.replace('name="name"', 'name="email"'), "abcdefgh", form_errors.append)
    expect(any("duplicate field" in error for error in form_errors), "duplicate form field was not rejected")
    form_errors.clear()
    validate_form_source(valid_form.replace('maxlength="5000"', 'maxlength="50"'), "abcdefgh", form_errors.append)
    expect(any("maxlength" in error for error in form_errors), "invalid form maxlength was not rejected")
    form_errors.clear()
    validate_form_source(valid_form, "", form_errors.append)
    expect(any("formspree_id" in error for error in form_errors), "empty Formspree ID was not rejected")

    if failures:
        print(f"Validator self-test failed with {len(failures)} error(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("Validator self-test passed: negative parser, privacy, form and remote-resource cases.")
    return 0


def main() -> int:
    validate_required_files()
    validate_ui()
    validate_projects()
    validate_page_counterparts()
    validate_form()
    validate_urls_and_assets()
    validate_private_exclusions()
    validate_metadata_contract()
    if ERRORS:
        print(f"Site validation failed with {len(ERRORS)} error(s):", file=sys.stderr)
        for error in ERRORS:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Site validation passed: files, bilingual data/routes, assets, form, URLs, privacy and dependencies.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(run_self_tests())
    if len(sys.argv) != 1:
        print("usage: validate_site.py [--self-test]", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())

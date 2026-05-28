import argparse
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_TOPICS = {
    "Fever",
    "Cough",
    "Sore Throat",
    "Headache",
    "Common Cold",
    "Flu",
    "COVID-19 (Coronavirus Disease 2019)",
    "Diarrhea",
    "Nausea and Vomiting",
    "Dehydration",
    "Abdominal Pain",
    "Chest Pain",
    "Asthma",
    "Allergy",
    "High Blood Pressure",
    "Diabetes",
    "Diabetes Type 2",
    "Back Pain",
    "Anxiety",
    "Depression",
}


def slugify(title: str) -> str:
    slug = title.lower()
    slug = slug.replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug or "topic"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def element_text(element) -> str:
    if element is None:
        return ""

    return normalize_text(" ".join(part.strip() for part in element.itertext() if part.strip()))


def get_children_texts(topic, tag_name: str) -> list[str]:
    values = []

    for child in topic.findall(tag_name):
        text = element_text(child)

        if text:
            values.append(text)

    return values


def build_topic_text(topic) -> str:
    title = topic.attrib.get("title", "Untitled")
    url = topic.attrib.get("url", "")
    language = topic.attrib.get("language", "")
    meta_desc = topic.attrib.get("meta-desc", "")

    also_called = get_children_texts(topic, "also-called")
    groups = get_children_texts(topic, "group")
    related_topics = get_children_texts(topic, "related-topic")
    summary = element_text(topic.find("full-summary"))

    sections = [
        f"Source: MedlinePlus.gov",
        f"Topic: {title}",
        f"URL: {url}",
        f"Language: {language}",
    ]

    if meta_desc:
        sections.append(f"\nMeta description:\n{meta_desc}")

    if also_called:
        sections.append("\nAlso called:\n" + "\n".join(f"- {item}" for item in also_called))

    if groups:
        sections.append("\nGroups:\n" + "\n".join(f"- {item}" for item in groups))

    if summary:
        sections.append("\nSummary:\n" + summary)

    if related_topics:
        sections.append(
            "\nRelated topics:\n" + "\n".join(f"- {item}" for item in related_topics)
        )

    return normalize_text("\n".join(sections)) + "\n"


def load_xml_from_zip(zip_path: Path):
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        xml_names = [
            name for name in archive.namelist()
            if name.lower().endswith(".xml")
        ]

        if not xml_names:
            raise RuntimeError("No XML file found inside the zip.")

        xml_name = xml_names[0]
        xml_bytes = archive.read(xml_name)

    return ET.fromstring(xml_bytes)


def extract_topics(
    zip_path: Path,
    output_dir: Path,
    extract_all_english: bool = False,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    root = load_xml_from_zip(zip_path)

    exported = []
    skipped = 0

    for topic in root.findall("health-topic"):
        title = topic.attrib.get("title", "")
        language = topic.attrib.get("language", "")

        if language != "English":
            skipped += 1
            continue

        if not extract_all_english and title not in DEFAULT_TOPICS:
            skipped += 1
            continue

        text = build_topic_text(topic)

        if not text.strip():
            skipped += 1
            continue

        filename = f"{slugify(title)}.txt"
        output_path = output_dir / filename

        output_path.write_text(text, encoding="utf-8")

        exported.append(
            {
                "title": title,
                "filename": filename,
            }
        )

    return {
        "zip_path": str(zip_path),
        "output_dir": str(output_dir),
        "exported_count": len(exported),
        "skipped_count": skipped,
        "exported": exported,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract selected MedlinePlus health topics from XML zip into raw .txt files."
    )

    parser.add_argument(
        "zip_path",
        nargs="?",
        default="/app/data/source/mplus_topics_compressed_2026-05-27.zip",
        help="Path to MedlinePlus compressed health topics zip.",
    )

    parser.add_argument(
        "--output-dir",
        default="/app/data/raw",
        help="Folder where .txt files will be written.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract all English topics instead of only the default common symptoms set.",
    )

    args = parser.parse_args()

    result = extract_topics(
        zip_path=Path(args.zip_path),
        output_dir=Path(args.output_dir),
        extract_all_english=args.all,
    )

    print("MedlinePlus topics extracted successfully.")
    print(f"Zip file: {result['zip_path']}")
    print(f"Output folder: {result['output_dir']}")
    print(f"Exported files: {result['exported_count']}")
    print(f"Skipped topics: {result['skipped_count']}")

    for item in result["exported"]:
        print(f"- {item['title']} -> {item['filename']}")


if __name__ == "__main__":
    main()
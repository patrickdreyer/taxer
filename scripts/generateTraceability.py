import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

log = logging.getLogger('mkdocs.plugins')


def on_pre_build(config, **kwargs):
    docsDir = Path(config['docs_dir'])
    traceabilityFile = docsDir / "requirements" / "traceability.md"
    
    try:
        log.info("Checking requirements traceability matrix...")
        newContent = generateTraceabilityMatrix(docsDir)
        
        if not newContent:
            log.error("No content generated for traceability matrix")
            return
        
        currentContent = ""
        if traceabilityFile.exists():
            currentContent = readExistingTraceabilityContent(traceabilityFile)
        
        if shouldUpdateTraceabilityFile(currentContent, newContent):
            writeTraceabilityFile(traceabilityFile, newContent)
            log.info(f"Traceability matrix updated: {traceabilityFile}")
        else:
            log.debug("Traceability matrix is up to date")
        
    except Exception as e:
        log.error(f"Error generating traceability matrix: {e}")
    
    return config

def generateTraceabilityMatrix(docsDir: Path) -> str:
    productDir = docsDir / "requirements" / "product"
    prqFiles = getPrqFiles(productDir)
    traceabilityData = buildTraceabilityData(prqFiles)
    return generateMarkdownContent(traceabilityData)

def readExistingTraceabilityContent(traceabilityFile: Path) -> str:
    try:
        with open(traceabilityFile, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log.warning(f"Could not read existing traceability file: {e}")
        return ""

def shouldUpdateTraceabilityFile(currentContent: str, newContent: str) -> bool:
    return currentContent != newContent

def writeTraceabilityFile(traceabilityFile: Path, content: str) -> None:
    traceabilityFile.parent.mkdir(parents=True, exist_ok=True)
    with open(traceabilityFile, 'w', encoding='utf-8') as f:
        f.write(content)

def getPrqFiles(productDir: Path) -> List[Path]:
    return sorted([f for f in productDir.glob("prq*.md") if f.name != "template.txt"])

def buildTraceabilityData(prqFiles: List[Path]) -> List[Tuple[str, str, str]]:
    traceabilityData = []
    for prqFile in prqFiles:
        prqTitle = getPrqTitle(prqFile)
        prqFilename = prqFile.name
        downstreamRefs = extractDownstreamRefs(prqFile)
        if downstreamRefs:
            traceabilityData.extend(buildTraceabilityRowsWithRefs(prqTitle, prqFilename, downstreamRefs))
        else:
            traceabilityData.append(buildTraceabilityRowWithoutRefs(prqTitle, prqFilename))
    return traceabilityData

def generateMarkdownContent(traceabilityData: List[Tuple[str, str, str]]) -> str:
    content = """# Requirements Traceability Matrix

This document provides a matrix to trace high-level product requirements (PRQs) through to user-centric customer requirements (CRQs) and finally to their technical implementations (TRQs). This ensures that all development work is directly linked to a defined product goal.

| Product Requirement (PRQ) | Customer Requirement (CRQ) | Technical Requirement (TRQ) |
| :--- | :--- | :--- |
"""
    
    for prq, crq, trq in traceabilityData:
        content += f"| {prq} | {crq} | {trq} |\n"
    
    return content

def getPrqTitle(filePath: Path) -> str:
    try:
        title = extractTitleFromFile(filePath)
        if title:
            return title
    except Exception as e:
        log.warning(f"Error reading title from {filePath}: {e}")
    
    return generateFallbackTitle(filePath)

def extractDownstreamRefs(filePath: Path) -> List[Tuple[str, str]]:
    refs = []
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()
        downstreamSection = re.search(r'## Down-stream references\s*\n(.*?)(?=\n##|\n#|\Z)', content, re.DOTALL | re.IGNORECASE)
        if not downstreamSection:
            downstreamSection = findAlternativeDownstreamSection(content)
        if downstreamSection:
            refs = extractReferencesFromSection(downstreamSection.group(1))
    except Exception as e:
        log.warning(f"Error processing {filePath}: {e}")
    return refs

def buildTraceabilityRowsWithRefs(prqTitle: str, prqFilename: str, downstreamRefs: List[Tuple[str, str]]) -> List[Tuple[str, str, str]]:
    rows = []
    for i, (crqTitle, crqPath) in enumerate(downstreamRefs):
        if i == 0:
            rows.append((
                f"**[{prqTitle}](product/{prqFilename})**",
                f"[{crqTitle}]({crqPath})",
                "*TBD*"
            ))
        else:
            rows.append((
                "",
                f"[{crqTitle}]({crqPath})",
                "*TBD*"
            ))
    return rows

def buildTraceabilityRowWithoutRefs(prqTitle: str, prqFilename: str) -> Tuple[str, str, str]:
    return (
        f"**[{prqTitle}](product/{prqFilename})**",
        "*No downstream requirements*",
        "*TBD*"
    )

def extractTitleFromFile(filePath: Path) -> str:
    with open(filePath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# PRQ-'):
                return line[2:].strip()
    return ""

def generateFallbackTitle(filePath: Path) -> str:
    stem = filePath.stem
    prqMatch = re.match(r'prq(\d+)-(.+)', stem)
    if prqMatch:
        num, title = prqMatch.groups()
        formattedTitle = formatTitleFromFilename(title)
        return f"PRQ-{num.zfill(2)}: {formattedTitle}"
    return stem

def findAlternativeDownstreamSection(content: str):
    return re.search(r'### Down-stream references\s*\n(.*?)(?=\n##|\n#|\Z)', content, re.DOTALL | re.IGNORECASE)

def extractReferencesFromSection(sectionContent: str) -> List[Tuple[str, str]]:
    refs = []
    linkPattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(linkPattern, sectionContent)
    for title, path in matches:
        if 'crq' in path.lower():
            filename = Path(path).name
            refs.append((title, f"customer/{filename}"))
    return refs

def formatTitleFromFilename(title: str) -> str:
    formattedTitle = title.replace('-', ' ').replace('_', ' ')
    return ' '.join(word.capitalize() for word in formattedTitle.split())

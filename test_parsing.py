#!/usr/bin/env python3
"""
Test script to verify the updated parsing logic captures full content from Docusaurus pages
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.parsers import extract_clean_text_from_html, parse_book_page

# Sample HTML from a Docusaurus page (similar to what we'd find in the textbook)
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Module 2: The Digital Twin (Gazebo & Unity)</title>
</head>
<body>
    <nav class="navbar">Navigation content</nav>
    <header>Header content</header>

    <article class="theme-doc-markdown">
        <h1>Module 2: The Digital Twin (Gazebo & Unity)</h1>
        <p>Digital twins provide virtual representations of physical systems, enabling design, testing, and validation of robotic systems in safe, controlled environments.</p>
        <h2>What is a Digital Twin?</h2>
        <p>A digital twin is a virtual representation of a physical system that mirrors the real-world object in real-time. In robotics, digital twins enable:</p>
        <ul>
            <li>Design validation without physical prototypes</li>
            <li>Testing of control algorithms in safe environments</li>
            <li>Optimization of robot performance before deployment</li>
        </ul>
        <h2>Gazebo Simulation</h2>
        <p>Gazebo is a powerful 3D simulation environment that provides realistic physics simulation, high-quality graphics, and convenient programmatic interfaces. It allows roboticists to:</p>
        <ul>
            <li>Test robot behaviors in realistic environments</li>
            <li>Validate control algorithms</li>
            <li>Simulate sensor data</li>
        </ul>
        <h2>Unity Integration</h2>
        <p>Unity provides a game-engine based simulation environment with advanced rendering capabilities. It's particularly useful for:</p>
        <ul>
            <li>High-fidelity visual simulation</li>
            <li>Virtual reality integration</li>
            <li>Complex environment modeling</li>
        </ul>
    </article>

    <aside class="toc">Table of contents</aside>
    <footer>Footer content</footer>
</body>
</html>
"""

print("Testing updated parsing logic...")
print("=" * 50)

# Test the extract_clean_text_from_html function
clean_content = extract_clean_text_from_html(sample_html, "https://example.com/module2")
print("Extracted content:")
print(clean_content)
print("=" * 50)

# Test the full parse_book_page function
book_content = parse_book_page(sample_html, "https://example.com/module2")
print("Parsed BookContent object:")
print(f"Title: {book_content.title}")
print(f"Content length: {len(book_content.content)} characters")
print(f"Content preview: {book_content.content[:200]}...")
print(f"Chapter: {book_content.chapter}")
print(f"Section: {book_content.section}")
print("=" * 50)

# Verify that we're getting more than just the title
if len(book_content.content) > len(book_content.title) * 2:
    print("[SUCCESS] Content extraction is working properly - full content captured")
else:
    print("[ISSUE] Content extraction may still be limited - only title captured")

print("\nContent contains expected phrases:")
expected_phrases = [
    "Digital twins provide virtual representations",
    "Gazebo is a powerful 3D simulation environment",
    "Unity provides a game-engine based simulation"
]

for phrase in expected_phrases:
    if phrase in book_content.content:
        print(f"[FOUND] '{phrase[:50]}...'")
    else:
        print(f"[MISSING] '{phrase[:50]}...'")
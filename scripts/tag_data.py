import json

def tag_content_manually(structured_chunks):
    """
    Iterates through content chunks and prompts the user for metadata.
    """
    tagged_chunks = []
    for i, chunk in enumerate(structured_chunks):
        print("-" * 50)
        print(f"Tagging Chunk {i+1}/{len(structured_chunks)}")
        print(f"Unit: {chunk.get('unit_name', 'N/A')}")
        print(f"Content: {chunk['content'][:300]}...")
        print("-" * 50)
        objectives = input("Enter Learning Objective(s) (comma-separated): ")
        difficulty = input("Enter Difficulty (easy, medium, hard): ")
        prerequisites = input("Enter Prerequisite Knowledge (comma-separated): ")
        chunk['metadata'] = {
            'learning_objectives': [obj.strip() for obj in objectives.split(',')],
            'difficulty': difficulty.strip().lower(),
            'prerequisites': [pre.strip() for pre in prerequisites.split(',')]
        }
        tagged_chunks.append(chunk)
        print("\nChunk tagged successfully!\n")
    return tagged_chunks

if __name__ == "__main__":
    # You should load structured_data from the output of parse_text.py
    with open('path/to/your/structured_data.json', 'r', encoding='utf-8') as f:  # <-- UPDATE THIS
        structured_data = json.load(f)
    tagged_data = tag_content_manually(structured_data)
    OUTPUT_JSON_PATH = 'tagged_knowledge_base.json'  # <-- UPDATE IF NEEDED
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(tagged_data, f, indent=4)
    print(f"--- Tagging complete. Knowledge base saved to {OUTPUT_JSON_PATH} ---")

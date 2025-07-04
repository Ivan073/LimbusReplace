import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

from line_profiler import profile

compiled_patterns = {}


def split_sentences(data):
    """Split string into sentences"""
    # Split by ". "
    sentences = re.split(r'(?<=\.)\s', data)
    sentences_with_space = [sentence + (' ' if i < len(sentences) - 1 else '') for i, sentence in enumerate(sentences)]
    # Split by \n
    final_result = []
    for sentence in sentences_with_space:
        split_by_newline = sentence.split('\n')
        for i, part in enumerate(split_by_newline):
            if '\n' in sentence and i < len(split_by_newline) - 1:
                final_result.append(part + '\n')
            else:
                final_result.append(part)

    return final_result


@profile
def replace_in_string(data, config, skillTagPersistency):
    """Replacement via regex in acquired strings"""
    global compiled_patterns
    sentences = split_sentences(data)
    processed_sentences = []

    for sentence in sentences:
        skill_tag_match = re.match(r'^\[(.*?)]', sentence) if skillTagPersistency else None

        for change in config.get('changes', []):
            from_pattern = change.get('from')
            to_pattern = change.get('to', '')
            use_regex = change.get('regex', False)

            if use_regex:
                pattern = compiled_patterns.get(from_pattern)
                try:
                    if skill_tag_match:
                        first_word = skill_tag_match.group(0)
                        rest_of_sentence = sentence[skill_tag_match.end():].lstrip()
                        rest_of_sentence = pattern.sub(to_pattern, rest_of_sentence)
                        sentence = f"{first_word} {rest_of_sentence}"
                    else:
                        sentence = pattern.sub(to_pattern, sentence)
                except Exception as e:
                    print(
                        f"Failed to apply <{from_pattern}> to <{sentence}>: {e}\n"
                        f"pattern: {pattern}\n"
                        f"to: {to_pattern}\n"
                    )
            else:
                sentence = sentence.replace(from_pattern, to_pattern)

        processed_sentences.append(sentence)

    return "".join(processed_sentences)


@profile
def recursive_replace(data, config_list, skillTagPersistency):
    """Recursive replace in JSON fields"""
    if isinstance(data, dict):
        for key in list(data.keys()):
            for config in config_list:
                if key in config['fields'] and isinstance(data[key], str):
                    data[key] = replace_in_string(data[key], config, skillTagPersistency)
            data[key] = recursive_replace(data[key], config_list, skillTagPersistency)
    elif isinstance(data, list):
        with ThreadPoolExecutor() as executor:
            data = list(executor.map(lambda item: recursive_replace(item, config_list, skillTagPersistency), data))
    return data


@profile
def add_status_regex(replace_config, status_processed_files):
    """Replace status names and ids with linked sprites"""
    from statuses import name_id_map
    ordered_status_names = sorted(name_id_map.items(), key=lambda x: len(x[0]), reverse=True)
    status_names = [re.escape(name) for name, _ in ordered_status_names]
    status_ids = [re.escape(id_) for _, id_ in ordered_status_names]
    pattern_names = r'(?<!\[)\b(' + '|'.join(status_names) + r')\b(?!\])'
    pattern_ids = r'\[(' + '|'.join(status_ids) + r')\]'

    name_to_id = dict(ordered_status_names)

    def repl_name(match):
        name = match.group(1)
        id_ = name_to_id[name]
        return f'<link="{id_}"><sprite name="{id_}"></link>'

    def repl_id(match):
        id_ = match.group(1)
        return f'<link="{id_}"><sprite name="{id_}"></link>'

    status_sprite_remove = {
        'fields': ['desc'],
        'changes': [{
            'from': rf"<sprite [^>]+><color[^>]+><u><link[^>]+>([^>]+)</color></link></u>",
            'to': rf"\1", 'regex': True
        }],
        'ignoredFiles': status_processed_files
    }
    status_name_replace = {
        'fields': ['desc'],
        'changes': [{'from': pattern_names, 'to': repl_name, 'regex': True}],
        'ignoredFiles': status_processed_files
    }
    status_id_replace = {
        'fields': ['desc'],
        'changes': [{'from': pattern_ids, 'to': repl_id, 'regex': True}],
        'ignoredFiles': status_processed_files
    }
    replace_config.append(status_sprite_remove)
    replace_config.append(status_name_replace)
    replace_config.append(status_id_replace)


@profile
def process_replaces(directory, config, status_processed_files):
    replace_config = config['replace']
    skillTagPersistency = config['skillTagPersistency']
    add_status_regex(replace_config, status_processed_files)

    total_files = sum(1 for filename in os.listdir(directory) if filename.endswith('.json'))
    processed_count = 0

    # Pattern compilation for perfomance boost
    global compiled_patterns
    for replace in replace_config:
        for change in replace["changes"]:
            if change.get('regex') and change['regex'] and change['from'] not in compiled_patterns:
                compiled_patterns[change['from']] = re.compile(rf'{change["from"]}')

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            path = os.path.join(directory, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                active_replaces = [
                    r for r in replace_config
                    if filename not in r.get('ignoredFiles', [])
                ]
                modified_data = recursive_replace(data, active_replaces, skillTagPersistency)

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(modified_data, f, indent=4, ensure_ascii=False)

                processed_count += 1
                print(f"{filename} processed ({processed_count}/{total_files})")

            except Exception as e:
                print(f"Error in file {filename}: {str(e)}")

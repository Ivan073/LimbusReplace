import json
import os
import re
from line_profiler import profile
from concurrent.futures import ThreadPoolExecutor


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
    # Разбиваем текст на предложения
    sentences = split_sentences(data)
    processed_sentences = []
    for sentence in sentences:
        for change in config['changes']:
            if change.get('regex') and change['regex']:
                pattern = compiled_patterns.get(change['from'])
                if pattern:
                    try:
                        skillTagMatch = re.match(r'^\[(.*?)\]', sentence)
                        if skillTagPersistency and skillTagMatch:
                            first_word = skillTagMatch.group(0)
                            rest_of_sentence = sentence[skillTagMatch.end():].lstrip()
                            rest_of_sentence = pattern.sub(change['to'], rest_of_sentence)
                            sentence = first_word + ' ' + rest_of_sentence
                        else:
                            # Если нет, то просто проводим замену во всём предложении
                            sentence = pattern.sub(change['to'], sentence)
                    except Exception as e:
                        print(
                            f"Failed to apply <{change['from']}> to <{sentence}>: {str(e)}\npattern:{pattern}\nto: {change['to']}\n")
            else:
                sentence = sentence.replace(change['from'], change['to'])
        processed_sentences.append(sentence)

    processed_data = "".join(processed_sentences)
    return processed_data


@profile
def recursive_replace(data, config_list, skillTagPersistency):
    """Recursive replace in JSON fields"""
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key in [field for config in config_list for field in config['fields']]:
                if isinstance(data[key], str):
                    for config in config_list:
                        if key in config['fields']:
                            data[key] = replace_in_string(data[key], config, skillTagPersistency)
            else:
                data[key] = recursive_replace(data[key], config_list, skillTagPersistency)
    elif isinstance(data, list):
        with ThreadPoolExecutor() as executor:
            data = list(executor.map(lambda item: recursive_replace(item, config_list, skillTagPersistency), data))
    return data


@profile
def process_replaces(directory, config, status_processed_files):
    replace_config = config['replace']
    skillTagPersistency = config['skillTagPersistency']
    from statuses import name_id_map
    # Additional replaces for collected statuses
    status_replace = {
        'fields': ['desc'],
        'changes': [{'from': f"\\b{re.escape(k)}\\b", 'to': v, 'regex': True} for k, v in name_id_map.items()],
        'ignoredFiles': status_processed_files
    }
    replace_config.append(status_replace)

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

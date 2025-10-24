class Utils:
    @staticmethod
    def remove_duplicate_example(examples, text):
        filtered = []
        i = 0
        while i < len(examples):
            msg = examples[i]
            if msg['role'] == 'user' and text.strip().lower() in msg['content'].lower():
                print("few-shot example matched!!")
                i += 2 if i + 1 < len(examples) and examples[i + 1]['role'] == 'assistant' else 1
            else:
                filtered.append(msg)
                i += 1
        return filtered

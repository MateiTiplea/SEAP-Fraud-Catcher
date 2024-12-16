import os

from seap_api.decision_module.StringClustering import StringClastering

call_history = []

def log_to_file(message, filename="clean_validate_history.txt"):
    log_dir = os.path.dirname(filename)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def monitor_function_with_history(func):
    def wrapper(*args, **kwargs):
        global call_history
        call_history.append(func.__name__)
        log_to_file(f"Se execută {func.__name__} cu parametrii: {args}, {kwargs}")
        result = func(*args, **kwargs)
        log_to_file(f"Rezultat {func.__name__}: {result}")
        return result
    return wrapper


class EnhancedClustering(StringClastering):

    @monitor_function_with_history
    def clean_invalid_items(self):
        """
        Elimină item-urile care nu respectă  reguli de validitate.
        """
        print("Executing CLEAN")
        valid_items = []
        for item in self.list_of_items:
            if item.name and item.closing_price > 0 and item.quantity > 0:
                valid_items.append(item)
            else:
                print(f"Invalid item removed: {item.name if item.name else 'Unnamed Item'}")
        self.list_of_items = valid_items

    @monitor_function_with_history
    def validate_items(self, log_filename="validation_log.txt"):
        """
        Validează dacă toate item-urile respectă structura așteptată și scrie logurile într-un fișier text.
        """

        if "clean_invalid_items" not in call_history:
            self.clean_invalid_items()

        with open(log_filename, "w", encoding="utf-8") as log_file:
            log_file.write("Executing VALIDATE\n")
            if not self.list_of_items:
                log_file.write("Validation failed: No items found!\n")
                return False

            for index, item in enumerate(self.list_of_items):
                log_file.write(
                    f"Validating item {index + 1}/{len(self.list_of_items)}: {item.name if item.name else 'Unnamed Item'}\n")
                if not all([item.name, item.cpv_code_id, item.closing_price]):
                    log_file.write(
                        f"Validation failed for item {index + 1}: Missing fields in item {item.name if item.name else 'Unnamed Item'}\n")
                    return False
                else:
                    log_file.write(f"Item {index + 1} passed validation.\n")

            log_file.write("Validation successful\n")
            return True



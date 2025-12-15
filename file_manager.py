import os
import logging
from functools import wraps
from typing import Any, Dict
import yaml


class FileCorruptedError(Exception):
    def __init__(self, filepath, reason=""):
        self.filepath = filepath
        self.reason = reason
        message = f"The file is corrupted: {filepath}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


def logged(exception_type, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.INFO)
            logger.handlers.clear()

            handler = (
                logging.StreamHandler() if mode == "console"
                else logging.FileHandler("operations.log", encoding="utf-8")
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            try:
                logger.info(f"Performing the operation: {func.__name__}")
                result = func(*args, **kwargs)
                logger.info(f"The operation was completed successfully")
                return result

            except exception_type as e:
                logger.error(f"An exception {exception_type.__name__}: {str(e)}")
                raise

            except Exception as e:
                logger.error(f"An unexpected incident {type(e).__name__}: {str(e)}")
                raise

            finally:
                handler.close()
                logger.removeHandler(handler)

        return wrapper
    return decorator


class YAMLFileHandler:

    def __init__(self, filepath: str):
        self.filepath = filepath

        # AUTOMATIC FILE CREATION 
        if not os.path.exists(self.filepath):
            print(f"File not found - creating a new one: {self.filepath}")
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.dump({}, f, allow_unicode=True)

    @logged(FileCorruptedError, mode="console")
    def read(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}

        except yaml.YAMLError as e:
            raise FileCorruptedError(self.filepath, f"Error YAML: {e}")

        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Read error: {e}")

    @logged(FileCorruptedError, mode="file")
    def write(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.filepath, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)

        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Write error: {e}")

    @logged(FileCorruptedError, mode="file")
    def append(self, data: Dict[str, Any]) -> None:
        try:
            if not isinstance(data, dict):
                self.write(data)
                return
        
            existing = self.read()

            if existing is None:
                self.write(data)
                return

            if isinstance(existing, dict):
                existing.update(data)
                self.write(existing)
            else:
                raise FileCorruptedError(
                    self.filepath,
                    f"Existing data is of wrong type ({type(existing).__name__}), expected dict."
            )
        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Posting error: {e}")

def main():
    test_file = "test_data.yaml"

    print("\n--- Тест 1: Create/verify file ---")
    handler = YAMLFileHandler(test_file)

    print("\n--- Тест 2: Initial content ---")
    print(handler.read())

    print("\n--- Тест 3: Data recording ---")
    handler.write({
        "name": "Ivan Petrenko",
        "age": 20,
        "university": "NULP",
        "subjects": ["Math, History, Phisics"]
    })
    print(handler.read())

    print("\n--- Тест 4: Adding data ---")
    handler.append({"semester": 2, "grade": "A"})
    print(handler.read())

    print("\n--- Тест 5: Corrupted YAML file ---")
    corrupted = "corrupted.yaml"
    with open(corrupted, "w", encoding="utf-8") as f:
        f.write("invalid: : yaml: broken::: text")

    try:
        bad = YAMLFileHandler(corrupted)
        bad.read()
    except FileCorruptedError as e:
        print("Сaught:", e)

    print("\n--- Cleaning ---")
    os.remove(test_file)
    os.remove(corrupted)
    print("Files deleted.")

    print("\n Check operations.log for logs.")


if __name__ == "__main__":
    main()

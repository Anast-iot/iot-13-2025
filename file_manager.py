import os
import logging
from functools import wraps
from typing import Any, Dict
import yaml


class FileCorruptedError(Exception):
    def __init__(self, filepath, reason=""):
        self.filepath = filepath
        self.reason = reason
        message = f"Файл пошкоджено: {filepath}"
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
                logger.info(f"Виконання операції: {func.__name__}")
                result = func(*args, **kwargs)
                logger.info(f"Операція успішно завершена")
                return result

            except exception_type as e:
                logger.error(f"Виняток {exception_type.__name__}: {str(e)}")
                raise

            except Exception as e:
                logger.error(f"Несподіваний виняток {type(e).__name__}: {str(e)}")
                raise

            finally:
                handler.close()
                logger.removeHandler(handler)

        return wrapper
    return decorator


class YAMLFileHandler:

    def __init__(self, filepath: str):
        self.filepath = filepath

        # ▶ AUTOMATIC FILE CREATION ◀
        if not os.path.exists(self.filepath):
            print(f"Файл не знайдено — створюю новий: {self.filepath}")
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.dump({}, f, allow_unicode=True)

    @logged(FileCorruptedError, mode="console")
    def read(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}

        except yaml.YAMLError as e:
            raise FileCorruptedError(self.filepath, f"Помилка YAML: {e}")

        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Помилка читання: {e}")

    @logged(FileCorruptedError, mode="file")
    def write(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.filepath, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)

        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Помилка запису: {e}")

    @logged(FileCorruptedError, mode="file")
    def append(self, data: Dict[str, Any]) -> None:
        try:
            existing = self.read()

            if isinstance(existing, dict) and isinstance(data, dict):
                existing.update(data)
            else:
                existing = data

            self.write(existing)

        except Exception as e:
            raise FileCorruptedError(self.filepath, f"Помилка дописування: {e}")


def main():
    test_file = "test_data.yaml"

    print("\n--- Тест 1: Створення/перевірка файлу ---")
    handler = YAMLFileHandler(test_file)

    print("\n--- Тест 2: Початковий вміст ---")
    print(handler.read())

    print("\n--- Тест 3: Запис даних ---")
    handler.write({
        "name": "Іван Петренко",
        "age": 20,
        "university": "НУЛП",
        "subjects": ["Математика", "Історія", "Фізика"]
    })
    print(handler.read())

    print("\n--- Тест 4: Дописування даних ---")
    handler.append({"semester": 2, "grade": "A"})
    print(handler.read())

    print("\n--- Тест 5: Пошкоджений файл YAML ---")
    corrupted = "corrupted.yaml"
    with open(corrupted, "w", encoding="utf-8") as f:
        f.write("invalid: : yaml: broken::: text")

    try:
        bad = YAMLFileHandler(corrupted)
        bad.read()
    except FileCorruptedError as e:
        print("Спіймано:", e)

    print("\n--- Очищення ---")
    os.remove(test_file)
    os.remove(corrupted)
    print("Файли видалено.")

    print("\nПеревірте operations.log для логів.")


if __name__ == "__main__":
    main()

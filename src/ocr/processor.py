import concurrent.futures

from src.ocr.strategies import (
    MarkerOcrStrategy,
    MistralOcrStrategy,
    OcrStrategy,
    PyMuPdfOcrStrategy,
)


class OcrProcessor:
    def __init__(self):
        self.strategies: dict[str, list[type[OcrStrategy]]] = {
            "pdf": [PyMuPdfOcrStrategy, MarkerOcrStrategy, MistralOcrStrategy],
            "image": [MistralOcrStrategy],
        }

    def process(self, file_path: str) -> dict[str, str]:
        file_type = self._get_file_type(file_path)
        if not file_type:
            print(f"Unsupported file type for: {file_path}")
            return {}

        results = {}
        strategies_to_run = self.strategies.get(file_type, [])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_strategy = {}
            for strategy_class in strategies_to_run:
                future = executor.submit(strategy_class().execute, file_path)
                future_to_strategy[future] = strategy_class.__name__

            for future in concurrent.futures.as_completed(future_to_strategy):
                strategy_name = future_to_strategy[future]
                try:
                    result = future.result()
                    if result:
                        results[strategy_name] = result
                except Exception as exc:
                    print(f"{strategy_name} generated an exception: {exc}")

        return results

    def _get_file_type(self, file_path: str) -> str | None:
        if file_path.lower().endswith(".pdf"):
            return "pdf"
        elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            return "image"
        return None


if __name__ == "__main__":
    import pandas as pd

    processor = OcrProcessor()
    df = pd.read_csv("data/list.csv")
    file_to_process = df.iloc[3]["path"]

    ocr_results = processor.process(file_to_process)

    print(type(ocr_results))
    print(len(ocr_results))
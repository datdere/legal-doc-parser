import logging
import os

from helpers.markdown_renderer import render_markdown_to_html, render_plain_text_to_html
from models.conversion_result import ConversionResult
from models.enums import OutputFormat

logger = logging.getLogger(__name__)


class FileExportService:
    def save(
        self,
        result: ConversionResult,
        output_path: str,
        fmt: OutputFormat,
    ) -> bool:
        if not result.success or not result.content:
            return False

        try:
            parent = os.path.dirname(output_path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            content = result.content
            if fmt == OutputFormat.HTML:
                content = render_markdown_to_html(content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError as e:
            logger.error("파일 저장 실패 (%s): %s", output_path, e)
            return False

    def save_batch(
        self,
        items: list[tuple[str, ConversionResult]],
        output_dir: str,
        fmt: OutputFormat,
    ) -> list[tuple[str, bool]]:
        os.makedirs(output_dir, exist_ok=True)
        results: list[tuple[str, bool]] = []

        for source_path, conv_result in items:
            if not conv_result.success:
                results.append((source_path, False))
                continue

            base_name = os.path.splitext(os.path.basename(source_path))[0]
            output_path = os.path.join(output_dir, base_name + fmt.extension)

            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base_name}_{counter}{fmt.extension}")
                counter += 1

            success = self.save(conv_result, output_path, fmt)
            results.append((source_path, success))

        return results

    @staticmethod
    def get_extension(fmt: OutputFormat) -> str:
        return fmt.extension

    @staticmethod
    def render_for_display(content: str, fmt: OutputFormat) -> str:
        if fmt == OutputFormat.MARKDOWN:
            return render_markdown_to_html(content)
        elif fmt == OutputFormat.HTML:
            return content
        else:
            return render_plain_text_to_html(content)

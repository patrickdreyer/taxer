from .csvWriter import CsvWriter


class WriterFactory:
    def create(self, format):
        return CsvWriter()

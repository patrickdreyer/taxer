import logging
from xml.sax.saxutils import unescape

from odf.opendocument import OpenDocumentSpreadsheet
from odf.opendocument import load
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.style import Style, TableProperties, TextProperties, TableCellProperties, TableColumnProperties, Map
from odf.number import NumberStyle, DateStyle, CurrencyStyle, TextStyle, Number, Text, Day, Month, Year, Era
from odf.text import P, Date


class ShareholderFile:
    __fileName = 'Shareholder.ods'

    __log = logging.getLogger(__name__)

    def __init__(self):
        self.__tables = list()

    def load(self, filePath):
        doc = load(filePath)
        for sourceTable in doc.getElementsByType(Table):
            destinationTable = list()
            y = 0
            for row in sourceTable.getElementsByType(TableRow):
                x = 1
                y += 1
                for cell in row.getElementsByType(TableCell):
                    text = self.__getCellText(cell)
            self.__tables.append(destinationTable)
	
    def __getCellText(self, cell):
        text = ''
        for p in cell.getElementsByType(P):
            for p_data in p.childNodes:
                if p_data.tagName == 'Text':
                    data = p_data.data
                    text += unescape(data.encode('utf-8'))
                if p_data.tagName == 'text:span':
                    data = p_data.firstChild
                if data:
                    text += unescape(data.data.encode('utf-8'))
		
        return text

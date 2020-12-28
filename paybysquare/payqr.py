import base64
import binascii
import lzma
import os
import re
import typing
from dataclasses import dataclass, fields

import qrcode
import qrcode.image.svg
from lxml import etree as ET
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser

from .model.bysquare_pay_1_1_0 import Pay


@dataclass
class InvalidHeaderField(Exception):
    field: str
    value: int


@dataclass
class BySquareInfo:
    priority: int
    order: int
    max_length: int

    @staticmethod
    def init(attrib: dict):
        return BySquareInfo(
            priority=attrib.get('{http://www.bysquare.com/bysquare-addons}priority'),
            order=attrib.get('{http://www.bysquare.com/bysquare-addons}order'),
            max_length=attrib.get('{http://www.bysquare.com/bysquare-addons}maxLength'))


@dataclass
class Attribute:
    name: str
    info: BySquareInfo

    @staticmethod
    def extract_attributes(type: ET.Element):
        list_result = [Attribute(el.attrib['name'], BySquareInfo.init(el.attrib)) for el in
                       type.findall('.//{*}element')]
        list_result.sort(key=lambda x: int(x.info.order))
        return list_result


def _get_attribute(instance, attribute_name):
    if hasattr(instance, attribute_name):
        return getattr(instance, attribute_name)
    else:
        for field in filter(lambda x: x.metadata.get('name') == attribute_name, fields(instance)):
            return getattr(instance, field.name)


def _get_attribute_type(instance, attribute_name):
    for field in filter(lambda x: x.metadata.get('name') == attribute_name, fields(instance)):
        return field.type


class PayBySquare:
    _schema = ET.parse(os.path.dirname(__file__) + os.sep + 'bysquare-pay-1_1_0.xsd')
    _parser = XmlParser()
    _enumerations = {
        x.attrib['name']: {y.attrib['value']: y.find('.//{*}appinfo').text for y in x.findall('.//{*}enumeration')}
        for x in _schema.findall('.//{*}simpleType') if x.find('.//{*}enumeration') is not None}
    _info_type = {el.attrib['name']: Attribute.extract_attributes(el) for el in _schema.findall('.//{*}complexType')}
    _by_square_type = _schema.find('.//{*}element[@name="Pay"]').attrib[
        '{http://www.bysquare.com/bysquare-addons}bysquareType']
    _version = _schema.find('.//{*}element[@name="Pay"]').attrib['{http://www.bysquare.com/bysquare-addons}version']
    _document_type = _schema.find('.//{*}complexType[@name="Pay"]').attrib[
        '{http://www.bysquare.com/bysquare-addons}documentType']
    _reserved = '0'
    _separator = '\t'
    _date_pattern = re.compile('\d{4}-\d{2}-\d{2}')

    def __init__(self):
        self.parser = XmlParser(context=XmlContext())

    def generate_qr(self, input):
        if isinstance(input, bytearray) or isinstance(input, bytes):
            pay = self.parser.from_bytes(input, Pay)
        else:
            pay = self.parser.parse(input, Pay)
        type_name = type(pay).__name__

        result = self._process_attributes(pay)
        result = ''.join(result).encode('utf-8')
        result = binascii.crc32(result).to_bytes(4, 'little') + result
        length = len(result)
        result = Base32Hex.encode(self._header() + length.to_bytes(2, 'little') + LZMA.compress(result))
        return qrcode.make(result, image_factory=qrcode.image.svg.SvgImage)

    def _process_attributes(self, instance):
        result = []
        definition = self._type_definition(type(instance))
        for attrib in definition:
            result.extend(self._process_attribute(instance, attrib.name))
        return result

    def _process_attribute(self, instance, attribute_name):
        result = []
        value = _get_attribute(instance, attribute_name)
        attribute_type = _get_attribute_type(instance, attribute_name)
        attribute_type_nape = typing.get_args(attribute_type)[0].__name__
        is_type = attribute_type_nape in self._info_type
        is_enumeration = attribute_type_nape in self._enumerations

        if value is None:
            if is_type:
                result.append(str(0))
                result.append(self._separator)
            else:
                result.append(self._separator)
        elif is_type:
            if isinstance(value, list):
                result.append(str(len(value)))
                result.append(self._separator)
                for v in value:
                    result.extend(self._process_attributes(v))
            else:
                result.extend(self._process_attributes(value))
        elif is_enumeration:
            if isinstance(value, list):
                res = 0
                for v in value:
                    res += int(self._enumerations.get(type(v).__name__).get(v.value))
                result.append(str(res))
                result.append(self._separator)
            else:
                result.append(str(self._enumerations.get(type(value).__name__).get(value.value)))
                result.append(self._separator)
        else:
            value = str(value)
            if self._date_pattern.match(value):
                value = value.replace('-', '')
            result.append(value)
            result.append(self._separator)
        return result

    def _type_definition(self, clz):
        type_name = clz.__name__
        info = self._info_type.get(type_name)
        if info is None:
            return None
        if info:
            return info
        else:
            return self._type_definition(clz.__base__)

    def _decode_header(self, data: typing.Union[bytes, bytearray]):
        header = data[0:2].hex()

        by_square_type = int(header[0], 16)
        if by_square_type != self._by_square_type:
            raise InvalidHeaderField('BySquareType', by_square_type)
        version = int(header[1], 16)
        if version != self._version:
            raise InvalidHeaderField('Version', version)
        document_type = int(header[2], 16)
        if version != self._version:
            raise InvalidHeaderField('DocumentType', document_type)
        return data[2:]

    def _header(self):
        header = self._by_square_type + self._version + self._document_type + self._reserved
        return bytes.fromhex(header)


class LZMA:
    _filters = {"id": lzma.FILTER_LZMA1, "dict_size": 1 << 17, "lc": 3, "lp": 0, "pb": 2, }

    @staticmethod
    def decompress(compressed):
        return lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[LZMA._filters]).decompress(compressed)

    @staticmethod
    def compress(data):
        return lzma.compress(data, format=lzma.FORMAT_RAW, filters=[LZMA._filters])


class Base32Hex:
    _b32_alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    _b32hex_alphabet = b'0123456789ABCDEFGHIJKLMNOPQRSTUV'
    _translate_b32_to_b32hex = bytes.maketrans(_b32_alphabet, _b32hex_alphabet)
    _translate_b32hex_to_b32 = bytes.maketrans(_b32hex_alphabet, _b32_alphabet)

    @staticmethod
    def decode(data: typing.Union[bytes, bytearray]):
        if len(data) % 8: data = data.ljust(len(data) + 8 - len(data) % 8, b'=')
        return base64.b32decode(data.translate(Base32Hex._translate_b32hex_to_b32))

    @staticmethod
    def encode(data: typing.Union[bytes, bytearray]):
        return base64.b32encode(data).translate(Base32Hex._translate_b32_to_b32hex)

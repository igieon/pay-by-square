#!/usr/bin/env python3
import argparse
import os
import re
# from lxml import etree as ET
import xml.etree.ElementTree as ET
from paybysquare.payqr import PayBySquare
from dataclasses import dataclass, fields


@dataclass
class Payment:
    beneficiaryName: str = None
    amount: any = None
    variableSymbol: str = None
    constantSymbol: str = None
    specificSymbol: str = None
    iban: str = None
    date: str = None

    def __str__(self):
        res = ''
        for i in fields(self):
            res += f'{i.name}: {getattr(self, i.name)}<br/>\n'
        return res


def get_cli_args():
    parser = argparse.ArgumentParser(description='Generate qr code page')

    parser.add_argument('--input', '-i', required=True, help='input xml')
    parser.add_argument('--output', '-o', default='output', help='default output dir')
    parser.add_argument('--all', '-a', action='store_true')
    parser.add_argument('--date', default=None, help='Include date')
    return parser.parse_args()


vs_ss_ks_pattern = re.compile('/VS(.*)/SS(.*)/KS(.*)')


def generate_paymenent_xml(input_xml, all=False, date=False):
    input = ET.parse(input_xml)
    output = ET.Element('Pay')
    output.attrib['xmlns'] = "http://www.bysquare.com/bysquare"
    payments = ET.SubElement(output, 'Payments')
    for localPayment in input.findall('.//{*}CdtTrfTxInf'):
        payment = ET.SubElement(payments, 'Payment')
        p = Payment()
        ET.SubElement(payment, 'PaymentOptions').text = 'paymentorder'
        p.amount = localPayment.find('.//{*}InstdAmt').text
        ET.SubElement(payment, 'Amount').text = p.amount
        ET.SubElement(payment, 'CurrencyCode').text = localPayment.find('.//{*}InstdAmt').attrib['Ccy']
        if date:
            p.date = input.find('.//{*}ReqdExctnDt').text
            ET.SubElement(payment, 'PaymentDueDate').text = p.date
        match = vs_ss_ks_pattern.search(localPayment.find('.//{*}EndToEndId').text)
        if match:
            p.variableSymbol = match.group(1)
            p.constantSymbol = match.group(3)
            p.specificSymbol = match.group(2)
            ET.SubElement(payment, 'VariableSymbol').text = p.variableSymbol
            ET.SubElement(payment, 'ConstantSymbol').text = p.constantSymbol
            ET.SubElement(payment, 'SpecificSymbol').text = p.specificSymbol
        element = localPayment.find('.//{*}Ustrd')
        if element is not None:
            ET.SubElement(payment, 'PaymentNote').text = element.text
        bank_accounts = ET.SubElement(payment, 'BankAccounts')
        bank_account = ET.SubElement(bank_accounts, 'BankAccount')
        p.iban = localPayment.find('.//{*}IBAN').text
        ET.SubElement(bank_account, 'IBAN').text = p.iban
        ET.SubElement(bank_account, 'BIC').text = localPayment.find('.//{*}BIC').text
        p.beneficiaryName = localPayment.find('.//{*}Nm').text
        ET.SubElement(payment, 'BeneficiaryName').text = p.beneficiaryName
        if not all:
            yield (p, ET.tostring(output, encoding='utf-8'))
            payments.clear()
    if all:
        yield ('All', ET.tostring(output, encoding='utf-8'))


if __name__ == '__main__':
    arguments = get_cli_args()
    if not os.path.exists(arguments.output):
        os.makedirs(arguments.output)
    generator = PayBySquare()
    with open(arguments.output + os.sep + 'index.html', 'w') as f:
        for index, i in enumerate(generate_paymenent_xml(arguments.input, arguments.all, arguments.date)):
            f.write(f'<p>{i[0]}</p> <img src="qr{index}.svg">')
            img = generator.generate_qr(i[1])
            img.save(arguments.output + os.sep + f'qr{index}.svg')

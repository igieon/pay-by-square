#!/usr/bin/env python3
import argparse
import os
import re
# from lxml import etree as ET
import xml.etree.ElementTree as ET
from  paybysquare.payqr import PayBySquare

def get_cli_args():
    parser = argparse.ArgumentParser(description='Generate qr code page')

    parser.add_argument('--input', '-i', required=True, help='input xml')
    parser.add_argument('--output', '-o', default='output', help='default output dir')
    parser.add_argument('--all', '-a', action='store_true')

    return parser.parse_args()


vs_ss_ks_pattern = re.compile('/VS(.*)/SS(.*)/KS(.*)')


def generate_paymenent_xml(input_xml):
    input = ET.parse(input_xml)
    output = ET.Element('Pay')
    output.attrib['xmlns'] = "http://www.bysquare.com/bysquare"
    payments = ET.SubElement(output, 'Payments')
    for localPayment in input.findall('.//{*}CdtTrfTxInf'):
        payment = ET.SubElement(payments, 'Payment')
        ET.SubElement(payment, 'PaymentOptions').text = 'paymentorder'
        ET.SubElement(payment, 'Amount').text = localPayment.find('.//{*}InstdAmt').text
        ET.SubElement(payment, 'CurrencyCode').text = localPayment.find('.//{*}InstdAmt').attrib['Ccy']
        # ET.SubElement(payment,  'PaymentDueDate').text = input.find('//{*}ReqdExctnDt').text
        match = vs_ss_ks_pattern.search(localPayment.find('.//{*}EndToEndId').text)
        if match:
            ET.SubElement(payment, 'VariableSymbol').text = match.group(1)
            ET.SubElement(payment, 'ConstantSymbol').text = match.group(3)
            ET.SubElement(payment, 'SpecificSymbol').text = match.group(2)
        element = localPayment.find('.//{*}Ustrd')
        if element is not None:
            ET.SubElement(payment, 'PaymentNote').text = element.text
        bank_accounts = ET.SubElement(payment, 'BankAccounts')
        bank_account = ET.SubElement(bank_accounts, 'BankAccount')
        ET.SubElement(bank_account, 'IBAN').text = localPayment.find('.//{*}IBAN').text
        ET.SubElement(bank_account, 'BIC').text = localPayment.find('.//{*}BIC').text
        whom = localPayment.find('.//{*}Nm').text
        ET.SubElement(payment, 'BeneficiaryName').text = whom
        yield (whom, ET.tostring(output,encoding='utf-8'))
        payments.clear()

def generate_paymenent_xml_all(input_xml):
    input = ET.parse(input_xml)
    output = ET.Element('Pay')
    output.attrib['xmlns'] = "http://www.bysquare.com/bysquare"
    payments = ET.SubElement(output, 'Payments')
    for localPayment in input.findall('.//{*}CdtTrfTxInf'):
        payment = ET.SubElement(payments, 'Payment')
        ET.SubElement(payment, 'PaymentOptions').text = 'paymentorder'
        ET.SubElement(payment, 'Amount').text = localPayment.find('.//{*}InstdAmt').text
        ET.SubElement(payment, 'CurrencyCode').text = localPayment.find('.//{*}InstdAmt').attrib['Ccy']
        # ET.SubElement(payment,  'PaymentDueDate').text = input.find('//{*}ReqdExctnDt').text
        match = vs_ss_ks_pattern.search(localPayment.find('.//{*}EndToEndId').text)
        if match:
            ET.SubElement(payment, 'VariableSymbol').text = match.group(1)
            ET.SubElement(payment, 'ConstantSymbol').text = match.group(3)
            ET.SubElement(payment, 'SpecificSymbol').text = match.group(2)
        element = localPayment.find('.//{*}Ustrd')
        if element is not None:
            ET.SubElement(payment, 'PaymentNote').text = element.text
        bank_accounts = ET.SubElement(payment, 'BankAccounts')
        bank_account = ET.SubElement(bank_accounts, 'BankAccount')
        ET.SubElement(bank_account, 'IBAN').text = localPayment.find('.//{*}IBAN').text
        ET.SubElement(bank_account, 'BIC').text = localPayment.find('.//{*}BIC').text
        whom = localPayment.find('.//{*}Nm').text
        ET.SubElement(payment, 'BeneficiaryName').text = whom
    return ET.tostring(output,encoding='utf-8')

if __name__ == '__main__':
    arguments = get_cli_args()
    if not os.path.exists(arguments.output):
        os.makedirs(arguments.output)
    generator = PayBySquare()
    if arguments.all:
        img = generator.generate_qr(generate_paymenent_xml_all(arguments.input))
        img.save(arguments.output +os.sep + f'all.svg')

    else:
        with open(arguments.output +os.sep + 'index.html','w') as f:
            for index,i in enumerate(generate_paymenent_xml(arguments.input)):
                f.write(f'<p>{i[0]}</p> <img src="qr{index}.svg">')
                img = generator.generate_qr(i[1])
                img.save(arguments.output +os.sep + f'qr{index}.svg')

# Pay by square
Python library implementation of pay by square qr-code generation. Implementation is based on https://www.sbaonline.sk/wp-content/uploads/2020/03/pay-by-square-specifications-1_1_0.pdf. More information https://www.sbaonline.sk/projekt/projekty-z-oblasti-platobnych-sluzieb/.

##Usage

Example of use in [generate_html.py](generate_html.py)

Or here generate svg image of qrcode.
```python
from  paybysquare.payqr import PayBySquare

input_xml = b'''<?xml version="1.0"?>
<Pay xmlns="http://www.bysquare.com/bysquare">
	<Payments>
		<Payment>
			<BankAccounts>
				<BankAccount>
					<IBAN>SK7700000000000000000000</IBAN>
					<BIC>SPSRSKBA</BIC>
				</BankAccount>
			</BankAccounts>
			<VariableSymbol>0000000000</VariableSymbol>
			<ConstantSymbol>1148</ConstantSymbol>
			<Amount>1.46</Amount>
			<CurrencyCode>EUR</CurrencyCode>
			<PaymentDueDate>2020-12-28</PaymentDueDate>
			<BeneficiaryName>Danovyurad</BeneficiaryName>
			<PaymentOptions>paymentorder</PaymentOptions>
		</Payment>
	</Payments>
</Pay>'''
generator = PayBySquare()
img = generator.generate_qr(input_xml)
img.save('test.svg')
```
## Development environment

```bash
python3 -m venv .venv
#or 
# virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

#optional
./generate.sh
```

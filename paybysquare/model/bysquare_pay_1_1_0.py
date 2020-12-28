from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = "http://www.bysquare.com/bysquare"


@dataclass
class BankAccount:
    """
    single bank account.

    :ivar iban: IBAN code
    :ivar bic: SWIFT code
    """
    iban: Optional[str] = field(
        default=None,
        metadata={
            "name": "IBAN",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
            "pattern": r"[A-Z]{2}[0-9]{2}[A-Z0-9]{0,30}",
        }
    )
    bic: Optional[str] = field(
        default=None,
        metadata={
            "name": "BIC",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[A-Z]{4}[A-Z]{2}[A-Z\d]{2}([A-Z\d]{3})?",
        }
    )


@dataclass
class BySquareDocument:
    pass


class DirectDebitScheme(Enum):
    """direct debit scheme, can be "SEPA" or "other".

    Use "SEPA" if direct debit complies with SEPA direct debit scheme
    """
    OTHER = "other"
    SEPA = "SEPA"


class DirectDebitType(Enum):
    """
    type of direct debit, can be "one-off" or "recurrent".
    """
    ONE_OFF = "one-off"
    RECURRENT = "recurrent"


class Month(Enum):
    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


class PaymentOption(Enum):
    PAYMENTORDER = "paymentorder"
    STANDINGORDER = "standingorder"
    DIRECTDEBIT = "directdebit"


class Periodicity(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    BIMONTHLY = "Bimonthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"
    SEMIANNUALLY = "Semiannually"


@dataclass
class BankAccounts:
    """
    :ivar bank_account: single bank account
    """
    bank_account: List[BankAccount] = field(
        default_factory=list,
        metadata={
            "name": "BankAccount",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "min_occurs": 1,
        }
    )


@dataclass
class DirectDebitExt:
    """direct debit extension.

    Extends basic payment information with information required for
    identification and setup of direct debit

    :ivar direct_debit_scheme: direct debit scheme, can be "SEPA" or
        "other". Use "SEPA" if direct debit complies with SEPA direct
        debit scheme
    :ivar direct_debit_type: type of direct debit, can be "one-off" or
        "recurrent"
    :ivar variable_symbol: variable symbol
    :ivar specific_symbol: specific symbol
    :ivar originators_reference_information: reference information
    :ivar mandate_id: identification of the mandate between creditor and
        debtor
    :ivar creditor_id: identification of the creditor
    :ivar contract_id: identification of the contract between creditor
        and debtor
    :ivar max_amount: maximum amount that can be debited
    :ivar valid_till_date: direct debit valid till date
    """
    direct_debit_scheme: Optional[DirectDebitScheme] = field(
        default=None,
        metadata={
            "name": "DirectDebitScheme",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
        }
    )
    direct_debit_type: Optional[DirectDebitType] = field(
        default=None,
        metadata={
            "name": "DirectDebitType",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
        }
    )
    variable_symbol: Optional[str] = field(
        default=None,
        metadata={
            "name": "VariableSymbol",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[0-9]{0,10}",
        }
    )
    specific_symbol: Optional[str] = field(
        default=None,
        metadata={
            "name": "SpecificSymbol",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[0-9]{0,10}",
        }
    )
    originators_reference_information: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginatorsReferenceInformation",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    mandate_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MandateID",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    creditor_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CreditorID",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    contract_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContractID",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    max_amount: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "MaxAmount",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    valid_till_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "ValidTillDate",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )


@dataclass
class StandingOrderExt:
    """standing order extension.

    Extends basic payment information with information required for
    standing order setup

    :ivar day: this is the payment day. It‘s meaning depends on the
        periodicity, meaning either day of the month (number between 1
        and 31) or day of the week (1=Monday, 2=Tuesday, …, 7=Sunday).
    :ivar month: selection of months on which payment occurs. If used,
        set periodicity to "Annually". If payment occurs every month or
        every other month consider setting periodicity to "Monthly" or
        "Bimonthly" instead.
    :ivar periodicity: periodicity of the standing order
    :ivar last_date: date of the last payment of the standing order
    """
    day: Optional[int] = field(
        default=None,
        metadata={
            "name": "Day",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    month: List[Month] = field(
        default_factory=list,
        metadata={
            "name": "Month",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "tokens": True,
        }
    )
    periodicity: Optional[Periodicity] = field(
        default=None,
        metadata={
            "name": "Periodicity",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
        }
    )
    last_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "LastDate",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )


@dataclass
class Payment:
    """
    :ivar payment_options: Define which payment options are available:
        "paymentorder", "standingorder" - requires StandingOrderExt,
        "directdebit" - requires DirectDebitExt.
    :ivar amount: payment amount
    :ivar currency_code: payment currency code, 3 letter ISO4217 code
    :ivar payment_due_date: payment due date. Used also as first payment
        date for standing order.
    :ivar variable_symbol: variable symbol
    :ivar constant_symbol: constant symbol
    :ivar specific_symbol: specific symbol
    :ivar originators_reference_information: reference information
    :ivar payment_note: payment note
    :ivar bank_accounts: list of bank accounts
    :ivar standing_order_ext: standing order extension. Extends basic
        payment information with information required for standing order
        setup
    :ivar direct_debit_ext: direct debit extension. Extends basic
        payment information with information required for identification
        and setup of direct debit
    :ivar beneficiary_name:
    :ivar beneficiary_address_line1:
    :ivar beneficiary_address_line2:
    """
    payment_options: List[PaymentOption] = field(
        default_factory=list,
        metadata={
            "name": "PaymentOptions",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
            "tokens": True,
        }
    )
    amount: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Amount",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    currency_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "CurrencyCode",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
            "pattern": r"[A-Z]{3}",
        }
    )
    payment_due_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "PaymentDueDate",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    variable_symbol: Optional[str] = field(
        default=None,
        metadata={
            "name": "VariableSymbol",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[0-9]{0,10}",
        }
    )
    constant_symbol: Optional[str] = field(
        default=None,
        metadata={
            "name": "ConstantSymbol",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[0-9]{0,4}",
        }
    )
    specific_symbol: Optional[str] = field(
        default=None,
        metadata={
            "name": "SpecificSymbol",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "pattern": r"[0-9]{0,10}",
        }
    )
    originators_reference_information: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginatorsReferenceInformation",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    payment_note: Optional[str] = field(
        default=None,
        metadata={
            "name": "PaymentNote",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    bank_accounts: Optional[BankAccounts] = field(
        default=None,
        metadata={
            "name": "BankAccounts",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
        }
    )
    standing_order_ext: Optional[StandingOrderExt] = field(
        default=None,
        metadata={
            "name": "StandingOrderExt",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    direct_debit_ext: Optional[DirectDebitExt] = field(
        default=None,
        metadata={
            "name": "DirectDebitExt",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    beneficiary_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "BeneficiaryName",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    beneficiary_address_line1: Optional[str] = field(
        default=None,
        metadata={
            "name": "BeneficiaryAddressLine1",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    beneficiary_address_line2: Optional[str] = field(
        default=None,
        metadata={
            "name": "BeneficiaryAddressLine2",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )


@dataclass
class Payments:
    """
    :ivar payment: Payment order definition.
    """
    payment: List[Payment] = field(
        default_factory=list,
        metadata={
            "name": "Payment",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "min_occurs": 1,
        }
    )


@dataclass
class PayBase(BySquareDocument):
    """
    :ivar invoice_id: Invoice identification code. Only used when pay by
        square is part of the invoice. Otherwise this field is empty.
    :ivar payments: Lists one or more payments.
    """
    invoice_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "InvoiceID",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
        }
    )
    payments: Optional[Payments] = field(
        default=None,
        metadata={
            "name": "Payments",
            "type": "Element",
            "namespace": "http://www.bysquare.com/bysquare",
            "required": True,
        }
    )


@dataclass
class Pay(PayBase):
    class Meta:
        namespace = "http://www.bysquare.com/bysquare"

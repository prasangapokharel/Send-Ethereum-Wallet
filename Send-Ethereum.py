import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from eth_account import Account
from eth_utils import is_hex, to_checksum_address
import socket

# Etherscan API key
ETHERSCAN_API_KEY = 'I756VBZC1WW8CDAIXIW4IPGGET1SB6664G'

# Function to get the nonce for an address
def get_nonce(address):
    url = f'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionCount&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url).json()
    return int(response['result'], 16)

# Function to get the current gas price
def get_gas_price():
    url = f'https://api.etherscan.io/api?module=proxy&action=eth_gasPrice&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url).json()
    return int(response['result'], 16)

# Function to send Ethereum transaction
def send_eth(private_key, to_address, amount):
    account = Account.from_key(private_key)
    from_address = account.address

    nonce = get_nonce(from_address)
    gas_price = get_gas_price()

    tx = {
        'nonce': nonce,
        'to': to_checksum_address(to_address),
        'value': amount,
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': 1  # Mainnet chain ID
    }

    signed_tx = account.sign_transaction(tx)
    tx_hex = signed_tx.raw_transaction.hex()

    url = f'https://api.etherscan.io/api?module=proxy&action=eth_sendRawTransaction&hex={tx_hex}&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url).json()
    return response

class EthereumTransactionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ethereum Transaction')
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.private_key_label = QLabel('Private Key:')
        self.private_key_input = QLineEdit()
        layout.addWidget(self.private_key_label)
        layout.addWidget(self.private_key_input)

        self.to_address_label = QLabel('Destination Address:')
        self.to_address_input = QLineEdit()
        layout.addWidget(self.to_address_label)
        layout.addWidget(self.to_address_input)

        self.amount_label = QLabel('Amount (ETH):')
        self.amount_input = QLineEdit()
        layout.addWidget(self.amount_label)
        layout.addWidget(self.amount_input)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_transaction)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_transaction(self):
        private_key = self.private_key_input.text().strip()
        to_address = self.to_address_input.text().strip()
        amount = float(self.amount_input.text().strip())

        # Validate private key
        if not is_hex(private_key):
            self.show_error_message('Invalid private key format. Private key should be a hex string.')
            return

        # Convert ETH to Wei
        amount_wei = int(amount * 10**18)

        confirmation = QMessageBox.question(self, 'Confirmation', f'Are you ready to send {amount} ETH to {to_address}?', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            response = send_eth(private_key, to_address, amount_wei)
            ip_address = socket.gethostbyname(socket.gethostname())
            QMessageBox.information(self, 'Transaction Sent', f'{amount} ETH successfully transferred from this IP: {ip_address}')

    def show_error_message(self, message):
        QMessageBox.critical(self, 'Error', message, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    eth_app = EthereumTransactionApp()
    eth_app.show()
    sys.exit(app.exec_())

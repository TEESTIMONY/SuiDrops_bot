import re

def is_valid_sui_address(address: str) -> bool:
    # Remove '0x' prefix if present
    if address.startswith('0x'):
        address = address[2:]
    
    # Check if the address is a valid hexadecimal string
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    # Sui addresses are typically 64 characters long (32 bytes)
    if len(address) == 64 and hex_pattern.match(address):
        return True
    else:
        return False

# Test with the provided address
sui_address = "0x55c9ae81d98777aaf4c622946876bd04043ccb4f2cca1d825e72173587217d23"

if is_valid_sui_address(sui_address):
    print("The Sui wallet address is valid.")
else:
    print("The Sui wallet address is invalid.")

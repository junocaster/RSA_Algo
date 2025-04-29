import socket


def power(base, expo, m):
    """Fast modular exponentiation"""
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1:
            res = (res * base) % m
        base = (base * base) % m
        expo = expo // 2
    return res


def encrypt(m, e, n):
    """Encrypt message using public key (e, n)"""
    return power(m, e, n)


def decrypt(c, e, n):
    """Decrypt message using public key (simplified for demo)"""
    return power(c, e, n)


def get_public_key_from_file():
    """Read public key from com.txt file"""
    try:
        with open("com.txt", "r") as f:
            content = f.read().strip()
            e, n = map(int, content.split(","))
            return e, n
    except FileNotFoundError:
        print("com.txt file not found.")
        return None, None


def main():
    """Run Bob's client"""
    # Try to get public key from file
    file_e, file_n = get_public_key_from_file()
    if file_e and file_n:
        print(f"Found public key in com.txt: ({file_e}, {file_n})")

    # Connect to Alice
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "172.20.10.5"

    try:
        client.connect((host, 5000))
        print("Connected to Alice's server")

        # Receive Alice's public key
        key_data = client.recv(1024).decode()
        e, n = map(int, key_data.split(","))
        print(f"Received Alice's public key: ({e}, {n})")

        while True:
            # Get message from Bob
            message = input("Bob: ")
            if message.lower() == "exit":
                break

            # Encrypt each character in the message
            encrypted_msg = [encrypt(ord(c), e, n) for c in message]
            # Convert to comma-separated string
            encrypted_str = ",".join(str(c) for c in encrypted_msg)
            print(f"Alice: {encrypted_msg}")
            client.sendall(encrypted_str.encode())

            # Receive and decrypt Alice's response
            response_data = client.recv(4096).decode()
            if not response_data:
                break

            # Parse the encrypted response
            encrypted_response = [int(num) for num in response_data.split(",") if num]

            # Decrypt each number in the response
            decrypted_chars = [decrypt(c, e, n) for c in encrypted_response]
            decrypted_msg = "".join(chr(c) for c in decrypted_chars)
            print(f"Alice: {decrypted_msg}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Client closed")


if __name__ == "__main__":
    main()

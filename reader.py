from imapclient import IMAPClient
import pyzmail

HOST = "imap.gmail.com"

def read_latest(username, password):
    """
    Returns (sender_email, subject, body) of the latest email.
    """
    try:
        server = IMAPClient(HOST, ssl=True)
        server.login(username, password)
        server.select_folder("INBOX")

        messages = server.search()
        if len(messages) == 0:
            server.logout()
            return None, None, None

        last_uid = messages[-1]
        raw_message = server.fetch([last_uid], ["BODY[]"])
        message = pyzmail.PyzMessage.factory(
            raw_message[last_uid][b"BODY[]"]
        )

        # Extract sender
        sender = message.get_addresses("from")
        sender_email = sender[0][1] if sender else "Unknown"

        subject = message.get_subject() or "(no subject)"

        body = ""
        if message.text_part:
            body = message.text_part.get_payload().decode(
                message.text_part.charset or "utf-8", errors="ignore"
            )
        elif message.html_part:
            body = message.html_part.get_payload().decode(
                message.html_part.charset or "utf-8", errors="ignore"
            )

        server.logout()
        return sender_email, subject, body

    except Exception as e:
        print("Error in read_latest:", e)
        return None, None, None
import re
from flask import Flask, request, jsonify
import smtplib
import dns.resolver

app = Flask(__name__)

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json

    if not data or "email" not in data:
        return jsonify({"status": "Error", "message": "Email is required"}), 400

    recipient = data.get("email").strip()

    # Validate format
    if not re.match(EMAIL_REGEX, recipient):
        return jsonify({
            "status": "Invalid",
            "message": "Invalid email format"
        }), 400

    sender = "test@gmail.com"

    try:
        domain = recipient.split('@')[1]

        # DNS check
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo('gmail.com')
        server.mail(sender)

        code, _ = server.rcpt(recipient)
        server.quit()

        if code == 250:
            return jsonify({"status": "Deliverable"})
        else:
            return jsonify({"status": "Not Deliverable"})

    except dns.resolver.NXDOMAIN:
        return jsonify({
            "status": "Invalid",
            "message": "Domain does not exist"
        })

    except dns.resolver.NoAnswer:
        return jsonify({
            "status": "Invalid",
            "message": "No MX records found"
        })

    except Exception as e:
        return jsonify({
            "status": "Error",
            "message": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
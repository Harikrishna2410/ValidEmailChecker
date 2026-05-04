from flask import Flask, request, jsonify
import smtplib
import dns.resolver

app = Flask(__name__)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    recipient = data.get("email")
    sender = "test@gmail.com"

    try:
        domain = recipient.split('@')[1]
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

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

# IMPORTANT for Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
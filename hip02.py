# DNS
import binascii
import datetime
import subprocess
import tempfile
import dns.resolver
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def resolve(HSD_IP, HSD_PORT, domain, token="HNS"):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [HSD_IP]
    resolver.port = HSD_PORT
    records = []
    try:
        # Query the DNS record
        response = resolver.resolve(domain, "A")
        for record in response:
            records.append(str(record))
        if not records:
            return False
    except Exception as e:
        return False

    Server_IP = records[0]
    curl_command = ["curl","--connect-to",f"{domain}:443:{Server_IP}:443",f"https://{domain}/.well-known/wallets/{token}","--insecure"]
    curl_process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    curl_output, _ = curl_process.communicate()
    return curl_output.decode("utf-8")

def TLSA_check(HSD_IP,HSD_PORT,domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [HSD_IP]
    resolver.port = HSD_PORT
    try:
        # Query the DNS record
        response = resolver.resolve(domain, "A")
        records = []
        for record in response:
            records.append(str(record))

        if not records:
            return "No A record found"
        
        # Get the first A record
        ip = records[0]
        
        # Run the openssl s_client command
        s_client_command = ["openssl","s_client","-showcerts","-connect",f"{ip}:443","-servername",domain,]
        s_client_process = subprocess.Popen(s_client_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        s_client_output, _ = s_client_process.communicate(input=b"\n")        
        certificates = []
        current_cert = ""
        for line in s_client_output.split(b"\n"):
            current_cert += line.decode("utf-8") + "\n"
            if "-----END CERTIFICATE-----" in line.decode("utf-8"):
                certificates.append(current_cert)
                current_cert = ""
        # Remove anything before -----BEGIN CERTIFICATE-----
        certificates = [cert[cert.find("-----BEGIN CERTIFICATE-----"):] for cert in certificates]
        if not certificates:
            return "No certificates found"        
        cert = certificates[0]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_cert_file:
            temp_cert_file.write(cert)
            temp_cert_file.seek(0)  # Move back to the beginning of the temporary file
        tlsa_command = ["openssl","x509","-in",temp_cert_file.name,"-pubkey","-noout","|","openssl","pkey","-pubin","-outform","der","|","openssl","dgst","-sha256","-binary",]        
        tlsa_process = subprocess.Popen(" ".join(tlsa_command), shell=True, stdout=subprocess.PIPE)
        tlsa_output, _ = tlsa_process.communicate()
        tlsa_server = "3 1 1 " + binascii.hexlify(tlsa_output).decode("utf-8")

        # Get domains
        cert_obj = x509.load_pem_x509_certificate(cert.encode("utf-8"), default_backend())

        domains = []
        for ext in cert_obj.extensions:
            if ext.oid == x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME:
                san_list = ext.value.get_values_for_type(x509.DNSName)
                domains.extend(san_list)
        
        # Extract the common name (CN) from the subject
        common_name = cert_obj.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        if common_name:
            if common_name[0].value not in domains:
                domains.append(common_name[0].value)

        if not domains:
            return "Invalid certificate"

        domain_parts = domain.split(".")        
        higher_domain = ""
        for i in range(1,len(domain_parts)):
            higher_domain = domain_parts[i] + "." + higher_domain
        
        higher_domain = higher_domain[:-1]

        if not domain in domains and not "*." + higher_domain in domains:
            return "Invalid certificate - Missing domain"
        
        expiry_date = cert_obj.not_valid_after
        # Check if expiry date is past
        if expiry_date < datetime.datetime.now():
            return "Invalid certificate - Expired"

        try:
            # Check for TLSA record
            response = resolver.resolve("_443._tcp."+domain, "TLSA")
            tlsa_records = []
            for record in response:
                tlsa_records.append(str(record))

            if not tlsa_records:
                return "No TLSA record found"
            else:
                if tlsa_server != tlsa_records[0]:
                    return "Invalid TLSA record"
        except:
            return "Exception in TLSA record check"
        return True
        
    # Catch all exceptions
    except Exception as e:
        return "Exception: "+str(e)
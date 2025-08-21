#!/usr/bin/env python3
"""
Subnetta - IPv4 Subnetting Tool
by Maximillian Urio

A cross-platform command-line tool for IPv4 subnetting calculations.
Supports Classes A, B, and C with interactive step-by-step guidance.
"""

import sys
import os
import ipaddress
import argparse
import math
import subprocess
import importlib.util
from typing import Tuple, List, Dict, Optional, Union


class DependencyManager:
    """Handles checking and installation of optional dependencies."""
    
    @staticmethod
    def check_dependency(package_name: str) -> bool:
        """Check if a package is installed."""
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    
    @staticmethod
    def install_dependency(package_name: str) -> bool:
        """Install a package using pip."""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def setup_colorama() -> bool:
        """Setup colorama for colored output."""
        if DependencyManager.check_dependency("colorama"):
            return True
        
        try:
            choice = input("colorama library not found. Do you want me to install it now? (Y/n): ").strip().lower()
            if choice in ['', 'y', 'yes']:
                print("Installing colorama...")
                if DependencyManager.install_dependency("colorama"):
                    print("✓ colorama installed successfully!")
                    return True
                else:
                    print("✗ Failed to install colorama. Continuing with plain text output.")
                    return False
            else:
                print("Continuing with plain text output.")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\nContinuing with plain text output.")
            return False


class Colors:
    """Color constants for terminal output."""
    
    def __init__(self, use_colors: bool = True):
        if use_colors and DependencyManager.check_dependency("colorama"):
            try:
                from colorama import Fore, Back, Style, init
                init(autoreset=True)
                self.RED = Fore.RED
                self.GREEN = Fore.GREEN
                self.YELLOW = Fore.YELLOW
                self.BLUE = Fore.BLUE
                self.MAGENTA = Fore.MAGENTA
                self.CYAN = Fore.CYAN
                self.WHITE = Fore.WHITE
                self.BOLD = Style.BRIGHT
                self.RESET = Style.RESET_ALL
                self.enabled = True
            except ImportError:
                self._disable_colors()
        else:
            self._disable_colors()
    
    def _disable_colors(self):
        """Disable all colors."""
        self.RED = self.GREEN = self.YELLOW = self.BLUE = ""
        self.MAGENTA = self.CYAN = self.WHITE = self.BOLD = self.RESET = ""
        self.enabled = False


class IPv4Validator:
    """Handles IPv4 address validation and classification."""
    
    @staticmethod
    def validate_ipv4(ip_str: str) -> Tuple[bool, Optional[ipaddress.IPv4Address]]:
        """
        Validate IPv4 address string.
        
        Returns:
            Tuple of (is_valid, IPv4Address object or None)
        """
        try:
            ip = ipaddress.IPv4Address(ip_str)
            return True, ip
        except ipaddress.AddressValueError:
            return False, None
    
    @staticmethod
    def get_ip_class(ip: ipaddress.IPv4Address) -> str:
        """
        Determine the class of an IPv4 address.
        
        Returns:
            'A', 'B', or 'C'
        """
        first_octet = int(str(ip).split('.')[0])
        
        if 1 <= first_octet <= 126 or first_octet == 127:  # Include loopback in Class A
            return 'A'
        elif 128 <= first_octet <= 191:
            return 'B'
        elif 192 <= first_octet <= 223:
            return 'C'
        else:
            # For multicast, reserved, etc., default to C
            return 'C'
    
    @staticmethod
    def get_default_mask(ip_class: str) -> Tuple[str, int]:
        """
        Get default subnet mask and prefix length for IP class.
        
        Returns:
            Tuple of (subnet_mask, prefix_length)
        """
        if ip_class == 'A':
            return '255.0.0.0', 8
        elif ip_class == 'B':
            return '255.255.0.0', 16
        else:  # Class C
            return '255.255.255.0', 24
    
    @staticmethod
    def is_private_ip(ip: ipaddress.IPv4Address) -> bool:
        """Check if IP address is private."""
        return ip.is_private
    
    @staticmethod
    def is_loopback(ip: ipaddress.IPv4Address) -> bool:
        """Check if IP address is loopback."""
        return ip.is_loopback
    
    @staticmethod
    def is_multicast(ip: ipaddress.IPv4Address) -> bool:
        """Check if IP address is multicast."""
        return ip.is_multicast


class SubnetCalculator:
    """Handles all subnet calculations."""
    
    def __init__(self, ip: ipaddress.IPv4Address, ip_class: str):
        self.ip = ip
        self.ip_class = ip_class
        self.default_mask, self.default_prefix = IPv4Validator.get_default_mask(ip_class)
    
    def calculate_from_subnets(self, num_subnets: int) -> Dict:
        """Calculate subnetting based on required number of subnets."""
        # Calculate bits needed for subnets
        subnet_bits = math.ceil(math.log2(num_subnets))
        
        # Calculate new prefix length
        new_prefix = self.default_prefix + subnet_bits
        
        if new_prefix > 30:  # Maximum usable prefix for host addresses
            raise ValueError(f"Cannot create {num_subnets} subnets with class {self.ip_class}. Too many subnet bits required.")
        
        return self._calculate_subnetting(new_prefix, subnet_bits)
    
    def calculate_from_hosts(self, hosts_per_subnet: int) -> Dict:
        """Calculate subnetting based on required hosts per subnet."""
        # Add 2 for network and broadcast addresses
        total_addresses_needed = hosts_per_subnet + 2
        
        # Calculate bits needed for hosts
        host_bits = math.ceil(math.log2(total_addresses_needed))
        
        # Calculate new prefix length
        new_prefix = 32 - host_bits
        
        if new_prefix <= self.default_prefix:
            raise ValueError(f"Cannot accommodate {hosts_per_subnet} hosts per subnet with class {self.ip_class}. Not enough host bits available.")
        
        subnet_bits = new_prefix - self.default_prefix
        
        return self._calculate_subnetting(new_prefix, subnet_bits)
    
    def _calculate_subnetting(self, new_prefix: int, subnet_bits: int) -> Dict:
        """Internal method to perform subnetting calculations."""
        # Create network with new prefix
        network = ipaddress.IPv4Network(f"{self.ip}/{new_prefix}", strict=False)
        
        # Calculate subnet mask and wildcard mask
        subnet_mask = str(network.netmask)
        wildcard_mask = str(network.hostmask)
        
        # Calculate number of possible subnets and hosts
        total_subnets = 2 ** subnet_bits
        hosts_per_subnet = network.num_addresses - 2  # Subtract network and broadcast
        
        # Get network address (first address in the original network)
        original_network = ipaddress.IPv4Network(f"{self.ip}/{self.default_prefix}", strict=False)
        
        # Generate all subnets
        subnets = list(original_network.subnets(new_prefix=new_prefix))
        
        return {
            'ip_class': self.ip_class,
            'original_ip': str(self.ip),
            'subnet_mask': subnet_mask,
            'prefix_length': new_prefix,
            'wildcard_mask': wildcard_mask,
            'total_subnets': total_subnets,
            'hosts_per_subnet': hosts_per_subnet,
            'subnets': subnets,
            'subnet_bits': subnet_bits,
            'host_bits': 32 - new_prefix
        }
    
    def get_subnet_details(self, subnet_network: ipaddress.IPv4Network) -> Dict:
        """Get detailed information about a specific subnet."""
        hosts = list(subnet_network.hosts())
        
        return {
            'network_address': str(subnet_network.network_address),
            'broadcast_address': str(subnet_network.broadcast_address),
            'first_usable_ip': str(hosts[0]) if hosts else "None",
            'last_usable_ip': str(hosts[-1]) if hosts else "None",
            'total_addresses': subnet_network.num_addresses,
            'usable_addresses': len(hosts),
            'subnet_mask': str(subnet_network.netmask),
            'prefix_length': subnet_network.prefixlen
        }


def display_ascii_banner(colors: Colors):
    """Display the Subnetta ASCII banner."""
    banner = f"""
{colors.CYAN}{colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════════════╗
                                                                                
                     ▄▄                                                         
                     ██                              ██        ██               
 ▄▄█████▄  ██    ██  ██▄███▄   ██▄████▄   ▄████▄   ███████   ███████    ▄█████▄ 
 ██▄▄▄▄ ▀  ██    ██  ██▀  ▀██  ██▀   ██  ██▄▄▄▄██    ██        ██       ▀ ▄▄▄██ 
  ▀▀▀▀██▄  ██    ██  ██    ██  ██    ██  ██▀▀▀▀▀▀    ██        ██      ▄██▀▀▀██ 
 █▄▄▄▄▄██  ██▄▄▄███  ███▄▄██▀  ██    ██  ▀██▄▄▄▄█    ██▄▄▄     ██▄▄▄   ██▄▄▄███ 
  ▀▀▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀ ▀▀▀    ▀▀    ▀▀    ▀▀▀▀▀      ▀▀▀▀      ▀▀▀▀    ▀▀▀▀ ▀▀ 
                                                                                
                                                                                    ║
║                                                                                   ║
║                               IPv4 Subnetting Tool                                ║
║                               by Maximillian Urio                                 ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
{colors.RESET}
{colors.YELLOW}Welcome to Subnetta - Your IPv4 Subnetting Companion!{colors.RESET}
{colors.GREEN}Supports Classes A, B, and C with step-by-step guidance.{colors.RESET}
"""
    print(banner)


class SubnettaApp:
    """Main Subnetta application class."""
    
    def __init__(self, colors: Colors):
        self.colors = colors
    
    def get_user_input(self, prompt: str, validation_func=None, error_msg: str = "Invalid input. Please try again.") -> str:
        """Get validated user input."""
        while True:
            try:
                user_input = input(f"{self.colors.CYAN}{prompt}{self.colors.RESET}").strip()
                
                if validation_func:
                    if validation_func(user_input):
                        return user_input
                    else:
                        print(f"{self.colors.RED}{error_msg}{self.colors.RESET}")
                else:
                    return user_input
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting Subnetta. Goodbye!")
                sys.exit(0)
    
    def get_ipv4_address(self) -> ipaddress.IPv4Address:
        """Get and validate IPv4 address from user."""
        print(f"\n{self.colors.BOLD}{self.colors.YELLOW}Step 1: IPv4 Address Input{self.colors.RESET}")
        print(f"{self.colors.WHITE}Please enter an IPv4 address (e.g., 192.168.1.0, 10.0.0.0){self.colors.RESET}")
        
        def validate_ip(ip_str):
            is_valid, _ = IPv4Validator.validate_ipv4(ip_str)
            return is_valid
        
        ip_str = self.get_user_input(
            "IPv4 Address: ",
            validate_ip,
            "Invalid IPv4 address format. Please use dotted decimal notation (e.g., 192.168.1.0)"
        )
        
        _, ip = IPv4Validator.validate_ipv4(ip_str)
        return ip
    
    def display_ip_info(self, ip: ipaddress.IPv4Address):
        """Display information about the IP address."""
        ip_class = IPv4Validator.get_ip_class(ip)
        is_private = IPv4Validator.is_private_ip(ip)
        is_loopback = IPv4Validator.is_loopback(ip)
        is_multicast = IPv4Validator.is_multicast(ip)
        
        print(f"\n{self.colors.BOLD}{self.colors.GREEN}IP Address Analysis:{self.colors.RESET}")
        print(f"{self.colors.WHITE}IP Address: {self.colors.YELLOW}{ip}{self.colors.RESET}")
        print(f"{self.colors.WHITE}IP Class: {self.colors.YELLOW}Class {ip_class}{self.colors.RESET}")
        
        if is_private:
            print(f"{self.colors.WHITE}Type: {self.colors.GREEN}Private IP{self.colors.RESET}")
        elif is_loopback:
            print(f"{self.colors.WHITE}Type: {self.colors.BLUE}Loopback IP{self.colors.RESET}")
        elif is_multicast:
            print(f"{self.colors.WHITE}Type: {self.colors.MAGENTA}Multicast IP{self.colors.RESET}")
        else:
            print(f"{self.colors.WHITE}Type: {self.colors.YELLOW}Public IP{self.colors.RESET}")
        
        default_mask, default_prefix = IPv4Validator.get_default_mask(ip_class)
        print(f"{self.colors.WHITE}Default Subnet Mask: {self.colors.YELLOW}{default_mask} (/{default_prefix}){self.colors.RESET}")
    
    def get_subnetting_choice(self) -> str:
        """Get user's choice for subnetting method."""
        print(f"\n{self.colors.BOLD}{self.colors.YELLOW}Step 2: Subnetting Method{self.colors.RESET}")
        print(f"{self.colors.WHITE}How would you like to specify your subnetting requirements?{self.colors.RESET}")
        print(f"{self.colors.GREEN}(a) Number of subnets needed{self.colors.RESET}")
        print(f"{self.colors.GREEN}(b) Number of hosts per subnet{self.colors.RESET}")
        
        def validate_choice(choice):
            return choice.lower() in ['a', 'b']
        
        choice = self.get_user_input(
            "Enter your choice (a/b): ",
            validate_choice,
            "Please enter 'a' or 'b'"
        )
        
        return choice.lower()
    
    def get_number_input(self, prompt: str, min_value: int = 1) -> int:
        """Get a positive integer from user."""
        def validate_number(num_str):
            try:
                num = int(num_str)
                return num >= min_value
            except ValueError:
                return False
        
        num_str = self.get_user_input(
            prompt,
            validate_number,
            f"Please enter a valid integer greater than or equal to {min_value}"
        )
        
        return int(num_str)
    
    def display_subnetting_results(self, results: Dict):
        """Display comprehensive subnetting results."""
        print(f"\n{self.colors.BOLD}{self.colors.GREEN}Subnetting Results:{self.colors.RESET}")
        print("=" * 60)
        
        print(f"{self.colors.WHITE}Original IP: {self.colors.YELLOW}{results['original_ip']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}IP Class: {self.colors.YELLOW}Class {results['ip_class']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Subnet Mask: {self.colors.YELLOW}{results['subnet_mask']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Prefix Length: {self.colors.YELLOW}/{results['prefix_length']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Wildcard Mask: {self.colors.YELLOW}{results['wildcard_mask']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Total Subnets: {self.colors.GREEN}{results['total_subnets']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Usable Hosts per Subnet: {self.colors.GREEN}{results['hosts_per_subnet']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Subnet Bits: {self.colors.BLUE}{results['subnet_bits']}{self.colors.RESET}")
        print(f"{self.colors.WHITE}Host Bits: {self.colors.BLUE}{results['host_bits']}{self.colors.RESET}")
        
        print(f"\n{self.colors.BOLD}{self.colors.CYAN}First 10 Subnets:{self.colors.RESET}")
        print("-" * 80)
        print(f"{self.colors.BOLD}{'#':<3} {'Network':<18} {'First IP':<15} {'Last IP':<15} {'Broadcast':<15}{self.colors.RESET}")
        print("-" * 80)
        
        for i, subnet in enumerate(results['subnets'][:10]):
            details = SubnetCalculator(ipaddress.IPv4Address(results['original_ip']), results['ip_class']).get_subnet_details(subnet)
            print(f"{self.colors.WHITE}{i+1:<3} {details['network_address']:<18} {details['first_usable_ip']:<15} {details['last_usable_ip']:<15} {details['broadcast_address']:<15}{self.colors.RESET}")
        
        if len(results['subnets']) > 10:
            print(f"{self.colors.YELLOW}... and {len(results['subnets']) - 10} more subnets{self.colors.RESET}")
    
    def get_nth_subnet(self, results: Dict):
        """Handle nth subnet lookup."""
        print(f"\n{self.colors.BOLD}{self.colors.YELLOW}Specific Subnet Lookup{self.colors.RESET}")
        
        while True:
            choice = self.get_user_input(
                f"Do you want to view details of a specific subnet? (y/n): ",
                lambda x: x.lower() in ['y', 'yes', 'n', 'no'],
                "Please enter 'y' or 'n'"
            )
            
            if choice.lower() in ['n', 'no']:
                break
            
            subnet_num = self.get_number_input(
                f"Enter subnet number (1-{results['total_subnets']}): ",
                1
            )
            
            if subnet_num > results['total_subnets']:
                print(f"{self.colors.RED}Subnet number {subnet_num} exceeds total subnets ({results['total_subnets']}){self.colors.RESET}")
                continue
            
            # Get the specific subnet (convert to 0-based index)
            subnet = results['subnets'][subnet_num - 1]
            details = SubnetCalculator(ipaddress.IPv4Address(results['original_ip']), results['ip_class']).get_subnet_details(subnet)
            
            print(f"\n{self.colors.BOLD}{self.colors.GREEN}Subnet #{subnet_num} Details:{self.colors.RESET}")
            print("=" * 50)
            print(f"{self.colors.WHITE}Network Address: {self.colors.YELLOW}{details['network_address']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Subnet Mask: {self.colors.YELLOW}{details['subnet_mask']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Prefix Length: {self.colors.YELLOW}/{details['prefix_length']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}First Usable IP: {self.colors.GREEN}{details['first_usable_ip']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Last Usable IP: {self.colors.GREEN}{details['last_usable_ip']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Broadcast Address: {self.colors.YELLOW}{details['broadcast_address']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Total Addresses: {self.colors.BLUE}{details['total_addresses']}{self.colors.RESET}")
            print(f"{self.colors.WHITE}Usable Addresses: {self.colors.BLUE}{details['usable_addresses']}{self.colors.RESET}")
    
    def run(self):
        """Run the main application loop."""
        while True:
            try:
                # Step 1: Get IPv4 address
                ip = self.get_ipv4_address()
                
                # Display IP information
                self.display_ip_info(ip)
                
                # Step 2: Get subnetting method
                choice = self.get_subnetting_choice()
                
                # Step 3: Get requirements and calculate
                calculator = SubnetCalculator(ip, IPv4Validator.get_ip_class(ip))
                
                try:
                    if choice == 'a':
                        num_subnets = self.get_number_input("Number of subnets needed: ")
                        results = calculator.calculate_from_subnets(num_subnets)
                    else:
                        hosts_per_subnet = self.get_number_input("Number of hosts per subnet: ")
                        results = calculator.calculate_from_hosts(hosts_per_subnet)
                    
                    # Step 4: Display results
                    self.display_subnetting_results(results)
                    
                    # Step 5: nth subnet lookup
                    self.get_nth_subnet(results)
                    
                except ValueError as e:
                    print(f"{self.colors.RED}Error: {e}{self.colors.RESET}")
                    continue
                
                # Ask if user wants to continue
                print(f"\n{self.colors.BOLD}{self.colors.YELLOW}Continue or Exit{self.colors.RESET}")
                continue_choice = self.get_user_input(
                    "Do you want to perform another calculation? (y/n): ",
                    lambda x: x.lower() in ['y', 'yes', 'n', 'no'],
                    "Please enter 'y' or 'n'"
                )
                
                if continue_choice.lower() in ['n', 'no']:
                    print(f"\n{self.colors.GREEN}Thank you for using Subnetta!{self.colors.RESET}")
                    print(f"{self.colors.CYAN}Happy subnetting! 🌐{self.colors.RESET}")
                    break
                
                print("\n" + "=" * 70 + "\n")
                
            except Exception as e:
                print(f"{self.colors.RED}An unexpected error occurred: {e}{self.colors.RESET}")
                print(f"{self.colors.YELLOW}Please try again.{self.colors.RESET}")


def main():
    """Main application entry point."""
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Subnetta - IPv4 Subnetting Tool",
        epilog="Example: python subnetta.py"
    )
    parser.add_argument(
        '--no-color', 
        action='store_true', 
        help='Disable colored output'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Subnetta 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup colors
    use_colors = not args.no_color
    if use_colors:
        DependencyManager.setup_colorama()
    
    colors = Colors(use_colors)
    
    # Display banner
    display_ascii_banner(colors)
    
    # Run the application
    app = SubnettaApp(colors)
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting Subnetta. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
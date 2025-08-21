#!/usr/bin/env python3
"""
Unit tests for Subnetta - IPv4 Subnetting Tool
"""

import unittest
import ipaddress
import sys
import os

# Add the parent directory to the path to import subnetta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subnetta import (
    IPv4Validator, SubnetCalculator, DependencyManager, Colors
)


class TestIPv4Validator(unittest.TestCase):
    """Test cases for IPv4Validator class."""
    
    def test_validate_ipv4_valid_addresses(self):
        """Test validation of valid IPv4 addresses."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.0",
            "172.16.0.1",
            "8.8.8.8",
            "127.0.0.1",
            "255.255.255.255"
        ]
        
        for ip_str in valid_ips:
            with self.subTest(ip=ip_str):
                is_valid, ip_obj = IPv4Validator.validate_ipv4(ip_str)
                self.assertTrue(is_valid)
                self.assertIsInstance(ip_obj, ipaddress.IPv4Address)
                self.assertEqual(str(ip_obj), ip_str)
    
    def test_validate_ipv4_invalid_addresses(self):
        """Test validation of invalid IPv4 addresses."""
        invalid_ips = [
            "256.1.1.1",
            "192.168.1",
            "192.168.1.1.1",
            "192.168.-1.1",
            "abc.def.ghi.jkl",
            "",
            "192.168.1.256",
            "192.168.999.1"
        ]
        
        for ip_str in invalid_ips:
            with self.subTest(ip=ip_str):
                is_valid, ip_obj = IPv4Validator.validate_ipv4(ip_str)
                self.assertFalse(is_valid)
                self.assertIsNone(ip_obj)
    
    def test_get_ip_class(self):
        """Test IP class detection."""
        test_cases = [
            ("10.0.0.1", "A"),
            ("126.255.255.255", "A"),
            ("128.0.0.1", "B"),
            ("172.16.0.1", "B"),
            ("191.255.255.255", "B"),
            ("192.0.0.1", "C"),
            ("192.168.1.1", "C"),
            ("223.255.255.255", "C"),
            ("224.0.0.1", "C"),  # Multicast defaults to C
            ("127.0.0.1", "A"),  # Loopback
        ]
        
        for ip_str, expected_class in test_cases:
            with self.subTest(ip=ip_str, expected=expected_class):
                ip = ipaddress.IPv4Address(ip_str)
                result_class = IPv4Validator.get_ip_class(ip)
                self.assertEqual(result_class, expected_class)
    
    def test_get_default_mask(self):
        """Test default subnet mask retrieval."""
        test_cases = [
            ("A", ("255.0.0.0", 8)),
            ("B", ("255.255.0.0", 16)),
            ("C", ("255.255.255.0", 24)),
        ]
        
        for ip_class, expected in test_cases:
            with self.subTest(ip_class=ip_class):
                mask, prefix = IPv4Validator.get_default_mask(ip_class)
                self.assertEqual((mask, prefix), expected)
    
    def test_ip_type_detection(self):
        """Test private, loopback, and multicast IP detection."""
        test_cases = [
            ("192.168.1.1", True, False, False),  # Private
            ("10.0.0.1", True, False, False),     # Private
            ("172.16.0.1", True, False, False),   # Private
            ("8.8.8.8", False, False, False),     # Public
            ("127.0.0.1", True, True, False),     # Loopback (considered private by ipaddress library)
            ("224.0.0.1", False, False, True),    # Multicast
        ]
        
        for ip_str, is_private, is_loopback, is_multicast in test_cases:
            with self.subTest(ip=ip_str):
                ip = ipaddress.IPv4Address(ip_str)
                self.assertEqual(IPv4Validator.is_private_ip(ip), is_private)
                self.assertEqual(IPv4Validator.is_loopback(ip), is_loopback)
                self.assertEqual(IPv4Validator.is_multicast(ip), is_multicast)


class TestSubnetCalculator(unittest.TestCase):
    """Test cases for SubnetCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ip_a = ipaddress.IPv4Address("10.0.0.0")
        self.ip_b = ipaddress.IPv4Address("172.16.0.0")
        self.ip_c = ipaddress.IPv4Address("192.168.1.0")
        
        self.calc_a = SubnetCalculator(self.ip_a, "A")
        self.calc_b = SubnetCalculator(self.ip_b, "B")
        self.calc_c = SubnetCalculator(self.ip_c, "C")
    
    def test_calculate_from_subnets_class_c(self):
        """Test subnet calculation based on number of subnets for Class C."""
        # Request 4 subnets from 192.168.1.0/24
        results = self.calc_c.calculate_from_subnets(4)
        
        self.assertEqual(results['ip_class'], 'C')
        self.assertEqual(results['original_ip'], '192.168.1.0')
        self.assertEqual(results['subnet_mask'], '255.255.255.192')
        self.assertEqual(results['prefix_length'], 26)
        self.assertEqual(results['wildcard_mask'], '0.0.0.63')
        self.assertEqual(results['total_subnets'], 4)
        self.assertEqual(results['hosts_per_subnet'], 62)
        self.assertEqual(results['subnet_bits'], 2)
        self.assertEqual(results['host_bits'], 6)
        self.assertEqual(len(results['subnets']), 4)
    
    def test_calculate_from_hosts_class_c(self):
        """Test subnet calculation based on hosts per subnet for Class C."""
        # Request 30 hosts per subnet from 192.168.1.0/24
        results = self.calc_c.calculate_from_hosts(30)
        
        self.assertEqual(results['ip_class'], 'C')
        self.assertEqual(results['subnet_mask'], '255.255.255.224')
        self.assertEqual(results['prefix_length'], 27)
        self.assertEqual(results['total_subnets'], 8)
        self.assertEqual(results['hosts_per_subnet'], 30)
        self.assertEqual(results['subnet_bits'], 3)
        self.assertEqual(results['host_bits'], 5)
    
    def test_calculate_from_subnets_class_b(self):
        """Test subnet calculation for Class B network."""
        # Request 256 subnets from 172.16.0.0/16
        results = self.calc_b.calculate_from_subnets(256)
        
        self.assertEqual(results['ip_class'], 'B')
        self.assertEqual(results['subnet_mask'], '255.255.255.0')
        self.assertEqual(results['prefix_length'], 24)
        self.assertEqual(results['total_subnets'], 256)
        self.assertEqual(results['hosts_per_subnet'], 254)
        self.assertEqual(results['subnet_bits'], 8)
    
    def test_calculate_from_subnets_class_a(self):
        """Test subnet calculation for Class A network."""
        # Request 4 subnets from 10.0.0.0/8
        results = self.calc_a.calculate_from_subnets(4)
        
        self.assertEqual(results['ip_class'], 'A')
        self.assertEqual(results['subnet_mask'], '255.192.0.0')
        self.assertEqual(results['prefix_length'], 10)
        self.assertEqual(results['total_subnets'], 4)
        self.assertEqual(results['subnet_bits'], 2)
    
    def test_get_subnet_details(self):
        """Test getting details of a specific subnet."""
        results = self.calc_c.calculate_from_subnets(4)
        first_subnet = results['subnets'][0]
        
        details = self.calc_c.get_subnet_details(first_subnet)
        
        self.assertEqual(details['network_address'], '192.168.1.0')
        self.assertEqual(details['broadcast_address'], '192.168.1.63')
        self.assertEqual(details['first_usable_ip'], '192.168.1.1')
        self.assertEqual(details['last_usable_ip'], '192.168.1.62')
        self.assertEqual(details['total_addresses'], 64)
        self.assertEqual(details['usable_addresses'], 62)
        self.assertEqual(details['subnet_mask'], '255.255.255.192')
        self.assertEqual(details['prefix_length'], 26)
    
    def test_error_handling_too_many_subnets(self):
        """Test error handling when requesting too many subnets."""
        with self.assertRaises(ValueError):
            # Try to create 2^25 subnets from a /24 (impossible)
            self.calc_c.calculate_from_subnets(33554432)
    
    def test_error_handling_too_many_hosts(self):
        """Test error handling when requesting too many hosts per subnet."""
        with self.assertRaises(ValueError):
            # Try to fit 300 hosts in a Class C network (impossible)
            self.calc_c.calculate_from_hosts(300)
    
    def test_edge_cases(self):
        """Test edge cases for subnet calculations."""
        # Test with 1 subnet (should work)
        results = self.calc_c.calculate_from_subnets(1)
        self.assertEqual(results['total_subnets'], 1)
        
        # Test with 1 host per subnet
        results = self.calc_c.calculate_from_hosts(1)
        self.assertEqual(results['hosts_per_subnet'], 2)  # Minimum is 2 (network + broadcast = 2 unusable)


class TestDependencyManager(unittest.TestCase):
    """Test cases for DependencyManager class."""
    
    def test_check_dependency_existing(self):
        """Test checking for existing dependencies."""
        # Test with a standard library module that should always exist
        self.assertTrue(DependencyManager.check_dependency("os"))
        self.assertTrue(DependencyManager.check_dependency("sys"))
    
    def test_check_dependency_nonexistent(self):
        """Test checking for non-existent dependencies."""
        # Test with a module that definitely doesn't exist
        self.assertFalse(DependencyManager.check_dependency("nonexistent_module_xyz123"))


class TestColors(unittest.TestCase):
    """Test cases for Colors class."""
    
    def test_colors_disabled(self):
        """Test Colors class with colors disabled."""
        colors = Colors(use_colors=False)
        
        self.assertFalse(colors.enabled)
        self.assertEqual(colors.RED, "")
        self.assertEqual(colors.GREEN, "")
        self.assertEqual(colors.BLUE, "")
        self.assertEqual(colors.RESET, "")
    
    def test_colors_enabled_without_colorama(self):
        """Test Colors class behavior when colorama is not available."""
        # This test assumes colorama might not be installed
        colors = Colors(use_colors=True)
        
        # Colors should either be enabled (if colorama is available) or disabled (if not)
        self.assertIsInstance(colors.enabled, bool)


class TestSubnettingScenarios(unittest.TestCase):
    """Test real-world subnetting scenarios."""
    
    def test_scenario_office_network(self):
        """Test typical office network subnetting scenario."""
        # Scenario: 192.168.1.0/24 network, need 6 departments with ~40 hosts each
        ip = ipaddress.IPv4Address("192.168.1.0")
        calc = SubnetCalculator(ip, "C")
        
        # Calculate for 40 hosts per subnet
        results = calc.calculate_from_hosts(40)
        
        # Should create /26 subnets (62 hosts each)
        self.assertEqual(results['prefix_length'], 26)
        self.assertEqual(results['hosts_per_subnet'], 62)
        self.assertEqual(results['total_subnets'], 4)
        
        # Verify first subnet details
        first_subnet = results['subnets'][0]
        details = calc.get_subnet_details(first_subnet)
        self.assertEqual(details['network_address'], '192.168.1.0')
        self.assertEqual(details['first_usable_ip'], '192.168.1.1')
        self.assertEqual(details['last_usable_ip'], '192.168.1.62')
        self.assertEqual(details['broadcast_address'], '192.168.1.63')
    
    def test_scenario_data_center(self):
        """Test data center subnetting scenario."""
        # Scenario: 10.0.0.0/8 network, need 1024 subnets
        ip = ipaddress.IPv4Address("10.0.0.0")
        calc = SubnetCalculator(ip, "A")
        
        results = calc.calculate_from_subnets(1024)
        
        # Should create /18 subnets
        self.assertEqual(results['prefix_length'], 18)
        self.assertEqual(results['total_subnets'], 1024)
        self.assertEqual(results['hosts_per_subnet'], 16382)
    
    def test_scenario_point_to_point_links(self):
        """Test point-to-point link subnetting scenario."""
        # Scenario: 192.168.0.0/24, need subnets for point-to-point links (2 hosts each)
        ip = ipaddress.IPv4Address("192.168.0.0")
        calc = SubnetCalculator(ip, "C")
        
        results = calc.calculate_from_hosts(2)
        
        # Should create /30 subnets (2 usable hosts each)
        self.assertEqual(results['prefix_length'], 30)
        self.assertEqual(results['hosts_per_subnet'], 2)
        self.assertEqual(results['total_subnets'], 64)


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestIPv4Validator,
        TestSubnetCalculator,
        TestDependencyManager,
        TestColors,
        TestSubnettingScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
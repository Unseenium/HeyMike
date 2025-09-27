#!/usr/bin/env python3
"""
Hey Mike! v2.0 Integration Test Suite
Comprehensive testing for voice command functionality
"""

import sys
import os
import logging
import time
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "Core"))
sys.path.insert(0, str(project_root / "Models"))
sys.path.insert(0, str(project_root / "Actions"))
sys.path.insert(0, str(project_root / "Security"))

def setup_logging():
    """Setup logging for tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_v2_components():
    """Test all v2.0 components"""
    print("🧪 Hey Mike! v2.0 Integration Test Suite")
    print("=" * 60)
    
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'details': []
    }
    
    # Test 1: MLX LLM Manager
    print("\n🧠 Testing MLX LLM Manager...")
    test_results['total_tests'] += 1
    try:
        from MLXLLMManager import MLXLLMManager
        llm_manager = MLXLLMManager()
        
        # Test model info
        models = llm_manager.get_available_models()
        model_info = llm_manager.get_model_info()
        
        if models and isinstance(models, dict):
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'MLX LLM Manager',
                'status': 'PASSED',
                'details': f"Found {len(models)} available models"
            })
            print(f"   ✅ MLX LLM Manager - {len(models)} models available")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'MLX LLM Manager',
                'status': 'FAILED',
                'error': 'No models found or invalid response'
            })
            print("   ❌ MLX LLM Manager - No models found")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'MLX LLM Manager',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ MLX LLM Manager - Error: {str(e)}")
    
    # Test 2: Wake Word Detector
    print("\n🎤 Testing Wake Word Detector...")
    test_results['total_tests'] += 1
    try:
        from WakeWordDetector import WakeWordDetector
        wake_detector = WakeWordDetector()
        
        # Test wake word detection
        test_cases = [
            ("Hey Mike, open Chrome", True),
            ("Hey mic, what's the weather?", True),
            ("Just talking about Mike", False),
            ("Hello Mike, search for Python", True)
        ]
        
        passed_cases = 0
        for text, expected in test_cases:
            result = wake_detector.is_command_mode_text(text)
            if result == expected:
                passed_cases += 1
        
        if passed_cases == len(test_cases):
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'Wake Word Detector',
                'status': 'PASSED',
                'details': f"All {len(test_cases)} test cases passed"
            })
            print(f"   ✅ Wake Word Detector - {passed_cases}/{len(test_cases)} test cases passed")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'Wake Word Detector',
                'status': 'FAILED',
                'error': f"Only {passed_cases}/{len(test_cases)} test cases passed"
            })
            print(f"   ❌ Wake Word Detector - Only {passed_cases}/{len(test_cases)} test cases passed")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'Wake Word Detector',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ Wake Word Detector - Error: {str(e)}")
    
    # Test 3: Command Processor
    print("\n⚙️ Testing Command Processor...")
    test_results['total_tests'] += 1
    try:
        from CommandProcessor import CommandProcessor
        processor = CommandProcessor()
        
        # Test command validation
        test_command = {
            'intent': 'app_control',
            'action': 'launch_app',
            'parameters': {'app_name': 'Chrome'},
            'confidence': 0.95
        }
        
        result = processor.process_command(test_command)
        stats = processor.get_processing_stats()
        
        if result and stats['total_commands'] > 0:
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'Command Processor',
                'status': 'PASSED',
                'details': f"Processed command successfully, stats: {stats}"
            })
            print(f"   ✅ Command Processor - Command processed successfully")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'Command Processor',
                'status': 'FAILED',
                'error': 'Command processing failed'
            })
            print("   ❌ Command Processor - Command processing failed")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'Command Processor',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ Command Processor - Error: {str(e)}")
    
    # Test 4: Action Executor
    print("\n🚀 Testing Action Executor...")
    test_results['total_tests'] += 1
    try:
        from ActionExecutor import ActionExecutor
        executor = ActionExecutor()
        
        # Test module loading
        modules_loaded = executor.load_action_modules()
        stats = executor.get_execution_stats()
        
        if modules_loaded and stats['modules_loaded']:
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'Action Executor',
                'status': 'PASSED',
                'details': f"Loaded {len(stats['available_modules'])} action modules"
            })
            print(f"   ✅ Action Executor - Loaded {len(stats['available_modules'])} action modules")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'Action Executor',
                'status': 'FAILED',
                'error': 'Failed to load action modules'
            })
            print("   ❌ Action Executor - Failed to load action modules")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'Action Executor',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ Action Executor - Error: {str(e)}")
    
    # Test 5: Action Modules
    print("\n📱 Testing Action Modules...")
    action_modules = [
        ('AppActions', 'AppActions'),
        ('WebActions', 'WebActions'),
        ('SystemActions', 'SystemActions'),
        ('TerminalActions', 'TerminalActions'),
        ('FileActions', 'FileActions')
    ]
    
    for module_name, class_name in action_modules:
        test_results['total_tests'] += 1
        try:
            module = __import__(module_name)
            action_class = getattr(module, class_name)
            action_instance = action_class()
            
            # Test module
            test_result = action_instance.test_module()
            
            if test_result['tests_passed'] > 0:
                test_results['passed_tests'] += 1
                test_results['details'].append({
                    'test': f'{module_name}',
                    'status': 'PASSED',
                    'details': f"{test_result['tests_passed']}/{test_result['tests_run']} tests passed"
                })
                print(f"   ✅ {module_name} - {test_result['tests_passed']}/{test_result['tests_run']} tests passed")
            else:
                test_results['failed_tests'] += 1
                test_results['details'].append({
                    'test': f'{module_name}',
                    'status': 'FAILED',
                    'error': f"No tests passed: {test_result}"
                })
                print(f"   ❌ {module_name} - No tests passed")
                
        except Exception as e:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': f'{module_name}',
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"   ❌ {module_name} - Error: {str(e)}")
    
    # Test 6: Command Validator
    print("\n🔒 Testing Command Validator...")
    test_results['total_tests'] += 1
    try:
        from CommandValidator import CommandValidator, ValidationResult
        validator = CommandValidator()
        
        # Test command validation
        safe_command = {
            'intent': 'app_control',
            'action': 'launch_app',
            'parameters': {'app_name': 'Chrome'},
            'confidence': 0.95
        }
        
        dangerous_command = {
            'intent': 'terminal',
            'action': 'run_command',
            'parameters': {'command': 'rm -rf /'},
            'confidence': 0.8
        }
        
        safe_result, safe_msg = validator.validate_command(safe_command)
        dangerous_result, dangerous_msg = validator.validate_command(dangerous_command)
        
        if safe_result == ValidationResult.APPROVED and dangerous_result == ValidationResult.REJECTED:
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'Command Validator',
                'status': 'PASSED',
                'details': 'Correctly validated safe and dangerous commands'
            })
            print("   ✅ Command Validator - Correctly validated commands")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'Command Validator',
                'status': 'FAILED',
                'error': f"Validation failed: safe={safe_result}, dangerous={dangerous_result}"
            })
            print(f"   ❌ Command Validator - Validation failed")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'Command Validator',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ Command Validator - Error: {str(e)}")
    
    # Test 7: Settings Integration
    print("\n⚙️ Testing Settings Integration...")
    test_results['total_tests'] += 1
    try:
        from AppSettings import AppSettings
        settings = AppSettings()
        
        # Test v2.0 settings
        v2_settings = [
            'command_mode_enabled',
            'llm_model',
            'wake_word_confidence',
            'restricted_commands_enabled',
            'terminal_access'
        ]
        
        settings_found = 0
        for setting in v2_settings:
            if setting in settings.default_settings:
                settings_found += 1
        
        if settings_found == len(v2_settings):
            test_results['passed_tests'] += 1
            test_results['details'].append({
                'test': 'Settings Integration',
                'status': 'PASSED',
                'details': f'All {len(v2_settings)} v2.0 settings found'
            })
            print(f"   ✅ Settings Integration - All {len(v2_settings)} v2.0 settings found")
        else:
            test_results['failed_tests'] += 1
            test_results['details'].append({
                'test': 'Settings Integration',
                'status': 'FAILED',
                'error': f'Only {settings_found}/{len(v2_settings)} v2.0 settings found'
            })
            print(f"   ❌ Settings Integration - Only {settings_found}/{len(v2_settings)} v2.0 settings found")
            
    except Exception as e:
        test_results['failed_tests'] += 1
        test_results['details'].append({
            'test': 'Settings Integration',
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"   ❌ Settings Integration - Error: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
    
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']} ✅")
    print(f"Failed: {test_results['failed_tests']} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if test_results['failed_tests'] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in test_results['details']:
            if detail['status'] == 'FAILED':
                print(f"   • {detail['test']}: {detail['error']}")
    
    print("\n🎯 NEXT STEPS:")
    if success_rate >= 80:
        print("   ✅ v2.0 implementation is ready for testing!")
        print("   🚀 Try running: python main.py")
        print("   🎤 Test voice commands: 'Hey Mike, open Calculator'")
    else:
        print("   ⚠️  Fix failing tests before proceeding")
        print("   🔧 Check dependencies and imports")
        
    return test_results

def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🔄 Testing End-to-End Workflow...")
    print("-" * 40)
    
    try:
        # Simulate complete workflow
        from WakeWordDetector import WakeWordDetector
        from MLXLLMManager import MLXLLMManager
        from CommandProcessor import CommandProcessor
        from ActionExecutor import ActionExecutor
        from CommandValidator import CommandValidator
        
        # Initialize components
        wake_detector = WakeWordDetector()
        llm_manager = MLXLLMManager()
        processor = CommandProcessor()
        executor = ActionExecutor()
        validator = CommandValidator()
        
        # Test workflow: "Hey Mike, open Calculator"
        test_input = "Hey Mike, open Calculator"
        
        print(f"1. Input: '{test_input}'")
        
        # Step 1: Wake word detection
        wake_result = wake_detector.detect_wake_word(test_input)
        if wake_result:
            print(f"2. Wake word detected: {wake_result['match_text']}")
            command_text = wake_result['command_text']
            print(f"3. Command extracted: '{command_text}'")
            
            # Step 2: Command interpretation (simulated - would need actual LLM)
            simulated_command = {
                'intent': 'app_control',
                'action': 'launch_app',
                'parameters': {'app_name': 'Calculator'},
                'confidence': 0.95,
                'raw_command': command_text
            }
            print(f"4. Command interpreted: {simulated_command['intent']}.{simulated_command['action']}")
            
            # Step 3: Command validation
            validation_result, validation_msg = validator.validate_command(simulated_command)
            print(f"5. Validation result: {validation_result.value}")
            
            # Step 4: Command processing
            processed_command = processor.process_command(simulated_command)
            if processed_command:
                print(f"6. Command processed: {processed_command['description']}")
                
                # Step 5: Action execution (simulated)
                executor.load_action_modules()
                print("7. Action modules loaded")
                print("8. ✅ End-to-end workflow completed successfully!")
                return True
            else:
                print("6. ❌ Command processing failed")
                return False
        else:
            print("2. ❌ Wake word not detected")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end workflow failed: {str(e)}")
        return False

if __name__ == "__main__":
    setup_logging()
    
    # Run component tests
    results = test_v2_components()
    
    # Run end-to-end test
    e2e_success = test_end_to_end_workflow()
    
    # Final status
    print("\n" + "🎉" * 20)
    if results['passed_tests'] >= results['total_tests'] * 0.8 and e2e_success:
        print("🎉 Hey Mike! v2.0 is ready for action! 🎉")
        print("Try saying: 'Hey Mike, open Chrome'")
    else:
        print("⚠️  Some issues need to be resolved first")
    print("🎉" * 20)

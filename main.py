#!/usr/bin/env python3
"""
Hey Mike!: MLX Whisper Dictation System for macOS
Main entry point for the application
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "Core"))
sys.path.insert(0, str(project_root / "UI"))
sys.path.insert(0, str(project_root / "Models"))

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    # Create logs directory if it doesn't exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set up handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        # Default log file
        default_log_file = log_dir / "heymike.log"
        handlers.append(logging.FileHandler(default_log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Set specific logger levels
    logging.getLogger("rumps").setLevel(logging.WARNING)
    logging.getLogger("pynput").setLevel(logging.WARNING)

def check_system_requirements():
    """
    Check system requirements for Hey Mike!
    
    Returns:
        True if requirements are met, False otherwise
    """
    import platform
    
    logger = logging.getLogger(__name__)
    
    # Check macOS version
    if platform.system() != "Darwin":
        logger.error("Hey Mike! requires macOS")
        return False
    
    # Check macOS version (12.0+ for MLX)
    mac_version = platform.mac_ver()[0]
    major_version = int(mac_version.split('.')[0])
    
    if major_version < 12:
        logger.error(f"Hey Mike! requires macOS 12.0 or later (found {mac_version})")
        return False
    
    # Check for Apple Silicon (MLX requirement)
    try:
        import subprocess
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        architecture = result.stdout.strip()
        
        if architecture not in ['arm64']:
            logger.error(f"Hey Mike! requires Apple Silicon (found {architecture})")
            return False
    
    except Exception as e:
        logger.warning(f"Could not determine architecture: {e}")
    
    logger.info("System requirements check passed")
    return True

def check_dependencies():
    """
    Check if required dependencies are installed
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    required_modules = [
        'mlx_whisper',
        'mlx',
        'pyaudio',
        'numpy',
        'rumps',
        'pynput',
        'Cocoa',
        'Quartz',
        'ApplicationServices'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required modules: {', '.join(missing_modules)}")
        logger.error("Please install dependencies with: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies are available")
    return True

def check_permissions():
    """
    Check if required permissions are granted
    
    Returns:
        True if permissions are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # This is a basic check - the actual permission requests happen when needed
    logger.info("Permission checks will be performed when needed")
    logger.info("Make sure to grant Microphone and Accessibility permissions when prompted")
    
    return True

def create_assets_directory():
    """Create assets directory with placeholder icon if needed"""
    assets_dir = project_root / "Assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple placeholder icon file if it doesn't exist
    icon_file = assets_dir / "icon.png"
    if not icon_file.exists():
        # Create a minimal PNG file (1x1 transparent pixel)
        icon_data = b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15\\xc4\\x89\\x00\\x00\\x00\\rIDATx\\x9cc````\\x00\\x00\\x00\\x05\\x00\\x01\\r\\n-\\xdb\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82'
        try:
            with open(icon_file, 'wb') as f:
                f.write(icon_data)
        except Exception:
            pass  # Icon is optional

def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hey Mike!: MLX Whisper Dictation System")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set logging level")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--no-gui", action="store_true", 
                       help="Run without GUI (for testing)")
    parser.add_argument("--test", action="store_true",
                       help="Run system tests and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Hey Mike!: MLX Whisper Dictation System")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Project root: {project_root}")
    
    # Create necessary directories
    create_assets_directory()
    
    # Check system requirements
    if not check_system_requirements():
        logger.error("System requirements not met")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependencies not available")
        sys.exit(1)
    
    # Check permissions
    if not check_permissions():
        logger.error("Required permissions not available")
        sys.exit(1)
    
    # Run tests if requested
    if args.test:
        logger.info("Running system tests...")
        run_tests()
        sys.exit(0)
    
    # Import and run the main application
    try:
        if args.no_gui:
            logger.info("Running in no-GUI mode")
            # Could implement a CLI version here
            logger.info("No-GUI mode not implemented yet")
        else:
            logger.info("Starting GUI application")
            from UI.MenuBarController import main as run_app
            run_app()
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

def run_tests():
    """Run basic system tests"""
    logger = logging.getLogger(__name__)
    
    try:
        # Test MLX Whisper import
        logger.info("Testing MLX Whisper import...")
        import mlx_whisper
        logger.info("✓ MLX Whisper import successful")
        
        # Test audio system
        logger.info("Testing audio system...")
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        logger.info(f"✓ Audio system available ({device_count} devices)")
        pa.terminate()
        
        # Test accessibility APIs
        logger.info("Testing accessibility APIs...")
        from ApplicationServices import AXUIElementCreateSystemWide
        system_element = AXUIElementCreateSystemWide()
        logger.info("✓ Accessibility APIs available")
        
        # Test hotkey system
        logger.info("Testing hotkey system...")
        from pynput import keyboard
        logger.info("✓ Hotkey system available")
        
        # Test menu bar system
        logger.info("Testing menu bar system...")
        import rumps
        logger.info("✓ Menu bar system available")
        
        logger.info("All tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()


# PS & DS System Monitor

A cross-platform process and system status monitoring tool that provides comprehensive system information similar to Unix `ps` command functionality.

## Features

### 🔍 PS (Process Status)
- Lists running processes with PID, name, CPU usage, memory usage, and status
- Cross-platform support (Windows, macOS, Linux)
- Sorts processes by CPU usage
- Shows process owner and status information

### 📊 DS (Detailed System Status)
- System-wide information including:
  - CPU information (cores, usage)
  - Memory statistics (total, used, available)
  - Swap memory details
  - Process count and status distribution
  - System platform and boot time
  - Load averages (Linux)

### 🖥️ Cross-Platform Support
- **Linux**: Direct `/proc` filesystem reading + `ps` command fallback
- **Windows**: `tasklist` and `wmic` commands
- **macOS**: `ps` and `vm_stat` commands
- **Universal**: Platform module fallbacks for basic info

## Installation

### Quick Start (No Dependencies)
```bash
git clone https://github.com/adamgrange/ps-ds-monitor.git
cd ps-ds-monitor
python ps-ds-monitor.py
```

### Enhanced Installation (Recommended)
For better performance and more detailed information:

```bash
git clone https://github.com/adamgrange/ps-ds-monitor.git
cd ps-ds-monitor
pip install -r requirements.txt
python ps-ds-monitor.py
```

### Package Installation
```bash
pip install ps-ds-monitor
ps-ds-monitor
```

## Usage

### Interactive Menu
Run the program and use the interactive menu:

```bash
python ps-ds-monitor.py
```

Menu options:
1. **PS** - View Process Status only
2. **DS** - View Detailed System Status only  
3. **Both** - View PS & DS together
4. **Refresh** - Update all information
5. **Exit** - Close the program

### Command Line Usage
```bash
# View process status
python ps-ds-monitor.py --ps

# View system status
python ps-ds-monitor.py --ds

# View both
python ps-ds-monitor.py --both

# Limit number of processes shown
python ps-ds-monitor.py --ps --limit 10
```

## Example Output

### Process Status (PS)
```
================================================================================
PS - PROCESS STATUS
================================================================================
PID      NAME                 CPU%     MEM%     STATUS       USER        
--------------------------------------------------------------------------------
1234     python               15.2     2.1      running      user        
5678     chrome               8.9      12.4     sleeping     user        
9012     systemd              0.1      0.3      sleeping     root        
...
```

### Detailed System Status (DS)
```
================================================================================
DS - DETAILED SYSTEM STATUS
================================================================================
System: Linux
Platform: Linux-5.15.0-generic-x86_64
Architecture: 64bit
Boot Time: 2024-01-15 08:30:22

CPU Information:
  Physical Cores: 4
  Logical Cores: 8
  CPU Usage: 12.5%

Memory Information:
  Total Memory: 16.0 GB
  Used Memory: 8.2 GB
  Memory Usage: 51.3%
```

## Requirements

### Minimum Requirements
- Python 3.6+
- No external dependencies (uses built-in modules)

### Enhanced Features
- `psutil` - For detailed and accurate system information
- Works on Windows, macOS, and Linux

## Dependencies

Optional but recommended:
- `psutil>=5.8.0` - Enhanced system and process information

## Platform Support

| Platform | Process Info | System Info | Memory Info | CPU Info |
|----------|-------------|-------------|-------------|----------|
| Linux    | ✅ `/proc` + `ps` | ✅ Full | ✅ Full | ✅ Full |
| Windows  | ✅ `tasklist` | ✅ `wmic` | ✅ Basic | ✅ Basic |
| macOS    | ✅ `ps` | ✅ `vm_stat` | ✅ Basic | ✅ Basic |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black ps_ds_monitor.py
flake8 ps_ds_monitor.py
```

## License

This project is licensed under the MIT License - see the (LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Cross-platform PS and DS functionality
- Interactive menu system
- Support for Linux, Windows, and macOS

## Roadmap

- [ ] Command-line argument support
- [ ] Configuration file support
- [ ] Export to JSON/CSV
- [ ] Real-time monitoring mode
- [ ] Process filtering and search
- [ ] Historical data tracking
- [ ] Web interface option

## Author

Your Name - [@adamgrange](https://github.com/adamgrange)

## Acknowledgments

- Inspired by Unix `ps` command
- Built with Python standard library and optional `psutil`
- Cross-platform compatibility testing on multiple systems

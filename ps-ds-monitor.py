#!/usr/bin/env python3
"""
PS & DS System Monitor
A cross-platform process and system status monitoring tool

PS (Process Status): Lists running processes with detailed information
DS (Detailed System status): System-wide statistics and information
"""

import os
import sys
import platform
import subprocess
import time
from collections import defaultdict
from typing import List, Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Note: psutil not available. Using fallback methods for some features.")


class SystemMonitor:
    """Cross-platform system and process monitoring utility"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.processes = []
        self.system_info = {}
        
    def get_process_status(self) -> List[Dict[str, Any]]:
        """Get process status information (PS functionality)"""
        if PSUTIL_AVAILABLE:
            return self._get_processes_psutil()
        else:
            return self._get_processes_fallback()
    
    def _get_processes_psutil(self) -> List[Dict[str, Any]]:
        """Get processes using psutil library with enhanced information"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'status', 'username', 'num_threads', 'memory_info',
                                           'create_time', 'nice', 'cmdline']):
                try:
                    # Get CPU percentage (this may take a moment on first call)
                    cpu_percent = proc.info['cpu_percent'] or proc.cpu_percent()
                    
                    # Get memory info in bytes
                    memory_info = proc.info.get('memory_info', None)
                    rss = memory_info.rss if memory_info else 0
                    vms = memory_info.vms if memory_info else 0
                    
                    process_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'] or 'Unknown',
                        'cpu_percent': round(cpu_percent, 1) if cpu_percent else 0.0,
                        'memory_percent': round(proc.info['memory_percent'] or 0.0, 1),
                        'status': proc.info['status'] or 'unknown',
                        'username': proc.info['username'] or 'unknown',
                        'num_threads': proc.info.get('num_threads', ''),
                        'rss': rss,
                        'vms': vms,
                        'nice': proc.info.get('nice', ''),
                        'create_time': proc.info.get('create_time', 0),
                        'cmdline': ' '.join(proc.info.get('cmdline', []))
                    }
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error getting processes: {e}")
            
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
    
    def _get_processes_fallback(self) -> List[Dict[str, Any]]:
        """Fallback method without psutil"""
        if self.system == 'windows':
            return self._get_processes_windows()
        else:
            return self._get_processes_unix()
    
    def _get_processes_windows(self) -> List[Dict[str, Any]]:
        """Get processes on Windows using tasklist"""
        processes = []
        try:
            result = subprocess.run(['tasklist', '/fo', 'csv'], 
                                  capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = [part.strip('"') for part in line.split('","')]
                if len(parts) >= 5:
                    # Convert memory from KB string to MB float
                    memory_str = parts[4].replace(',', '').replace(' K', '')
                    try:
                        memory_kb = float(memory_str)
                        memory_mb = round(memory_kb / 1024, 1)
                    except ValueError:
                        memory_mb = 0.0
                    
                    processes.append({
                        'pid': int(parts[1]),
                        'name': parts[0],
                        'cpu_percent': 0.0,  # Not available via tasklist
                        'memory_percent': 0.0,  # Would need total system memory
                        'memory_mb': memory_mb,
                        'status': parts[3] if len(parts) > 3 else 'unknown',
                        'username': 'unknown'
                    })
        except subprocess.CalledProcessError as e:
            print(f"Error running tasklist: {e}")
        except Exception as e:
            print(f"Error parsing tasklist output: {e}")
            
        return processes
    
    def _get_processes_unix(self) -> List[Dict[str, Any]]:
        """Get processes on Unix/Linux/macOS"""
        processes = []
        
        if self.system == 'linux' and os.path.exists('/proc'):
            processes = self._get_processes_proc()
        else:
            processes = self._get_processes_ps()
            
        return processes
    
    def _get_processes_proc(self) -> List[Dict[str, Any]]:
        """Get processes from /proc filesystem (Linux)"""
        processes = []
        try:
            for pid_dir in os.listdir('/proc'):
                if not pid_dir.isdigit():
                    continue
                    
                try:
                    pid = int(pid_dir)
                    stat_file = f'/proc/{pid}/stat'
                    status_file = f'/proc/{pid}/status'
                    
                    if os.path.exists(stat_file):
                        with open(stat_file, 'r') as f:
                            stat_data = f.read().split()
                            
                        name = stat_data[1].strip('()')
                        status = stat_data[2]
                        
                        # Get memory info from status file if available
                        memory_kb = 0
                        if os.path.exists(status_file):
                            with open(status_file, 'r') as f:
                                for line in f:
                                    if line.startswith('VmRSS:'):
                                        memory_kb = int(line.split()[1])
                                        break
                        
                        processes.append({
                            'pid': pid,
                            'name': name,
                            'cpu_percent': 0.0,  # Complex to calculate from /proc
                            'memory_percent': 0.0,
                            'memory_kb': memory_kb,
                            'status': status,
                            'username': 'unknown'
                        })
                        
                except (OSError, ValueError, IndexError):
                    continue
                    
        except OSError:
            pass
            
        return processes
    
    def _get_processes_ps(self) -> List[Dict[str, Any]]:
        """Get processes using ps command (Unix/macOS)"""
        processes = []
        try:
            # Use ps with format specifiers
            cmd = ['ps', 'axo', 'pid,comm,pcpu,pmem,stat,user']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split(None, 5)  # Split into max 6 parts
                if len(parts) >= 5:
                    try:
                        processes.append({
                            'pid': int(parts[0]),
                            'name': parts[1],
                            'cpu_percent': float(parts[2]),
                            'memory_percent': float(parts[3]),
                            'status': parts[4],
                            'username': parts[5] if len(parts) > 5 else 'unknown'
                        })
                    except ValueError:
                        continue
                        
        except subprocess.CalledProcessError as e:
            print(f"Error running ps command: {e}")
        except Exception as e:
            print(f"Error parsing ps output: {e}")
            
        return processes
    
    def get_detailed_system_status(self) -> Dict[str, Any]:
        """Get detailed system status information (DS functionality)"""
        if PSUTIL_AVAILABLE:
            return self._get_system_info_psutil()
        else:
            return self._get_system_info_fallback()
    
    def _get_system_info_psutil(self) -> Dict[str, Any]:
        """Get system information using psutil"""
        try:
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Process statistics
            process_count = len(psutil.pids())
            
            # Count processes by status
            status_counts = defaultdict(int)
            for proc in psutil.process_iter(['status']):
                try:
                    status_counts[proc.info['status']] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Boot time
            boot_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(psutil.boot_time()))
            
            return {
                'cpu_cores_physical': cpu_count,
                'cpu_cores_logical': cpu_count_logical,
                'cpu_percent': cpu_percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_percent': memory.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent,
                'process_count': process_count,
                'process_status_counts': dict(status_counts),
                'boot_time': boot_time,
                'system': platform.system(),
                'platform': platform.platform(),
                'architecture': platform.architecture()[0]
            }
            
        except Exception as e:
            print(f"Error getting system information: {e}")
            return {}
    
    def _get_system_info_fallback(self) -> Dict[str, Any]:
        """Fallback system information without psutil"""
        info = {
            'system': platform.system(),
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'cpu_cores_logical': os.cpu_count() or 'unknown'
        }
        
        # Try to get additional info based on system
        if self.system == 'linux':
            info.update(self._get_linux_system_info())
        elif self.system == 'darwin':
            info.update(self._get_macos_system_info())
        elif self.system == 'windows':
            info.update(self._get_windows_system_info())
            
        return info
    
    def _get_linux_system_info(self) -> Dict[str, Any]:
        """Get Linux-specific system information"""
        info = {}
        
        # Memory from /proc/meminfo
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_kb = int(line.split()[1])
                        info['memory_total_gb'] = round(total_kb / (1024**2), 2)
                    elif line.startswith('MemAvailable:'):
                        available_kb = int(line.split()[1])
                        info['memory_available_gb'] = round(available_kb / (1024**2), 2)
        except OSError:
            pass
            
        # Load average
        try:
            with open('/proc/loadavg', 'r') as f:
                load_avg = f.read().split()[:3]
                info['load_average'] = [float(x) for x in load_avg]
        except OSError:
            pass
            
        return info
    
    def _get_macos_system_info(self) -> Dict[str, Any]:
        """Get macOS-specific system information"""
        info = {}
        
        try:
            # Get memory info
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse vm_stat output (simplified)
                info['vm_stat_available'] = True
        except subprocess.CalledProcessError:
            pass
            
        return info
    
    def _get_windows_system_info(self) -> Dict[str, Any]:
        """Get Windows-specific system information"""
        info = {}
        
        try:
            # Get system info using wmic
            result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory', '/value'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'TotalPhysicalMemory=' in line:
                        memory_bytes = int(line.split('=')[1])
                        info['memory_total_gb'] = round(memory_bytes / (1024**3), 2)
        except (subprocess.CalledProcessError, ValueError):
            pass
            
        return info
    
    def display_process_status(self, page_size: int = 50):
        """Display PS (Process Status) information with paging support"""
        processes = self.get_process_status()
        
        if not processes:
            print("No process information available.")
            return
            
        total_processes = len(processes)
        current_page = 0
        
        while True:
            # Clear screen (cross-platform)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            start_idx = current_page * page_size
            end_idx = start_idx + page_size
            current_processes = processes[start_idx:end_idx]
            
            # Display header
            print("\n" + "="*100)
            print(f"PS - PROCESS STATUS (Page {current_page + 1}/{(total_processes + page_size - 1) // page_size})")
            print("="*100)
            
            # Enhanced header with more detailed column names
            print(f"{'PID':<8} {'NAME':<25} {'CPU%':<8} {'MEM%':<8} {'STATUS':<12} {'USER':<15} {'THREADS':<8}")
            print("-" * 100)
            
            # Display current page of processes with enhanced information
            for proc in current_processes:
                thread_count = proc.get('num_threads', '')  # Add thread count if available from psutil
                print(f"{proc['pid']:<8} {proc['name'][:24]:<25} "
                      f"{proc['cpu_percent']:<8.1f} {proc.get('memory_percent', 0.0):<8.1f} "
                      f"{proc['status'][:11]:<12} {proc['username'][:14]:<15} {thread_count:<8}")
            
            # Footer with statistics and navigation help
            print("\n" + "-"*100)
            print(f"Total Processes: {total_processes} | "
                  f"Showing {start_idx + 1}-{min(end_idx, total_processes)} | "
                  f"CPU Intensive: {sum(1 for p in processes if p['cpu_percent'] > 10.0)} | "
                  f"Memory Intensive: {sum(1 for p in processes if p.get('memory_percent', 0) > 10.0)}")
            print("\nNavigation: [N]ext page | [P]revious page | [F]irst page | [L]ast page | [Q]uit to menu")
            
            # Get user input for navigation
            choice = input("\nEnter choice: ").lower()
            if choice == 'n' and end_idx < total_processes:
                current_page += 1
            elif choice == 'p' and current_page > 0:
                current_page -= 1
            elif choice == 'f':
                current_page = 0
            elif choice == 'l':
                current_page = (total_processes - 1) // page_size
            elif choice == 'q':
                break
    
    def display_detailed_system_status(self):
        """Display DS (Detailed System Status) information"""
        print("\n" + "="*80)
        print("DS - DETAILED SYSTEM STATUS")
        print("="*80)
        
        info = self.get_detailed_system_status()
        
        if not info:
            print("System information not available.")
            return
        
        # System Information
        print(f"System: {info.get('system', 'unknown')}")
        print(f"Platform: {info.get('platform', 'unknown')}")
        print(f"Architecture: {info.get('architecture', 'unknown')}")
        
        if 'boot_time' in info:
            print(f"Boot Time: {info['boot_time']}")
        
        # CPU Information
        print(f"\nCPU Information:")
        if 'cpu_cores_physical' in info:
            print(f"  Physical Cores: {info['cpu_cores_physical']}")
        if 'cpu_cores_logical' in info:
            print(f"  Logical Cores: {info['cpu_cores_logical']}")
        if 'cpu_percent' in info:
            print(f"  CPU Usage: {info['cpu_percent']}%")
        
        # Memory Information
        print(f"\nMemory Information:")
        if 'memory_total_gb' in info:
            print(f"  Total Memory: {info['memory_total_gb']} GB")
        if 'memory_used_gb' in info:
            print(f"  Used Memory: {info['memory_used_gb']} GB")
        if 'memory_percent' in info:
            print(f"  Memory Usage: {info['memory_percent']}%")
        
        # Swap Information
        if 'swap_total_gb' in info and info['swap_total_gb'] > 0:
            print(f"\nSwap Information:")
            print(f"  Total Swap: {info['swap_total_gb']} GB")
            print(f"  Used Swap: {info['swap_used_gb']} GB")
            print(f"  Swap Usage: {info['swap_percent']}%")
        
        # Process Information
        if 'process_count' in info:
            print(f"\nProcess Information:")
            print(f"  Total Processes: {info['process_count']}")
            
            if 'process_status_counts' in info:
                print(f"  Process Status Distribution:")
                for status, count in sorted(info['process_status_counts'].items()):
                    print(f"    {status}: {count}")
        
        # Additional system-specific info
        if 'load_average' in info:
            print(f"\nLoad Average: {' '.join(map(str, info['load_average']))}")


def display_menu():
    """Display the interactive menu"""
    print("\n" + "="*50)
    print("PS & DS SYSTEM MONITOR")
    print("="*50)
    print("1. PS - View Process Status")
    print("2. DS - View Detailed System Status")
    print("3. Both - View PS & DS Together")
    print("4. Refresh/Update Information")
    print("5. Exit")
    print("-" * 50)


def main():
    """Main program loop"""
    monitor = SystemMonitor()
    
    print("PS & DS System Monitor")
    print("Cross-platform Process and System Status Tool")
    
    if not PSUTIL_AVAILABLE:
        print("\nNote: For enhanced features, install psutil: pip install psutil")
    
    while True:
        display_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                monitor.display_process_status()
            elif choice == '2':
                monitor.display_detailed_system_status()
            elif choice == '3':
                monitor.display_process_status()
                monitor.display_detailed_system_status()
            elif choice == '4':
                print("\nRefreshing system information...")
                monitor = SystemMonitor()  # Reinitialize
                print("Information updated.")
            elif choice == '5':
                print("\nExiting PS & DS System Monitor. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n\nExiting PS & DS System Monitor. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
